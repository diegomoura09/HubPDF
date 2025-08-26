"""
Authentication service for HubPDF
"""
import secrets
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status

from app.models import User
from app.utils.security import password_manager
from app.utils.validators import InputValidator
from app.config import settings

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password using Argon2"""
        return password_manager.hash_password(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return password_manager.verify_password(password, hashed)
    
    def create_user(self, db: Session, email: str, password: str, name: str, 
                   google_id: Optional[str] = None) -> User:
        """Create a new user"""
        # Validate input
        if not InputValidator.validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        if not InputValidator.validate_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be between 2 and 100 characters"
            )
        
        if password:
            password_errors = InputValidator.validate_password(password)
            if password_errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password validation failed: {', '.join(password_errors)}"
                )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        user = User(
            email=email,
            password_hash=self.hash_password(password) if password else None,
            name=name,
            google_id=google_id,
            email_verified=True if google_id else False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
        
        if not user or not user.password_hash:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def get_or_create_google_user(self, db: Session, google_user_info: Dict[str, Any]) -> User:
        """Get or create user from Google OAuth info"""
        google_id = google_user_info.get("sub")
        email = google_user_info.get("email")
        name = google_user_info.get("name", email)
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google user information"
            )
        
        # Try to find existing user by Google ID
        user = db.query(User).filter(User.google_id == google_id).first()
        if user:
            return user
        
        # Try to find existing user by email
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            user.email_verified = True
            db.commit()
            db.refresh(user)
            return user
        
        # Create new user
        user = User(
            email=email,
            name=name,
            google_id=google_id,
            email_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def update_password(self, db: Session, user: User, new_password: str) -> None:
        """Update user password"""
        password_errors = InputValidator.validate_password(new_password)
        if password_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_errors)}"
            )
        
        user.password_hash = self.hash_password(new_password)
        db.commit()
    
    def deactivate_user(self, db: Session, user: User) -> None:
        """Deactivate user account"""
        user.is_active = False
        db.commit()
    
    def promote_to_admin(self, db: Session, user: User) -> None:
        """Promote user to admin role"""
        user.role = "admin"
        db.commit()
