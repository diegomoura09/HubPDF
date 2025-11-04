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
    await init_db()
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    # Initialize job registry cleanup
    from app.services.job_service import job_registry
    cleanup_job_task = asyncio.create_task(periodic_job_cleanup())
    
    yield
    
    # Shutdown
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

# Security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=300, burst=50)
app.add_middleware(CSRFMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.DOMAIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware - Enable for webhook support
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            settings.DOMAIN, 
            f"*.{settings.DOMAIN}",
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
