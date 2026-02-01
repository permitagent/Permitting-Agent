#!/usr/bin/env python3
"""Run one end-to-end path: intake (City of Sample) -> document review with sample PDF."""

import sys
from pathlib import Path

# Add src to path when run from repo root
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from permitting_agent.intake import IntakeService
from permitting_agent.models import IntakeRequest, SiteDetails, ScopeOfWork, ScopeKind
from permitting_agent.document_review import DocumentReviewService
from permitting_agent.adapters import get_adapter


def main() -> None:
    data_dir = repo_root / "data"
    output_dir = repo_root / "output"
    samples_dir = repo_root / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Create sample PDF if missing
    sample_pdf = samples_dir / "sample.pdf"
    if not sample_pdf.exists():
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.cell(0, 10, "Permit application and site plan. Fee $250.")
            pdf.output(str(sample_pdf))
        except ImportError:
            from pypdf import PdfWriter
            w = PdfWriter()
            w.add_blank_page(612, 792)
            w.write(str(sample_pdf))
            w.close()
        print(f"Created {sample_pdf}")

    # 2) Intake: create case for City of Sample
    intake_svc = IntakeService(data_dir=data_dir)
    request = IntakeRequest(
        jurisdiction="City of Sample",
        site=SiteDetails(address="123 Main St", jurisdiction="City of Sample"),
        scope=ScopeOfWork(kind=ScopeKind.SMALL_CELL),
        existing_doc_paths=[sample_pdf],
    )
    case = intake_svc.create_case(request)
    print(f"Intake: case_id={case.id}")

    # 3) Document review: checklist from adapter, review sample PDF
    adapter = get_adapter("City of Sample")
    assert adapter is not None
    checklist = adapter.get_checklist(ScopeKind.SMALL_CELL)
    review_svc = DocumentReviewService(output_dir=output_dir)
    artifacts, report = review_svc.run_review(case.id, [sample_pdf], checklist)
    report_path = output_dir / "e2e_report"
    review_svc.save_report(report, report_path)
    print(f"Document review: {len(artifacts)} doc(s), {len(report.gaps)} gap(s)")
    print(f"Report: {report_path}.json and {report_path}.md")
    print("E2E done.")


if __name__ == "__main__":
    main()
