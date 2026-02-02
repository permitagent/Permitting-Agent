"""Crawl a portal URL and extract form fields (inputs, labels, required) from HTML."""

from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

# Default user agent; respect robots.txt via caller
DEFAULT_USER_AGENT = "PermittingAgent/1.0 (compliance; +https://github.com/permitting-agent)"
DEFAULT_TIMEOUT = 15.0


def crawl_form_fields(
    url: str,
    *,
    client: httpx.Client | None = None,
    user_agent: str = DEFAULT_USER_AGENT,
) -> list[dict]:
    """
    Fetch URL, parse HTML, and return a list of form fields found on the page.
    Each item: {"name": str, "label": str, "type": str, "required": bool}.
    Returns [] on fetch or parse failure.
    """
    fields: list[dict] = []
    try:
        use_client = client or httpx.Client()
        try:
            r = use_client.get(
                url,
                follow_redirects=True,
                timeout=DEFAULT_TIMEOUT,
                headers={"User-Agent": user_agent},
            )
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, "html.parser")
        finally:
            if not client:
                use_client.close()
    except Exception:
        return []

    seen_names: set[str] = set()
    for form in soup.find_all("form"):
        for tag in form.find_all(["input", "select", "textarea"]):
            name = tag.get("name") or tag.get("id")
            if not name or name in seen_names:
                continue
            if tag.name == "input" and (tag.get("type") or "text").lower() in ("hidden", "submit", "button", "image"):
                continue
            seen_names.add(name)
            label = _get_label(soup, tag)
            type_ = (tag.get("type") or "text").lower() if tag.name == "input" else tag.name
            required = tag.has_attr("required") or (tag.get("aria-required") == "true")
            fields.append({
                "name": name,
                "label": label or name.replace("_", " ").replace("-", " ").title(),
                "type": type_ if type_ in ("text", "email", "tel", "number", "url", "textarea", "select") else "text",
                "required": required,
            })
    return fields


def _get_label(soup: BeautifulSoup, tag) -> str | None:
    """Get associated label text for an input/select/textarea."""
    id_ = tag.get("id")
    if id_:
        label_el = soup.find("label", attrs={"for": id_})
        if label_el and label_el.get_text(strip=True):
            return label_el.get_text(strip=True)[:200]
    parent = tag.parent
    if parent and parent.name == "label" and parent.get_text(strip=True):
        return parent.get_text(strip=True)[:200]
    return None
