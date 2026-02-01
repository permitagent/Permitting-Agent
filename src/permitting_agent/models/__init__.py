"""Core Pydantic models for intake, documents, jurisdiction, outreach, and workflow."""

from permitting_agent.models.intake import (
    IntakeRequest,
    IntakeCase,
    ScopeOfWork,
    SiteDetails,
)
from permitting_agent.models.document import (
    ExtractedField,
    DocumentArtifact,
    ChecklistItem,
    WhatsNeededReport,
    Citation,
)
from permitting_agent.models.jurisdiction import (
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
    "ScopeOfWork",
    "SiteDetails",
    "ExtractedField",
    "DocumentArtifact",
    "ChecklistItem",
    "Checklist",
    "GapItem",
    "WhatsNeededReport",
    "Citation",
    "PermitRequirement",
    "PortalResearchResult",
    "ResearchSource",
    "Contact",
    "OutreachDraft",
    "ContactList",
]
