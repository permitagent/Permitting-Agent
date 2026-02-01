"""Sample jurisdiction adapter for end-to-end demo (no real scraping)."""

from datetime import datetime

from permitting_agent.models import (
    Checklist,
    ChecklistItem,
    PortalResearchResult,
    PermitRequirement,
    ResearchSource,
    ContactList,
    Contact,
)
from permitting_agent.models.intake import ScopeKind
from permitting_agent.adapters.base import JurisdictionAdapter


class SampleJurisdictionAdapter(JurisdictionAdapter):
    """Sample adapter: City of Sample. Returns static data for MVP demo."""

    @property
    def jurisdiction_name(self) -> str:
        return "City of Sample"

    @property
    def jurisdiction_id(self) -> str:
        return "city_of_sample"

    def get_checklist(self, scope: ScopeKind) -> Checklist:
        scope_str = scope.value if isinstance(scope, ScopeKind) else str(scope)
        return Checklist(
            jurisdiction=self.jurisdiction_name,
            scope=scope_str,
            items=[
                ChecklistItem(
                    id="app_form",
                    label="Permit application form",
                    required=True,
                    description="Signed application form",
                    typical_format="PDF",
                ),
                ChecklistItem(
                    id="site_plan",
                    label="Site plan",
                    required=True,
                    description="Site plan showing proposed location",
                    typical_format="PDF",
                ),
                ChecklistItem(
                    id="fee",
                    label="Application fee",
                    required=True,
                    description="Non-refundable fee",
                    typical_format="Check or online payment",
                ),
            ],
        )

    def research_portal(self) -> PortalResearchResult:
        now = datetime.utcnow()
        return PortalResearchResult(
            jurisdiction=self.jurisdiction_name,
            researched_at=now,
            requirements=[
                PermitRequirement(
                    key="application_fee",
                    label="Application fee",
                    value="$250",
                    certainty="cited",
                    sources=[
                        ResearchSource(
                            url="https://cityofsample.example.gov/permits",
                            fetched_at=now,
                            title="Permits - City of Sample",
                            snippet="Small cell permit fee: $250.",
                        ),
                    ],
                ),
                PermitRequirement(
                    key="submittal_format",
                    label="Submittal format",
                    value="PDF via portal or email",
                    certainty="cited",
                    sources=[
                        ResearchSource(
                            url="https://cityofsample.example.gov/permits",
                            fetched_at=now,
                            snippet="Submit applications in PDF format.",
                        ),
                    ],
                ),
            ],
            portal_url="https://cityofsample.example.gov/permits/apply",
            application_steps=[
                "Create account on portal",
                "Upload application form and site plan",
                "Pay fee online",
                "Submit for review",
            ],
            sources=[
                ResearchSource(url="https://cityofsample.example.gov/permits", fetched_at=now),
            ],
        )

    def discover_contacts(self) -> ContactList:
        now = datetime.utcnow()
        return ContactList(
            jurisdiction=self.jurisdiction_name,
            generated_at=now,
            contacts=[
                Contact(
                    name="Jane Planner",
                    role="planning",
                    email="planning@cityofsample.example.gov",
                    department="Planning",
                    source_url="https://cityofsample.example.gov/planning",
                    discovered_at=now,
                ),
                Contact(
                    name="Engineering Dept",
                    role="engineering",
                    email="engineering@cityofsample.example.gov",
                    department="Engineering",
                    source_url="https://cityofsample.example.gov/engineering",
                    discovered_at=now,
                ),
            ],
            source_urls=[
                "https://cityofsample.example.gov/planning",
                "https://cityofsample.example.gov/engineering",
            ],
        )
