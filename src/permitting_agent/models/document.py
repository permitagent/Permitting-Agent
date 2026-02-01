"""Document review models: extracted fields, checklist, What's Needed report with citations."""

from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    """Confidence in extracted or stated requirement."""

    CERTAIN = "certain"  # Cited from official source
    UNCERTAIN = "uncertain"  # Not found or ambiguous
    INFERRED = "inferred"  # Inferred from context, not direct cite


class Citation(BaseModel):
    """Evidence citation: page number and/or section heading."""

    page: int | None = None
    section_heading: str | None = None
    source_file: str | None = None
    excerpt: str | None = None


class ExtractedField(BaseModel):
    """A single field extracted from a document."""

    name: str
    value: str | None = None
    confidence: Confidence = Confidence.UNCERTAIN
    citations: list[Citation] = Field(default_factory=list)


class DocumentArtifact(BaseModel):
    """Result of ingesting one document (PDF/Word)."""

    path: Path
    kind: str = "pdf"  # pdf | docx
    extracted_fields: list[ExtractedField] = Field(default_factory=list)
    raw_text_preview: str | None = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


class ChecklistItem(BaseModel):
    """One item on the permit checklist (required vs optional)."""

    id: str
    label: str
    required: bool = True
    description: str | None = None
    typical_format: str | None = None  # e.g. "PDF", "Signed application"


class Checklist(BaseModel):
    """Full checklist for a jurisdiction/scope."""

    jurisdiction: str
    scope: str  # small_cell | fiber | both
    items: list[ChecklistItem] = Field(default_factory=list)


class GapItem(BaseModel):
    """A missing or incomplete item vs checklist."""

    checklist_item_id: str
    checklist_label: str
    status: str  # missing | incomplete | uncertain
    evidence: list[Citation] = Field(default_factory=list)
    notes: str | None = None


class WhatsNeededReport(BaseModel):
    """Human-readable 'What's Needed' report with evidence citations."""

    case_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    documents_reviewed: list[str] = Field(default_factory=list)
    gaps: list[GapItem] = Field(default_factory=list)
    summary: str | None = None
    citations: list[Citation] = Field(default_factory=list)
