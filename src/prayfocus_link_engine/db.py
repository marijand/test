"""SQLite persistence for prospects and the suppression list.

Deliberately dependency-free (stdlib sqlite3) so the engine runs anywhere.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Prospect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    category TEXT NOT NULL,
    opportunity_type TEXT NOT NULL,
    source TEXT,
    contact_name TEXT,
    contact_email TEXT,
    domain_authority INTEGER DEFAULT 0,
    relevance_score REAL DEFAULT 0,
    ease_score REAL DEFAULT 0,
    total_score REAL DEFAULT 0,
    personalized_opener TEXT,
    recommended_angle TEXT,
    chosen_template TEXT,
    draft_subject TEXT,
    draft_body TEXT,
    status TEXT DEFAULT 'new',
    notes TEXT,
    discovered_at TEXT,
    UNIQUE(domain, opportunity_type)
);

CREATE TABLE IF NOT EXISTS suppression (
    domain TEXT PRIMARY KEY,
    reason TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

_FIELDS = (
    "name", "url", "domain", "category", "opportunity_type", "source",
    "contact_name", "contact_email", "domain_authority",
    "relevance_score", "ease_score", "total_score",
    "personalized_opener", "recommended_angle", "chosen_template",
    "draft_subject", "draft_body", "status", "notes", "discovered_at",
)


class Store:
    def __init__(self, path: str | Path = "data/outreach.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # ---- prospects ---------------------------------------------------------
    def upsert(self, p: Prospect) -> int:
        """Insert a prospect, or update it if (domain, opportunity_type) exists.

        Returns the row id. Suppressed domains are skipped (returns -1).
        """
        if self.is_suppressed(p.domain):
            return -1
        cols = ", ".join(_FIELDS)
        placeholders = ", ".join("?" for _ in _FIELDS)
        updates = ", ".join(f"{f}=excluded.{f}" for f in _FIELDS if f not in ("discovered_at",))
        sql = (
            f"INSERT INTO prospects ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(domain, opportunity_type) DO UPDATE SET {updates}"
        )
        values = [getattr(p, f) for f in _FIELDS]
        cur = self.conn.execute(sql, values)
        self.conn.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = self.conn.execute(
            "SELECT id FROM prospects WHERE domain=? AND opportunity_type=?",
            (p.domain, p.opportunity_type),
        ).fetchone()
        return row["id"]

    def save(self, p: Prospect) -> None:
        """Persist mutations on an already-stored prospect (must have id)."""
        if p.id is None:
            self.upsert(p)
            return
        assignments = ", ".join(f"{f}=?" for f in _FIELDS)
        self.conn.execute(
            f"UPDATE prospects SET {assignments} WHERE id=?",
            [getattr(p, f) for f in _FIELDS] + [p.id],
        )
        self.conn.commit()

    def _row_to_prospect(self, row: sqlite3.Row) -> Prospect:
        data = {k: row[k] for k in row.keys()}
        return Prospect(**data)

    def all(self, status: str | None = None, order_by_score: bool = False) -> list[Prospect]:
        sql = "SELECT * FROM prospects"
        params: list = []
        if status:
            sql += " WHERE status=?"
            params.append(status)
        sql += " ORDER BY total_score DESC" if order_by_score else " ORDER BY id"
        return [self._row_to_prospect(r) for r in self.conn.execute(sql, params)]

    def top(self, n: int = 25) -> list[Prospect]:
        rows = self.conn.execute(
            "SELECT * FROM prospects WHERE status!='suppressed' "
            "ORDER BY total_score DESC LIMIT ?",
            (n,),
        )
        return [self._row_to_prospect(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) AS c FROM prospects").fetchone()["c"]

    # ---- suppression -------------------------------------------------------
    def suppress(self, domain: str, reason: str = "") -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO suppression (domain, reason) VALUES (?, ?)",
            (domain.lower(), reason),
        )
        self.conn.execute(
            "UPDATE prospects SET status='suppressed' WHERE domain=?", (domain.lower(),)
        )
        self.conn.commit()

    def is_suppressed(self, domain: str) -> bool:
        return (
            self.conn.execute(
                "SELECT 1 FROM suppression WHERE domain=?", (domain.lower(),)
            ).fetchone()
            is not None
        )

    def close(self) -> None:
        self.conn.close()
