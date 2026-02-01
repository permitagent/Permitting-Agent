"""Tests for outreach service: discover contacts, draft emails."""

from pathlib import Path

import pytest

from permitting_agent.outreach import OutreachService
from permitting_agent.models import ContactList


def test_discover_and_save(tmp_output_dir: Path) -> None:
    """Discover contacts for City of Sample saves JSON + Markdown."""
    svc = OutreachService(output_dir=tmp_output_dir)
    out = tmp_output_dir / "outreach" / "City_of_Sample_contacts.json"
    contact_list = svc.discover_and_save("City of Sample", output_path=out)
    assert contact_list.jurisdiction == "City of Sample"
    assert len(contact_list.contacts) >= 1
    assert out.exists()
    assert out.with_suffix(".md").exists()


def test_draft_emails() -> None:
    """draft_emails produces one draft per role with contacts."""
    svc = OutreachService()
    contact_list = ContactList(
        jurisdiction="City of Sample",
        contacts=[
            type("C", (), {"role": "planning", "email": "p@example.gov", "name": "Jane"})(),
        ],
    )
    # ContactList.contacts are Contact models
    from permitting_agent.models import Contact
    contact_list = ContactList(
        jurisdiction="City of Sample",
        contacts=[
            Contact(role="planning", email="p@example.gov", name="Jane"),
        ],
    )
    drafts = svc.draft_emails(contact_list)
    assert len(drafts) >= 1
    assert any(d.to_role == "planning" for d in drafts)
    assert "City of Sample" in drafts[0].subject
