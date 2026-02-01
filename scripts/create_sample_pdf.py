"""Create a minimal sample PDF for document review E2E."""

from pathlib import Path

try:
    from pypdf import PdfWriter
except ImportError:
    raise SystemExit("pip install pypdf")

try:
    from fpdf import FPDF
    _HAS_FPDF = True
except ImportError:
    _HAS_FPDF = False


def create_sample_pdf(out_path: Path) -> None:
    """Create sample.pdf with text 'Permit application and site plan. Fee $250.' if fpdf2 available."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if _HAS_FPDF:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, "Permit application and site plan. Fee $250.")
        pdf.output(str(out_path))
    else:
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.write(str(out_path))
        writer.close()


if __name__ == "__main__":
    import sys
    base = Path(__file__).resolve().parent.parent
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "samples" / "sample.pdf"
    create_sample_pdf(path)
    print(f"Created {path}")
