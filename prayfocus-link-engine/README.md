# PrayFocus Link Engine

A Python toolkit that automates **every step of a backlink + press outreach
campaign except the actual sending**. Built for [prayfocus.app](https://www.prayfocus.app),
a Christian prayer / focus app.

> ⚠️ **No emails are sent by this tool.** It researches and ranks opportunities,
> drafts personalized outreach, and exports review-ready drafts for a human to
> send manually. This is deliberate — it keeps you in control, protects your
> domain reputation, and keeps you on the right side of CAN-SPAM / GDPR.

## What it does (the pipeline)

```
  prospect  →  enrich  →  score  →  personalize  →  compose  →  export
  (collect)   (signals)  (rank)    (Claude)        (templates)  (CSV/MD)
                                                                  │
                                                            you review & send
```

| Step | Module | What it produces |
|------|--------|------------------|
| **Prospect** | `prospect/` | Link & press opportunities (CSV import, SERP/API, resource-page crawl) → SQLite |
| **Enrich** | `enrich/` | Domain-authority signal + best contact path, dedupe, suppression check |
| **Score** | `score/` | `relevance × authority × ease` ranking so you work the best 50, not 5,000 |
| **Personalize** | `personalize/` | Claude reads each prospect's page → a tailored first line + recommended angle |
| **Compose** | `compose/` | Merges personalization into a vetted template + compliant footer |
| **Export** | `export/` | Review-ready drafts as CSV / Markdown — nothing is sent |

## Strategy & assets

- `docs/PLAYBOOK.md` — link-building & press best-practices playbook
- `docs/TARGETS.md` — named Christian-niche target list (directories, blogs, podcasts, journalists, partners)
- `templates/` — outreach templates + follow-up sequences
- `docs/COMPLIANCE.md` — CAN-SPAM / GDPR / FTC checklist

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env          # add ANTHROPIC_API_KEY (+ optional enrichment keys)
cp config/settings.example.yaml config/settings.yaml

# 1. Load seed targets and run the full pipeline (no sending)
prayfocus-links import config/targets_seed.csv
prayfocus-links enrich
prayfocus-links score
prayfocus-links personalize        # uses Claude; skips gracefully without a key
prayfocus-links compose
prayfocus-links export --format md --out data/drafts.md

# inspect ranked opportunities
prayfocus-links list --top 25
```

Every step also runs offline with graceful fallbacks (no API keys required) so
you can try the workflow before wiring in paid services.

## Design principles

1. **Quality over volume.** A ranked shortlist beats a spray-and-pray blast.
2. **Human-in-the-loop.** Drafts are exported, never auto-sent.
3. **Pluggable.** Enrichment and search providers are thin adapters — swap in
   Hunter, Moz, Ahrefs, SerpAPI, etc. by setting an env var.
4. **Compliant by default.** Every draft carries a footer; a suppression list is enforced.

See `docs/` for the strategy behind the code.
