"""
File management service for HubPDF
"""
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import datetime, timedelta

from app.utils.security import sanitize_filename

class FileService:
    """Service for managing temporary files"""
    
    def __init__(self):
        self.temp_base_dir = Path("/tmp")
        self.retention_minutes = 30
    
    def create_job_directory(self, user_id: int) -> str:
        """Create a temporary directory for a job"""
        job_id = str(uuid.uuid4())
        job_dir = self.temp_base_dir / str(user_id) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_id
    
    def get_job_directory(self, user_id: int, job_id: str) -> Path:
        """Get job directory path"""
        return self.temp_base_dir / str(user_id) / job_id
    
    def save_upload_file(self, user_id: int, job_id: str, file: BinaryIO, 
                        original_filename: str) -> Path:
        """Save uploaded file to temporary directory"""
        job_dir = self.get_job_directory(user_id, job_id)
        safe_filename = sanitize_filename(original_filename)
        
        file_path = job_dir / safe_filename
        
        with open(file_path, "wb") as f:
            file.seek(0)
            shutil.copyfileobj(file, f)
        
        return file_path
    
    def save_result_file(self, user_id: int, job_id: str, content: bytes, 
                        filename: str) -> Path:
        """Save result file to temporary directory"""
        job_dir = self.get_job_directory(user_id, job_id)
        safe_filename = sanitize_filename(filename)
        
        file_path = job_dir / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path
    
    def cleanup_job_directory(self, user_id: int, job_id: str) -> None:
        """Clean up job directory"""
        job_dir = self.get_job_directory(user_id, job_id)
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
    
    def cleanup_old_files(self) -> None:
        """Clean up files older than retention period"""
        cutoff_time = datetime.now() - timedelta(minutes=self.retention_minutes)
        
        if not self.temp_base_dir.exists():
            return
        
        for user_dir in self.temp_base_dir.iterdir():
            if not user_dir.is_dir():
                continue
            
            for job_dir in user_dir.iterdir():
                if not job_dir.is_dir():
                    continue
                
                # Check directory modification time
                try:
                    mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                    if mtime < cutoff_time:
                        shutil.rmtree(job_dir, ignore_errors=True)
                except (OSError, ValueError):
                    # If we can't read the time, assume it's old and delete it
                    shutil.rmtree(job_dir, ignore_errors=True)
            
            # Remove empty user directories
            try:
                if not any(user_dir.iterdir()):
                    user_dir.rmdir()
            except OSError:
                pass
    
    def get_file_content(self, user_id: int, job_id: str, filename: str) -> Optional[bytes]:
        """Get file content from temporary directory"""
        job_dir = self.get_job_directory(user_id, job_id)
        file_path = job_dir / sanitize_filename(filename)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except OSError:
            return None
    
    def file_exists(self, user_id: int, job_id: str, filename: str) -> bool:
        """Check if file exists in job directory"""
        job_dir = self.get_job_directory(user_id, job_id)
        file_path = job_dir / sanitize_filename(filename)
        return file_path.exists()
    
    def get_file_size(self, user_id: int, job_id: str, filename: str) -> Optional[int]:
        """Get file size"""
        job_dir = self.get_job_directory(user_id, job_id)
        file_path = job_dir / sanitize_filename(filename)
        
        if not file_path.exists():
            return None
        
        try:
            return file_path.stat().st_size
        except OSError:
            return None
