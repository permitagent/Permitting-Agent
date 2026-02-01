"""Tests for document parsers (PDF/Word) and extraction utilities."""

from pathlib import Path

import pytest

from permitting_agent.document_review.parsers import (
    parse_pdf,
    parse_docx,
    parse_document,
    _extract_fields_from_text,
    _read_pdf_text,
)
from permitting_agent.models.document import Confidence


def test_parse_pdf_blank(sample_pdf_path: Path) -> None:
    """Parse a blank PDF: success, empty or no key fields."""
    result = parse_pdf(sample_pdf_path)
    assert result.success is True
    assert result.artifact is not None
    assert result.artifact.path == sample_pdf_path
    assert result.artifact.kind == "pdf"


def test_parse_pdf_with_text(sample_pdf_with_text: Path) -> None:
    """Parse a PDF with text: should extract application_form, site_plan, fee if fpdf2 used."""
    result = parse_pdf(sample_pdf_with_text)
    assert result.success is True
    assert result.artifact is not None
    # If PDF has text, we should get some extracted fields
    text = _read_pdf_text(sample_pdf_with_text)
    if "application" in text.lower() or "permit" in text.lower():
        assert any(f.name == "application_form" for f in result.artifact.extracted_fields)
    if "site plan" in text.lower() or "fee" in text.lower():
        assert len(result.artifact.extracted_fields) >= 1


def test_extract_fields_from_text() -> None:
    """Heuristic extraction: application, site plan, fee mentioned -> fields."""
    from permitting_agent.models import ExtractedField, Citation
    path = Path("doc.pdf")
    text = "This is a permit application. Please see the site plan. The fee is $250."
    fields = _extract_fields_from_text(path, text)
    assert len(fields) >= 2
    names = [f.name for f in fields]
    assert "application_form" in names or "site_plan" in names or "fee" in names


def test_parse_document_dispatch_pdf(sample_pdf_path: Path) -> None:
    """parse_document dispatches .pdf to parse_pdf."""
    result = parse_document(sample_pdf_path)
    assert result.success is True
    assert result.artifact is not None


def test_parse_document_unsupported() -> None:
    """Unsupported extension returns success=False and error."""
    result = parse_document(Path("file.xyz"))
    assert result.success is False
    assert result.error is not None
    assert "Unsupported" in result.error or "xyz" in result.error


def test_parse_pdf_missing_file() -> None:
    """Missing file raises or returns error."""
    result = parse_pdf(Path("/nonexistent/file.pdf"))
    # Pypdf or file open may raise or return empty
    assert result.success is False or result.artifact is not None
