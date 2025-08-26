"""
Anonymous user service for managing visitor sessions and quotas
"""
import uuid
import hashlib
import secrets
from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import Request, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AnonQuota


class AnonymousUserService:
    """Service for managing anonymous user sessions and quotas"""
    
    def __init__(self):
        # Use a fallback secret if not configured
        self.anon_secret = getattr(settings, 'ANON_COOKIE_SECRET', 
                                  'fallback-anon-secret-change-in-production')
        self.serializer = URLSafeTimedSerializer(self.anon_secret)
        self.cookie_name = "anon_id"
        self.cookie_max_age = 24 * 60 * 60  # 24 hours
    
    def get_anon_id(self, request: Request) -> str:
        """Get or create anonymous user ID from signed cookie"""
        try:
            # Try to get existing signed cookie
            signed_cookie = request.cookies.get(self.cookie_name)
            if signed_cookie:
                # Verify and extract the anon_id (valid for 24 hours)
                anon_id = self.serializer.loads(
                    signed_cookie, 
                    max_age=self.cookie_max_age
                )
                return anon_id
        except (BadSignature, Exception):
            # Invalid or expired cookie, generate new one
            pass
        
        # Generate new anonymous ID
        return str(uuid.uuid4())
    
    def set_anon_cookie(self, response: Response, anon_id: str):
        """Set signed anonymous ID cookie"""
        signed_anon_id = self.serializer.dumps(anon_id)
        response.set_cookie(
            self.cookie_name,
            signed_anon_id,
            max_age=self.cookie_max_age,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax"
        )
    
    def hash_anon_id(self, anon_id: str) -> str:
        """Create SHA256 hash of anonymous ID for storage"""
        return hashlib.sha256(anon_id.encode()).hexdigest()
    
    def get_anon_quota(self, db: Session, anon_id: str) -> AnonQuota:
        """Get or create anonymous quota for today"""
        anon_hash = self.hash_anon_id(anon_id)
        today = date.today()
        
        quota = db.query(AnonQuota).filter(
            AnonQuota.anon_id_hash == anon_hash,
            AnonQuota.date == today
        ).first()
        
        if not quota:
            quota = AnonQuota(
                anon_id_hash=anon_hash,
                date=today,
                ops_count=0
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)
        
        return quota
    
    def check_anon_quota(self, db: Session, anon_id: str) -> dict:
        """Check if anonymous user can perform operation"""
        quota = self.get_anon_quota(db, anon_id)
        
        # Anonymous users get 1 operation per day
        allowed_ops = 1
        remaining = max(0, allowed_ops - quota.ops_count)
        
        return {
            "allowed": quota.ops_count < allowed_ops,
            "used": quota.ops_count,
            "total": allowed_ops,
            "remaining": remaining,
            "watermark_required": True  # Always watermark for anonymous
        }
    
    def increment_anon_quota(self, db: Session, anon_id: str) -> bool:
        """Increment anonymous user operation count"""
        quota = self.get_anon_quota(db, anon_id)
        
        if quota.ops_count >= 1:  # Daily limit reached
            return False
        
        quota.ops_count += 1
        quota.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    def cleanup_old_anon_quotas(self, db: Session, days_old: int = 30):
        """Clean up anonymous quota records older than specified days"""
        cutoff_date = date.today() - timedelta(days=days_old)
        deleted = db.query(AnonQuota).filter(
            AnonQuota.date < cutoff_date
        ).delete()
        db.commit()
        return deleted


# Global service instance
anon_service = AnonymousUserService()