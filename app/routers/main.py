"""
Main application routes
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_optional_user, get_current_user
from app.models import User
from app.services.i18n import get_user_locale, set_user_locale, get_translations
from app.services.quota_service import QuotaService
from app.template_helpers import get_template_response, templates

router = APIRouter()
quota_service = QuotaService()

@router.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to home page"""
    return RedirectResponse(url="/home", status_code=302)

@router.get("/home", response_class=HTMLResponse)
async def home(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_optional_user)
):
    """Home page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Get usage summary if user is logged in
    usage_summary = None
    if user:
        usage_summary = quota_service.get_usage_summary(db, user)
    
    return get_template_response(
        "index.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations,
            "usage_summary": usage_summary
        },
        locale
    )

@router.post("/set-language")
async def set_language(
    request: Request,
    language: str = Form(...),
    redirect_url: str = Form(default="/home")
):
    """Set user language preference"""
    if language not in ["pt", "en"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language"
        )
    
    response = RedirectResponse(url=redirect_url, status_code=302)
    set_user_locale(response, language)
    
    return response

@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """About page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/privacy", response_class=HTMLResponse)
async def privacy(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Privacy policy page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/terms", response_class=HTMLResponse)
async def terms(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Terms of service page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "hubpdf"}

@router.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Contact page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """User dashboard"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Get user statistics
    usage_summary = quota_service.get_usage_summary(db, user)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations,
            "usage_summary": usage_summary
        }
    )

@router.get("/account/plan", response_class=HTMLResponse)
async def account_plan(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """User account plan page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Get user statistics
    usage_summary = quota_service.get_usage_summary(db, user)
    
    return templates.TemplateResponse(
        "account/plan.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations,
            "usage_summary": usage_summary
        }
    )
