"""
Database configuration and initialization
"""
import os
import asyncio
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create engine with proper SQLite configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # Use local SQLite file in data directory
    db_path = "data/app.db"
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False,
            # Enable WAL mode for better performance
            "timeout": 30
        },
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    
    # Set WAL mode for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        with dbapi_connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=1000")
            cursor.execute("PRAGMA foreign_keys=ON")
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
    from app.models import User, Subscription, Invoice, Coupon, AuditLog, QuotaUsage, AnonQuota
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
