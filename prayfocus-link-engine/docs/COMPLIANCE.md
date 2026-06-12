# Outreach Compliance Checklist

This tool does not send email, but the drafts it produces are meant to be sent
by a human. Keep every message on the right side of the rules.

## CAN-SPAM (US)
- [ ] **Truthful headers** — real "From", real domain, no deceptive subject lines.
- [ ] **Identify the message** — it's outreach, not a disguised ad.
- [ ] **Physical postal address** in every message (set `app.physical_address`).
- [ ] **Clear opt-out** — every draft footer includes a plain-language opt-out.
- [ ] **Honor opt-outs promptly** — add the domain to the suppression list
      (`Store.suppress(domain)`); suppressed domains are never re-imported.

## GDPR / ePrivacy (EU) & PECR (UK)
- [ ] **Lawful basis** — B2B outreach that is relevant to the recipient's
      professional role can rely on legitimate interest; document why.
- [ ] **Relevance** — only contact people for whom your app is genuinely relevant.
- [ ] **Easy opt-out** + honor data-deletion requests.
- [ ] **No consumer spam** — do not cold-email private individuals.

## CASL (Canada)
- [ ] Stricter than CAN-SPAM — prefer implied/express consent; include identity
      and opt-out. When unsure about a Canadian contact, skip it.

## FTC disclosure
- [ ] Any **partnership / affiliate / sponsored** arrangement must be disclosed
      by both parties (`rel="sponsored"` on paid links; clear written disclosure).

## SEO link hygiene
- [ ] Editorial links should be natural — never buy dofollow links.
- [ ] Mark paid/affiliate links `rel="sponsored"`, user-generated `rel="ugc"`.

## Deliverability hygiene (for whoever sends)
- [ ] SPF, DKIM, DMARC configured on the sending domain.
- [ ] Warm the domain; keep volume low and personalized.
- [ ] Verify addresses before sending; never send to role/catch-all guesses.

> When in doubt about a contact, leave `contact_email` blank and find the right
> person manually. The engine never fabricates addresses.
