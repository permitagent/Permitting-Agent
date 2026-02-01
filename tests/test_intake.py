"""Tests for intake service: create case, persist, load."""

from pathlib import Path

import pytest

from permitting_agent.models import IntakeRequest, SiteDetails, ScopeOfWork, ScopeKind
from permitting_agent.intake import IntakeService


def test_create_case(intake_service: IntakeService) -> None:
    """Create case returns case with id and persists."""
    request = IntakeRequest(
        jurisdiction="City of Sample",
        site=SiteDetails(address="123 Main St", jurisdiction="City of Sample"),
        scope=ScopeOfWork(kind=ScopeKind.SMALL_CELL),
    )
    case = intake_service.create_case(request)
    assert case.id
    assert case.request.jurisdiction == "City of Sample"
    assert case.request.site.address == "123 Main St"


def test_get_case(intake_service: IntakeService, sample_case: tuple[str, IntakeRequest]) -> None:
    """Load case by id returns same data."""
    case_id, _ = sample_case
    loaded = intake_service.get_case(case_id)
    assert loaded is not None
    assert loaded.id == case_id
    assert loaded.request.jurisdiction == "City of Sample"


def test_get_case_missing(intake_service: IntakeService) -> None:
    """Load nonexistent case returns None."""
    assert intake_service.get_case("nonexistent") is None


def test_resolve_adapter(intake_service: IntakeService) -> None:
    """resolve_adapter('City of Sample') returns adapter."""
    adapter = intake_service.resolve_adapter("City of Sample")
    assert adapter is not None
    assert adapter.jurisdiction_name == "City of Sample"
