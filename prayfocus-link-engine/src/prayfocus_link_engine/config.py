"""Load settings.yaml (with sane defaults) and .env."""

from __future__ import annotations

from pathlib import Path

import yaml
from dotenv import load_dotenv

_DEFAULTS = {
    "app": {
        "name": "PrayFocus",
        "url": "https://www.prayfocus.app",
        "one_liner": "A Christian prayer & focus app that helps you build a steady, "
        "distraction-free prayer habit.",
        "sender_name": "The PrayFocus team",
        "physical_address": "<your postal address>",
    },
    "database": {"path": "data/outreach.db"},
    "personalize": {"model": "claude-sonnet-4-6", "max_tokens": 600},
    "scoring": {"weight_relevance": 0.45, "weight_authority": 0.35, "weight_ease": 0.20},
    "relevance_priors": {},
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: str | Path = "config/settings.yaml") -> dict:
    load_dotenv()
    path = Path(path)
    if path.exists():
        user_cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return _deep_merge(_DEFAULTS, user_cfg)
    return dict(_DEFAULTS)
