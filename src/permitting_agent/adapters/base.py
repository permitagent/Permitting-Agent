"""Base interface for pluggable jurisdiction adapters."""

from abc import ABC, abstractmethod

from permitting_agent.models import (
    PortalResearchResult,
    ContactList,
    Checklist,
)
from permitting_agent.models.intake import ScopeKind


class JurisdictionAdapter(ABC):
    """Adapter for a specific jurisdiction: research, checklist, contacts.
    New jurisdictions can be added by implementing this interface.
    """

    @property
    @abstractmethod
    def jurisdiction_name(self) -> str:
        """Display name for the jurisdiction (e.g. 'City of Sample')."""
        ...

    @property
    @abstractmethod
    def jurisdiction_id(self) -> str:
        """Stable id used in config and case storage (e.g. 'city_of_sample')."""
        ...

    @abstractmethod
    def get_checklist(self, scope: ScopeKind) -> Checklist:
        """Return the permit checklist for this jurisdiction and scope."""
        ...

    @abstractmethod
    def research_portal(self) -> PortalResearchResult:
        """Crawl/scrape official pages for requirements, fees, portal link.
        Must respect robots.txt and rate limits; cite sources or mark uncertain.
        """
        ...

    @abstractmethod
    def discover_contacts(self) -> ContactList:
        """Discover key contacts from official sources; return list with source URLs."""
        ...
