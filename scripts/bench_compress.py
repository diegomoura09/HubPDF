#!/usr/bin/env python3
"""
Benchmark de compressão de PDFs com diferentes níveis.
Testa os 3 níveis (light, balanced, strong) + opções (grayscale, rasterize).
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pdf_compress import compress_pdf
from app.pdf_analyze import analyze_pdf


def format_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_ratio(ratio):
    """Format compression ratio with color"""
    if ratio >= 60:
        return f"🟢 {ratio:.1f}%"
    elif ratio >= 30:
        return f"🟡 {ratio:.1f}%"
    else:
        return f"🔴 {ratio:.1f}%"


def benchmark_compression(input_pdf: str):
    """Benchmark compression on a single PDF"""
    input_path = Path(input_pdf)
    
    if not input_path.exists():
        print(f"❌ Arquivo não encontrado: {input_pdf}")
        return
    
    print(f"\n{'='*80}")
    print(f"📄 Testando: {input_path.name}")
    print(f"{'='*80}\n")
    
    # Analyze PDF first
    print("🔍 Analisando PDF...")
    analysis = analyze_pdf(str(input_path))
    print(f"  • Páginas: {analysis['pages']}")
    print(f"  • Tamanho original: {format_size(analysis['file_size'])}")
    print(f"  • Imagens: {analysis['images_pct']*100:.1f}%")
    print(f"  • Tem texto: {'Sim' if analysis['has_text'] else 'Não'}")
    print(f"  • Modo de cor: {analysis['color_mode_hint']}")
    print()
    
    # Test configurations
    configs = [
        ("light", False, False, "Leve (alta qualidade)"),
        ("balanced", False, False, "Equilibrado (recomendado)"),
        ("strong", False, False, "Forte (máxima compressão)"),
        ("balanced", True, False, "Equilibrado + Tons de cinza"),
        ("strong", True, False, "Forte + Tons de cinza"),
        ("strong", False, True, "Extremo (rasterizado)"),
    ]
    
    # Results table header
    print(f"{'Configuração':<35} {'Resultado':<15} {'Redução':<12} {'Engine':<20}")
    print(f"{'-'*35} {'-'*15} {'-'*12} {'-'*20}")
    
    output_dir = Path("/tmp/benchmark_output")
    output_dir.mkdir(exist_ok=True)
    
    for level, grayscale, rasterize, description in configs:
        # Create output filename
        suffix = f"_{level}"
        if grayscale:
            suffix += "_gray"
        if rasterize:
            suffix += "_raster"
        
        output_path = output_dir / f"{input_path.stem}{suffix}.pdf"
        
        # Compress
        try:
            result = compress_pdf(
                input_path=str(input_path),
                output_path=str(output_path),
                level=level,
                grayscale=grayscale,
                rasterize=rasterize
            )
            
            if result["success"]:
                size_str = format_size(result["output_bytes"])
                ratio_str = format_ratio(result["ratio"])
                engine_str = result["engine_used"]
                
                print(f"{description:<35} {size_str:<15} {ratio_str:<12} {engine_str:<20}")
            else:
                print(f"{description:<35} {'ERRO':<15} {'-':<12} {result.get('message', 'Unknown')}")
                
        except Exception as e:
            print(f"{description:<35} {'ERRO':<15} {'-':<12} {str(e)[:20]}")
    
    print(f"\n✅ Arquivos de teste salvos em: {output_dir}\n")


def main():
    """Main benchmark function"""
    print("\n🔬 HubPDF - Benchmark de Compressão de PDFs")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Look for test PDFs
    test_files_dir = Path("docs/examples")
    
    if not test_files_dir.exists():
        print(f"⚠️  Diretório de exemplos não encontrado: {test_files_dir}")
        print("📝 Criando PDF de teste...")
        
        # Create a simple test PDF
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            test_pdf = Path("/tmp/test_sample.pdf")
            c = canvas.Canvas(str(test_pdf), pagesize=letter)
            c.setFont("Helvetica", 12)
            
            for page in range(5):
                c.drawString(100, 750, f"Página {page + 1} - Teste de Compressão")
                c.drawString(100, 700, "Este é um PDF de teste para benchmark de compressão.")
                c.drawString(100, 650, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
                c.showPage()
            
            c.save()
            
            print(f"✅ PDF de teste criado: {test_pdf}")
            benchmark_compression(str(test_pdf))
            
        except Exception as e:
            print(f"❌ Erro ao criar PDF de teste: {e}")
            print("\n💡 Dica: Coloque PDFs de teste em docs/examples/")
            return
    else:
        # Test all PDFs in examples directory
        pdf_files = list(test_files_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ Nenhum PDF encontrado em {test_files_dir}")
            print("💡 Adicione arquivos PDF em docs/examples/ para testar")
            return
        
        for pdf_file in pdf_files[:3]:  # Limit to first 3 PDFs
            benchmark_compression(str(pdf_file))
    
    print("\n" + "="*80)
    print("✅ Benchmark concluído!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
