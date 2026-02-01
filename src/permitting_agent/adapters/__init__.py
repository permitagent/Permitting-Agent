"""Pluggable jurisdiction adapters for portal research, outreach, checklists."""

from permitting_agent.adapters.base import JurisdictionAdapter
from permitting_agent.adapters.registry import get_adapter, list_adapters

__all__ = [
    "JurisdictionAdapter",
    "get_adapter",
    "list_adapters",
]
