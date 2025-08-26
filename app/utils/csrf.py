"""
CSRF protection utility using itsdangerous for token generation and validation
"""
import time
import os
from itsdangerous import URLSafeSerializer, BadSignature

CSRF_SECRET = os.getenv("CSRF_SECRET", "dev-csrf-secret-change-me")
s = URLSafeSerializer(CSRF_SECRET, salt="csrf-v1")

def generate_csrf_token() -> str:
    """Generate a CSRF token with timestamp"""
    return s.dumps({"ts": int(time.time())})

def validate_csrf_token(token: str, max_age_seconds: int = 7200) -> bool:
    """Validate a CSRF token, checking signature and expiration"""
    try:
        data = s.loads(token)
    except BadSignature:
        return False
    return (int(time.time()) - int(data.get("ts", 0))) <= max_age_seconds