"""
Security utility functions
"""
import secrets
import hashlib
import hmac
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError

from app.config import settings

class PasswordManager:
    """Secure password hashing using Argon2"""
    
    def __init__(self):
        self.ph = PasswordHasher()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        try:
            return self.ph.hash(password)
        except HashingError as e:
            raise ValueError(f"Failed to hash password: {str(e)}")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            self.ph.verify(hashed, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature (for Mercado Pago)"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    import re
    # Remove any path separators and special characters
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    # Remove leading dots and spaces
    sanitized = sanitized.lstrip('. ')
    # Limit length
    return sanitized[:255]

def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
    """Check if redirect URL is safe"""
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(url)
        # Allow relative URLs
        if not parsed.netloc:
            return True
        # Check if host is in allowed list
        return parsed.netloc in allowed_hosts
    except Exception:
        return False

password_manager = PasswordManager()
