"""Tests for document review service: run_review, report, markdown."""

from pathlib import Path

import pytest

from permitting_agent.models import Checklist, ChecklistItem, WhatsNeededReport
from permitting_agent.document_review import DocumentReviewService
from permitting_agent.adapters import get_adapter
from permitting_agent.models.intake import ScopeKind


@pytest.fixture
def sample_checklist() -> Checklist:
    adapter = get_adapter("City of Sample")
    assert adapter is not None
    return adapter.get_checklist(ScopeKind.SMALL_CELL)


def test_run_review_empty_docs(tmp_output_dir: Path, sample_checklist: Checklist) -> None:
    """Review with no existing doc paths: no artifacts, all gaps."""
    svc = DocumentReviewService(output_dir=tmp_output_dir)
    artifacts, report = svc.run_review("case1", [], sample_checklist)
    assert len(artifacts) == 0
    assert len(report.gaps) == len(sample_checklist.items)


def test_run_review_with_pdf(
    tmp_output_dir: Path,
    sample_checklist: Checklist,
    sample_pdf_with_text: Path,
) -> None:
    """Review with one PDF: at least one artifact; gaps may be reduced if text matches."""
    svc = DocumentReviewService(output_dir=tmp_output_dir)
    artifacts, report = svc.run_review("case1", [sample_pdf_with_text], sample_checklist)
    assert len(artifacts) >= 1
    assert report.case_id == "case1"
    assert len(report.documents_reviewed) >= 1


def test_save_report(tmp_output_dir: Path, sample_checklist: Checklist) -> None:
    """save_report writes JSON and Markdown."""
    svc = DocumentReviewService(output_dir=tmp_output_dir)
    _, report = svc.run_review("case1", [], sample_checklist)
    out = tmp_output_dir / "report"
    svc.save_report(report, out)
    assert (tmp_output_dir / "report.json").exists()
    assert (tmp_output_dir / "report.md").exists()
    content = (tmp_output_dir / "report.md").read_text()
    assert "What's Needed" in content
    assert "case1" in content
