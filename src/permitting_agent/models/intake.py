"""Intake models: jurisdiction, address/site details, scope of work, existing docs."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ScopeKind(str, Enum):
    """Type of telecom work."""

    SMALL_CELL = "small_cell"
    FIBER = "fiber"
    BOTH = "both"


class ScopeOfWork(BaseModel):
    """Scope of work for the permit."""

    kind: ScopeKind = ScopeKind.SMALL_CELL
    description: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class SiteDetails(BaseModel):
    """Address and site-specific details."""

    address: str
    parcel_id: str | None = None
    lat: float | None = None
    lon: float | None = None
    jurisdiction: str
    county: str | None = None
    state: str | None = None
    zip_code: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class IntakeRequest(BaseModel):
    """User-provided intake: jurisdiction, site, scope, optional doc paths."""

    jurisdiction: str
    site: SiteDetails
    scope: ScopeOfWork = Field(default_factory=lambda: ScopeOfWork(kind=ScopeKind.SMALL_CELL))
    existing_doc_paths: list[Path] = Field(default_factory=list)


class IntakeCase(BaseModel):
    """Persisted intake case with id and timestamps."""

    id: str
    request: IntakeRequest
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta: dict[str, Any] = Field(default_factory=dict)
