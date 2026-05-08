---
name: mb-vsl
description: "Write high-converting Video Sales Letter scripts for any offer type. Routes to appropriate framework based on context. Use when: (1) Creating VSL scripts for Skool communities or membership offers (2) Writing sales videos for B2B high-ticket services ($3K-$50K+) (3) User says \"VSL\", \"video sales letter\", \"sales video script\", \"about page video\" (4) Need structured frameworks: 18-section for Skool/membership or 7-step Haynes for B2B. Produces camera-ready scripts optimized for spoken delivery. Never invents facts."
loops: [ship]
---

# VSL Script Writer

Routes to the right framework based on your offer type.

## Output destinations and operator vocabulary

VSL scripts that wrap a coordinated push (a launch, drop, challenge, etc.)
land under `pushes/<YYYY-MM-DD-slug>/` (canonical engine primitive). The
push record itself is `pushes/<YYYY-MM-DD-slug>/push.md` (`type: push`).
A one-off VSL that isn't part of a coordinated push can sit under the
relevant offer in `core/offers/<offer>/` instead.

If `core/vocabulary.md` defines display words (e.g. `terms.push.singular:
launch`), speak the operator's word in conversation while still writing
canonical files. If the repo still has legacy `campaigns/` records,
recommend `mb doctor` and `mb migrate campaigns --plan` before creating
new push work.

When creating `push.md`, include the validator-required frontmatter and fill
the values from repo truth or operator answers:

```yaml
---
type: push
slug: YYYY-MM-DD-slug
kind: launch
status: planned
health: unknown
goal: { metric: "", target: "", by: YYYY-MM-DD }
owner: ""
audience: ""
offer: core/offers/<offer>/offer.md
promise: ""
---
```

---

## Pull Latest Updates

For the canonical engine resolution + pull bash block (and the failure warning), see [`references/pull-engine-updates.md`](references/pull-engine-updates.md). Run it at the start of every invocation.

Then run `mb status --json --peek` from the business repo and use its
`readiness`, `drift.items`, and `ranked_actions` facts before asking for missing
setup or reference context. Do not duplicate repo-health checks in prose.

---

## Critical Rule: Never Invent Facts

Before writing ANY VSL, verify you have explicit confirmation for every claim.

- Do NOT invent statistics, numbers, or credentials
- Do NOT assume pricing, years in business, or client counts
- Do NOT fabricate testimonials or results
- If information is missing, ASK for it before proceeding

After gathering context, re-read every factual claim and verify against source material.

---

## Triage: Which Framework?

| Signal | Framework | Reference |
|--------|-----------|-----------|
| Skool community, membership, $47-$497/month | **Skool 18-Section** | `references/frameworks/skool-18-section.md` |
| B2B, agency, high-ticket ($3K-$50K+), affluent buyers | **B2B Haynes 7-Step** | `references/frameworks/b2b-haynes.md` |

**Keyword triggers:**
- "Skool", "community", "membership", "about page" → Skool framework
- "B2B", "agency", "high-ticket", "affluent", "service provider" → B2B framework

If unclear, ask: "Is this for a Skool/membership community ($47-$497/month) or a B2B high-ticket service ($3K+)?"

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. If a future `mb` JSON field exposes active offer state, use it.
2. Do not treat `.vip/local.yaml` as canonical active-offer state. If legacy
   state exists, confirm the offer with the user instead of silently routing.
3. If an offer is selected and `core/offers/[offer]/offer.md` exists, load it as the active offer.
4. If no offer is selected AND `core/offers/` exists: ask which offer.
5. If no `core/offers/` folder: use `core/offer.md` (single-offer mode)
6. Legacy fallback: if the repo does not have `core/`, read the old
   `reference/core/` and `reference/offers/` paths.

In current repos, `reference/core` and `reference/offers` are compatibility
bridges to `core/` and `core/offers/`. Treat them as aliases, not duplicate
files, and write once to the canonical `core/` path.

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

**Offer argument:** `/mb-vsl [framework] [offer]` — e.g., `/mb-vsl skool community`
If offer specified, it selects the offer for this run only. If the active offer type is known (community/membership offer), default to Skool framework; if B2B/high-ticket, default to B2B Haynes.

---

## Reference Required (Both Frameworks)

| File | Path | Purpose |
|------|------|---------|
| Offer | `core/offers/[active]/offer.md` or `core/offer.md` (resolved via path resolution) | What you sell, price, inclusions, guarantee |
| Audience | `core/offers/[active]/audience.md` or `core/audience.md` (resolved via path resolution) | Who buys, their pains, objections |
| Testimonials | `core/proof/testimonials.md` + `core/offers/[active]/testimonials.md` (accumulate) | Success stories with specifics |
| Skool Surfaces | `core/operations/funnel/skool-surfaces.md` | Live Skool about page + pricing copy (congruence) |

**If missing:** Ask user to provide or run `/mb-think` first.

**Skool VSL congruence:** When writing a Skool VSL, load `skool-surfaces.md` if it exists. The VSL script must not contradict or overpromise beyond what the about page and pricing cards state. Pricing, benefit claims, and positioning in the VSL should align with the live surfaces the viewer will see after clicking through.

---

## Framework Quick Summaries

### Skool 18-Section Framework

For community/membership offers. Full reference: `references/frameworks/skool-18-section.md`

**Flow:** Hook → Epiphany Bridge → Peek Plan → Features/Soft CTA → The Plan → Answer Questions → Stack Proof → Change Tone → Zoom Out → Price Anchor → Low Effort/High Reward → Recap Obstacles → Address Objections → Roadmap → Worst/Best Case → Hard CTA → Risk Reversal → Final CTA

**Key principles:**
- Hook creates pain recognition ("that's exactly how I feel")
- Epiphany bridge shows your journey from struggle to solution
- Social proof covers diverse backgrounds
- CTAs progress: soft → soft → hard
- Risk reversal makes joining feel safer than not joining

---

### B2B Haynes 7-Step Framework

For high-ticket B2B services. Full reference: `references/frameworks/b2b-haynes.md`

**Flow:** 60-90 Second Summary → Hook → Why (Legitimacy) → Market Drivers → Offer & Price → Objection Handling → Qualification → CTA

**Example:** See `references/examples/b2b-ijanitorial.md`

**Key principles:**
- Tweet version (first 90 seconds) covers entire pitch
- State price upfront (trains pixel on qualified buyers)
- For affluent: direct, conservative claims, no hype
- Clear qualification: who it IS and ISN'T for
- Vocabulary control (no "money", "guaranteed", "savings")

---

## Process

1. **Triage** — Determine framework from offer type
2. **Gather context** — Verify you have required reference files
3. **Get campaign name** — Ask: "What should we call this VSL? (e.g., 'skool-about', 'agency-pitch')"
4. **Load framework** — Read the appropriate reference file
5. **Write script** — Follow framework structure
6. **Verify facts** — Check every claim against source material
7. **Optimize for spoken delivery** — Contractions, short sentences, natural flow
8. **Save and commit prompt** — Save to output path, ask: "Saved to [path]. Want me to commit this to git?"

---

## Output Path

**Standard:** `pushes/YYYY-MM-DD-vsl-[offer]-{slug}/vsl-script.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode). On legacy repos that still have `campaigns/`, run `mb migrate campaigns --plan` first; do not write new VSLs under `campaigns/`.

Campaign name is REQUIRED. Ask user if not provided. Examples: `skool-about`, `agency-pitch`, `membership-sales`.

**Files:**
- `vsl-script.md` — The full VSL script
- `review-log.md` — Created if compliance reviewed

---

## Output Format

**Output frontmatter:**
```yaml
---
type: output
format: vsl
date: YYYY-MM-DD
status: final
platform: skool | website
---
```

Both frameworks produce scripts with:
- Header: Target audience, transformation, runtime estimate
- Sections with timestamps/chapter markers
- Delivery/production notes
- Quality checklist verification

---

## Recovery from Compaction

When conversations get long, Claude's memory compresses. This helps resume VSL sessions.

### For Users

Just say `/mb-vsl` again and describe where you were:
- "We were working on the Skool VSL, got through section 5"
- "Continue the B2B script for my agency"
- "Where was I on the sales video?"

### For Claude

1. **Restore offer context:** Use a future `mb` JSON active-offer field if present; otherwise ask the user to restore offer context. Do not silently route from `.vip/local.yaml`.

2. **Check for in-progress scripts:**

```bash
ls -ltd pushes/*-vsl-*/ 2>/dev/null | head -3
```

3. **Re-read key files:**

| File | What It Provides |
|------|------------------|
| This SKILL.md | Triage logic, critical rules |
| `references/frameworks/skool-18-section.md` | Full 18-section template |
| `references/frameworks/b2b-haynes.md` | Full 7-step B2B framework |
| Resolved `offer.md` | Offer details for script (offer-specific or core) |
| User's `core/proof/testimonials.md` | Proof for script |

3. **Confirm with user:**

> "I see you were working on [framework] VSL. You're at [section]. Continue from here?"

---

## When NOT to Use

- Static image ads (use `/mb-ads`)
- Short-form video scripts under 60 seconds (use `/mb-ads` video scripts)
- General copywriting or landing pages (use `/mb-site`)
- Content without sales intent

Use `/mb-vsl` when creating structured 5-20 minute sales video scripts.
