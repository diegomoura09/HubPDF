"""
Main application routes
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_optional_user, get_current_user
from app.models import User
from app.services.quota_service import QuotaService
from app.template_helpers import templates

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
    # Get usage summary if user is logged in
    usage_summary = None
    if user:
        usage_summary = quota_service.get_usage_summary(db, user)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "usage_summary": usage_summary
        }
    )

@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """About page"""
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/privacy", response_class=HTMLResponse)
async def privacy(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Privacy policy page"""
    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/terms", response_class=HTMLResponse)
async def terms(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Terms of service page"""
    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "user": user
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
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """User dashboard"""
    # Get user statistics
    usage_summary = quota_service.get_usage_summary(db, user)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
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
    # Get user statistics
    usage_summary = quota_service.get_usage_summary(db, user)
    
    return templates.TemplateResponse(
        "account/plan.html",
        {
            "request": request,
            "user": user,
            "usage_summary": usage_summary
        }
    )
