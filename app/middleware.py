"""
Custom middleware for security, rate limiting, and CSRF protection
"""
import time
import secrets
from collections import defaultdict
from typing import Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.config import settings

class SecurityMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls_per_minute: int = 60, burst: int = 10):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.burst = burst
        self.clients: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "calls": [],
            "burst_calls": 0,
            "last_reset": time.time()
        })
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static files
        if request.url.path.startswith("/static"):
            return await call_next(request)
        
        client_ip = self.get_client_ip(request)
        now = time.time()
        client_data = self.clients[client_ip]
        
        # Reset burst counter every minute
        if now - client_data["last_reset"] > 60:
            client_data["burst_calls"] = 0
            client_data["last_reset"] = now
            client_data["calls"] = []
        
        # Remove calls older than 1 minute
        client_data["calls"] = [call_time for call_time in client_data["calls"] 
                               if now - call_time < 60]
        
        # Check burst limit
        if client_data["burst_calls"] >= self.burst:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Check calls per minute limit
        if len(client_data["calls"]) >= self.calls_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Record this call
        client_data["calls"].append(now)
        client_data["burst_calls"] += 1
        
        response = await call_next(request)
        return response

class CSRFMiddleware(BaseHTTPMiddleware):
    """Simple Origin-based CSRF protection (more reliable than tokens)"""
    
    def __init__(self, app):
        super().__init__(app)
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
        self.exempt_paths = {
            "/billing/webhook",
            "/healthz",
            "/static"
        }
        self.allowed_origins = {
            "http://localhost:5000",
            "https://localhost:5000",
            f"http://{settings.DOMAIN}",
            f"https://{settings.DOMAIN}"
        }
    
    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        return secrets.token_urlsafe(32)
    
    async def dispatch(self, request: Request, call_next):
        # CSRF DISABLED - No more token validation
        # Security relies on SameSite cookies and session management
        return await call_next(request)
