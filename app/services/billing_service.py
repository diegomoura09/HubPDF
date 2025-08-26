"""
Billing service for Mercado Pago integration
"""
import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import User, Subscription, Invoice, Coupon
from app.config import settings
from app.utils.security import verify_webhook_signature

class BillingService:
    """Service for handling billing and Mercado Pago integration"""
    
    def __init__(self):
        self.access_token = settings.MP_ACCESS_TOKEN
        self.webhook_secret = settings.MP_WEBHOOK_SECRET
        self.base_url = "https://api.mercadopago.com"
    
    def create_checkout_preference(self, user: User, plan: str, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        """Create Mercado Pago checkout preference"""
        if plan not in ["pro", "business"]:
            raise ValueError("Invalid plan")
        
        price = settings.PLAN_PRICES[plan]
        
        # Apply coupon if provided
        if coupon_code:
            # This would be implemented with actual coupon logic
            pass
        
        preference_data = {
            "items": [
                {
                    "title": f"HubPDF {plan.capitalize()} Plan",
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": user.email,
                "name": user.name
            },
            "back_urls": {
                "success": f"{settings.DOMAIN}/billing/success",
                "failure": f"{settings.DOMAIN}/billing/failure",
                "pending": f"{settings.DOMAIN}/billing/pending"
            },
            "auto_return": "approved",
            "notification_url": f"{settings.DOMAIN}/billing/webhook",
            "external_reference": f"{user.id}:{plan}",
            "expires": True,
            "expiration_date_from": datetime.now().isoformat(),
            "expiration_date_to": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/checkout/preferences",
            json=preference_data,
            headers=headers
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create preference: {response.text}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Mercado Pago webhook signature"""
        return verify_webhook_signature(payload, signature, self.webhook_secret)
    
    def process_payment_notification(self, db: Session, payment_id: str) -> bool:
        """Process payment notification from Mercado Pago"""
        # Get payment details from Mercado Pago
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.get(
            f"{self.base_url}/v1/payments/{payment_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            return False
        
        payment_data = response.json()
        
        # Check if payment is approved
        if payment_data.get("status") != "approved":
            return False
        
        # Extract user and plan from external_reference
        external_reference = payment_data.get("external_reference", "")
        if ":" not in external_reference:
            return False
        
        try:
            user_id, plan = external_reference.split(":", 1)
            user_id = int(user_id)
        except ValueError:
            return False
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Create or update subscription
        self.create_subscription(db, user, plan, payment_data)
        
        return True
    
    def create_subscription(self, db: Session, user: User, plan: str, payment_data: Dict[str, Any]) -> Subscription:
        """Create new subscription for user"""
        # Cancel existing subscriptions
        existing_subs = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).all()
        
        for sub in existing_subs:
            sub.status = "cancelled"
        
        # Create new subscription
        start_date = date.today()
        end_date = start_date + timedelta(days=30)  # Monthly subscription
        
        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            status="active",
            mp_subscription_id=payment_data.get("id"),
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        db.add(subscription)
        
        # Update user plan
        user.plan = plan
        
        # Create invoice record
        invoice = Invoice(
            subscription_id=subscription.id,
            mp_payment_id=payment_data.get("id"),
            amount=payment_data.get("transaction_amount", 0),
            status="paid",
            due_date=start_date,
            paid_at=datetime.now()
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def cancel_subscription(self, db: Session, subscription: Subscription) -> None:
        """Cancel subscription"""
        subscription.status = "cancelled"
        
        # Revert user to free plan at the end of current period
        # This would typically be handled by a background job
        
        db.commit()
    
    def get_user_subscription(self, db: Session, user: User) -> Optional[Subscription]:
        """Get user's active subscription"""
        return db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).first()
    
    def check_subscription_status(self, db: Session, subscription: Subscription) -> bool:
        """Check if subscription is still valid"""
        if subscription.status != "active":
            return False
        
        if subscription.current_period_end < date.today():
            # Subscription expired
            subscription.status = "expired"
            subscription.user.plan = "free"
            db.commit()
            return False
        
        return True
    
    def apply_coupon(self, db: Session, coupon_code: str, amount: float) -> float:
        """Apply coupon discount to amount"""
        coupon = db.query(Coupon).filter(
            Coupon.code == coupon_code,
            Coupon.is_active == True,
            Coupon.valid_from <= date.today(),
            Coupon.valid_until >= date.today()
        ).first()
        
        if not coupon:
            return amount
        
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return amount
        
        # Apply discount
        discount = amount * (coupon.discount_percent / 100)
        discounted_amount = amount - discount
        
        # Update coupon usage
        coupon.used_count += 1
        db.commit()
        
        return discounted_amount
