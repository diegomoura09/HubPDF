"""
Billing and subscription routes
"""
import hmac
import hashlib
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_auth, get_optional_user
from app.models import User, Subscription
from app.services.billing_service import BillingService
from app.template_helpers import templates
from app.config import settings

router = APIRouter()
billing_service = BillingService()

@router.get("/pricing", response_class=HTMLResponse)
async def pricing(
    request: Request,
    user: User = Depends(get_optional_user)
):
    """Pricing page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    plans = [
        {
            "name": "free",
            "price": 0.00,
            "price_display": "R$ 0",
            "subtitle": "/mês",
            "popular": False,
            "features": [
                "10+ ferramentas de gerenciamento de documentos",
                "Downloads limitados de documentos", 
                "Marca d'água após 4ª operação",
                "Acesso limitado"
            ]
        },
        {
            "name": "pro",
            "price": settings.PLAN_PRICES["pro"],
            "price_display": "R$ 9",
            "subtitle": "/mês",
            "annual_price": "Cobrado como R$ 108/ano",
            "popular": True,
            "features": [
                "Acesso ilimitado a todas as ferramentas",
                "Downloads ilimitados de documentos",
                "Compressão forte",
                "Sem marcas d'água",
                "Acesso completo"
            ]
        },
        {
            "name": "custom",
            "price": 0,
            "price_display": "Personalizado",
            "subtitle": "Fale com nossa equipe para obter uma oferta personalizada",
            "popular": False,
            "contact": True,
            "features": [
                "Preços personalizados",
                "Opções flexíveis de pagamento",
                "Suporte dedicado ao cliente",
                "Acesso completo"
            ]
        }
    ]
    
    return templates.TemplateResponse(
        "billing/pricing.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations,
            "plans": plans
        }
    )

@router.post("/checkout")
async def create_checkout(
    request: Request,
    plan: str = Form(...),
    coupon_code: str = Form(None),
    user: User = Depends(require_auth)
):
    """Create Mercado Pago checkout preference"""
    try:
        if plan not in ["pro", "custom"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )
        
        # Create checkout preference
        preference = billing_service.create_checkout_preference(user, plan, coupon_code)
        
        # Redirect to Mercado Pago checkout
        return RedirectResponse(
            url=preference["init_point"],
            status_code=302
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout: {str(e)}"
        )

@router.post("/webhook")
async def mercado_pago_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Mercado Pago webhook notifications"""
    try:
        # Get request body
        body = await request.body()
        
        # Verify signature
        signature = request.headers.get("x-signature", "")
        if not billing_service.verify_webhook_signature(body, signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid signature"
            )
        
        # Parse notification
        import json
        notification = json.loads(body)
        
        # Process payment notification
        if notification.get("type") == "payment":
            payment_id = notification.get("data", {}).get("id")
            if payment_id:
                background_tasks.add_task(
                    billing_service.process_payment_notification,
                    db, payment_id
                )
        
        return {"status": "ok"}
    
    except Exception as e:
        # Log error but return success to avoid webhook retries
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    user: User = Depends(require_auth)
):
    """Payment success page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "billing/success.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/failure", response_class=HTMLResponse)
async def payment_failure(
    request: Request,
    user: User = Depends(require_auth)
):
    """Payment failure page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "billing/failure.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )

@router.get("/pending", response_class=HTMLResponse)
async def payment_pending(
    request: Request,
    user: User = Depends(require_auth)
):
    """Payment pending page"""
    locale = get_user_locale(request)
    translations = get_translations(locale)
    
    return templates.TemplateResponse(
        "billing/pending.html",
        {
            "request": request,
            "user": user,
            "locale": locale,
            "translations": translations
        }
    )
