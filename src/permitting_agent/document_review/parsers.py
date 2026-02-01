"""Document parsers: PDF and Word (stubs with one working path for sample PDF)."""

from pathlib import Path

from pydantic import BaseModel

from permitting_agent.models import DocumentArtifact, ExtractedField, Citation
from permitting_agent.models.document import Confidence


class ParseResult(BaseModel):
    """Result of parsing a single document."""

    path: Path
    success: bool
    artifact: DocumentArtifact | None = None
    error: str | None = None


def parse_pdf(path: Path) -> ParseResult:
    """Extract text and key fields from a PDF. Stub: sample PDF returns mock fields."""
    try:
        # Stub: for MVP we use pypdf for text; key-field extraction is heuristic/sample
        text = _read_pdf_text(path)
        fields = _extract_fields_from_text(path, text) if text else []
        artifact = DocumentArtifact(
            path=path,
            kind="pdf",
            extracted_fields=fields,
            raw_text_preview=(text[:2000] + "..." if text and len(text) > 2000 else text),
        )
        return ParseResult(path=path, success=True, artifact=artifact)
    except Exception as e:
        return ParseResult(path=path, success=False, error=str(e))


def parse_docx(path: Path) -> ParseResult:
    """Extract text and key fields from a Word document. Stub: returns basic extraction."""
    try:
        text = _read_docx_text(path)
        fields = _extract_fields_from_text(path, text) if text else []
        artifact = DocumentArtifact(
            path=path,
            kind="docx",
            extracted_fields=fields,
            raw_text_preview=(text[:2000] + "..." if text and len(text) > 2000 else text),
        )
        return ParseResult(path=path, success=True, artifact=artifact)
    except Exception as e:
        return ParseResult(path=path, success=False, error=str(e))


def _read_pdf_text(path: Path) -> str:
    """Read raw text from PDF using pypdf."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n\n".join(parts) or ""
    except Exception:
        return ""


def _read_docx_text(path: Path) -> str:
    """Read raw text from Word using python-docx."""
    try:
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs) or ""
    except Exception:
        return ""


def _extract_fields_from_text(path: Path, text: str) -> list[ExtractedField]:
    """Heuristic extraction of common permit fields from text. Stub for MVP."""
    fields: list[ExtractedField] = []
    lower = text.lower()
    # Stub: look for common phrases and treat as "application" or "site plan" mentioned
    if "application" in lower or "permit" in lower:
        fields.append(
            ExtractedField(
                name="application_form",
                value="mentioned",
                confidence=Confidence.INFERRED,
                citations=[Citation(source_file=path.name, section_heading="Document text")],
            )
        )
    if "site plan" in lower or "location" in lower:
        fields.append(
            ExtractedField(
                name="site_plan",
                value="mentioned",
                confidence=Confidence.INFERRED,
                citations=[Citation(source_file=path.name, section_heading="Document text")],
            )
        )
    if "fee" in lower or "payment" in lower or "$" in text:
        fields.append(
            ExtractedField(
                name="fee",
                value="mentioned",
                confidence=Confidence.UNCERTAIN,
                citations=[Citation(source_file=path.name)],
            )
        )
    return fields


def parse_document(path: Path) -> ParseResult:
    """Dispatch to PDF or Word parser by extension."""
    suf = path.suffix.lower()
    if suf == ".pdf":
        return parse_pdf(path)
    if suf in (".docx", ".doc"):
        return parse_docx(path)
    return ParseResult(path=path, success=False, error=f"Unsupported format: {suf}")
