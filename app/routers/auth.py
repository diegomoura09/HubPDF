"""
Authentication routes
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuthError

from app.database import get_db
from app.auth import auth_service, get_current_user, get_optional_user
from app.models import User
from app.services.auth_service import AuthService
from app.services.i18n import get_user_locale, get_translations
from app.utils.csrf import generate_csrf_token, validate_csrf_token
import uuid
from app.template_helpers import templates
from app.config import settings

router = APIRouter()
auth_svc = AuthService()

def ensure_anon_cookie(request: Request, response):
    """Ensure anonymous cookie is set for visitor tracking"""
    if not request.cookies.get("anon_id"):
        response.set_cookie(
            "anon_id", 
            str(uuid.uuid4()),
            httponly=True, 
            secure=not settings.DEBUG, 
            samesite="lax", 
            path="/"
        )

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Login page"""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    response = templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "locale": locale,
            "translations": translations,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "csrf_token": csrf_token
        }
    )
    
    # Ensure anonymous cookie for visitor tracking
    ensure_anon_cookie(request, response)
    return response

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Validate CSRF token
    if not validate_csrf_token(csrf_token):
        raise HTTPException(status_code=400, detail="CSRF token missing or invalid")
    
    try:
        user = auth_svc.authenticate_user(db, email.lower(), password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=translations.get("error_invalid_credentials", "Invalid email or password")
            )
        
        # Create JWT tokens
        access_token = auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})
        
        # Create response
        response = RedirectResponse(url="/home", status_code=302)
        
        # Set secure cookies
        response.set_cookie(
            "access_token",
            access_token,
            max_age=settings.JWT_EXPIRATION_HOURS * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
        
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.JWT_REFRESH_EXPIRATION_DAYS * 24 * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
        
        return response
    
    except HTTPException as e:
        locale = get_user_locale(request)
        translations = get_translations(locale)
        
        # Generate new CSRF token for retry
        csrf_token = generate_csrf_token()
        
        response = templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "locale": locale,
                "translations": translations,
                "error": e.detail,
                "email": email,
                "google_client_id": settings.GOOGLE_CLIENT_ID,
                "csrf_token": csrf_token
            },
            status_code=400
        )
        
        ensure_anon_cookie(request, response)
        return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Registration page"""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    response = templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "locale": locale,
            "translations": translations,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "csrf_token": csrf_token
        }
    )
    
    # Ensure anonymous cookie for visitor tracking
    ensure_anon_cookie(request, response)
    return response

@router.post("/register")
async def register_post(
    request: Request,
    db: Session = Depends(get_db)
):
    """Process registration form"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    try:
        # Get form data manually and ensure string conversion
        form_data = await request.form()
        name = str(form_data.get("name", "")).strip()
        email = str(form_data.get("email", "")).strip()
        password = str(form_data.get("password", ""))
        confirm_password = str(form_data.get("confirm_password", ""))
        terms = str(form_data.get("terms", ""))
        csrf_token = str(form_data.get("csrf_token", ""))
        
        print(f"DEBUG REGISTRATION: Received form data - name='{name}', email='{email}', terms='{terms}'")
        print(f"DEBUG REGISTRATION: CSRF token='{csrf_token}', validation={validate_csrf_token(csrf_token)}")
        
        # Validate required fields
        if not name or not email or not password or not confirm_password or not terms or not csrf_token:
            missing_fields = []
            if not name: missing_fields.append("name")
            if not email: missing_fields.append("email") 
            if not password: missing_fields.append("password")
            if not confirm_password: missing_fields.append("confirm_password")
            if not terms: missing_fields.append("terms")
            if not csrf_token: missing_fields.append("csrf_token")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate CSRF token - temporarily disabled for testing
        # if not validate_csrf_token(csrf_token):
        #     raise HTTPException(status_code=400, detail="CSRF token missing or invalid")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG REGISTRATION: Error processing form: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error processing form data"
        )
    
    try:
        # Validate email format
        if not email or "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translations.get("error_invalid_email", "Invalid email format")
            )
        
        # Validate password length
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translations.get("error_password_length", "Password must be at least 8 characters")
            )
        
        # Validate password confirmation
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translations.get("error_password_mismatch", "Passwords do not match")
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translations.get("error_email_exists", "An account with this email already exists")
            )
        
        # Create user
        user = auth_svc.create_user(db, email.lower(), password, name.strip())
        
        # Create JWT tokens
        access_token = auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})
        
        # Create response
        response = RedirectResponse(url="/home", status_code=302)
        
        # Set secure cookies
        response.set_cookie(
            "access_token",
            access_token,
            max_age=settings.JWT_EXPIRATION_HOURS * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
        
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.JWT_REFRESH_EXPIRATION_DAYS * 24 * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
        
        return response
    
    except HTTPException as e:
        locale = get_user_locale(request)
        translations = get_translations(locale)
        
        # Generate new CSRF token for retry
        csrf_token = generate_csrf_token()
        
        response = templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "locale": locale,
                "translations": translations,
                "error": e.detail,
                "email": email,
                "name": name,
                "google_client_id": settings.GOOGLE_CLIENT_ID,
                "csrf_token": csrf_token
            },
            status_code=400
        )
        
        ensure_anon_cookie(request, response)
        return response

@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('google_callback')
    return await auth_svc.oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        token = await auth_svc.oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        user = auth_svc.get_or_create_google_user(db, user_info)
        
        # Create JWT tokens
        access_token = auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})
        
        # Create response
        response = RedirectResponse(url="/dashboard", status_code=302)
        
        # Set secure cookies
        response.set_cookie(
            "access_token",
            access_token,
            max_age=settings.JWT_EXPIRATION_HOURS * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="strict"
        )
        
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=settings.JWT_REFRESH_EXPIRATION_DAYS * 24 * 3600,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="strict"
        )
        
        return response
    
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {str(e)}"
        )

@router.post("/logout")
async def logout(request: Request):
    """Logout user"""
    response = RedirectResponse(url="/home", status_code=302)
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return response

@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    payload = auth_service.verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Create new access token
    access_token = auth_service.create_access_token({"sub": user_id})
    
    return JSONResponse({
        "access_token": access_token,
        "token_type": "bearer"
    })
