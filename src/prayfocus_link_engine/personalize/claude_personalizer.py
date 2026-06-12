"""Claude-powered personalization.

For each prospect we (optionally) fetch a snippet of their page, then ask Claude
for a one-sentence, genuine personalized opener and a recommended outreach angle.
If ANTHROPIC_API_KEY is absent, we fall back to a neutral, non-fabricated opener
so the pipeline still completes.

Model default: claude-sonnet-4-6 (good quality/cost for per-prospect drafting).
Use claude-opus-4-8 for your highest-value journalist/partner targets.
"""

from __future__ import annotations

import json
import os

import httpx

from .. import APP_NAME, APP_URL
from ..models import Prospect

_HEADERS = {"User-Agent": "PrayFocusOutreachBot/0.1 (+https://www.prayfocus.app)"}

_SYSTEM = (
    "You are an outreach research assistant for a Christian prayer & focus app "
    f"called {APP_NAME} ({APP_URL}). Given a snippet of a prospect's web page, "
    "write a SHORT, sincere, specific opener line referencing something real on "
    "their site, and recommend the best outreach angle. Be warm and respectful "
    "of faith. Never invent facts. Return STRICT JSON: "
    '{"opener": "...", "angle": "..."}'
)


def _fetch_snippet(url: str, limit: int = 2500) -> str:
    try:
        with httpx.Client(timeout=15, headers=_HEADERS, follow_redirects=True) as c:
            from bs4 import BeautifulSoup

            text = BeautifulSoup(c.get(url).text, "html.parser").get_text(" ", strip=True)
            return text[:limit]
    except Exception:
        return ""


def _neutral_opener(p: Prospect) -> tuple[str, str]:
    return (
        f"I've been following {p.name} and appreciate the work you publish for your readers.",
        "Lead with shared mission; keep the ask soft.",
    )


def personalize_prospect(
    p: Prospect,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 600,
    fetch_page: bool = True,
) -> None:
    """Populate p.personalized_opener and p.recommended_angle in place."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        p.personalized_opener, p.recommended_angle = _neutral_opener(p)
        return

    snippet = _fetch_snippet(p.url) if fetch_page else ""
    user = (
        f"Prospect: {p.name}\nURL: {p.url}\nCategory: {p.category}\n"
        f"Opportunity: {p.opportunity_type}\n\nPage snippet:\n{snippet or '(no snippet available)'}"
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        raw = "".join(block.text for block in resp.content if block.type == "text").strip()
        # tolerate fenced or bare JSON
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        p.personalized_opener = data.get("opener", "").strip()
        p.recommended_angle = data.get("angle", "").strip()
    except Exception:
        p.personalized_opener, p.recommended_angle = _neutral_opener(p)

    if not p.personalized_opener:
        p.personalized_opener, p.recommended_angle = _neutral_opener(p)
