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

If you run multiple businesses, each gets its own repo with its own `soul.md`, `voice.md`, `offer.md`, and `audience.md`. The engine (vip) stays the same -- you just point it at a different data repo.

The relevant question during a session is: "Are any other business repos relevant right now?" NOT "Do you have multiple businesses?" Each session works with one business repo at a time. Cross-business work means switching repos, not merging them.

---

## Required Domain Structure

```
reference/
├── core/                        # Brand-level (always present)
│   ├── soul.md                  # ALWAYS core, never per-offer
│   ├── offer.md                 # Brand thesis (multi-offer) or full offer (single)
│   ├── audience.md              # Base audience (shared across offers)
│   └── voice.md                 # ALWAYS core, never per-offer
├── offers/                      # (multi-offer only)
│   └── [name]/
│       ├── offer.md             # Offer-specific details (required)
│       └── audience.md          # Offer-specific audience override (optional)
├── brand/                       # Deep brand systems (always core)
├── proof/
│   ├── testimonials.md          # Brand-level testimonials
│   ├── typicality.md            # FTC outcome data
│   └── angles/                  # Messaging entry points
│       └── [angle-name].md
└── domain/
    ├── product-ladder.md        # How offers relate (multi-offer only)
    ├── content-strategy.md      # Pillars, platforms, cadence (brand-level)
    └── ...                      # Business-type specific folders
```

### Offer Folder Contents

Each offer folder under `offers/` contains:

| File | Required | Purpose |
|------|----------|---------|
| `offer.md` | Yes | Offer-specific pricing, mechanism, benefits, transformation |
| `audience.md` | No | Audience override if this offer targets a different segment |

**Offer-specific testimonials** can be placed as `offers/[name]/testimonials.md` if testimonials are strongly offer-specific. Otherwise, brand-level `proof/testimonials.md` suffices.

---

## File Resolution Rules

Skills resolve context files using a cascading lookup. The active offer is determined by `.vip/local.yaml`.

### Always Core (Never Per-Offer)

| File | Resolution | Rationale |
|------|------------|-----------|
| `soul.md` | `core/soul.md` | Soul is brand identity -- if offers need different souls, they need different repos |
| `voice.md` | `core/voice.md` | Voice is brand personality -- consistent across all offers |
| `content-strategy.md` | `domain/content-strategy.md` | Content strategy is brand-level distribution |
| `brand/*` | `brand/*` | Brand systems are always shared |

### Offer-Aware (Cascade with Fallback)

| File | Resolution | Fallback |
|------|------------|----------|
| `offer.md` | `offers/[active]/offer.md` | `core/offer.md` |
| `audience.md` | `offers/[active]/audience.md` | `core/audience.md` |

### Accumulate (Merge Brand + Offer)

| File | Resolution |
|------|------------|
| `testimonials.md` | `offers/[active]/testimonials.md` (if exists) + `proof/testimonials.md` |
| `angles/*.md` | All angles apply to all offers (brand-level) |

### Resolution Pseudocode

```
resolve_context(file_type):
  # Always core -- no offer override possible
  if file_type in [soul, voice]:
    return core/{file_type}.md

  # Always domain -- brand-level
  if file_type in [content-strategy]:
    return domain/content-strategy.md

  # Offer-aware -- check active offer first
  current_offer = read .vip/local.yaml -> current_offer

  if current_offer AND exists offers/{current_offer}/{file_type}.md:
    return offers/{current_offer}/{file_type}.md

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
- Written by `/start` when user selects an offer
- Read by all skills that need offer context
- If file is missing or `current_offer` is null: single-offer mode (everything reads from `core/`)
- Skills should never fail because `.vip/local.yaml` is missing -- they fall back to single-offer behavior

**The .vip/ folder** is for local session state only. Never commit it. Add `.vip/` to `.gitignore` during `/setup`.

---

## product-ladder.md

**Location:** `reference/domain/product-ladder.md`

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
| **1** | Single-offer mode. No `offers/` folder needed. Everything in `core/`. |
| **2-3** | Multi-offer sweet spot. Clean separation, easy to manage. |
| **4-10** | Still works. `product-ladder.md` should group offers into tiers or families. Consider whether some offers are variants vs. truly separate products. |
| **10+** | Reconsider architecture. Either group into product families (sub-folders under `offers/`) or split into separate repos if souls diverge. |

**Warning signs you need separate repos:**
- Offers need different voice.md files
- Offers serve fundamentally different audiences with no overlap
- You find yourself writing "for [offer X] only" in soul.md
- Content strategy makes no sense as a unified plan

---

## Migration Path: Single-Offer to Multi-Offer

This is an atomic operation performed by `/setup` when a user adds their second offer.

### What Happens

1. Current `core/offer.md` becomes the brand thesis (high-level, covers all offers)
2. Current offer details move to `offers/[name]/offer.md`
3. `offers/` folder is created
4. `domain/product-ladder.md` is created
5. `.vip/local.yaml` is created (and `.vip/` added to `.gitignore`)
6. `core/audience.md` stays in place (shared baseline)
7. If the new offer targets a different audience segment, `offers/[name]/audience.md` is created

### What Does NOT Change

- `core/soul.md` -- untouched
- `core/voice.md` -- untouched
- `brand/*` -- untouched
- `proof/*` -- untouched (testimonials stay brand-level unless explicitly split)
- `domain/content-strategy.md` -- untouched
- All research, decisions, outputs -- untouched

### Rollback

If a user removes all but one offer, the `offers/` folder can be deleted and the remaining offer details merged back into `core/offer.md`. This is the reverse atomic operation.

---

## What NEVER Goes Per-Offer

| File/Folder | Why |
|-------------|-----|
| `soul.md` | Soul is brand identity. Different souls = different repos. |
| `voice.md` | Voice is brand personality. One brand, one voice. |
| `content-strategy.md` | Distribution is brand-level. Offers are topics within pillars, not separate strategies. |
| `brand/*` | Brand systems (visual, guardrails) are unified. |

---

## Integration with Core Reference

| Universal (reference/) | Multi-Offer Specific |
|------------------------|----------------------|
| `core/soul.md` | -- (always core) |
| `core/voice.md` | -- (always core) |
| `core/offer.md` | `offers/[name]/offer.md` |
| `core/audience.md` | `offers/[name]/audience.md` |
| `proof/testimonials.md` | `offers/[name]/testimonials.md` (optional) |
| `domain/content-strategy.md` | -- (always brand-level) |
| -- | `domain/product-ladder.md` |

---

## Skills That Use This Domain

| Skill | How It Uses Multi-Offer |
|-------|-------------------------|
| `/start` | Detects `offers/` folder, prompts for offer selection, writes `.vip/local.yaml` |
| `/setup` | Creates `offers/` structure, handles single-to-multi migration |
| `/think` | Reads active offer context; decisions may affect specific offers |
| `/ads` | Generates ads for active offer using resolved offer.md + audience.md |
| `/vsl` | Writes scripts for active offer |
| `/organic` | Creates content using brand-level strategy + active offer details |
| `/site` | Builds landing pages for active offer |
| `/end` | Summarizes work across whichever offer was active |

---

*Rubric version: 1.0*
*Last updated: 2026-02-04*
