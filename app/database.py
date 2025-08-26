"""
Database configuration and initialization
"""
import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

# Create engine
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    from app.models import User, Subscription, Invoice, Coupon, AuditLog, QuotaUsage
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@hubpdf.com").first()
        if not admin_user:
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            
            admin_user = User(
                email="admin@hubpdf.com",
                password_hash=auth_service.hash_password("admin123"),
                name="Admin User",
                role="admin",
                is_active=True,
                email_verified=True
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
