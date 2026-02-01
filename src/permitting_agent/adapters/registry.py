"""Registry for pluggable jurisdiction adapters."""

from permitting_agent.adapters.base import JurisdictionAdapter
from permitting_agent.adapters.sample_jurisdiction import SampleJurisdictionAdapter

# Register adapters by jurisdiction_id (normalized: lower, spaces -> underscores)
_REGISTRY: dict[str, type[JurisdictionAdapter]] = {
    "city_of_sample": SampleJurisdictionAdapter,
}


def _normalize_jurisdiction_id(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def get_adapter(jurisdiction: str) -> JurisdictionAdapter | None:
    """Return an adapter instance for the given jurisdiction name, or None."""
    key = _normalize_jurisdiction_id(jurisdiction)
    cls = _REGISTRY.get(key)
    if cls is None:
        return None
    return cls()


def list_adapters() -> list[str]:
    """Return list of registered jurisdiction ids."""
    return list(_REGISTRY.keys())


def register_adapter(jurisdiction_id: str, adapter_class: type[JurisdictionAdapter]) -> None:
    """Register a new adapter (for tests or dynamic loading)."""
    _REGISTRY[_normalize_jurisdiction_id(jurisdiction_id)] = adapter_class
