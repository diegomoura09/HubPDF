"""
Job management service for handling asynchronous conversion tasks
"""
import uuid
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json

from app.services.conversion import conversion_service, ConversionError

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobResult:
    """Result of a conversion job"""
    job_id: str
    status: JobStatus
    progress: int
    message: str
    output_files: List[str]
    error: Optional[str] = None
    created_at: float = None
    completed_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

class JobRegistry:
    """In-memory job registry with optional persistence"""
    
    def __init__(self):
        self.jobs: Dict[str, JobResult] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.cleanup_task = None
        
    def create_job(self, job_id: str = None) -> str:
        """Create a new job and return its ID"""
        if job_id is None:
            job_id = str(uuid.uuid4())
            
        job = JobResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            message="Job created",
            output_files=[]
        )
        
        self.jobs[job_id] = job
        self.locks[job_id] = asyncio.Lock()
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobResult]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs):
        """Update job properties"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
    
    def list_jobs(self, limit: int = 50) -> List[JobResult]:
        """List recent jobs"""
        jobs = list(self.jobs.values())
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove old completed jobs"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        jobs_to_remove = []
        for job_id, job in self.jobs.items():
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                job.created_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            self.jobs.pop(job_id, None)
            self.locks.pop(job_id, None)
            logger.info(f"Cleaned up old job: {job_id}")

# Global job registry
job_registry = JobRegistry()

class ConversionJobService:
    """Service for managing conversion jobs"""
    
    def __init__(self):
        self.registry = job_registry
    
    async def start_conversion(
        self, 
        operation: str, 
        input_files: List[str], 
        options: Dict[str, Any] = None,
        job_id: str = None
    ) -> str:
        """Start a new conversion job"""
        # Create job if not provided
        if job_id is None:
            job_id = str(uuid.uuid4())
            
        # Ensure job is registered
        if job_id not in self.registry.jobs:
            self.registry.create_job(job_id)
            
        logger.info(f"Starting conversion job {job_id} with operation {operation}")
        
        # Start the conversion in the background
        asyncio.create_task(self._run_conversion_job(job_id, operation, input_files, options or {}))
        
        return job_id
    
    async def _run_conversion_job(
        self, 
        job_id: str, 
        operation: str, 
        input_files: List[str], 
        options: Dict[str, Any]
    ):
        """Run the conversion job"""
        try:
            # Ensure job exists and has lock
            if job_id not in self.registry.locks:
                self.registry.locks[job_id] = asyncio.Lock()
                
            async with self.registry.locks[job_id]:
                logger.info(f"Running conversion job {job_id}")
                
                self.registry.update_job(
                    job_id,
                    status=JobStatus.RUNNING,
                    progress=10,
                    message=f"Starting {operation} conversion..."
                )
                
                # Route to appropriate conversion method
                output_files = await self._execute_conversion(
                    operation, input_files, options, job_id
                )
                
                self.registry.update_job(
                    job_id,
                    status=JobStatus.COMPLETED,
                    progress=100,
                    message="Conversion completed successfully",
                    output_files=output_files,
                    completed_at=time.time()
                )
                logger.info(f"Job {job_id} completed successfully")
                
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
            self.registry.update_job(
                job_id,
                status=JobStatus.FAILED,
                progress=0,
                message=f"Conversion failed: {str(e)}",
                error=str(e),
                completed_at=time.time()
            )
    
    async def _execute_conversion(
        self, 
        operation: str, 
        input_files: List[str], 
        options: Dict[str, Any],
        job_id: str
    ) -> List[str]:
        """Execute the specific conversion operation"""
        if not input_files:
            raise ConversionError("No input files provided")
        
        input_file = input_files[0]  # Most operations use single input
        
        # Update progress
        self.registry.update_job(job_id, progress=30, message=f"Processing {operation}...")
        
        try:
            if operation == "pdf_to_docx":
                result = await conversion_service.pdf_to_docx(input_file, job_id)
                return [result]
                
            elif operation == "docx_to_pdf":
                result = await conversion_service.docx_to_pdf(input_file, job_id)
                return [result]
                
            elif operation == "pdf_to_xlsx":
                result = await conversion_service.pdf_to_xlsx(input_file, job_id)
                return [result]
                
            elif operation == "xlsx_to_pdf":
                result = await conversion_service.xlsx_to_pdf(input_file, job_id)
                return [result]
                
            elif operation == "pdf_to_pptx":
                result = await conversion_service.pdf_to_pptx(input_file, job_id)
                return [result]
                
            elif operation == "pptx_to_pdf":
                result = await conversion_service.pptx_to_pdf(input_file, job_id)
                return [result]
                
            elif operation == "pdf_to_images":
                fmt = options.get("format", "png")
                dpi = options.get("dpi", 200)
                self.registry.update_job(job_id, progress=50, message="Converting pages to images...")
                results = await conversion_service.pdf_to_images(input_file, fmt, dpi, job_id)
                return results
                
            elif operation == "images_to_pdf":
                self.registry.update_job(job_id, progress=50, message="Combining images to PDF...")
                result = await conversion_service.images_to_pdf(input_files, job_id)
                return [result]
                
            elif operation == "pdf_to_txt":
                use_ocr = options.get("use_ocr", False)
                self.registry.update_job(job_id, progress=50, message="Extracting text...")
                result = await conversion_service.pdf_to_txt(input_file, use_ocr, job_id)
                return [result]
                
            elif operation == "split_pdf":
                ranges = options.get("ranges", "1")
                self.registry.update_job(job_id, progress=50, message="Splitting PDF...")
                results = await conversion_service.split_pdf(input_file, ranges, job_id)
                return results
                
            elif operation == "compress_pdf":
                level = options.get("level", "normal")
                self.registry.update_job(job_id, progress=50, message="Compressing PDF...")
                result = await conversion_service.compress_pdf(input_file, level, job_id)
                return [result]
                
            elif operation == "extract_text_to_pdf":
                self.registry.update_job(job_id, progress=50, message="Creating text-only PDF...")
                result = await conversion_service.extract_text_to_pdf(input_file, job_id)
                return [result]
                
            elif operation == "pdf_to_ico":
                sizes = options.get("sizes", [16, 32, 48, 64, 128, 256])
                self.registry.update_job(job_id, progress=50, message="Creating ICO file...")
                result = await conversion_service.create_ico_from_pdf(input_file, sizes, job_id)
                return [result]
                
            else:
                raise ConversionError(f"Unknown operation: {operation}")
                
        except Exception as e:
            # Update progress on error
            self.registry.update_job(job_id, progress=0, message=f"Error: {str(e)}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        job = self.registry.get_job(job_id)
        if job:
            return job.to_dict()
        return None
    
    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent jobs"""
        jobs = self.registry.list_jobs(limit)
        return [job.to_dict() for job in jobs]
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        job = self.registry.get_job(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            self.registry.update_job(
                job_id,
                status=JobStatus.CANCELLED,
                message="Job cancelled by user",
                completed_at=time.time()
            )
            return True
        return False

# Global service instance
job_service = ConversionJobService()