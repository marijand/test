"""Command-line interface — orchestrates the pipeline. Never sends anything.

Commands:
    prayfocus import <csv>      import seed targets
    prayfocus enrich            attach authority + contact signals
    prayfocus score             rank prospects
    prayfocus personalize       Claude-drafted opener + angle (per prospect)
    prayfocus compose           build subject + body + compliant footer
    prayfocus export            write review-ready drafts (md/csv)
    prayfocus list              show the top-ranked prospects
    prayfocus run <csv>         import → enrich → score → personalize → compose
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.table import Table

from .config import load_config
from .db import Store
from .prospect import import_csv
from .enrich import enrich_domain_authority, find_contact
from .score import score_prospect
from .personalize import personalize_prospect
from .compose import compose_draft
from .export import export_drafts

console = Console()


def _store(cfg: dict) -> Store:
    return Store(cfg["database"]["path"])


def cmd_import(args, cfg) -> None:
    store = _store(cfg)
    n = import_csv(store, args.csv)
    console.print(f"[green]Imported[/] {n} prospects (total in db: {store.count()}).")


def cmd_enrich(args, cfg) -> None:
    store = _store(cfg)
    rows = store.all()
    for p in rows:
        enrich_domain_authority(p)
        find_contact(p)
        p.status = "enriched"
        store.save(p)
    console.print(f"[green]Enriched[/] {len(rows)} prospects.")


def cmd_score(args, cfg) -> None:
    store = _store(cfg)
    weights = {
        "relevance": cfg["scoring"]["weight_relevance"],
        "authority": cfg["scoring"]["weight_authority"],
        "ease": cfg["scoring"]["weight_ease"],
    }
    priors = cfg.get("relevance_priors") or None
    rows = store.all()
    for p in rows:
        score_prospect(p, weights=weights, relevance_priors=priors)
        p.status = "scored"
        store.save(p)
    console.print(f"[green]Scored[/] {len(rows)} prospects.")


def cmd_personalize(args, cfg) -> None:
    store = _store(cfg)
    model = cfg["personalize"]["model"]
    max_tokens = cfg["personalize"]["max_tokens"]
    rows = store.all()
    with console.status(f"Personalizing with {model}…"):
        for p in rows:
            personalize_prospect(p, model=model, max_tokens=max_tokens, fetch_page=not args.no_fetch)
            p.status = "personalized"
            store.save(p)
    console.print(f"[green]Personalized[/] {len(rows)} prospects.")


def cmd_compose(args, cfg) -> None:
    store = _store(cfg)
    rows = store.all()
    for p in rows:
        compose_draft(p, cfg["app"])
        p.status = "composed"
        store.save(p)
    console.print(f"[green]Composed[/] {len(rows)} drafts (not sent).")


def cmd_export(args, cfg) -> None:
    store = _store(cfg)
    rows = store.top(args.top) if args.top else store.all(order_by_score=True)
    out = export_drafts(rows, args.out, fmt=args.format)
    console.print(f"[green]Exported[/] {len(rows)} drafts → {out} (review before sending).")


def cmd_list(args, cfg) -> None:
    store = _store(cfg)
    rows = store.top(args.top)
    table = Table(title=f"Top {len(rows)} outreach prospects")
    for col in ("#", "Score", "Name", "Category", "Type", "DA", "Contact"):
        table.add_column(col, overflow="fold")
    for i, p in enumerate(rows, 1):
        table.add_row(
            str(i), f"{p.total_score:.1f}", p.name[:40], p.category,
            p.opportunity_type, str(p.domain_authority), p.contact_email or "—",
        )
    console.print(table)


def cmd_run(args, cfg) -> None:
    cmd_import(args, cfg)
    cmd_enrich(args, cfg)
    cmd_score(args, cfg)
    cmd_personalize(args, cfg)
    cmd_compose(args, cfg)
    console.print("[bold green]Pipeline complete.[/] Run `prayfocus export` to get drafts.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="prayfocus", description=__doc__)
    p.add_argument("--config", default="config/settings.yaml")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("import"); s.add_argument("csv"); s.set_defaults(func=cmd_import)
    s = sub.add_parser("enrich"); s.set_defaults(func=cmd_enrich)
    s = sub.add_parser("score"); s.set_defaults(func=cmd_score)
    s = sub.add_parser("personalize"); s.add_argument("--no-fetch", action="store_true")
    s.set_defaults(func=cmd_personalize)
    s = sub.add_parser("compose"); s.set_defaults(func=cmd_compose)
    s = sub.add_parser("export")
    s.add_argument("--format", choices=["md", "csv"], default="md")
    s.add_argument("--out", default="data/drafts.md")
    s.add_argument("--top", type=int, default=0)
    s.set_defaults(func=cmd_export)
    s = sub.add_parser("list"); s.add_argument("--top", type=int, default=25)
    s.set_defaults(func=cmd_list)
    s = sub.add_parser("run"); s.add_argument("csv")
    s.add_argument("--no-fetch", action="store_true"); s.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    args.func(args, cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
