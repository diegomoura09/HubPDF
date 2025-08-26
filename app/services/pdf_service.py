"""
PDF processing service for HubPDF
"""
import os
import io
import zipfile
import tempfile
from pathlib import Path
from typing import List, BinaryIO, Optional, Tuple
import PyPDF2
import pikepdf
import pdfplumber
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from app.utils.security import sanitize_filename

class PDFService:
    """Service for PDF operations"""
    
    def __init__(self):
        self.temp_dir = Path("/tmp")
    
    def create_user_temp_dir(self, user_id: int, job_id: str) -> Path:
        """Create temporary directory for user files"""
        user_temp_dir = self.temp_dir / str(user_id) / job_id
        user_temp_dir.mkdir(parents=True, exist_ok=True)
        return user_temp_dir
    
    def add_watermark(self, pdf_bytes: bytes, watermark_text: str) -> bytes:
        """Add watermark to PDF"""
        try:
            # Create watermark PDF
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=letter)
            
            # Set watermark properties
            c.setFillColor(colors.grey, alpha=0.3)
            c.setFont("Helvetica", 48)
            
            # Add diagonal watermark
            c.saveState()
            c.translate(300, 400)
            c.rotate(45)
            c.drawCentredText(0, 0, watermark_text)
            c.restoreState()
            c.save()
            
            watermark_buffer.seek(0)
            watermark_pdf = PyPDF2.PdfReader(watermark_buffer)
            
            # Apply watermark to original PDF
            input_pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            output_pdf = PyPDF2.PdfWriter()
            
            for page_num in range(len(input_pdf.pages)):
                page = input_pdf.pages[page_num]
                if watermark_pdf.pages:
                    page.merge_page(watermark_pdf.pages[0])
                output_pdf.add_page(page)
            
            output_buffer = io.BytesIO()
            output_pdf.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.read()
        
        except Exception as e:
            # If watermarking fails, return original PDF
            return pdf_bytes
    
    def merge_pdfs(self, pdf_files: List[BinaryIO], user_id: int, job_id: str, 
                   apply_watermark: bool = False, watermark_text: str = "") -> bytes:
        """Merge multiple PDF files"""
        try:
            merger = PyPDF2.PdfMerger()
            
            for pdf_file in pdf_files:
                pdf_file.seek(0)
                merger.append(pdf_file)
            
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            output_buffer.seek(0)
            result_bytes = output_buffer.read()
            
            if apply_watermark and watermark_text:
                result_bytes = self.add_watermark(result_bytes, watermark_text)
            
            return result_bytes
        
        except Exception as e:
            raise Exception(f"Failed to merge PDFs: {str(e)}")
    
    def split_pdf(self, pdf_file: BinaryIO, page_ranges: str, user_id: int, job_id: str,
                  apply_watermark: bool = False, watermark_text: str = "") -> bytes:
        """Split PDF by page ranges and return as ZIP"""
        try:
            pdf_file.seek(0)
            input_pdf = PyPDF2.PdfReader(pdf_file)
            total_pages = len(input_pdf.pages)
            
            # Create temp directory
            temp_dir = self.create_user_temp_dir(user_id, job_id)
            
            # Parse page ranges (e.g., "1-3,5,7-9")
            ranges = []
            for range_str in page_ranges.split(','):
                range_str = range_str.strip()
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    ranges.append((start - 1, end))  # Convert to 0-indexed
                else:
                    page_num = int(range_str) - 1
                    ranges.append((page_num, page_num + 1))
            
            # Create split PDFs
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, (start, end) in enumerate(ranges):
                    output_pdf = PyPDF2.PdfWriter()
                    
                    for page_num in range(max(0, start), min(end, total_pages)):
                        output_pdf.add_page(input_pdf.pages[page_num])
                    
                    pdf_buffer = io.BytesIO()
                    output_pdf.write(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    pdf_bytes = pdf_buffer.read()
                    
                    if apply_watermark and watermark_text:
                        pdf_bytes = self.add_watermark(pdf_bytes, watermark_text)
                    
                    zip_file.writestr(f"split_{i+1}.pdf", pdf_bytes)
            
            zip_buffer.seek(0)
            return zip_buffer.read()
        
        except Exception as e:
            raise Exception(f"Failed to split PDF: {str(e)}")
    
    def compress_pdf(self, pdf_file: BinaryIO, user_id: int, job_id: str,
                     apply_watermark: bool = False, watermark_text: str = "") -> bytes:
        """Compress PDF file"""
        try:
            pdf_file.seek(0)
            
            with pikepdf.open(pdf_file) as pdf:
                output_buffer = io.BytesIO()
                pdf.save(output_buffer, compress_streams=True, 
                        object_stream_mode=pikepdf.ObjectStreamMode.generate)
                output_buffer.seek(0)
                
                result_bytes = output_buffer.read()
                
                if apply_watermark and watermark_text:
                    result_bytes = self.add_watermark(result_bytes, watermark_text)
                
                return result_bytes
        
        except Exception as e:
            raise Exception(f"Failed to compress PDF: {str(e)}")
    
    def pdf_to_images(self, pdf_file: BinaryIO, user_id: int, job_id: str,
                      format: str = "png", apply_watermark: bool = False, 
                      watermark_text: str = "") -> bytes:
        """Convert PDF to images and return as ZIP"""
        try:
            pdf_file.seek(0)
            temp_dir = self.create_user_temp_dir(user_id, job_id)
            
            if PDF2IMAGE_AVAILABLE:
                # Use pdf2image for better quality
                images = pdf2image.convert_from_bytes(pdf_file.read(), dpi=200)
            else:
                # Fallback to basic conversion
                # This is a simplified fallback - in production you'd want a more robust solution
                raise Exception("PDF to image conversion not available")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, image in enumerate(images):
                    img_buffer = io.BytesIO()
                    
                    # Add text watermark to image if needed
                    if apply_watermark and watermark_text:
                        from PIL import ImageDraw, ImageFont
                        draw = ImageDraw.Draw(image)
                        # Use default font
                        font_size = min(image.width, image.height) // 20
                        try:
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                        
                        # Calculate text position (center)
                        bbox = draw.textbbox((0, 0), watermark_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        x = (image.width - text_width) // 2
                        y = (image.height - text_height) // 2
                        
                        # Draw semi-transparent text
                        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
                        overlay_draw = ImageDraw.Draw(overlay)
                        overlay_draw.text((x, y), watermark_text, font=font, 
                                        fill=(128, 128, 128, 128))
                        image = Image.alpha_composite(image.convert('RGBA'), overlay)
                        image = image.convert('RGB')
                    
                    image.save(img_buffer, format=format.upper())
                    img_buffer.seek(0)
                    
                    zip_file.writestr(f"page_{i+1}.{format.lower()}", img_buffer.read())
            
            zip_buffer.seek(0)
            return zip_buffer.read()
        
        except Exception as e:
            raise Exception(f"Failed to convert PDF to images: {str(e)}")
    
    def images_to_pdf(self, image_files: List[BinaryIO], user_id: int, job_id: str,
                      apply_watermark: bool = False, watermark_text: str = "") -> bytes:
        """Convert images to PDF"""
        try:
            images = []
            
            for img_file in image_files:
                img_file.seek(0)
                image = Image.open(img_file)
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                images.append(image)
            
            if not images:
                raise Exception("No valid images provided")
            
            # Create PDF
            output_buffer = io.BytesIO()
            images[0].save(output_buffer, format='PDF', save_all=True, 
                          append_images=images[1:], resolution=200)
            output_buffer.seek(0)
            
            result_bytes = output_buffer.read()
            
            if apply_watermark and watermark_text:
                result_bytes = self.add_watermark(result_bytes, watermark_text)
            
            return result_bytes
        
        except Exception as e:
            raise Exception(f"Failed to convert images to PDF: {str(e)}")
    
    def extract_text(self, pdf_file: BinaryIO, user_id: int, job_id: str) -> str:
        """Extract text from PDF"""
        try:
            pdf_file.seek(0)
            text_content = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return '\n\n'.join(text_content)
        
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
