"""Import prospects from a CSV file.

Expected columns (header row): name,url,category,opportunity_type,contact_name,
contact_email,notes. Only name + url are required; the rest fall back to defaults.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..db import Store
from ..models import Prospect


def import_csv(store: Store, path: str | Path) -> int:
    """Load a CSV of seed targets. Returns the number of rows imported."""
    path = Path(path)
    imported = 0
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("name") or "").strip()
            url = (row.get("url") or "").strip()
            if not name or not url:
                continue
            p = Prospect(
                name=name,
                url=url,
                category=(row.get("category") or "blog").strip() or "blog",
                opportunity_type=(row.get("opportunity_type") or "backlink").strip() or "backlink",
                contact_name=(row.get("contact_name") or "").strip(),
                contact_email=(row.get("contact_email") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                source="csv_import",
            )
            if store.upsert(p) != -1:
                imported += 1
    return imported
