"""
Tools router for PDF conversion and manipulation
"""
import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
import mimetypes
try:
    import magic
except ImportError:
    magic = None

from fastapi import APIRouter, Request, Response, Form, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.template_helpers import templates
from app.auth import require_auth, get_current_user, get_optional_user
from app.services.job_service import job_service
from app.services.conversion import ConversionError
from app.models import User
from app.config import settings
from app.services.quota_service import QuotaService

router = APIRouter()
logger = logging.getLogger(__name__)
quota_service = QuotaService()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove path separators and special characters
    safe_name = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    safe_name = re.sub(r'\s+', '_', safe_name)
    return safe_name[:255]  # Limit length

# Supported conversion operations - 6 funções essenciais
CONVERSION_OPERATIONS = {
    "merge_pdf": {"input": "pdf", "output": "pdf", "name": "Juntar PDFs"},
    "split_pdf": {"input": "pdf", "output": "pdf", "name": "Dividir PDF"},
    "compress_pdf": {"input": "pdf", "output": "pdf", "name": "Comprimir PDF"},
    "pdf_to_docx": {"input": "pdf", "output": "docx", "name": "PDF para DOCX"},
    "extract_text": {"input": "pdf", "output": "txt", "name": "Extrair Texto"},
    "pdf_to_images": {"input": "pdf", "output": "images", "name": "PDF para Imagens"},
}

ALLOWED_MIME_TYPES = {
    "pdf": ["application/pdf"],
    "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    "images": ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp", "image/tiff"],
}

def get_max_file_size(user: Optional[User] = None) -> int:
    """Get maximum file size based on user plan"""
    if not user:
        return settings.MAX_FILE_SIZE_FREE
    
    # Use user.plan directly instead of subscription
    user_plan = str(user.plan) if user.plan is not None else "free"
    if user_plan == "pro":
        return settings.MAX_FILE_SIZE_PRO
    elif user_plan == "business" or user_plan == "custom":
        return settings.MAX_FILE_SIZE_BUSINESS
    else:
        return settings.MAX_FILE_SIZE_FREE

async def save_uploaded_file(upload_file: UploadFile, work_dir: Path) -> str:
    """Save uploaded file to work directory"""
    # Validate file type using python-magic if available
    file_content = await upload_file.read()
    await upload_file.seek(0)  # Reset file pointer
    
    if magic:
        try:
            detected_mime = magic.from_buffer(file_content, mime=True)
            logger.info(f"Detected MIME type: {detected_mime} for file: {upload_file.filename}")
        except Exception as e:
            logger.warning(f"Failed to detect MIME type: {e}")
    else:
        logger.warning("python-magic not available for MIME type detection")
    
    # Save file with sanitized name
    filename = upload_file.filename or "uploaded_file"
    safe_filename = sanitize_filename(filename)
    file_path = work_dir / safe_filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)

@router.get("/")
async def tools_index(
    request: Request,
    user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Tools index page"""
    
    # Get usage summary if user is logged in
    usage_summary = None
    if user:
        quota_usage = quota_service.get_user_quota_usage(db, user)
        user_plan = str(user.plan) if user.plan is not None else "free"
        plan_limits = quota_service.get_plan_limits(user_plan)
        usage_summary = {
            "plan": user_plan,
            "operations_used": quota_usage.operations_count,
            "operations_limit": plan_limits["daily_operations"],
            "operations_percentage": min(100, (quota_usage.operations_count / plan_limits["daily_operations"]) * 100) if plan_limits["daily_operations"] > 0 else 0
        }
    
    return templates.TemplateResponse("tools/index.html", {
        "request": request,
        "user": user,
        "usage_summary": usage_summary,
        "operations": CONVERSION_OPERATIONS
    })

# Legacy tool routes (for backward compatibility)
@router.get("/merge")
async def merge_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """PDF merge tool page"""
    return await tools_index(request, user, db)

@router.get("/split")
async def split_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """PDF split tool page"""
    return await tools_index(request, user, db)

@router.get("/compress")
async def compress_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """PDF compress tool page"""
    return await tools_index(request, user, db)

@router.get("/extract-text")
async def extract_text_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """PDF text extraction tool page"""
    return await tools_index(request, user, db)

@router.get("/pdf-to-images")
async def pdf_to_images_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """PDF to images tool page"""
    return await tools_index(request, user, db)

@router.get("/images-to-pdf")
async def images_to_pdf_tool(request: Request, user: User = Depends(get_optional_user), db: Session = Depends(get_db)):
    """Images to PDF tool page"""
    return await tools_index(request, user, db)

# API Endpoints for conversions
@router.post("/api/convert")
async def start_conversion(
    request: Request,
    background_tasks: BackgroundTasks,
    operation: str = Form(...),
    target_format: Optional[str] = Form(None),
    compression_level: Optional[str] = Form("balanced"),
    page_ranges: Optional[str] = Form(None),
    image_format: Optional[str] = Form("png"),
    image_dpi: Optional[int] = Form(200),
    use_ocr: Optional[bool] = Form(False),
    grayscale: Optional[bool] = Form(False),
    rasterize: Optional[bool] = Form(False),
    files: List[UploadFile] = File(...),
    user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Start a new conversion job"""
    try:
        # Validate operation
        if operation not in CONVERSION_OPERATIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {operation}")
        
        # Check quotas and limits
        if user:
            allowed, message, requires_watermark = quota_service.check_operation_allowed(db, user)
            if not allowed:
                raise HTTPException(status_code=429, detail=message)
        
        # Validate files
        max_file_size = get_max_file_size(user)
        for file in files:
            if file.size and file.size > max_file_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File {file.filename} exceeds maximum size limit"
                )
        
        # Validate files exist and are accessible
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Create job ID and work directory
        job_id = str(uuid.uuid4())
        work_dir = Path(tempfile.gettempdir()) / "hubpdf_jobs" / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Processing {len(files)} files for job {job_id}")
        
        # Save uploaded files
        input_files = []
        for i, file in enumerate(files):
            if file.filename:
                file_path = await save_uploaded_file(file, work_dir)
                input_files.append(file_path)
                logger.info(f"Saved file {i+1}: {file.filename} -> {file_path}")
        
        if not input_files:
            raise HTTPException(status_code=400, detail="No valid files found")
        
        # Prepare options
        options = {
            "format": image_format,
            "dpi": image_dpi,
            "level": compression_level,
            "ranges": page_ranges or "1",
            "use_ocr": use_ocr and settings.ENABLE_OCR,
            "grayscale": grayscale,
            "rasterize": rasterize,
        }
        
        # Start conversion job
        logger.info(f"Starting conversion job {job_id} with operation {operation}")
        result_job_id = await job_service.start_conversion(
            operation=operation,
            input_files=input_files,
            options=options,
            job_id=job_id
        )
        
        # Increment user operations count
        if user:
            quota_service.increment_operation_count(db, user)
        
        return JSONResponse({
            "job_id": result_job_id,
            "status": "started",
            "message": "Conversion job started successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start conversion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start conversion job")

@router.get("/api/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    user: User = Depends(get_optional_user)
):
    """Get job status and progress"""
    try:
        job_status = job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JSONResponse(job_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get job status")

@router.get("/api/jobs/{job_id}/download/{file_index}")
async def download_job_result(
    job_id: str,
    file_index: int,
    user: User = Depends(get_optional_user)
):
    """Download a result file from completed job"""
    try:
        job_status = job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job_status["status"] != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        output_files = job_status.get("output_files", [])
        if file_index >= len(output_files):
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = output_files[file_index]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File no longer available")
        
        # Determine content type and filename
        file_name = Path(file_path).name
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@router.delete("/api/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    user: User = Depends(get_optional_user)
):
    """Cancel a running job"""
    try:
        success = await job_service.cancel_job(job_id)
        if success:
            return JSONResponse({"message": "Job cancelled successfully"})
        else:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel job")

@router.get("/api/jobs")
async def list_jobs(
    limit: int = 50,
    user: User = Depends(get_optional_user)
):
    """List recent jobs"""
    try:
        jobs = job_service.list_jobs(limit)
        return JSONResponse({"jobs": jobs})
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

# Legacy endpoints for backward compatibility
@router.post("/merge")
async def legacy_merge_pdf(request: Request):
    """Legacy merge endpoint - redirect to new API"""
    return RedirectResponse(url="/tools/api/convert", status_code=307)

@router.post("/split")
async def legacy_split_pdf(request: Request):
    """Legacy split endpoint - redirect to new API"""
    return RedirectResponse(url="/tools/api/convert", status_code=307)

@router.post("/compress")
async def legacy_compress_pdf(request: Request):
    """Legacy compress endpoint - redirect to new API"""
    return RedirectResponse(url="/tools/api/convert", status_code=307)

@router.post("/extract-text")
async def legacy_extract_text(request: Request):
    """Legacy extract text endpoint - redirect to new API"""
    return RedirectResponse(url="/tools/api/convert", status_code=307)