"""
Compressão avançada de PDFs usando Ghostscript, qpdf e pikepdf.
"""
import subprocess
import shutil
import pikepdf
from pathlib import Path
from typing import Dict, Any, Optional
from app.pdf_analyze import analyze_pdf, recommend_compression_strategy


def compress_pdf(
    input_path: str,
    output_path: str,
    level: str = "balanced",
    grayscale: bool = False,
    rasterize: bool = False
) -> Dict[str, Any]:
    """
    Comprime um PDF usando a melhor estratégia baseada em análise automática.
    
    Args:
        input_path: Caminho do PDF de entrada
        output_path: Caminho do PDF de saída
        level: "light"|"balanced"|"strong" (nível de compressão)
        grayscale: Se True, converte para tons de cinza
        rasterize: Se True, rasteriza páginas (modo extremo)
        
    Returns:
        dict com:
        - input_bytes: int
        - output_bytes: int
        - ratio: float (% de redução)
        - engine_used: str
        - level: str
        - grayscale: bool
        - rasterize: bool
        - success: bool
        - message: str
    """
    # Analisar PDF
    analysis = analyze_pdf(input_path)
    input_size = analysis["file_size"]
    
    result = {
        "input_bytes": input_size,
        "output_bytes": input_size,
        "ratio": 0.0,
        "engine_used": "none",
        "level": level,
        "grayscale": grayscale,
        "rasterize": rasterize,
        "success": False,
        "message": ""
    }
    
    # Verificar se Ghostscript está disponível
    gs_available = shutil.which("gs") is not None
    
    if not gs_available:
        # Fallback para qpdf+pikepdf
        result["engine_used"] = "qpdf_pikepdf"
        result["message"] = "Compressão limitada (Ghostscript não disponível)"
        success = _compress_with_qpdf_pikepdf(input_path, output_path)
        
        if success:
            output_size = Path(output_path).stat().st_size
            result["output_bytes"] = output_size
            result["ratio"] = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0
            result["success"] = True
        
        return result
    
    # Escolher estratégia baseada na análise
    strategy = recommend_compression_strategy(analysis)
    
    # Modo rasterize sempre usa Ghostscript
    if rasterize:
        strategy = "ghostscript"
        result["engine_used"] = "ghostscript_rasterize"
        success = _compress_with_ghostscript_rasterize(
            input_path, output_path, level, grayscale
        )
    elif strategy == "ghostscript":
        result["engine_used"] = "ghostscript"
        success = _compress_with_ghostscript(
            input_path, output_path, level, grayscale, analysis
        )
    else:
        result["engine_used"] = "qpdf"
        success = _compress_with_qpdf_pikepdf(input_path, output_path)
    
    # Pós-processamento com qpdf e pikepdf (se não foi rasterizado)
    if success and not rasterize and strategy == "ghostscript":
        _postprocess_with_qpdf_pikepdf(output_path)
    
    # Verificar resultado
    if success and Path(output_path).exists():
        output_size = Path(output_path).stat().st_size
        
        # Se saída >= entrada, retornar original
        if output_size >= input_size:
            shutil.copy2(input_path, output_path)
            result["output_bytes"] = input_size
            result["ratio"] = 0.0
            result["success"] = True
            result["message"] = "Sem redução significativa - arquivo já otimizado"
        else:
            result["output_bytes"] = output_size
            result["ratio"] = ((input_size - output_size) / input_size * 100)
            result["success"] = True
            result["message"] = "Compressão bem-sucedida"
    else:
        result["success"] = False
        result["message"] = "Erro durante compressão"
    
    return result


def _compress_with_ghostscript(
    input_path: str,
    output_path: str,
    level: str,
    grayscale: bool,
    analysis: Dict[str, Any]
) -> bool:
    """Comprime PDF usando Ghostscript com configurações otimizadas."""
    try:
        # Args base (comuns a todos os níveis)
        gs_args = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dDetectDuplicateImages=true",
            "-dUseFlateCompression=true",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dPreserveAnnots=false",
            "-dAutoRotatePages=/None",
            "-dDownsampleColorImages=true",
            "-dDownsampleGrayImages=true",
            "-dDownsampleMonoImages=true",
        ]
        
        # Configurações por nível
        if level == "light":
            gs_args.extend([
                "-dPDFSETTINGS=/printer",
                "-dColorImageDownsampleType=/Bicubic",
                "-dColorImageResolution=180",
                "-dGrayImageDownsampleType=/Bicubic",
                "-dGrayImageResolution=180",
                "-dMonoImageDownsampleType=/Subsample",
                "-dMonoImageResolution=600",
                "-dAutoFilterColorImages=false",
                "-sColorImageFilter=/DCTEncode",
                "-dJPEGQ=70",
                "-dAutoFilterGrayImages=false",
                "-sGrayImageFilter=/DCTEncode",
            ])
        elif level == "strong":
            gs_args.extend([
                "-dPDFSETTINGS=/screen",
                "-dColorImageResolution=96",
                "-dGrayImageResolution=96",
                "-dMonoImageResolution=600",
                "-dAutoFilterColorImages=false",
                "-sColorImageFilter=/DCTEncode",
                "-dJPEGQ=40",
                "-dAutoFilterGrayImages=false",
                "-sGrayImageFilter=/DCTEncode",
            ])
        else:  # balanced (default)
            gs_args.extend([
                "-dPDFSETTINGS=/ebook",
                "-dColorImageResolution=120",
                "-dGrayImageResolution=120",
                "-dMonoImageResolution=600",
                "-dAutoFilterColorImages=false",
                "-sColorImageFilter=/DCTEncode",
                "-dJPEGQ=55",
                "-dAutoFilterGrayImages=false",
                "-sGrayImageFilter=/DCTEncode",
            ])
        
        # Modo monocromático (se detectado)
        if analysis.get("color_mode_hint") == "mono":
            gs_args.append("-sMonoImageFilter=/JBIG2Encode")
        
        # Conversão para grayscale
        if grayscale:
            gs_args.extend([
                "-sProcessColorModel=DeviceGray",
                "-sColorConversionStrategy=Gray",
                "-dConvertCMYKImagesToRGB=false",
            ])
        
        # Arquivos de entrada/saída
        gs_args.extend([
            f"-sOutputFile={output_path}",
            input_path
        ])
        
        # Executar Ghostscript
        subprocess.run(gs_args, check=True, capture_output=True, timeout=120)
        return True
        
    except subprocess.TimeoutExpired:
        print("Error: Ghostscript timeout")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error: Ghostscript failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Error: Ghostscript exception: {e}")
        return False


def _compress_with_ghostscript_rasterize(
    input_path: str,
    output_path: str,
    level: str,
    grayscale: bool
) -> bool:
    """Modo extremo: rasteriza páginas do PDF."""
    try:
        # DPI baseado no nível
        dpi = 150 if level == "balanced" else 110 if level == "strong" else 180
        
        gs_args = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dPDFSETTINGS=/screen",
            f"-r{dpi}",
            "-dDownsampleColorImages=true",
            "-dColorImageResolution=96",
            "-dGrayImageResolution=96",
            "-dJPEGQ=35",
        ]
        
        if grayscale:
            gs_args.extend([
                "-sProcessColorModel=DeviceGray",
                "-sColorConversionStrategy=Gray",
            ])
        
        gs_args.extend([
            f"-sOutputFile={output_path}",
            input_path
        ])
        
        subprocess.run(gs_args, check=True, capture_output=True, timeout=180)
        return True
        
    except Exception as e:
        print(f"Error: Rasterize failed: {e}")
        return False


def _compress_with_qpdf_pikepdf(input_path: str, output_path: str) -> bool:
    """Comprime usando qpdf + pikepdf (otimização estrutural)."""
    try:
        # Tentar qpdf primeiro
        if shutil.which("qpdf"):
            qpdf_args = [
                "qpdf",
                "--linearize",
                "--object-streams=generate",
                "--compress-streams=y",
                "--recompress-flate",
                input_path,
                output_path
            ]
            subprocess.run(qpdf_args, check=True, capture_output=True, timeout=60)
        else:
            # Fallback para apenas pikepdf
            shutil.copy2(input_path, output_path)
        
        # Pós-processar com pikepdf
        with pikepdf.open(output_path, allow_overwriting_input=True) as pdf:
            pdf.remove_unreferenced_resources()
            pdf.save(
                output_path,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                linearize=True
            )
        
        return True
        
    except Exception as e:
        print(f"Error: qpdf/pikepdf failed: {e}")
        return False


def _postprocess_with_qpdf_pikepdf(pdf_path: str) -> None:
    """Pós-processamento com qpdf e pikepdf para otimização final."""
    try:
        temp_path = str(Path(pdf_path).with_suffix('.tmp.pdf'))
        
        # qpdf pass
        if shutil.which("qpdf"):
            qpdf_args = [
                "qpdf",
                "--linearize",
                "--object-streams=generate",
                "--compress-streams=y",
                "--recompress-flate",
                pdf_path,
                temp_path
            ]
            subprocess.run(qpdf_args, check=True, capture_output=True, timeout=60)
            
            # pikepdf final pass
            with pikepdf.open(temp_path, allow_overwriting_input=True) as pdf:
                pdf.remove_unreferenced_resources()
                pdf.save(
                    pdf_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate,
                    linearize=True
                )
            
            # Remover temp
            Path(temp_path).unlink(missing_ok=True)
        else:
            # Apenas pikepdf
            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                pdf.remove_unreferenced_resources()
                pdf.save(
                    pdf_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate,
                    linearize=True
                )
    except Exception as e:
        print(f"Warning: Post-processing failed: {e}")
