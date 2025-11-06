"""
Conversão de múltiplas imagens para PDF com opções avançadas.
"""
import img2pdf
import io
from pathlib import Path
from typing import List, Dict, Any, BinaryIO
from PIL import Image, ImageOps
import pillow_heif

# Registrar suporte a HEIC/HEIF no Pillow
pillow_heif.register_heif_opener()

# Tamanhos de página em pontos (1 pt = 1/72 inch)
PAGE_SIZES = {
    "a3": (841.89, 1190.55),
    "a4": (595.28, 841.89),
    "a5": (419.53, 595.28),
    "letter": (612, 792),
    "auto": None  # Tamanho automático baseado na imagem
}

# Conversão mm → pontos
MM_TO_PT = 2.83464567


def images_to_pdf(
    image_files: List[BinaryIO],
    page_size: str = "a4",
    orientation: str = "auto",
    margin_mm: int = 0,
    fit_mode: str = "fit",
    grayscale: bool = False,
    jpeg_quality: int = 75
) -> bytes:
    """
    Converte múltiplas imagens em um único PDF.
    
    Args:
        image_files: Lista de arquivos de imagem (BinaryIO)
        page_size: Tamanho da página ("a3", "a4", "a5", "letter", "auto")
        orientation: Orientação ("auto", "portrait", "landscape")
        margin_mm: Margem em milímetros (aplicada em todos os lados)
        fit_mode: Como ajustar a imagem ("fit" ou "fill")
        grayscale: Se True, converte imagens para escala de cinza
        jpeg_quality: Qualidade JPEG (40-100) para compressão
        
    Returns:
        bytes: PDF gerado
    """
    processed_images = []
    
    for img_file in image_files:
        img_file.seek(0)
        img_bytes = img_file.read()
        
        # Abrir imagem com Pillow
        img = Image.open(io.BytesIO(img_bytes))
        
        # Corrigir rotação EXIF
        img = ImageOps.exif_transpose(img)
        
        # Converter para RGB se necessário (img2pdf requer RGB ou L)
        if img.mode not in ("RGB", "L", "1"):
            img = img.convert("RGB")
        
        # Converter para escala de cinza se solicitado
        if grayscale:
            img = img.convert("L")
        
        # Processar imagem conforme opções
        processed_img = _process_image(
            img, page_size, orientation, margin_mm, fit_mode
        )
        
        # Converter para bytes
        img_buffer = io.BytesIO()
        
        # Salvar como JPEG com qualidade especificada (exceto para imagens monocromáticas)
        if processed_img.mode == "1":
            # Imagens binárias (1-bit) salvamos como PNG
            processed_img.save(img_buffer, format="PNG", optimize=True)
        elif processed_img.mode == "L":
            # Escala de cinza
            processed_img.save(img_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
        else:
            # RGB
            processed_img.save(img_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
        
        processed_images.append(img_buffer.getvalue())
    
    # Gerar PDF com img2pdf
    pdf_bytes = img2pdf.convert(processed_images)
    
    return pdf_bytes


def _process_image(
    img: Image.Image,
    page_size: str,
    orientation: str,
    margin_mm: int,
    fit_mode: str
) -> Image.Image:
    """
    Processa imagem conforme configurações de página.
    
    Returns:
        Image.Image: Imagem processada (redimensionada conforme necessário)
    """
    # Tamanho automático: retornar imagem original (img2pdf usa tamanho natural)
    if page_size == "auto":
        return img
    
    # Obter dimensões da página em pontos
    page_w, page_h = PAGE_SIZES[page_size]
    
    # Aplicar orientação
    if orientation == "landscape":
        page_w, page_h = max(page_w, page_h), min(page_w, page_h)
    elif orientation == "portrait":
        page_w, page_h = min(page_w, page_h), max(page_w, page_h)
    elif orientation == "auto":
        # Determinar orientação baseada na imagem
        img_w, img_h = img.size
        is_landscape = img_w > img_h
        
        if is_landscape:
            page_w, page_h = max(page_w, page_h), min(page_w, page_h)
        else:
            page_w, page_h = min(page_w, page_h), max(page_w, page_h)
    
    # Calcular margens em pontos
    margin_pt = margin_mm * MM_TO_PT
    
    # Área útil (descontando margens)
    usable_w = page_w - (2 * margin_pt)
    usable_h = page_h - (2 * margin_pt)
    
    # Dimensões da imagem
    img_w, img_h = img.size
    
    if fit_mode == "fit":
        # Escalar mantendo proporção para caber na área útil
        scale = min(usable_w / img_w, usable_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # Redimensionar imagem
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return img_resized
    
    elif fit_mode == "fill":
        # Escalar para preencher toda a área (pode cortar)
        scale = max(usable_w / img_w, usable_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # Redimensionar imagem
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Recortar centro para caber na área útil
        left = (new_w - usable_w) // 2
        top = (new_h - usable_h) // 2
        right = left + usable_w
        bottom = top + usable_h
        
        img_cropped = img_resized.crop((int(left), int(top), int(right), int(bottom)))
        return img_cropped
    
    return img


def get_compression_info(input_images: List[BinaryIO], output_pdf: bytes) -> Dict[str, Any]:
    """
    Retorna informações sobre a conversão.
    
    Returns:
        dict com input_bytes_sum, output_bytes, num_pages
    """
    input_total = sum(len(img.read()) if hasattr(img, 'read') else 0 for img in input_images)
    output_size = len(output_pdf)
    
    # Reset file pointers
    for img in input_images:
        if hasattr(img, 'seek'):
            img.seek(0)
    
    return {
        "input_bytes_sum": input_total,
        "output_bytes": output_size,
        "num_pages": len(input_images),
        "reduction_pct": ((input_total - output_size) / input_total * 100) if input_total > 0 else 0
    }
