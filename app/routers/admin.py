"""
Admin panel routes for HubPDF
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.database import get_db
from app.auth import require_admin
from app.models import User, Subscription, Invoice, Coupon, AuditLog, QuotaUsage
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.quota_service import QuotaService
from app.template_helpers import templates
from app.utils.validators import InputValidator

router = APIRouter()
auth_service = AuthService()
billing_service = BillingService()
quota_service = QuotaService()

def log_admin_action(db: Session, admin_user: User, action: str, target_type: str, target_id: int, details: str = None):
    """Log admin action for audit trail"""
    audit_log = AuditLog(
        admin_user_id=admin_user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.add(audit_log)
    db.commit()

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin dashboard with KPIs"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Calculate KPIs
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    active_subscriptions = db.query(Subscription).filter(
        Subscription.status == "active"
    ).count()
    
    # Revenue calculation (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_revenue = db.query(func.sum(Invoice.amount)).filter(
        and_(
            Invoice.status == "paid",
            Invoice.paid_at >= thirty_days_ago
        )
    ).scalar() or 0
    
    # User registrations (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_registrations = db.query(User).filter(
        User.created_at >= seven_days_ago
    ).count()
    
    # Recent audit logs
    recent_logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(10).all()
    
    kpis = {
        "total_users": total_users,
        "active_users": active_users,
        "active_subscriptions": active_subscriptions,
        "recent_revenue": recent_revenue,
        "recent_registrations": recent_registrations
    }
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "kpis": kpis,
            "recent_logs": recent_logs
        }
    )

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    search: str = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """User management page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Build query
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.contains(search)) |
            (User.name.contains(search))
        )
    
    # Pagination
    per_page = 20
    offset = (page - 1) * per_page
    users = query.order_by(desc(User.created_at)).offset(offset).limit(per_page).all()
    total_users = query.count()
    
    total_pages = (total_users + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "users": users,
            "search": search or "",
            "page": page,
            "total_pages": total_pages,
            "total_users": total_users
        }
    )

@router.post("/users/{user_id}/update-plan")
async def update_user_plan(
    user_id: int,
    plan: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update user plan"""
    if plan not in ["free", "pro", "business"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_plan = user.plan
    user.plan = plan
    db.commit()
    
    # Log admin action
    log_admin_action(
        db, admin, "update_plan", "user", user_id,
        f"Changed plan from {old_plan} to {plan}"
    )
    
    return JSONResponse({"status": "success", "message": "Plan updated successfully"})

@router.post("/users/{user_id}/reset-quota")
async def reset_user_quota(
    user_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Reset user daily quota"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    quota_service.reset_daily_quota(db, user)
    
    # Log admin action
    log_admin_action(db, admin, "reset_quota", "user", user_id, "Reset daily quota")
    
    return JSONResponse({"status": "success", "message": "Quota reset successfully"})

@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Toggle user active status"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    action = "activate" if user.is_active else "deactivate"
    log_admin_action(db, admin, action, "user", user_id, f"User {action}d")
    
    return JSONResponse({
        "status": "success", 
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "is_active": user.is_active
    })

@router.post("/users/{user_id}/promote")
async def promote_user(
    user_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Promote user to admin"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = "admin"
    db.commit()
    
    log_admin_action(db, admin, "promote", "user", user_id, "Promoted to admin")
    
    return JSONResponse({"status": "success", "message": "User promoted to admin successfully"})

@router.get("/subscriptions", response_class=HTMLResponse)
async def admin_subscriptions(
    request: Request,
    status_filter: str = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Subscription management page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Build query
    query = db.query(Subscription).join(User)
    
    if status_filter and status_filter in ["active", "cancelled", "expired"]:
        query = query.filter(Subscription.status == status_filter)
    
    # Pagination
    per_page = 20
    offset = (page - 1) * per_page
    subscriptions = query.order_by(desc(Subscription.created_at)).offset(offset).limit(per_page).all()
    total_subscriptions = query.count()
    
    total_pages = (total_subscriptions + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "admin/subscriptions.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "subscriptions": subscriptions,
            "status_filter": status_filter or "",
            "page": page,
            "total_pages": total_pages,
            "total_subscriptions": total_subscriptions
        }
    )

@router.post("/subscriptions/{subscription_id}/extend")
async def extend_subscription(
    subscription_id: int,
    days: int = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Extend subscription period"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    subscription.current_period_end += timedelta(days=days)
    db.commit()
    
    log_admin_action(
        db, admin, "extend_subscription", "subscription", subscription_id,
        f"Extended by {days} days"
    )
    
    return JSONResponse({"status": "success", "message": f"Subscription extended by {days} days"})

@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Cancel subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    billing_service.cancel_subscription(db, subscription)
    
    log_admin_action(db, admin, "cancel_subscription", "subscription", subscription_id)
    
    return JSONResponse({"status": "success", "message": "Subscription cancelled successfully"})

@router.get("/coupons", response_class=HTMLResponse)
async def admin_coupons(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Coupon management page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    coupons = db.query(Coupon).order_by(desc(Coupon.created_at)).all()
    
    return templates.TemplateResponse(
        "admin/coupons.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "coupons": coupons
        }
    )

@router.post("/coupons")
async def create_coupon(
    code: str = Form(...),
    discount_percent: float = Form(...),
    valid_from: str = Form(...),
    valid_until: str = Form(...),
    usage_limit: Optional[int] = Form(None),
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create new coupon"""
    try:
        # Validate dates
        valid_from_date = datetime.strptime(valid_from, "%Y-%m-%d").date()
        valid_until_date = datetime.strptime(valid_until, "%Y-%m-%d").date()
        
        if valid_from_date >= valid_until_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid from date must be before valid until date"
            )
        
        # Check if coupon code already exists
        existing_coupon = db.query(Coupon).filter(Coupon.code == code).first()
        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon code already exists"
            )
        
        coupon = Coupon(
            code=code,
            discount_percent=discount_percent,
            valid_from=valid_from_date,
            valid_until=valid_until_date,
            usage_limit=usage_limit,
            is_active=True
        )
        
        db.add(coupon)
        db.commit()
        db.refresh(coupon)
        
        log_admin_action(db, admin, "create_coupon", "coupon", coupon.id, f"Created coupon {code}")
        
        return JSONResponse({"status": "success", "message": "Coupon created successfully"})
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format"
        )

@router.post("/coupons/{coupon_id}/toggle")
async def toggle_coupon(
    coupon_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Toggle coupon active status"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    coupon.is_active = not coupon.is_active
    db.commit()
    
    action = "activate" if coupon.is_active else "deactivate"
    log_admin_action(db, admin, f"{action}_coupon", "coupon", coupon_id)
    
    return JSONResponse({
        "status": "success",
        "message": f"Coupon {'activated' if coupon.is_active else 'deactivated'} successfully",
        "is_active": coupon.is_active
    })

@router.get("/invoices", response_class=HTMLResponse)
async def admin_invoices(
    request: Request,
    status_filter: str = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Invoice management page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Build query
    query = db.query(Invoice).join(Subscription).join(User)
    
    if status_filter and status_filter in ["pending", "paid", "failed", "cancelled"]:
        query = query.filter(Invoice.status == status_filter)
    
    # Pagination
    per_page = 20
    offset = (page - 1) * per_page
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(per_page).all()
    total_invoices = query.count()
    
    total_pages = (total_invoices + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "admin/invoices.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "invoices": invoices,
            "status_filter": status_filter or "",
            "page": page,
            "total_pages": total_pages,
            "total_invoices": total_invoices
        }
    )

@router.get("/audit-logs", response_class=HTMLResponse)
async def admin_audit_logs(
    request: Request,
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Audit logs page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    # Pagination
    per_page = 50
    offset = (page - 1) * per_page
    logs = db.query(AuditLog).join(User).order_by(desc(AuditLog.created_at)).offset(offset).limit(per_page).all()
    total_logs = db.query(AuditLog).count()
    
    total_pages = (total_logs + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "admin/audit_logs.html",
        {
            "request": request,
            "user": admin,
            "locale": locale,
            "translations": translations,
            "logs": logs,
            "page": page,
            "total_pages": total_pages,
            "total_logs": total_logs
        }
    )
