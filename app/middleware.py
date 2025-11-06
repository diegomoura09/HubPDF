"""
Custom middleware for security, rate limiting, and CSRF protection
Migrated to pure ASGI middleware to avoid request body consumption issues
"""
import time
import json
import logging
import secrets
from collections import defaultdict
from typing import Dict, Any, Callable
from fastapi import Request, status
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.datastructures import Headers
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Add security headers to all responses - Pure ASGI"""
    
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                headers[b"permissions-policy"] = b"geolocation=(), microphone=(), camera=()"
                
                if not settings.DEBUG:
                    headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                
                message["headers"] = [(k.lower() if isinstance(k, str) else k, 
                                      v.encode() if isinstance(v, str) else v) 
                                     for k, v in headers.items()]
            
            await send(message)
        
        await self.app(scope, receive, send_with_headers)


class RateLimitMiddleware:
    """Rate limiting middleware - Pure ASGI"""
    
    def __init__(self, app: ASGIApp, calls_per_minute: int = 60, burst: int = 10):
        self.app = app
        self.calls_per_minute = calls_per_minute
        self.burst = burst
        self.clients: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "calls": [],
            "burst_calls": 0,
            "last_reset": time.time()
        })
    
    def get_client_ip(self, scope: Scope) -> str:
        """Get client IP address from scope"""
        headers = Headers(scope=scope)
        forwarded = headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        client = scope.get("client")
        if client:
            return client[0]
        return "unknown"
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        
        if path.startswith("/static"):
            await self.app(scope, receive, send)
            return
        
        client_ip = self.get_client_ip(scope)
        now = time.time()
        client_data = self.clients[client_ip]
        
        if now - client_data["last_reset"] > 60:
            client_data["burst_calls"] = 0
            client_data["last_reset"] = now
            client_data["calls"] = []
        
        client_data["calls"] = [call_time for call_time in client_data["calls"] 
                               if now - call_time < 60]
        
        if client_data["burst_calls"] >= self.burst or len(client_data["calls"]) >= self.calls_per_minute:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Muitas requisições. Tente novamente em alguns instantes."}
            )
            await response(scope, receive, send)
            return
        
        client_data["calls"].append(now)
        client_data["burst_calls"] += 1
        
        await self.app(scope, receive, send)


class CSRFMiddleware:
    """Simple Origin-based CSRF protection - Pure ASGI (currently disabled)"""
    
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)


class RequestLoggingMiddleware:
    """Log all requests with structured data - Pure ASGI"""
    
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope.get("method", "")
        path = scope.get("path", "")
        headers = Headers(scope=scope)
        
        status_code = 200
        
        async def send_with_logging(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)
        
        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as e:
            status_code = 500
            logger.error(
                f"Request failed",
                extra={
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "client": scope.get("client", ["unknown"])[0] if scope.get("client") else "unknown"
                },
                exc_info=True
            )
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            if not path.startswith("/static"):
                log_data = {
                    "method": method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client": scope.get("client", ["unknown"])[0] if scope.get("client") else "unknown",
                    "user_agent": headers.get("user-agent", ""),
                    "content_length": headers.get("content-length", "0")
                }
                
                if status_code >= 500:
                    logger.error(f"Server error: {json.dumps(log_data)}")
                elif status_code >= 400:
                    logger.warning(f"Client error: {json.dumps(log_data)}")
                else:
                    logger.info(f"Request: {json.dumps(log_data)}")
