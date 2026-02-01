"""CLI for Permitting + Site Acquisition agent (typer)."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from permitting_agent.intake import IntakeService
from permitting_agent.intake.service import IntakeService as IntakeServiceType
from permitting_agent.models import (
    IntakeRequest,
    SiteDetails,
    ScopeOfWork,
    ScopeKind,
)
from permitting_agent.document_review import DocumentReviewService
from permitting_agent.portal_research import PortalResearchService
from permitting_agent.portal_automation import PortalAutomationService
from permitting_agent.outreach import OutreachService
from permitting_agent.adapters import get_adapter, list_adapters

app = typer.Typer(
    name="permitting",
    help="Permitting + Site Acquisition agent for telecom (small cell + fiber).",
)
console = Console()


@app.command()
def intake(
    jurisdiction: str = typer.Option(..., "--jurisdiction", "-j", help="Jurisdiction name (e.g. City of Sample)"),
    address: str = typer.Option(..., "--address", "-a", help="Site address"),
    scope: str = typer.Option("small_cell", "--scope", "-s", help="Scope: small_cell | fiber | both"),
    docs: list[Path] = typer.Option(default=[], "--docs", "-d", path_type=Path, help="Paths to existing docs"),
    output_dir: Path = typer.Option(Path("output"), "--output-dir", "-o", path_type=Path),
    data_dir: Path = typer.Option(Path("data"), "--data-dir", path_type=Path),
) -> None:
    """Create an intake case from jurisdiction, address, scope, and optional docs."""
    try:
        kind = ScopeKind(scope) if scope in ("small_cell", "fiber", "both") else ScopeKind.SMALL_CELL
    except ValueError:
        kind = ScopeKind.SMALL_CELL
    site = SiteDetails(address=address, jurisdiction=jurisdiction)
    request = IntakeRequest(
        jurisdiction=jurisdiction,
        site=site,
        scope=ScopeOfWork(kind=kind),
        existing_doc_paths=docs,
    )
    service: IntakeServiceType = IntakeService(data_dir=data_dir)
    case = service.create_case(request)
    console.print(f"[green]Created case[/green] [bold]{case.id}[/bold]")
    console.print(f"  Jurisdiction: {jurisdiction}")
    console.print(f"  Address: {address}")
    console.print(f"  Scope: {kind.value}")
    if docs:
        console.print(f"  Docs: {[str(p) for p in docs]}")
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case_path = out_dir / "intake_case.json"
    case_path.write_text(case.model_dump_json(indent=2))
    console.print(f"  Saved: {case_path}")


@app.command()
def document_review(
    case_id: str = typer.Option(..., "--case-id", "-c", help="Intake case ID"),
    docs: list[Path] = typer.Option(..., "--docs", "-d", path_type=Path, help="Paths to documents to review"),
    checklist_path: Path | None = typer.Option(None, "--checklist", path_type=Path),
    output: Path = typer.Option(Path("output/report"), "--output", "-o", path_type=Path),
    data_dir: Path = typer.Option(Path("data"), "--data-dir", path_type=Path),
) -> None:
    """Review documents against checklist; output What's Needed report (JSON + Markdown)."""
    intake_svc = IntakeService(data_dir=data_dir)
    case = intake_svc.get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        raise typer.Exit(1)
    adapter = get_adapter(case.request.jurisdiction)
    if adapter is None:
        console.print("[yellow]No jurisdiction adapter; using default checklist.[/yellow]")
        from permitting_agent.models import Checklist, ChecklistItem
        checklist = Checklist(
            jurisdiction=case.request.jurisdiction,
            scope=case.request.scope.kind.value,
            items=[
                ChecklistItem(id="app_form", label="Permit application form", required=True),
                ChecklistItem(id="site_plan", label="Site plan", required=True),
                ChecklistItem(id="fee", label="Application fee", required=True),
            ],
        )
    else:
        checklist = adapter.get_checklist(case.request.scope.kind)
    review_svc = DocumentReviewService(output_dir=output.parent)
    doc_paths = [p for p in docs if p.exists()]
    if not doc_paths:
        console.print("[red]No existing document paths provided.[/red]")
        raise typer.Exit(1)
    artifacts, report = review_svc.run_review(case_id, doc_paths, checklist)
    review_svc.save_report(report, output)
    console.print(f"[green]Document review complete.[/green]")
    console.print(f"  Documents reviewed: {len(artifacts)}")
    console.print(f"  Gaps: {len(report.gaps)}")
    console.print(f"  Report: {output.with_suffix('.json')} and {output.with_suffix('.md')}")


@app.command()
def portal_research(
    jurisdiction: str = typer.Option(..., "--jurisdiction", "-j", help="Jurisdiction name"),
    output: Path = typer.Option(Path("output/research"), "--output", "-o", path_type=Path),
) -> None:
    """Fetch permit requirements from jurisdiction (adapter or uncertain stub). Saves JSON + sources."""
    svc = PortalResearchService(output_dir=output.parent)
    result = svc.research_and_save(jurisdiction, output_path=output)
    console.print(f"[green]Portal research complete.[/green]")
    console.print(f"  Jurisdiction: {result.jurisdiction}")
    console.print(f"  Requirements: {len(result.requirements)}")
    if result.portal_url:
        console.print(f"  Portal: {result.portal_url}")
    console.print(f"  Saved: {output}")


@app.command()
def portal_automation(
    case_id: str = typer.Option(..., "--case-id", "-c"),
    approve_each_step: bool = typer.Option(True, "--approve-each-step/--no-approve", help="Require approval before each step"),
    data_dir: Path = typer.Option(Path("data"), "--data-dir", path_type=Path),
) -> None:
    """Run Playwright-based submission flow with human-in-the-loop. Never submits without confirmation."""
    intake_svc = IntakeService(data_dir=data_dir)
    case = intake_svc.get_case(case_id)
    portal_url = None
    if case:
        adapter = get_adapter(case.request.jurisdiction)
        if adapter:
            research = adapter.research_portal()
            portal_url = research.portal_url
    svc = PortalAutomationService(approve_each_step=approve_each_step)
    if approve_each_step:
        def approve(step_name: str, step_data: dict) -> bool:
            typer.echo(f"Step: {step_name}")
            if step_data.get("danger"):
                typer.echo("  [DANGER] This step submits the application.")
            return typer.confirm("Approve this step?", default=False)
        svc._approval_callback = approve
    result = svc.run_flow(case_id, case=case, portal_url=portal_url)
    console.print(f"[green]Flow status:[/green] {result['status']}")
    console.print(f"  Completed steps: {result.get('completed_steps', [])}")


@app.command()
def outreach(
    jurisdiction: str = typer.Option(..., "--jurisdiction", "-j"),
    output: Path = typer.Option(Path("output/outreach"), "--output", "-o", path_type=Path),
) -> None:
    """Discover contacts from official sources; save contact list and generate email drafts."""
    svc = OutreachService(output_dir=output.parent)
    contact_list = svc.discover_and_save(jurisdiction, output_path=output)
    drafts = svc.draft_emails(contact_list)
    console.print(f"[green]Outreach data generated.[/green]")
    console.print(f"  Contacts: {len(contact_list.contacts)}")
    console.print(f"  Email drafts: {len(drafts)}")
    console.print(f"  Saved: {output} (JSON + .md)")


@app.command()
def adapters() -> None:
    """List registered jurisdiction adapters."""
    names = list_adapters()
    table = Table(title="Jurisdiction adapters")
    table.add_column("ID", style="cyan")
    for n in names:
        table.add_row(n)
    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
