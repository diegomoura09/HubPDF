"""
Configuration settings for HubPDF
"""
import os
from typing import Optional, Dict, Any, ClassVar
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App settings
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    DOMAIN: str = Field(default="hubpdf.pro")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./hubpdf.db")
    
    # JWT settings
    JWT_SECRET: str = Field(default="your-jwt-secret-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=30)
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="https://hubpdf.pro/auth/google/callback")
    
    # Mercado Pago
    MP_ACCESS_TOKEN: str = Field(default="")
    MP_WEBHOOK_SECRET: str = Field(default="")
    MP_PUBLIC_KEY: str = Field(default="")
    
    # File upload limits (configurable via environment variable)
    # Removed limits - users can upload large files
    MAX_UPLOAD_MB: int = Field(default=10000)  # 10GB - practically unlimited
    MAX_FILE_SIZE_FREE: int = Field(default=10 * 1024 * 1024 * 1024)  # 10GB
    MAX_FILE_SIZE_PRO: int = Field(default=10 * 1024 * 1024 * 1024)  # 10GB
    MAX_FILE_SIZE_BUSINESS: int = Field(default=10 * 1024 * 1024 * 1024)  # 10GB
    
    @property
    def MAX_PART_SIZE(self) -> int:
        """Calculate max part size in bytes from MAX_UPLOAD_MB"""
        return self.MAX_UPLOAD_MB * 1024 * 1024
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_BURST: int = Field(default=10)
    
    # File cleanup
    TEMP_FILE_RETENTION_MINUTES: int = Field(default=30)
    
    # Conversion settings
    CONVERSION_TIMEOUT_SECONDS: int = Field(default=300)  # 5 minutes
    MAX_CONVERSION_FILE_SIZE_MB: int = Field(default=100)
    ENABLE_OCR: bool = Field(default=False)
    
    # Job settings
    MAX_CONCURRENT_JOBS: int = Field(default=4)
    JOB_CLEANUP_HOURS: int = Field(default=24)
    
    # Security & CSRF
    CSRF_SECRET: str = Field(default="csrf-secret-key-change-in-production")
    SESSION_SECRET: str = Field(default="session-secret-key-change-in-production")
    
    # Anonymous users
    ANON_COOKIE_SECRET: str = Field(default="change-this-anon-secret-in-production")
    
    # Plans - using ClassVar since it's not a configuration field
    PLAN_PRICES: ClassVar[Dict[str, float]] = {
        "pro": 9.90,
        "custom": 0.00  # Contact for pricing
    }
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()
