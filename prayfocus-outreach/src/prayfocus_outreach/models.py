"""Core data model for an outreach prospect."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from urllib.parse import urlparse

# Opportunity categories we pursue for a Christian prayer/focus app.
CATEGORIES = (
    "app_directory",
    "review_site",
    "blog",
    "podcast",
    "journalist",
    "partner",
    "resource_page",
)

OPPORTUNITY_TYPES = ("backlink", "press", "partnership")

# Pipeline status of a prospect.
STATUSES = ("new", "enriched", "scored", "personalized", "composed", "exported", "suppressed")


def _domain_of(url: str) -> str:
    netloc = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


@dataclass
class Prospect:
    """A single link / press opportunity moving through the pipeline."""

    name: str
    url: str
    category: str = "blog"
    opportunity_type: str = "backlink"
    source: str = "manual"

    # populated by enrich/
    domain: str = ""
    contact_name: str = ""
    contact_email: str = ""
    domain_authority: int = 0

    # populated by score/
    relevance_score: float = 0.0
    ease_score: float = 0.0
    total_score: float = 0.0

    # populated by personalize/ & compose/
    personalized_opener: str = ""
    recommended_angle: str = ""
    chosen_template: str = ""
    draft_subject: str = ""
    draft_body: str = ""

    status: str = "new"
    notes: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.domain:
            self.domain = _domain_of(self.url)
        if self.category not in CATEGORIES:
            raise ValueError(f"unknown category {self.category!r}; expected one of {CATEGORIES}")
        if self.opportunity_type not in OPPORTUNITY_TYPES:
            raise ValueError(f"unknown opportunity_type {self.opportunity_type!r}")

    def as_dict(self) -> dict:
        return asdict(self)
