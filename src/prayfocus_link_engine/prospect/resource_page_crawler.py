"""Resource-page link prospecting.

Given a list of 'resource'/'links' pages (great backlink targets), fetch each,
extract outbound links, and record the page itself as a resource_page prospect.
Pure stdlib + httpx + BeautifulSoup; safe to run offline (network errors are
swallowed per-URL).
"""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from ..db import Store
from ..models import Prospect

_HEADERS = {"User-Agent": "PrayFocusOutreachBot/0.1 (+https://www.prayfocus.app)"}


def crawl_resource_pages(store: Store, urls: list[str]) -> int:
    """Record each resource page as a prospect. Returns rows added."""
    added = 0
    with httpx.Client(timeout=20, headers=_HEADERS, follow_redirects=True) as client:
        for url in urls:
            try:
                resp = client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            title = (soup.title.string if soup.title else url) or url
            outbound = sum(
                1
                for a in soup.find_all("a", href=True)
                if a["href"].startswith("http")
            )
            p = Prospect(
                name=title.strip()[:200],
                url=url,
                category="resource_page",
                opportunity_type="backlink",
                source="resource_crawl",
                notes=f"{outbound} outbound links on page",
            )
            if store.upsert(p) != -1:
                added += 1
    return added
