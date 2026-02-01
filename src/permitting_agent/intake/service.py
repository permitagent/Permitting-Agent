"""Intake service: create case, persist to JSON, resolve jurisdiction adapter."""

import json
import uuid
from pathlib import Path

from permitting_agent.models import IntakeRequest, IntakeCase
from permitting_agent.adapters import get_adapter


class IntakeService:
    """Create intake cases and persist to data dir."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = Path(data_dir or "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cases_dir = self.data_dir / "cases"
        self.cases_dir.mkdir(parents=True, exist_ok=True)

    def create_case(self, request: IntakeRequest) -> IntakeCase:
        """Create a new case with generated id and timestamps."""
        case_id = str(uuid.uuid4())[:8]
        case = IntakeCase(id=case_id, request=request)
        self._save_case(case)
        return case

    def get_case(self, case_id: str) -> IntakeCase | None:
        """Load case by id."""
        path = self.cases_dir / f"{case_id}.json"
        if not path.exists():
            return None
        raw = json.loads(path.read_text())
        # Paths in existing_doc_paths stored as strings
        req = raw["request"]
        if "existing_doc_paths" in req:
            req["existing_doc_paths"] = [Path(p) for p in req["existing_doc_paths"]]
        return IntakeCase.model_validate(raw)

    def _save_case(self, case: IntakeCase) -> None:
        path = self.cases_dir / f"{case.id}.json"
        # Serialize Paths as strings
        payload = case.model_dump(mode="json")
        payload["request"]["existing_doc_paths"] = [str(p) for p in case.request.existing_doc_paths]
        path.write_text(json.dumps(payload, indent=2))

    def resolve_adapter(self, jurisdiction: str):
        """Return jurisdiction adapter for name, or None."""
        return get_adapter(jurisdiction)
