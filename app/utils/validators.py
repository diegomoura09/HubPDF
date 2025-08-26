"""
Input validation utilities
"""
import re
import mimetypes
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status

class FileValidator:
    """File upload validation"""
    
    ALLOWED_PDF_TYPES = ["application/pdf"]
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp"]
    
    @staticmethod
    def validate_pdf_file(file: UploadFile, max_size: int) -> None:
        """Validate PDF file upload"""
        # Check file size
        if file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Check MIME type
        content_type = file.content_type
        if content_type not in FileValidator.ALLOWED_PDF_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF files are allowed."
            )
        
        # Additional PDF validation by reading file header
        file.file.seek(0)
        header = file.file.read(4)
        file.file.seek(0)
        
        if header != b'%PDF':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file format."
            )
    
    @staticmethod
    def validate_image_file(file: UploadFile, max_size: int) -> None:
        """Validate image file upload"""
        # Check file size
        if file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Check MIME type
        content_type = file.content_type
        if content_type not in FileValidator.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only image files are allowed."
            )
    
    @staticmethod
    def validate_multiple_files(files: List[UploadFile], max_count: int = 10) -> None:
        """Validate multiple file upload"""
        if len(files) > max_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many files. Maximum: {max_count}"
            )
        
        if len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )

class InputValidator:
    """General input validation"""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PASSWORD_MIN_LENGTH = 8
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return bool(InputValidator.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_password(password: str) -> List[str]:
        """Validate password strength, return list of errors"""
        errors = []
        
        if len(password) < InputValidator.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {InputValidator.PASSWORD_MIN_LENGTH} characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return errors
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        return bool(name and len(name.strip()) >= 2 and len(name.strip()) <= 100)
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'\&]', '', value)
        return sanitized.strip()[:max_length]
