"""Pytest fixtures: temp dirs, sample PDF, sample case."""

import json
from pathlib import Path

import pytest

from permitting_agent.models import IntakeRequest, SiteDetails, ScopeOfWork, ScopeKind
from permitting_agent.intake import IntakeService


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """Create a minimal PDF with extractable text (using pypdf only: blank page + we write a .txt for parser)."""
    # Create a fake "PDF" that is actually a text file with .pdf extension for parser test,
    # OR use pypdf to create blank PDF. Parser reads with pypdf - blank PDF gives empty text.
    # So we need real text. Create a file that pypdf can read: use pypdf to add a page, then
    # we can't add text easily. So: create a real PDF with pypdf (blank) and in the test
    # we assert on the parser behavior for empty text (no fields). For "with text" test,
    # we use a temporary .txt file renamed to .pdf - no, that would break pypdf. So we need
    # either fpdf2 in test env or we mock. Let me create a minimal PDF that contains text
    # using raw PDF structure. Actually the simpler approach: in test_parsers we test
    # parse_pdf with a real PDF from pypdf (blank) and assert success and empty fields;
    # and we test _extract_fields_from_text with a string that contains "application" and "site plan"
    # to assert fields are extracted. So we don't need a PDF with text in the fixture.
    from pypdf import PdfWriter
    path = tmp_path / "sample.pdf"
    w = PdfWriter()
    w.add_blank_page(612, 792)
    w.write(str(path))
    w.close()
    return path


@pytest.fixture
def sample_pdf_with_text(tmp_path: Path) -> Path:
    """Create a PDF with text 'Permit application and site plan. Fee $250.' if fpdf2 available."""
    try:
        from fpdf import FPDF
        path = tmp_path / "sample_with_text.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, "Permit application and site plan. Fee $250.")
        pdf.output(str(path))
        return path
    except ImportError:
        from pypdf import PdfWriter
        path = tmp_path / "sample_with_text.pdf"
        w = PdfWriter()
        w.add_blank_page(612, 792)
        w.write(str(path))
        w.close()
        return path


@pytest.fixture
def intake_service(tmp_data_dir: Path) -> IntakeService:
    return IntakeService(data_dir=tmp_data_dir)


@pytest.fixture
def sample_case(intake_service: IntakeService) -> tuple[str, IntakeRequest]:
    """Create a case for City of Sample and return (case_id, request)."""
    request = IntakeRequest(
        jurisdiction="City of Sample",
        site=SiteDetails(address="123 Main St", jurisdiction="City of Sample"),
        scope=ScopeOfWork(kind=ScopeKind.SMALL_CELL),
        existing_doc_paths=[],
    )
    case = intake_service.create_case(request)
    return case.id, request
