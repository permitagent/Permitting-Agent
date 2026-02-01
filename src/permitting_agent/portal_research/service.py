"""Portal research service: use adapter or crawl; respect robots.txt and rate limit; save sources."""

import json
from pathlib import Path

from permitting_agent.models import PortalResearchResult, ResearchSource
from permitting_agent.adapters import get_adapter
from permitting_agent.portal_research.crawler import (
    get_robots_parser,
    can_fetch,
    fetch_page,
    DEFAULT_RATE_LIMIT_RPS,
)


class PortalResearchService:
    """Run portal research via jurisdiction adapter; optionally crawl; save JSON + sources."""

    def __init__(
        self,
        output_dir: Path | None = None,
        rate_limit_rps: float = DEFAULT_RATE_LIMIT_RPS,
    ):
        self.output_dir = Path(output_dir or "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_rps = rate_limit_rps

    def research(self, jurisdiction: str) -> PortalResearchResult:
        """Run research: use adapter if available, else return uncertain stub with no crawl."""
        adapter = get_adapter(jurisdiction)
        if adapter is not None:
            result = adapter.research_portal()
            # If adapter returned live URLs we could verify with crawler (optional)
            return result

        # No adapter: return uncertain result (never guess legal requirements)
        return PortalResearchResult(
            jurisdiction=jurisdiction,
            requirements=[],
            raw_notes="No jurisdiction adapter found. Requirements not researched; mark as uncertain.",
        )

    def research_and_save(self, jurisdiction: str, output_path: Path | None = None) -> PortalResearchResult:
        """Run research and save JSON + sources to output dir."""
        result = self.research(jurisdiction)
        out = output_path or (self.output_dir / "portal_research" / f"{jurisdiction.replace(' ', '_')}.json")
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)

        # JSON
        out.write_text(result.model_dump_json(indent=2))

        # Sources audit
        sources_path = out.with_suffix(".sources.jsonl")
        sources = result.sources or []
        for r in result.requirements:
            sources.extend(r.sources)
        if sources:
            sources_path.write_text("\n".join(s.model_dump_json() for s in sources))

        return result
