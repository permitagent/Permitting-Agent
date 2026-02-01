"""Crawler utilities: robots.txt check, rate limit, fetch with sources + timestamps."""

import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from robotexclusionrulesparser import RobotExclusionRulesParser

from permitting_agent.models import ResearchSource


DEFAULT_RATE_LIMIT_RPS = 1.0
DEFAULT_USER_AGENT = "PermittingAgent/1.0 (compliance; +https://github.com/permitting-agent)"


def can_fetch(parsed: RobotExclusionRulesParser, url: str, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """Return True if robots.txt allows fetching url for user_agent."""
    try:
        return parsed.is_allowed(user_agent, url)
    except Exception:
        return False


def get_robots_parser(base_url: str, client: httpx.Client | None = None) -> RobotExclusionRulesParser:
    """Fetch robots.txt for base_url and return parser. Respects rate limit via caller."""
    parsed = RobotExclusionRulesParser()
    parsed.user_agent = DEFAULT_USER_AGENT
    robots_url = urljoin(base_url, "/robots.txt")
    use_client = client or httpx.Client()
    try:
        r = use_client.get(robots_url, timeout=10.0)
        if r.status_code == 200:
            parsed.parse(r.text)
    except Exception:
        pass
    if not client:
        use_client.close()
    return parsed


def fetch_page(
    url: str,
    *,
    client: httpx.Client | None = None,
    rate_limit_rps: float = DEFAULT_RATE_LIMIT_RPS,
    last_fetch_time: float | None = None,
) -> tuple[str | None, ResearchSource]:
    """Fetch URL and return (body or None, ResearchSource with timestamp)."""
    now = datetime.utcnow()
    source = ResearchSource(url=url, fetched_at=now)
    if last_fetch_time is not None and rate_limit_rps > 0:
        elapsed = time.monotonic() - last_fetch_time
        if elapsed < 1.0 / rate_limit_rps:
            time.sleep(1.0 / rate_limit_rps - elapsed)
    use_client = client or httpx.Client()
    try:
        r = use_client.get(url, follow_redirects=True, timeout=15.0)
        if r.status_code == 200:
            source.snippet = (r.text[:500] + "...") if len(r.text) > 500 else r.text
            return r.text, source
        return None, source
    except Exception:
        return None, source
    finally:
        if client is None:
            use_client.close()


def save_sources(sources: list[ResearchSource], path: Path) -> None:
    """Write list of ResearchSource to JSON for audit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(s.model_dump_json() for s in sources),
        encoding="utf-8",
    )
