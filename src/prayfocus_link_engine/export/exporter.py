"""Export composed drafts for human review.

Two formats:
- md  : a readable review sheet (one block per prospect) — best for editing
- csv : a flat file you can paste into a CRM / mail-merge tool yourself

This is the end of the pipeline. The tool never sends anything.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..models import Prospect

_CSV_COLS = (
    "total_score", "name", "url", "category", "opportunity_type",
    "contact_name", "contact_email", "chosen_template",
    "draft_subject", "draft_body", "recommended_angle", "notes",
)


def export_drafts(prospects: list[Prospect], out_path: str | Path, fmt: str = "md") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_CSV_COLS)
            writer.writeheader()
            for p in prospects:
                writer.writerow({c: getattr(p, c) for c in _CSV_COLS})
        return out_path

    # markdown review sheet
    lines = [
        "# PrayFocus Outreach — Draft Review Sheet",
        "",
        "> Review and edit before sending. **Nothing here has been sent.**",
        "",
        f"_{len(prospects)} prospects, ranked by score._",
        "",
    ]
    for i, p in enumerate(prospects, 1):
        contact = p.contact_email or "(find contact manually)"
        lines += [
            f"## {i}. {p.name}  ·  score {p.total_score}",
            f"- **URL:** {p.url}",
            f"- **Category / opportunity:** {p.category} / {p.opportunity_type}",
            f"- **Contact:** {contact}",
            f"- **Template:** {p.chosen_template}",
            f"- **Recommended angle:** {p.recommended_angle or '—'}",
            "",
            f"**Subject:** {p.draft_subject}",
            "",
            "```",
            p.draft_body,
            "```",
            "",
            "---",
            "",
        ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
