"""
Quota management service for HubPDF
"""
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional, Union
from sqlalchemy.orm import Session
from fastapi import Request

from app.models import User, QuotaUsage
from app.config import settings
from app.services.anon_service import anon_service

class QuotaService:
    """Service for managing user quotas and limits"""
    
    PLAN_LIMITS = {
        "free": {
            "max_file_size": settings.MAX_FILE_SIZE_FREE,
            "daily_operations": 8,
            "watermark_threshold": 4
        },
        "pro": {
            "max_file_size": settings.MAX_FILE_SIZE_PRO,
            "daily_operations": 999999,  # Unlimited
            "watermark_threshold": None  # No watermark
        },
        "custom": {
            "max_file_size": settings.MAX_FILE_SIZE_BUSINESS,
            "daily_operations": 999999,  # Unlimited
            "watermark_threshold": None  # No watermark
        },
        "anonymous": {
            "max_file_size": settings.MAX_FILE_SIZE_FREE,  # Same as free
            "daily_operations": 1,  # Only 1 operation per day
            "watermark_threshold": 0  # Always watermark
        }
    }
    
    def __init__(self):
        pass
    
    def get_plan_limits(self, plan: str) -> Dict[str, Any]:
        """Get limits for a specific plan"""
        return self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["free"])
    
    def get_usage_summary(self, db: Session, user: User) -> Dict[str, Any]:
        """Get comprehensive usage summary for user"""
        if not user:
            # Return default summary for anonymous users
            return {
                "plan": "anonymous",
                "operations_used": 0,
                "operations_limit": 1,
                "operations_percentage": 0,
                "max_file_size_mb": 10,
                "watermark_threshold": 0
            }
        
        quota_usage = self.get_user_quota_usage(db, user)
        plan_limits = self.get_plan_limits(user.plan)
        
        # Convert file size to MB for display
        max_file_size_mb = plan_limits["max_file_size"] // (1024 * 1024)
        
        return {
            "plan": user.plan,
            "operations_used": quota_usage.operations_count,
            "operations_limit": plan_limits["daily_operations"],
            "operations_percentage": min(100, (quota_usage.operations_count / plan_limits["daily_operations"]) * 100) if plan_limits["daily_operations"] > 0 else 0,
            "max_file_size_mb": max_file_size_mb,
            "watermark_threshold": plan_limits["watermark_threshold"]
        }
    
    def get_user_quota_usage(self, db: Session, user: User) -> QuotaUsage:
        """Get or create today's quota usage for user"""
        today = date.today()
        
        quota_usage = db.query(QuotaUsage).filter(
            QuotaUsage.user_id == user.id,
            QuotaUsage.date == today
        ).first()
        
        if not quota_usage:
            quota_usage = QuotaUsage(
                user_id=user.id,
                date=today,
                operations_count=0
            )
            db.add(quota_usage)
            db.commit()
            db.refresh(quota_usage)
        
        return quota_usage
    
    def check_operation_allowed(self, db: Session, user: User) -> Tuple[bool, str, bool]:
        """
        Check if user can perform an operation
        Returns: (allowed, message, requires_watermark)
        """
        limits = self.get_plan_limits(user.plan)
        quota_usage = self.get_user_quota_usage(db, user)
        
        # Check daily limit
        if quota_usage.operations_count >= limits["daily_operations"]:
            from app.services.i18n import translate
            return False, translate("quota_exceeded", "pt"), False
        
        # Check if watermark is required
        requires_watermark = False
        if limits["watermark_threshold"] is not None:
            if quota_usage.operations_count >= limits["watermark_threshold"]:
                requires_watermark = True
        
        return True, "", requires_watermark
    
    def check_file_size_allowed(self, user: User, file_size: int) -> Tuple[bool, str]:
        """Check if file size is within user's plan limits"""
        limits = self.get_plan_limits(user.plan)
        max_size = limits["max_file_size"]
        
        if file_size > max_size:
            from app.services.i18n import translate
            max_mb = max_size // (1024 * 1024)
            return False, translate("file_too_large", "pt", max_size=max_mb)
        
        return True, ""
    
    def increment_operation_count(self, db: Session, user: User) -> None:
        """Increment user's daily operation count"""
        quota_usage = self.get_user_quota_usage(db, user)
        quota_usage.operations_count += 1
        db.commit()
    
    def get_usage_summary(self, db: Session, user: User) -> Dict[str, Any]:
        """Get usage summary for user"""
        if not user:
            # Return default summary for anonymous users
            return {
                "plan": "anonymous",
                "operations_used": 0,
                "operations_limit": 1,
                "operations_remaining": 1,
                "max_file_size_mb": 10,
                "watermark_threshold": 0,
                "date": date.today()
            }
        
        limits = self.get_plan_limits(user.plan)
        quota_usage = self.get_user_quota_usage(db, user)
        
        return {
            "plan": user.plan,
            "operations_used": quota_usage.operations_count,
            "operations_limit": limits["daily_operations"],
            "operations_remaining": max(0, limits["daily_operations"] - quota_usage.operations_count),
            "max_file_size_mb": limits["max_file_size"] // (1024 * 1024),
            "watermark_threshold": limits["watermark_threshold"],
            "date": quota_usage.date
        }
    
    def reset_daily_quota(self, db: Session, user: User) -> None:
        """Reset user's daily quota (admin function)"""
        today = date.today()
        quota_usage = db.query(QuotaUsage).filter(
            QuotaUsage.user_id == user.id,
            QuotaUsage.date == today
        ).first()
        
        if quota_usage:
            quota_usage.operations_count = 0
            db.commit()
    
    def get_plan_upgrade_suggestion(self, user: User) -> str:
        """Get suggestion for plan upgrade"""
        if user.plan == "free":
            return "pro"
        elif user.plan == "pro":
            return "business"
        else:
            return None
