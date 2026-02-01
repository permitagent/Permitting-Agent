"""Outreach service: use adapter to discover contacts, generate email drafts and contact list."""

import json
from pathlib import Path

from permitting_agent.models import ContactList, Contact, OutreachDraft
from permitting_agent.adapters import get_adapter


class OutreachService:
    """Discover contacts and produce outreach drafts and contact list."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = Path(output_dir or "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def discover_and_save(self, jurisdiction: str, output_path: Path | None = None) -> ContactList:
        """Discover contacts via adapter; save contact list JSON + Markdown."""
        adapter = get_adapter(jurisdiction)
        if adapter is None:
            contact_list = ContactList(jurisdiction=jurisdiction, contacts=[], source_urls=[])
        else:
            contact_list = adapter.discover_contacts()

        out = output_path or (self.output_dir / "outreach" / f"{jurisdiction.replace(' ', '_')}_contacts.json")
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(contact_list.model_dump_json(indent=2))

        md_path = out.with_suffix(".md")
        md_path.write_text(self._contact_list_to_markdown(contact_list))

        return contact_list

    def draft_emails(self, contact_list: ContactList) -> list[OutreachDraft]:
        """Generate outreach email drafts for planning/engineering/ROW/clerk."""
        drafts: list[OutreachDraft] = []
        by_role: dict[str, list[Contact]] = {}
        for c in contact_list.contacts:
            by_role.setdefault(c.role, []).append(c)

        for role in ("planning", "engineering", "row", "clerk"):
            contacts = by_role.get(role, [])
            if not contacts:
                continue
            drafts.append(
                OutreachDraft(
                    to_role=role,
                    subject=f"Permit inquiry – {contact_list.jurisdiction}",
                    body=_default_body(role, contact_list.jurisdiction),
                    contact_ids=[c.email or c.name or str(i) for i, c in enumerate(contacts)],
                    template_used="default",
                )
            )
        return drafts

    def _contact_list_to_markdown(self, cl: ContactList) -> str:
        lines = [
            f"# Contact list: {cl.jurisdiction}",
            f"Generated: {cl.generated_at.isoformat()}",
            "",
            "## Contacts",
        ]
        for c in cl.contacts:
            lines.append(f"- **{c.role}**")
            if c.name:
                lines.append(f"  - Name: {c.name}")
            if c.email:
                lines.append(f"  - Email: {c.email}")
            if c.phone:
                lines.append(f"  - Phone: {c.phone}")
            if c.source_url:
                lines.append(f"  - Source: {c.source_url}")
        lines.extend(["", "## Source URLs", ""])
        for u in cl.source_urls:
            lines.append(f"- {u}")
        return "\n".join(lines)


def _default_body(role: str, jurisdiction: str) -> str:
    return f"""Hello,

We are preparing a permit application for telecom infrastructure (small cell / fiber) within {jurisdiction}.
Could you please advise on the current application process, required documents, and any key contacts in your {role} department?

Thank you."""
