"""End-to-end smoke test of the pipeline (offline, no API keys)."""

import os
import tempfile

from prayfocus_outreach.db import Store
from prayfocus_outreach.models import Prospect
from prayfocus_outreach.enrich import enrich_domain_authority, find_contact
from prayfocus_outreach.score import score_prospect
from prayfocus_outreach.personalize import personalize_prospect
from prayfocus_outreach.compose import compose_draft
from prayfocus_outreach.export import export_drafts
from prayfocus_outreach.compliance import draft_is_compliant

APP_CFG = {
    "name": "PrayFocus",
    "url": "https://www.prayfocus.app",
    "one_liner": "A Christian prayer & focus app.",
    "sender_name": "Marijan",
    "physical_address": "PrayFocus, 1 Test St, Testville",
}


def _store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    return Store(tmp.name)


def test_upsert_dedupes_by_domain_and_type():
    store = _store()
    a = Prospect(name="Example", url="https://example.com/a", category="blog")
    b = Prospect(name="Example2", url="https://www.example.com/b", category="blog")
    store.upsert(a)
    store.upsert(b)
    assert store.count() == 1  # same domain + opportunity_type collapses


def test_suppression_blocks_upsert():
    store = _store()
    store.suppress("spammy.com", "low quality")
    rid = store.upsert(Prospect(name="Spam", url="https://spammy.com"))
    assert rid == -1
    assert store.count() == 0


def test_full_pipeline_offline(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    store = _store()
    store.upsert(Prospect(name="The Gospel Coalition", url="https://thegospelcoalition.org",
                          category="review_site", opportunity_type="backlink"))
    store.upsert(Prospect(name="Relevant", url="https://relevantmagazine.com",
                          category="journalist", opportunity_type="press"))

    for p in store.all():
        enrich_domain_authority(p)
        find_contact(p)
        score_prospect(p)
        personalize_prospect(p, fetch_page=False)
        compose_draft(p, APP_CFG)
        store.save(p)

    ranked = store.top(10)
    assert ranked[0].total_score >= ranked[-1].total_score  # sorted desc
    for p in ranked:
        assert p.draft_subject and p.draft_body
        assert draft_is_compliant(p.draft_subject, p.draft_body, APP_CFG) == []

    out = export_drafts(ranked, tempfile.mktemp(suffix=".md"))
    assert os.path.getsize(out) > 0
