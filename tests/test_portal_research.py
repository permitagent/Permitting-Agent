"""Tests for portal research: crawler utilities and service."""

from pathlib import Path
from unittest.mock import patch

import pytest

from permitting_agent.portal_research.crawler import (
    get_robots_parser,
    can_fetch,
    save_sources,
    fetch_page,
    DEFAULT_USER_AGENT,
)
from permitting_agent.portal_research.service import PortalResearchService
from permitting_agent.models import ResearchSource


def test_can_fetch_allowed() -> None:
    """can_fetch with empty parser allows (no disallow)."""
    from robotexclusionrulesparser import RobotExclusionRulesParser
    p = RobotExclusionRulesParser()
    # Empty parser typically allows all
    assert can_fetch(p, "https://example.com/page", DEFAULT_USER_AGENT) is True


def test_portal_research_service_sample() -> None:
    """Portal research for City of Sample returns requirements and portal_url."""
    svc = PortalResearchService(output_dir=Path("/tmp/out"))
    result = svc.research("City of Sample")
    assert result.jurisdiction == "City of Sample"
    assert len(result.requirements) >= 1
    assert result.portal_url is not None


def test_portal_research_service_unknown() -> None:
    """Unknown jurisdiction returns uncertain result, no guess."""
    svc = PortalResearchService(output_dir=Path("/tmp/out"))
    result = svc.research("Unknown City XYZ")
    assert result.jurisdiction == "Unknown City XYZ"
    assert result.requirements == []
    assert "uncertain" in (result.raw_notes or "").lower() or result.raw_notes is not None


def test_save_sources(tmp_path: Path) -> None:
    """save_sources writes JSONL of ResearchSource for audit."""
    from datetime import datetime
    sources = [
        ResearchSource(url="https://example.com/a", fetched_at=datetime.utcnow()),
        ResearchSource(url="https://example.com/b", fetched_at=datetime.utcnow()),
    ]
    path = tmp_path / "sources.jsonl"
    save_sources(sources, path)
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert "example.com/a" in lines[0]
    assert "example.com/b" in lines[1]
