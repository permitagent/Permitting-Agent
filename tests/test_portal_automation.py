"""Tests for portal automation: human-in-the-loop, never submit without approval."""

import pytest

from permitting_agent.portal_automation import PortalAutomationService
from permitting_agent.models import IntakeCase, IntakeRequest, SiteDetails, ScopeOfWork, ScopeKind


@pytest.fixture
def sample_case() -> IntakeCase:
    return IntakeCase(
        id="case1",
        request=IntakeRequest(
            jurisdiction="City of Sample",
            site=SiteDetails(address="123 Main St", jurisdiction="City of Sample"),
            scope=ScopeOfWork(kind=ScopeKind.SMALL_CELL),
        ),
    )


def test_run_flow_approve_each_step_default_callback(sample_case: IntakeCase) -> None:
    """With approve_each_step and default callback (True), flow completes."""
    svc = PortalAutomationService(approve_each_step=True)
    result = svc.run_flow("case1", case=sample_case, portal_url="https://example.gov/permits")
    assert result["status"] == "completed"
    assert "completed_steps" in result
    assert len(result["completed_steps"]) >= 1


def test_run_flow_abort_on_disapproval(sample_case: IntakeCase) -> None:
    """When callback returns False, flow aborts and never submits."""
    def reject_all(_name: str, _data: dict) -> bool:
        return False
    svc = PortalAutomationService(approve_each_step=True, approval_callback=reject_all)
    result = svc.run_flow("case1", case=sample_case)
    assert result["status"] == "aborted"
    assert "aborted_at" in result
    # Submit step never completed because we reject on first step
    assert "submit" not in result.get("completed_steps", [])
