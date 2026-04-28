# Lander — Build Flow

The lander shape: 1 page, all-in-one. Hero + offer + proof + CTA + footer, all on `index.html`. Maximum focus, minimum nav.

**V1 status:** the per-offer lander generation system prompt is not yet written. For single-page-feel use cases in V1, use the **minisite** shape — the home page does the brand work and links straight to Stripe checkout. See [`minisite-build.md`](minisite-build.md).

When per-offer lander generation lands, this file gets the same shape as `minisite-build.md`:

- `setup (lander)` — atom chain (domain, dns, pages, custom-domain), single-file project repo, Cloudflare Pages git-connected
- `build --one-shot (lander)` — generation subagent invoked with `lander-generation-system.md` (also future) + offer/audience/reference URLs; produces `index.html` + `_headers` + `og.svg` + `favicon.svg` (no per-section subdirectories)
- Validation: footer presence, OG render, single-page Lighthouse score
- What's NOT (no nav, no multi-page structure, no `/start/thanks/` separate page — thanks state shown inline or via Stripe's default thanks page)

---

## Why not ship a lander generation system in V1

Three reasons:

1. **The minisite covers the use case.** A 4-page minisite where 3 of the pages are linked from the home hero gives the same psychological "single focused funnel" feel as a 1-page lander, without losing the room for proof + how-it-works + faq.
2. **Vagueness at single-page is harder.** Less surface area for variance — the system prompt risks producing visually identical output across runs unless we're disciplined. Minisite has more room to surprise.
3. **Conversion data lives at the minisite tier.** Devon's first V1 run is paid Google Ads → minisite → Stripe deposit. The lander shape becomes load-bearing only when there's a real reason to compress to one page (very specific offers, retargeting flows, etc.) — that signal hasn't surfaced yet.

When it does, this file gets the full shape and `/site` adds a `lander-generation-system.md` peer to `minisite-generation-system.md`.

---

## Graduating up

A successful lander often pulls traffic that wants more proof / more pages → graduate to **minisite**. See [`graduation.md`](graduation.md) for the path.
