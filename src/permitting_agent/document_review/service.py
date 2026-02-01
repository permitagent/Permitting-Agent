"""Document review service: ingest docs, compare to checklist, produce What's Needed report."""

import json
from pathlib import Path

from permitting_agent.models import (
    Checklist,
    ChecklistItem,
    WhatsNeededReport,
    GapItem,
    Citation,
    DocumentArtifact,
)
from permitting_agent.document_review.parsers import parse_document


class DocumentReviewService:
    """Ingest documents, compare to checklist, output What's Needed with citations."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = Path(output_dir or "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_review(
        self,
        case_id: str,
        doc_paths: list[Path],
        checklist: Checklist,
    ) -> tuple[list[DocumentArtifact], WhatsNeededReport]:
        """Parse all docs, compare to checklist, return artifacts and What's Needed report."""
        artifacts: list[DocumentArtifact] = []
        for p in doc_paths:
            if not p.exists():
                continue
            result = parse_document(p)
            if result.success and result.artifact:
                artifacts.append(result.artifact)

        # Map checklist item id -> normalized field names we might find in docs
        checklist_key_to_field: dict[str, list[str]] = {
            "app_form": ["application_form", "application", "permit"],
            "site_plan": ["site_plan", "site plan"],
            "fee": ["fee", "payment", "application_fee"],
        }

        gaps: list[GapItem] = []
        for item in checklist.items:
            found = False
            evidence: list[Citation] = []
            for art in artifacts:
                for ef in art.extracted_fields:
                    names = checklist_key_to_field.get(item.id, [item.id])
                    if ef.name.lower() in [n.lower() for n in names]:
                        found = True
                        if ef.citations:
                            evidence.extend(ef.citations)
            if not found:
                gaps.append(
                    GapItem(
                        checklist_item_id=item.id,
                        checklist_label=item.label,
                        status="missing",
                        evidence=evidence,
                        notes=f"Required: {item.description or item.label}",
                    )
                )

        report = WhatsNeededReport(
            case_id=case_id,
            documents_reviewed=[str(a.path) for a in artifacts],
            gaps=gaps,
            summary=f"Found {len(artifacts)} document(s). {len(gaps)} checklist item(s) missing or uncertain.",
            citations=[c for a in artifacts for ef in a.extracted_fields for c in ef.citations],
        )
        return artifacts, report

    def save_report(self, report: WhatsNeededReport, output_path: Path) -> None:
        """Write report as JSON and sidecar Markdown."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        json_path = output_path.with_suffix(".json")
        json_path.write_text(report.model_dump_json(indent=2))

        md_path = output_path.with_suffix(".md")
        md_path.write_text(self._report_to_markdown(report))

    def _report_to_markdown(self, report: WhatsNeededReport) -> str:
        """Human-readable Markdown for What's Needed report."""
        lines = [
            "# What's Needed Report",
            f"**Case ID:** {report.case_id}",
            f"**Generated:** {report.generated_at.isoformat()}",
            "",
            "## Documents reviewed",
        ]
        for d in report.documents_reviewed:
            lines.append(f"- {d}")
        lines.extend(["", "## Gaps (missing or uncertain)", ""])
        for g in report.gaps:
            lines.append(f"- **{g.checklist_label}** ({g.checklist_item_id}): {g.status}")
            if g.notes:
                lines.append(f"  - {g.notes}")
        if report.summary:
            lines.extend(["", "## Summary", "", report.summary])
        return "\n".join(lines)
