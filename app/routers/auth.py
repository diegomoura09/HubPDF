"""
Authentication routes
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuthError

from app.database import get_db
from app.auth import auth_service, get_current_user, get_optional_user
from app.models import User
from app.services.auth_service import AuthService
from app.services.i18n import get_user_locale, get_translations
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
auth_svc = AuthService()

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
    
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "locale": locale,
            "translations": translations,
            "google_client_id": settings.GOOGLE_CLIENT_ID
        }
    )

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form"""
    try:
        user = auth_svc.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
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
    
    except HTTPException as e:
        locale = get_user_locale(request)
        translations = get_translations(locale)
        
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "locale": locale,
                "translations": translations,
                "error": e.detail,
                "email": email,
                "google_client_id": settings.GOOGLE_CLIENT_ID
            },
            status_code=400
        )

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
    
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "locale": locale,
            "translations": translations,
            "google_client_id": settings.GOOGLE_CLIENT_ID
        }
    )

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process registration form"""
    try:
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        user = auth_svc.create_user(db, email, password, name)
        
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
    
    except HTTPException as e:
        locale = get_user_locale(request)
        translations = get_translations(locale)
        
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "locale": locale,
                "translations": translations,
                "error": e.detail,
                "email": email,
                "name": name,
                "google_client_id": settings.GOOGLE_CLIENT_ID
            },
            status_code=400
        )

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
