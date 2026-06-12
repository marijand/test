"""Draft composition.

Picks a built-in template based on the prospect's category, fills merge fields
(including Claude's personalized opener), and appends a compliant footer.

Built-in templates are intentionally short; the richer, channel-specific
templates live in ../../templates/ for human use. These inline versions keep the
engine runnable end-to-end on its own.
"""

from __future__ import annotations

from ..models import Prospect
from ..compliance import footer

TEMPLATE_FOR_CATEGORY = {
    "app_directory": "directory",
    "review_site": "review",
    "resource_page": "resource_page",
    "blog": "guest_post",
    "podcast": "podcast",
    "journalist": "press",
    "partner": "partnership",
}

_SUBJECTS = {
    "directory": "Submitting {app} for your app list",
    "review": "A prayer & focus app you might cover: {app}",
    "resource_page": "A resource for your readers on {site}",
    "guest_post": "Guest post idea for {site}",
    "podcast": "Guest idea: building a steady prayer habit",
    "press": "Story idea: how people pray in a distracted age",
    "partnership": "A possible collaboration between {app} and {site}",
}

_BODIES = {
    "directory": (
        "{opener}\n\n"
        "I'd love to submit {app} — {one_liner} — to your directory. "
        "Here's the link: {app_url}. Happy to provide assets or a short description "
        "in whatever format works best.\n\nThank you for considering it."
    ),
    "review": (
        "{opener}\n\n"
        "I build {app} ({app_url}) — {one_liner} If it'd be a fit for your readers, "
        "I'd gladly set you up with free access and answer any questions.\n\n"
        "No pressure either way — thank you for the work you do."
    ),
    "resource_page": (
        "{opener}\n\n"
        "I noticed your resources page and wondered if {app} ({app_url}) might be a "
        "helpful addition for your readers — {one_liner}\n\n"
        "Totally understand if it's not a fit. Thanks for considering it."
    ),
    "guest_post": (
        "{opener}\n\n"
        "I'd love to contribute a practical, non-promotional guest post for {site} on "
        "building a distraction-free prayer habit. I run {app} ({app_url}) and care a "
        "lot about this topic.\n\nWould an outline be welcome?"
    ),
    "podcast": (
        "{opener}\n\n"
        "I'd love to come on your show to talk about staying focused in prayer in a "
        "distracted age — practical, listener-first, not a pitch. I'm the maker of "
        "{app} ({app_url}).\n\nWould that be a fit for an upcoming episode?"
    ),
    "press": (
        "{opener}\n\n"
        "I'm reaching out with a story idea about how people sustain a prayer practice "
        "amid constant digital distraction. I run {app} ({app_url}) and can share user "
        "stories or data.\n\nHappy to send a short briefing if useful."
    ),
    "partnership": (
        "{opener}\n\n"
        "I think there may be a natural fit between {site} and {app} ({app_url}) — "
        "{one_liner} Could we find 15 minutes to explore a simple collaboration?\n\n"
        "No worries at all if the timing isn't right."
    ),
}


def compose_draft(p: Prospect, app_cfg: dict) -> None:
    """Fill p.chosen_template, p.draft_subject, p.draft_body in place."""
    template = TEMPLATE_FOR_CATEGORY.get(p.category, "guest_post")
    fields = {
        "app": app_cfg.get("name", "PrayFocus"),
        "app_url": app_cfg.get("url", "https://www.prayfocus.app"),
        "one_liner": app_cfg.get("one_liner", ""),
        "site": p.name,
        "opener": p.personalized_opener or "Hi there,",
    }
    p.chosen_template = template
    p.draft_subject = _SUBJECTS[template].format(**fields)
    body = _BODIES[template].format(**fields)
    p.draft_body = body + "\n\n" + footer(app_cfg)
