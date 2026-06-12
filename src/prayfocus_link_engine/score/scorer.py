"""Prospect scoring.

total = relevance*w_rel + authority_norm*w_auth + ease*w_ease   (all 0-1, *100)

- relevance: category prior, nudged up if a contact email is already known
- authority: domain_authority normalised to 0-1 (DA is 0-100)
- ease: easier-to-win opportunities (directories, resource pages) score higher
"""

from __future__ import annotations

from ..models import Prospect

# How winnable each opportunity type tends to be (0-1).
_EASE_BY_CATEGORY = {
    "app_directory": 0.95,
    "resource_page": 0.85,
    "review_site": 0.7,
    "blog": 0.55,
    "podcast": 0.5,
    "partner": 0.4,
    "journalist": 0.3,
}

_DEFAULT_PRIORS = {
    "app_directory": 0.7,
    "review_site": 0.75,
    "blog": 0.8,
    "podcast": 0.8,
    "journalist": 0.85,
    "partner": 0.9,
    "resource_page": 0.85,
}


def score_prospect(
    p: Prospect,
    weights: dict | None = None,
    relevance_priors: dict | None = None,
) -> None:
    """Compute relevance/ease/total in place (0-100 scale for total)."""
    w = weights or {"relevance": 0.45, "authority": 0.35, "ease": 0.20}
    priors = relevance_priors or _DEFAULT_PRIORS

    relevance = priors.get(p.category, 0.6)
    if p.contact_email:
        relevance = min(1.0, relevance + 0.05)
    ease = _EASE_BY_CATEGORY.get(p.category, 0.5)
    authority_norm = max(0.0, min(p.domain_authority / 100.0, 1.0))

    p.relevance_score = round(relevance, 3)
    p.ease_score = round(ease, 3)
    p.total_score = round(
        (relevance * w["relevance"] + authority_norm * w["authority"] + ease * w["ease"]) * 100,
        2,
    )
