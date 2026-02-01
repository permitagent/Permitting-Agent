"""Tests for jurisdiction adapters and registry."""

import pytest

from permitting_agent.adapters import get_adapter, list_adapters
from permitting_agent.adapters.sample_jurisdiction import SampleJurisdictionAdapter
from permitting_agent.models.intake import ScopeKind


def test_list_adapters() -> None:
    """At least City of Sample is registered."""
    names = list_adapters()
    assert "city_of_sample" in names


def test_get_adapter_city_of_sample() -> None:
    """get_adapter('City of Sample') returns SampleJurisdictionAdapter instance."""
    adapter = get_adapter("City of Sample")
    assert adapter is not None
    assert isinstance(adapter, SampleJurisdictionAdapter)
    assert adapter.jurisdiction_name == "City of Sample"
    assert adapter.jurisdiction_id == "city_of_sample"


def test_get_adapter_unknown() -> None:
    """Unknown jurisdiction returns None."""
    assert get_adapter("Unknown City") is None


def test_sample_adapter_checklist() -> None:
    """Sample adapter returns checklist with expected items."""
    adapter = SampleJurisdictionAdapter()
    checklist = adapter.get_checklist(ScopeKind.SMALL_CELL)
    assert checklist.jurisdiction == "City of Sample"
    assert checklist.scope == "small_cell"
    ids = [i.id for i in checklist.items]
    assert "app_form" in ids
    assert "site_plan" in ids
    assert "fee" in ids


def test_sample_adapter_research_portal() -> None:
    """Sample adapter returns portal research with requirements and sources."""
    adapter = SampleJurisdictionAdapter()
    result = adapter.research_portal()
    assert result.jurisdiction == "City of Sample"
    assert len(result.requirements) >= 1
    assert result.portal_url is not None
    assert any(r.key == "application_fee" for r in result.requirements)


def test_sample_adapter_discover_contacts() -> None:
    """Sample adapter returns contact list with source URLs."""
    adapter = SampleJurisdictionAdapter()
    contacts = adapter.discover_contacts()
    assert contacts.jurisdiction == "City of Sample"
    assert len(contacts.contacts) >= 1
    assert len(contacts.source_urls) >= 1
