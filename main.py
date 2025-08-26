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
from app.routers import auth, tools, billing, admin, main as main_router
from app.services.i18n import get_translations, get_user_locale
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
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

async def periodic_cleanup():
    """Run cleanup every 10 minutes"""
    while True:
        await cleanup_temp_files()
        await asyncio.sleep(600)  # 10 minutes

# Create FastAPI app
app = FastAPI(
    title="HubPDF",
    description="A comprehensive PDF tools hub with security-first architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.DOMAIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware - Disable for Replit development
# if not settings.DEBUG:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=[settings.DOMAIN, f"*.{settings.DOMAIN}"]
#     )

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates - Import centralized templates
from app.templates import templates

# Include routers
app.include_router(main_router.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Root redirect
@app.get("/")
async def root():
    return RedirectResponse(url="/home", status_code=302)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        access_log=not settings.DEBUG
    )
