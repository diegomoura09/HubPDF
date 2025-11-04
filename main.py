"""
HubPDF - A comprehensive PDF tools hub with security-first architecture
"""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from app.database import init_db
from app.middleware import SecurityMiddleware, RateLimitMiddleware, CSRFMiddleware
from app.routers import auth, tools, billing, admin, health, main as main_router
from app.config import settings

# Cleanup task for temporary files
async def cleanup_temp_files():
    """Background task to clean up temporary files older than 30 minutes"""
    import shutil
    import time
    from pathlib import Path
    
    temp_dir = Path("/tmp")
    if not temp_dir.exists():
        return
    
    current_time = time.time()
    for user_dir in temp_dir.glob("*/"):
        if user_dir.is_dir():
            # Check if directory is older than 30 minutes
            if current_time - user_dir.stat().st_mtime > 1800:  # 30 minutes
                try:
                    shutil.rmtree(user_dir)
                except Exception:
                    pass  # Ignore errors during cleanup

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    env = os.getenv("REPL_DEPLOYMENT", "development")
    print(f"🚀 HubPDF starting in {env} mode")
    print(f"📍 Environment: {os.getenv('REPL_SLUG', 'local')}")
    
    await init_db()
    print("✅ Database initialized")
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    # Initialize job registry cleanup
    from app.services.job_service import job_registry
    cleanup_job_task = asyncio.create_task(periodic_job_cleanup())
    
    print("✅ HubPDF app started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down HubPDF...")
    cleanup_task.cancel()
    cleanup_job_task.cancel()
    try:
        await cleanup_task
        await cleanup_job_task
    except asyncio.CancelledError:
        pass

async def periodic_cleanup():
    """Run cleanup every 10 minutes"""
    while True:
        await cleanup_temp_files()
        await asyncio.sleep(600)  # 10 minutes

async def periodic_job_cleanup():
    """Run job cleanup every hour"""
    while True:
        try:
            from app.services.job_service import job_registry
            job_registry.cleanup_old_jobs(max_age_hours=settings.JOB_CLEANUP_HOURS)
        except Exception as e:
            print(f"Job cleanup failed: {e}")
        await asyncio.sleep(3600)  # 1 hour

# Create FastAPI app
app = FastAPI(
    title="HubPDF",
    description="A comprehensive PDF tools hub with security-first architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Patch Starlette Request.form() to enforce max upload size globally
# This ensures all multipart/form-data uploads respect the 60MB limit
from starlette import requests as _starlette_requests
_orig_form = _starlette_requests.Request.form

async def _patched_form(self, *args, **kwargs):
    """Patched form method that enforces global upload limits"""
    kwargs.setdefault("max_part_size", settings.MAX_PART_SIZE)  # 60 MB by default
    kwargs.setdefault("max_files", 100)
    kwargs.setdefault("max_fields", 1000)
    return await _orig_form(self, *args, **kwargs)

_starlette_requests.Request.form = _patched_form

# Redirect middleware for HTTPS and apex domain
@app.middleware("http")
async def redirect_middleware(request: Request, call_next):
    """Redirect HTTP to HTTPS and www to apex domain"""
    # Get host and scheme
    host = request.headers.get("host", "")
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    
    # Force HTTPS in production (non-localhost)
    if scheme == "http" and "localhost" not in host and "127.0.0.1" not in host:
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(url), status_code=301)
    
    # Redirect www to apex domain
    if host.startswith("www."):
        new_host = host[4:]  # Remove "www."
        url = request.url.replace(netloc=new_host)
        return RedirectResponse(url=str(url), status_code=301)
    
    response = await call_next(request)
    return response

# Security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=300, burst=50)
app.add_middleware(CSRFMiddleware)

# CORS middleware - Specific origins for production security
# Allow only hubpdf.pro, localhost, and all replit domains
if settings.DEBUG:
    # Development: allow localhost only
    cors_origins = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]
    cors_credentials = True
else:
    # Production: allow custom domain and replit domains
    # Note: CORS doesn't support wildcards in allow_origins, so we use regex in origin validation
    cors_origins = [
        "https://hubpdf.pro",
        "https://www.hubpdf.pro",
    ]
    cors_credentials = True
    
    # Add specific Replit URLs if available
    repl_slug = os.getenv("REPL_SLUG")
    if repl_slug:
        cors_origins.append(f"https://{repl_slug}.replit.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware - Enable for webhook support and Replit deployments
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "hubpdf.pro",  # Custom domain
            "www.hubpdf.pro",  # Custom domain with www
            settings.DOMAIN, 
            f"*.{settings.DOMAIN}",
            "*.replit.app",  # Replit deployment domains
            "*.replit.dev",  # Replit development domains
            "*.spock.replit.dev",  # For Mercado Pago webhooks
            "localhost", 
            "127.0.0.1"
        ]
    )

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates - Import centralized templates
from app.template_helpers import templates

# Include routers
app.include_router(main_router.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(health.router, prefix="/api", tags=["health"])


# Demo page for alerts system
@app.get("/demo/alerts")
async def alerts_demo(request: Request):
    return templates.TemplateResponse(
        "demo/alerts.html",
        {
            "request": request
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        access_log=not settings.DEBUG
    )
