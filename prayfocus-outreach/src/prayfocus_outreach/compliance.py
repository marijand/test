"""Compliance helpers — keep every draft on the right side of the rules.

This tool does not send mail, but the drafts it produces are meant for sending,
so we bake compliance in:

- CAN-SPAM (US): truthful subject/from, a real physical postal address, and a
  clear opt-out mechanism in every message.
- GDPR / PECR (EU): a lawful basis (legitimate interest for relevant B2B
  outreach), easy opt-out, and no sending to suppressed contacts.
- FTC: disclose material connections in any partnership/affiliate arrangement.

See docs/COMPLIANCE.md for the full checklist.
"""

from __future__ import annotations


def footer(app_cfg: dict) -> str:
    """A CAN-SPAM/GDPR-friendly footer to append to every draft."""
    sender = app_cfg.get("sender_name", "The team")
    app = app_cfg.get("name", "PrayFocus")
    address = app_cfg.get("physical_address", "<your postal address>")
    return (
        f"Warmly,\n{sender} — {app}\n"
        f"{app_cfg.get('url', 'https://www.prayfocus.app')}\n\n"
        f"{address}\n"
        "If you'd rather not hear from me, just reply 'no thanks' and I won't follow up."
    )


def draft_is_compliant(subject: str, body: str, app_cfg: dict) -> list[str]:
    """Return a list of compliance problems (empty list == OK)."""
    problems: list[str] = []
    if not subject.strip():
        problems.append("missing subject line")
    if "no thanks" not in body.lower() and "unsubscribe" not in body.lower():
        problems.append("no clear opt-out mechanism")
    addr = app_cfg.get("physical_address", "")
    if not addr or addr.startswith("<"):
        problems.append("no real physical postal address configured")
    return problems
