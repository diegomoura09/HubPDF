"""
Watermark service for PDF documents
"""
import io
from typing import BinaryIO, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
import math



class WatermarkService:
    """Service for applying watermarks to PDF documents"""
    
    def __init__(self):
        self.opacity = 0.15
        self.font_size = 36
        self.rotation = 45  # degrees
    
    def create_watermark_pdf(self, text: str, width: float, height: float) -> bytes:
        """Create a watermark PDF overlay"""
        buffer = io.BytesIO()
        
        # Create PDF canvas
        p = canvas.Canvas(buffer, pagesize=(width, height))
        
        # Set up watermark properties
        gray_value = 0.8  # Light gray
        p.setFillColor(Color(gray_value, gray_value, gray_value, alpha=self.opacity))
        p.setFont("Helvetica-Bold", self.font_size)
        
        # Calculate center position
        center_x = width / 2
        center_y = height / 2
        
        # Save graphics state
        p.saveState()
        
        # Move to center and rotate
        p.translate(center_x, center_y)
        p.rotate(self.rotation)
        
        # Draw text centered
        text_width = p.stringWidth(text, "Helvetica-Bold", self.font_size)
        p.drawString(-text_width / 2, -self.font_size / 2, text)
        
        # Restore graphics state
        p.restoreState()
        
        # Add multiple watermarks for better coverage
        self._add_diagonal_watermarks(p, text, width, height)
        
        # Finalize PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_diagonal_watermarks(self, canvas_obj, text: str, width: float, height: float):
        """Add multiple diagonal watermarks across the page"""
        # Calculate spacing
        spacing_x = width / 3
        spacing_y = height / 3
        
        # Add watermarks in a grid pattern
        for x_offset in [-spacing_x, 0, spacing_x]:
            for y_offset in [-spacing_y, 0, spacing_y]:
                if x_offset == 0 and y_offset == 0:
                    continue  # Skip center (already added)
                
                canvas_obj.saveState()
                canvas_obj.translate(width/2 + x_offset, height/2 + y_offset)
                canvas_obj.rotate(self.rotation)
                
                text_width = canvas_obj.stringWidth(text, "Helvetica-Bold", self.font_size)
                canvas_obj.drawString(-text_width / 2, -self.font_size / 2, text)
                canvas_obj.restoreState()
    
    def apply_watermark(
        self, 
        pdf_bytes: bytes, 
        watermark_text: str = None,
        locale: str = "pt"
    ) -> bytes:
        """Apply watermark to PDF document"""
        if not watermark_text:
            translations = get_translations(locale)
            watermark_text = translations.get("watermark_text", "HubPDF - Grátis")
        
        # Read input PDF
        input_buffer = io.BytesIO(pdf_bytes)
        reader = PdfReader(input_buffer)
        writer = PdfWriter()
        
        # Process each page
        for page_num, page in enumerate(reader.pages):
            # Get page dimensions
            page_box = page.mediabox
            width = float(page_box.width)
            height = float(page_box.height)
            
            # Create watermark for this page size
            watermark_bytes = self.create_watermark_pdf(watermark_text, width, height)
            watermark_buffer = io.BytesIO(watermark_bytes)
            watermark_reader = PdfReader(watermark_buffer)
            watermark_page = watermark_reader.pages[0]
            
            # Merge watermark with original page
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Write output
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    def should_apply_watermark(self, user: Optional[object], is_anonymous: bool = False) -> bool:
        """Determine if watermark should be applied based on user context"""
        # Always watermark for anonymous users
        if is_anonymous or user is None:
            return True
        
        # For logged in users, check plan and usage
        if hasattr(user, 'plan'):
            # Free plan: watermark after 4 operations
            if user.plan == "free":
                # This would need quota service to check daily usage
                return False  # For now, implement in quota service
            
            # Pro/Business: no watermark
            if user.plan in ["pro", "business"]:
                return False
        
        # Default to watermark for safety
        return True


# Global service instance
watermark_service = WatermarkService()