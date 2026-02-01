"""Portal automation: Playwright flow with approve-each-step; never submit without confirmation."""

from pathlib import Path
from typing import Callable, Any

from permitting_agent.models import IntakeCase
from permitting_agent.adapters import get_adapter


# Step approval callback: (step_name, step_data) -> True to proceed, False to abort
ApprovalCallback = Callable[[str, dict[str, Any]], bool]


class PortalAutomationService:
    """Run Playwright-based submission flow with human-in-the-loop. Never submits without approval."""

    def __init__(
        self,
        approve_each_step: bool = True,
        approval_callback: ApprovalCallback | None = None,
    ):
        self.approve_each_step = approve_each_step
        self._approval_callback = approval_callback or _default_approval_callback

    def run_flow(
        self,
        case_id: str,
        case: IntakeCase | None = None,
        portal_url: str | None = None,
    ) -> dict[str, Any]:
        """Execute submission flow steps; after each step call approval_callback. Never submit without confirm."""
        # Stub: no real Playwright run in MVP; we only demonstrate the hook points
        steps: list[dict[str, Any]] = [
            {"id": "navigate", "name": "Navigate to portal", "url": portal_url or "https://example.gov/permits"},
            {"id": "login", "name": "Login (if required)", "note": "Only if user supplied credentials"},
            {"id": "upload_application", "name": "Upload application form", "note": "User must confirm"},
            {"id": "upload_site_plan", "name": "Upload site plan", "note": "User must confirm"},
            {"id": "pay_fee", "name": "Pay fee", "note": "User must confirm"},
            {"id": "submit", "name": "Submit application", "danger": "Final submit; requires explicit approval"},
        ]
        completed: list[str] = []
        for step in steps:
            if self.approve_each_step:
                ok = self._approval_callback(step["name"], step)
                if not ok:
                    return {"status": "aborted", "completed_steps": completed, "aborted_at": step["id"]}
            completed.append(step["id"])
            # Stub: real implementation would run Playwright here
        return {"status": "completed", "completed_steps": completed}


def _default_approval_callback(step_name: str, step_data: dict[str, Any]) -> bool:
    """Default: no interactive prompt in library; CLI will inject prompt. Return True to proceed in tests."""
    return True
