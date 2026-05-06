---
type: reference
status: active
domain: multi-offer
date: 2026-02-04
---

# Multi-Offer Domain Rubric

Guide for structuring businesses with multiple offers under a single brand. When a brand sells more than one product or service but shares a unified identity, use this rubric instead of duplicating repos.

---

## When to Use Multi-Offer

**The shared soul test:** If your products share `soul.md` and `voice.md`, they belong in the same repo. One brand, one soul, one voice, multiple offers.

**Examples:**

| Scenario | Structure |
|----------|-----------|
| Coaching community + digital course | Multi-offer (same brand, same soul) |
| Free Skool group + paid Skool group | Multi-offer (same brand, different tiers) |
| Coaching practice + unrelated e-commerce store | Separate repos (different brands, different souls) |
| Agency + personal brand | Separate repos (different voices) |

**The question is NOT** "do you have multiple businesses?" **The question IS** "does this product share the same soul and voice as your other products?"

---

## Multi-Business Boundary

Separate brands = separate repos. Always.

If you run multiple businesses, each gets its own repo with its own `soul.md`, `voice.md`, `offer.md`, and `audience.md`. The Main Branch engine stays the same -- you just point it at a different data repo.

The relevant question during a session is: "Are any other business repos relevant right now?" NOT "Do you have multiple businesses?" Each session works with one business repo at a time. Cross-business work means switching repos, not merging them.

---

## Required Repo Structure

```
core/
├── soul.md                      # ALWAYS core, never per-offer
├── offer.md                     # Brand thesis (multi-offer) or full offer (single)
├── audience.md                  # Base audience (shared across offers)
├── voice.md                     # ALWAYS core, never per-offer
├── content-strategy.md          # Pillars, platforms, cadence (brand-level)
├── product-ladder.md            # How offers relate (multi-offer only)
├── offers/                      # (multi-offer only)
│   └── [name]/
│       ├── offer.md             # Offer-specific details (required)
│       └── audience.md          # Offer-specific audience override (optional)
├── brand/                       # Deep brand systems
├── proof/
│   ├── testimonials.md          # Brand-level testimonials
│   ├── typicality.md            # FTC outcome data
│   └── angles/                  # Messaging entry points
│       └── [angle-name].md
└── operations/                  # Business-type specific folders
```

### Offer Folder Contents

Each offer folder under `core/offers/` contains:

| File | Required | Purpose |
|------|----------|---------|
| `offer.md` | Yes | Offer-specific pricing, mechanism, benefits, transformation |
| `audience.md` | No | Audience override if this offer targets a different segment |

**Offer-specific testimonials** can be placed as
`core/offers/[name]/testimonials.md` if testimonials are strongly
offer-specific. Otherwise, brand-level `core/proof/testimonials.md` suffices.

---

## File Resolution Rules

Skills resolve context files using a cascading lookup. The active offer is determined by `.vip/local.yaml`.

### Always Core (Never Per-Offer)

| File | Resolution | Rationale |
|------|------------|-----------|
| `soul.md` | `core/soul.md` | Soul is brand identity -- if offers need different souls, they need different repos |
| `voice.md` | `core/voice.md` | Voice is brand personality -- consistent across all offers |
| `content-strategy.md` | `core/content-strategy.md` | Content strategy is brand-level distribution |
| `brand/*` | `core/brand/*` | Brand systems are always shared |

### Offer-Aware (Cascade with Fallback)

| File | Resolution | Fallback |
|------|------------|----------|
| `offer.md` | `core/offers/[active]/offer.md` | `core/offer.md` |
| `audience.md` | `core/offers/[active]/audience.md` | `core/audience.md` |

### Accumulate (Merge Brand + Offer)

| File | Resolution |
|------|------------|
| `testimonials.md` | `core/offers/[active]/testimonials.md` (if exists) + `core/proof/testimonials.md` |
| `angles/*.md` | `core/proof/angles/*.md` applies to all offers by default |

### Resolution Pseudocode

```
resolve_context(file_type):
  # Always core -- no offer override possible
  if file_type in [soul, voice]:
    return core/{file_type}.md

  # Always domain -- brand-level
  if file_type in [content-strategy]:
    return core/content-strategy.md

  # Offer-aware -- check active offer first
  current_offer = read .vip/local.yaml -> current_offer

  if current_offer AND exists core/offers/{current_offer}/{file_type}.md:
    return core/offers/{current_offer}/{file_type}.md

  # Fallback to core
  return core/{file_type}.md
```

---

## Session Offer Context (.vip/local.yaml)

```yaml
current_offer: community    # Active offer for this session
```

**Location:** `.vip/local.yaml` in the business repo root.

**Rules:**
- Git-ignored (session state, not shared between machines or collaborators)
- Written by `/mb-start` when user selects an offer
- Read by all skills that need offer context
- If file is missing or `current_offer` is null: single-offer mode (everything reads from `core/`)
- Skills should never fail because `.vip/local.yaml` is missing -- they fall back to single-offer behavior

**The .vip/ folder** is for local session state only. Never commit it. Add `.vip/` to `.gitignore` during `/mb-setup`.

---

## product-ladder.md

**Location:** `core/product-ladder.md`

**Purpose:** Documents how offers relate to each other -- the strategic relationship, not just a list.

**Required sections:**

```markdown
---
type: reference
status: active
---

# Product Ladder

## Offers

### [Offer Name]
- **Type:** Free / Low-ticket / Mid-ticket / High-ticket
- **Price:** $X
- **Purpose in ladder:** Lead gen / Conversion / Ascension / Retention
- **Feeds into:** [Next offer in ladder]
- **Feeds from:** [Previous offer in ladder]

## Flow
[Describe the journey: how someone enters, ascends, and where they land]

## Cross-Sell Opportunities
[Which offers complement each other]
```

---

## Scaling Guidelines

| Offer Count | Guidance |
|-------------|----------|
| **1** | Single-offer mode. No `core/offers/` folder needed. Everything in `core/`. |
| **2-3** | Multi-offer sweet spot. Clean separation, easy to manage. |
| **4-10** | Still works. `product-ladder.md` should group offers into tiers or families. Consider whether some offers are variants vs. truly separate products. |
| **10+** | Reconsider architecture. Either group into product families under `core/offers/` or split into separate repos if souls diverge. |

**Warning signs you need separate repos:**
- Offers need different voice.md files
- Offers serve fundamentally different audiences with no overlap
- You find yourself writing "for [offer X] only" in soul.md
- Content strategy makes no sense as a unified plan

---

## Migration Path: Single-Offer to Multi-Offer

This is an atomic operation performed by `/mb-setup` when a user adds their second offer.

### What Happens

1. Current `core/offer.md` becomes the brand thesis (high-level, covers all offers)
2. Current offer details move to `core/offers/[name]/offer.md`
3. `core/offers/` folder is created
4. `core/product-ladder.md` is created
5. `.vip/local.yaml` is created (and `.vip/` added to `.gitignore`)
6. `core/audience.md` stays in place (shared baseline)
7. If the new offer targets a different audience segment, `core/offers/[name]/audience.md` is created

### What Does NOT Change

- `core/soul.md` -- untouched
- `core/voice.md` -- untouched
- `core/brand/*` -- untouched
- `core/proof/*` -- untouched (testimonials stay brand-level unless explicitly split)
- `core/content-strategy.md` -- untouched
- All research, decisions, campaigns -- untouched

### Rollback

If a user removes all but one offer, the `core/offers/` folder can be deleted
and the remaining offer details merged back into `core/offer.md`. This is the
reverse atomic operation.

---

## What NEVER Goes Per-Offer

| File/Folder | Why |
|-------------|-----|
| `soul.md` | Soul is brand identity. Different souls = different repos. |
| `voice.md` | Voice is brand personality. One brand, one voice. |
| `content-strategy.md` | Distribution is brand-level. Offers are topics within pillars, not separate strategies. |
| `core/brand/*` | Brand systems (visual, guardrails) are unified. |

---

## Integration with Core Reference

| Core file | Multi-offer specific file |
|-----------|---------------------------|
| `core/soul.md` | -- (always core) |
| `core/voice.md` | -- (always core) |
| `core/offer.md` | `core/offers/[name]/offer.md` |
| `core/audience.md` | `core/offers/[name]/audience.md` |
| `core/proof/testimonials.md` | `core/offers/[name]/testimonials.md` (optional) |
| `core/content-strategy.md` | -- (always brand-level) |
| -- | `core/product-ladder.md` |

---

## Skills That Use This Domain

| Skill | How It Uses Multi-Offer |
|-------|-------------------------|
| `/mb-start` | Detects `core/offers/` folder, prompts for offer selection, writes `.vip/local.yaml` |
| `/mb-setup` | Creates `core/offers/` structure, handles single-to-multi migration |
| `/mb-think` | Reads active offer context; decisions may affect specific offers |
| `/mb-ads` | Generates ads for active offer using resolved offer.md + audience.md |
| `/mb-vsl` | Writes scripts for active offer |
| `/mb-organic` | Creates content using brand-level strategy + active offer details |
| `/mb-site` | Builds landing pages for active offer |
| `/mb-end` | Summarizes work across whichever offer was active |

---

*Rubric version: 1.0*
*Last updated: 2026-02-04*
