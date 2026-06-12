"""Search-based prospecting.

Thin adapter around a SERP API (SerpAPI by default). If SERPAPI_KEY is not set,
this is a no-op that returns 0, so the pipeline still runs offline.

Typical queries for a Christian prayer/focus app, e.g.:
    "best christian prayer apps" , "prayer app review",
    "christian productivity resources", inurl:resources christian prayer
"""

from __future__ import annotations

import os

import httpx

from ..db import Store
from ..models import Prospect

_CATEGORY_HINTS = {
    "review": "review_site",
    "directory": "app_directory",
    "podcast": "podcast",
    "blog": "blog",
}


def _guess_category(title: str, url: str) -> str:
    blob = f"{title} {url}".lower()
    for hint, category in _CATEGORY_HINTS.items():
        if hint in blob:
            return category
    return "blog"


def collect_from_search(store: Store, queries: list[str], per_query: int = 10) -> int:
    """Run search queries and add results as prospects. Returns rows added.

    Requires SERPAPI_KEY. Without it, returns 0 (graceful no-op).
    """
    key = os.environ.get("SERPAPI_KEY")
    if not key:
        return 0

    added = 0
    with httpx.Client(timeout=20) as client:
        for q in queries:
            resp = client.get(
                "https://serpapi.com/search.json",
                params={"q": q, "num": per_query, "api_key": key, "engine": "google"},
            )
            resp.raise_for_status()
            for item in resp.json().get("organic_results", [])[:per_query]:
                url = item.get("link")
                title = item.get("title") or url
                if not url:
                    continue
                p = Prospect(
                    name=title,
                    url=url,
                    category=_guess_category(title, url),
                    opportunity_type="backlink",
                    source=f"serp:{q}",
                    notes=item.get("snippet", ""),
                )
                if store.upsert(p) != -1:
                    added += 1
    return added
