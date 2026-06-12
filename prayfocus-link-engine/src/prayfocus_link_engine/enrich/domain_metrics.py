"""Domain-authority enrichment.

Uses Moz if credentials are present; otherwise falls back to a deterministic
heuristic so the pipeline still produces usable rankings offline. The heuristic
is intentionally simple (length/ TLD signals) and is clearly NOT a real metric —
swap in Moz/Ahrefs/Majestic for production.
"""

from __future__ import annotations

import os

from ..models import Prospect

_TRUSTED_TLDS = (".org", ".edu", ".gov")


def _heuristic_authority(domain: str) -> int:
    """Cheap stand-in DA in the 10-60 range when no provider is configured."""
    score = 35
    if any(domain.endswith(t) for t in _TRUSTED_TLDS):
        score += 15
    # shorter domains skew toward established brands
    core = domain.split(".")[0]
    if len(core) <= 8:
        score += 8
    score -= max(0, domain.count("-") * 4)  # hyphen-heavy = often lower quality
    return max(5, min(score, 60))


def enrich_domain_authority(p: Prospect) -> None:
    """Populate p.domain_authority in place."""
    if os.environ.get("MOZ_ACCESS_ID") and os.environ.get("MOZ_SECRET_KEY"):
        try:
            p.domain_authority = _moz_da(p.domain)
            return
        except Exception:  # pragma: no cover - network/provider issues
            pass
    p.domain_authority = _heuristic_authority(p.domain)


def _moz_da(domain: str) -> int:  # pragma: no cover - requires live credentials
    """Fetch Domain Authority from Moz Links API. Stubbed signature.

    Implement the Moz JWT-signed request here; raising on any failure lets
    enrich_domain_authority() fall back to the heuristic.
    """
    raise NotImplementedError("wire up Moz Links API call")
