"""
Análise de PDFs para determinar a melhor estratégia de compressão.
"""
import pikepdf
from pdfminer.high_level import extract_text
from pathlib import Path
from typing import Dict, Any


def analyze_pdf(input_path: str) -> Dict[str, Any]:
    """
    Analisa um PDF e retorna características para otimizar a compressão.
    
    Args:
        input_path: Caminho do arquivo PDF
        
    Returns:
        dict com:
        - images_pct: float 0..1 (% estimada de objetos de imagem)
        - pages: int (número de páginas)
        - has_text: bool (se tem texto extraível)
        - color_mode_hint: str ("color"|"gray"|"mono")
        - file_size: int (tamanho em bytes)
    """
    result = {
        "images_pct": 0.0,
        "pages": 0,
        "has_text": False,
        "color_mode_hint": "color",
        "file_size": 0
    }
    
    try:
        # Tamanho do arquivo
        result["file_size"] = Path(input_path).stat().st_size
        
        # Abrir com pikepdf
        with pikepdf.open(input_path) as pdf:
            result["pages"] = len(pdf.pages)
            
            # Contar objetos de imagem vs objetos totais
            image_count = 0
            total_objects = 0
            colorspace_hints = []
            
            for page in pdf.pages:
                if "/Resources" in page and "/XObject" in page["/Resources"]:
                    xobjects = page["/Resources"]["/XObject"]
                    for obj_name in xobjects:
                        total_objects += 1
                        obj = xobjects[obj_name]
                        
                        # Verificar se é imagem
                        if "/Subtype" in obj and obj["/Subtype"] == "/Image":
                            image_count += 1
                            
                            # Analisar colorspace
                            if "/ColorSpace" in obj:
                                cs = str(obj["/ColorSpace"])
                                if "DeviceGray" in cs or "Gray" in cs:
                                    colorspace_hints.append("gray")
                                elif "DeviceCMYK" in cs or "DeviceRGB" in cs:
                                    colorspace_hints.append("color")
            
            # Calcular % de imagens
            if total_objects > 0:
                result["images_pct"] = image_count / total_objects
            
            # Determinar modo de cor predominante
            if colorspace_hints:
                gray_count = colorspace_hints.count("gray")
                if gray_count / len(colorspace_hints) > 0.7:
                    result["color_mode_hint"] = "gray"
                    
                    # Se quase tudo é grayscale, pode ser mono
                    if gray_count / len(colorspace_hints) > 0.9:
                        result["color_mode_hint"] = "mono"
        
        # Tentar extrair texto
        try:
            text = extract_text(input_path)
            # Considerar que tem texto se extrair mais de 50 caracteres alfanuméricos
            text_chars = sum(1 for c in text if c.isalnum())
            result["has_text"] = text_chars > 50
        except:
            result["has_text"] = False
            
    except Exception as e:
        # Em caso de erro, retornar valores padrão
        print(f"Warning: Erro ao analisar PDF: {e}")
        result["file_size"] = Path(input_path).stat().st_size if Path(input_path).exists() else 0
    
    return result


def recommend_compression_strategy(analysis: Dict[str, Any]) -> str:
    """
    Recomenda a melhor estratégia de compressão baseada na análise.
    
    Args:
        analysis: Resultado de analyze_pdf()
        
    Returns:
        "ghostscript" ou "qpdf"
    """
    # Se tem muitas imagens (>30%), usar Ghostscript para recomprimir
    if analysis["images_pct"] >= 0.3:
        return "ghostscript"
    
    # Se tem pouco conteúdo de imagem mas tem texto, usar qpdf
    if analysis["has_text"] and analysis["images_pct"] < 0.3:
        return "qpdf"
    
    # Default: Ghostscript (mais agressivo)
    return "ghostscript"
