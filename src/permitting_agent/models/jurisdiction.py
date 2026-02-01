"""Jurisdiction and portal research models: requirements, sources, timestamps."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Certainty(str, Enum):
    """Whether a requirement is from an official source or uncertain."""

    CITED = "cited"  # From official source (URL + timestamp)
    UNCERTAIN = "uncertain"  # Not found or could not verify


class ResearchSource(BaseModel):
    """A single source URL with fetch timestamp (audit)."""

    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    title: str | None = None
    snippet: str | None = None


class PermitRequirement(BaseModel):
    """One permit requirement (step, fee, format, etc.)."""

    key: str  # e.g. application_fee, submittal_format
    label: str
    value: str | None = None  # e.g. "$500", "PDF only"
    certainty: Certainty = Certainty.UNCERTAIN
    sources: list[ResearchSource] = Field(default_factory=list)
    notes: str | None = None


class PortalResearchResult(BaseModel):
    """Structured result of portal/jurisdiction research."""

    jurisdiction: str
    researched_at: datetime = Field(default_factory=datetime.utcnow)
    requirements: list[PermitRequirement] = Field(default_factory=list)
    portal_url: str | None = None
    application_steps: list[str] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    raw_notes: str | None = None
