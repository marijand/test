"""Contact discovery.

Uses Hunter.io if HUNTER_API_KEY is set; otherwise records the likely contact
path (e.g. a /contact page) without inventing an address. We never fabricate
emails — an empty contact_email means "find manually".
"""

from __future__ import annotations

import os

import httpx

from ..models import Prospect


def find_contact(p: Prospect) -> None:
    """Populate p.contact_email / notes in place. Never fabricates an address."""
    if p.contact_email:
        return

    key = os.environ.get("HUNTER_API_KEY")
    if not key:
        p.notes = (p.notes + " | contact: check site /contact or /about").strip(" |")
        return

    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": p.domain, "api_key": key, "limit": 1},
            )
            resp.raise_for_status()
            emails = resp.json().get("data", {}).get("emails", [])
            if emails:
                top = emails[0]
                p.contact_email = top.get("value", "")
                if top.get("first_name"):
                    p.contact_name = top.get("first_name", "")
    except httpx.HTTPError:
        p.notes = (p.notes + " | contact lookup failed; check manually").strip(" |")
