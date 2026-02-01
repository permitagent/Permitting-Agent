"""Outreach models: contacts, email drafts, contact list with source URLs."""

from datetime import datetime

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """A single contact (planning, engineering, ROW, clerk)."""

    name: str | None = None
    role: str  # e.g. planning, engineering, row, clerk
    email: str | None = None
    phone: str | None = None
    department: str | None = None
    source_url: str | None = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str | None = None


class OutreachDraft(BaseModel):
    """Draft outreach email."""

    to_role: str  # e.g. planning
    subject: str
    body: str
    contact_ids: list[str] = Field(default_factory=list)
    template_used: str | None = None


class ContactList(BaseModel):
    """Exported contact list with source URLs."""

    jurisdiction: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    contacts: list[Contact] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
