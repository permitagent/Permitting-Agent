"""Core Pydantic models for intake, documents, jurisdiction, outreach, and workflow."""

from permitting_agent.models.intake import (
    IntakeRequest,
    IntakeCase,
    ScopeKind,
    ScopeOfWork,
    SiteDetails,
)
from permitting_agent.models.document import (
    Citation,
    Checklist,
    ChecklistItem,
    Confidence,
    DocumentArtifact,
    ExtractedField,
    GapItem,
    WhatsNeededReport,
)
from permitting_agent.models.jurisdiction import (
    Certainty,
    PermitRequirement,
    PortalResearchResult,
    ResearchSource,
)
from permitting_agent.models.outreach import (
    Contact,
    OutreachDraft,
    ContactList,
)

__all__ = [
    "IntakeRequest",
    "IntakeCase",
    "ScopeKind",
    "ScopeOfWork",
    "SiteDetails",
    "Citation",
    "Checklist",
    "ChecklistItem",
    "Confidence",
    "DocumentArtifact",
    "ExtractedField",
    "GapItem",
    "WhatsNeededReport",
    "Certainty",
    "PermitRequirement",
    "PortalResearchResult",
    "ResearchSource",
    "Contact",
    "OutreachDraft",
    "ContactList",
]
