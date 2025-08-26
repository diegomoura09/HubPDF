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
    DOMAIN: str = Field(default="localhost:5000")
    
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
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:5000/auth/google/callback")
    
    # Mercado Pago
    MP_ACCESS_TOKEN: str = Field(default="")
    MP_WEBHOOK_SECRET: str = Field(default="")
    MP_PUBLIC_KEY: str = Field(default="")
    
    # File upload limits
    MAX_FILE_SIZE_FREE: int = Field(default=10 * 1024 * 1024)  # 10MB
    MAX_FILE_SIZE_PRO: int = Field(default=100 * 1024 * 1024)  # 100MB
    MAX_FILE_SIZE_BUSINESS: int = Field(default=250 * 1024 * 1024)  # 250MB
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_BURST: int = Field(default=10)
    
    # File cleanup
    TEMP_FILE_RETENTION_MINUTES: int = Field(default=30)
    
    # Plans - using ClassVar since it's not a configuration field
    PLAN_PRICES: ClassVar[Dict[str, float]] = {
        "pro": 14.90,
        "business": 29.90
    }
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()
