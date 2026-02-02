---
type: reference
status: active
domain: community
date: 2026-01-16
---

# Community/Skool Domain Rubric

Guide for structuring `reference/domain/` folder for community-based businesses (Skool, Circle, memberships).

---

## Required Domain Structure

```
reference/
└── domain/
    ├── content-strategy.md   # Pillars, platforms, cadence, metrics
    │
    ├── classroom/
    │   ├── modules.md        # Course modules and lessons
    │   └── resources.md      # Downloads, templates, tools
    │
    ├── funnel/
    │   ├── stages.md         # Awareness → Member journey
    │   ├── touchpoints.md    # Key conversion moments
    │   └── skool-surfaces.md # Live about page + pricing card copy
    │
    └── membership/
        ├── pricing.md        # Pricing model (whatever structure you use)
        └── benefits.md       # What members get
```

---

## File Specifications

### classroom/modules.md

**Purpose:** Complete curriculum structure for content planning and member communication.

**Required per module:**
- Module name
- Learning outcome (what they'll be able to do)
- Format (video, text, live call, etc.)
- Duration/length
- Prerequisites (if any)
- Key deliverables

**Example structure:**
```markdown
## Module 1: [Name]

- **Outcome:** Member can [specific skill/result]
- **Format:** 4 video lessons + workbook
- **Duration:** ~2 hours total
- **Prerequisites:** None
- **Deliverable:** Completed [worksheet/project/assessment]

### Lessons
1. Lesson title (15 min)
2. Lesson title (20 min)
3. Lesson title (25 min)
4. Lesson title (20 min)
```

---

### classroom/resources.md

**Purpose:** Catalog of all downloadable/bonus materials.

**Required:**
- Resource name
- Format (PDF, spreadsheet, template, etc.)
- Which module it supports
- Access level

---

### funnel/stages.md

**Purpose:** Document the member journey from discovery to retention.

**Typical stages:**
1. Awareness - How they find you
2. Interest - Free content that builds trust
3. Consideration - Objection handling, social proof
4. Conversion - Offer presentation
5. Onboarding - First 7 days experience
6. Engagement - Ongoing value delivery
7. Retention - Renewal/upgrade triggers

---

### funnel/touchpoints.md

**Purpose:** Specific conversion moments and their optimization.

**Document:**
- Landing pages (URLs, purpose)
- Email sequences (trigger, # emails, goal)
- Sales pages
- Checkout flow
- Onboarding sequence

---

### funnel/skool-surfaces.md

**Purpose:** Live copy from Skool about page and pricing cards. Content-generating skills (`/ads`, `/organic`, `/vsl`, `/site`) check this for congruence — ensuring all customer-facing surfaces speak the same language.

**Required sections:**
- About page copy (verbatim, with character count)
- Pricing card bullets (all tiers)
- Key claims extracted for congruence checks
- Congruence rules
- Update trigger (when to refresh this file)

**Update when:** About page copy changes, pricing tiers change, or new claims are added to any Skool surface.

---

### membership/pricing.md

**Purpose:** Document your pricing model, whatever structure you use.

**Common models:**

| Model | Structure |
|-------|-----------|
| **Fixed** | Single price, one tier |
| **Tiered** | Free/paid levels with different access |
| **Free trial** | Trial period → paid conversion |
| **Freemium** | Free forever + paid upgrades |
| **Annual/monthly** | Same tier, different billing |

**Document what applies to your community:**
- Price point(s)
- Billing frequency
- Trial period (if any)
- What's gated vs. open

---

### membership/benefits.md

**Purpose:** What members get (for sales pages, emails, objection handling).

**Structure by access level:**
```markdown
## [Access Level Name]

- Community access
- Classroom modules X, Y, Z
- Weekly live calls
- Resource library
- Direct messaging
```

---

### content-strategy.md

**Purpose:** Strategic backbone for all content creation. Defines pillars, platforms, cadence, and metrics. Consumed by `/organic`, `/ads`, and `/newsletter` (coming soon).

**Required sections:**
- Content Pillars (3-5 themes with sub-topics)
- Platform Strategy (priority-ordered platforms with format and cadence)
- Content Mix (ratios: educational / entertaining / community / promotional)
- Weekly Cadence (day-by-day template)
- Metrics (PRP benchmarks, review cadence)

**Optional sections (populate over time):**
- Repurposing Flow
- Content Genotype Defaults
- Framework Library
- Hooks Library

**How it gets built:** Through `/think` cycles, not upfront. `/setup` scaffolds an empty template. Users fill sections through research, experimentation, and iteration.

**How pillars are derived:**
Each pillar must pass three tests:
1. **Soul test** — Does this connect to why you exist?
2. **Offer test** — Does this lead toward your mechanism?
3. **Audience test** — Does your audience care?

Pillars emerge from the intersection of soul.md + offer.md + audience.md. If a pillar fails any test, it is either the wrong pillar or the wrong business.

---

## Optional Extensions

| Folder | Use Case |
|--------|----------|
| `events/` | Live events, workshops, challenges |
| `gamification/` | Points, levels, badges system |
| `affiliates/` | Partner/affiliate program details |

---

## Integration with Core Reference

| Universal (reference/) | Community Specific (reference/domain/) |
|------------------------|---------------------------------------|
| `core/offer.md` | `membership/pricing.md` |
| `core/audience.md` | `funnel/stages.md` |
| `core/voice.md` | — |
| `proof/testimonials.md` | — |
| — | `content-strategy.md` |

**The relationship:** `core/offer.md` summarizes the transformation. `domain/classroom/` is the delivery. `domain/membership/` is the access structure. `domain/content-strategy.md` is the distribution backbone — it connects ALL core files (soul for pillar derivation, offer for promotional content, audience for topic relevance, voice for content tone).

---

## Skool-Specific Notes

Skool uses "Classroom" with Modules → Lessons hierarchy.

- Map `classroom/modules.md` to Skool's structure
- Note dripped vs. immediate access content
- Track level unlock requirements
- Document gamification (points per action, level thresholds)

---

## Skool Analytics Reference

When mining performance data, Skool's dashboard (Settings → Dashboard) provides:

### Core Metrics (header row)

| Metric | What It Measures |
|--------|------------------|
| **Members** | Total active paying members |
| **MRR** | Monthly recurring revenue |
| **Conversion** | About page visitor → member (30-day) |
| **Retention** | MRR retained month-over-month |

### Dashboard Tabs

| Tab | What It Shows |
|-----|---------------|
| **Members** | Monthly breakdown: New, Existing, Churn |
| **MRR** | Monthly breakdown: New, Upgrades, Existing, Downgrades, Churn |
| **Unit Economics** | ARPU (average revenue per user), LTV (lifetime value) |
| **Cashflow** | One-time payments, subscriptions, affiliates, refunds |
| **About Page** | Daily visitors and conversion rate |
| **Free Trials** | Trial starts, conversions, churn |
| **Cohorts** | Retention heatmap by signup month |

### Mining Suggestions

When running `/think` to analyze Skool performance:
- Screenshot the Dashboard header (Members, MRR, Conversion, Retention)
- Screenshot the Members tab (shows churn trends)
- Screenshot the Cohorts tab (shows retention by signup month)
- Compare to previous mining research files for trends

---

## Skills That Use This Domain

| Skill | What It Reads |
|-------|---------------|
| `/think` | Writes to `content-strategy.md` during codify phase |
| `/organic` | `content-strategy.md` for pillar alignment, platform format |
| `/ads` | `content-strategy.md` for topic selection, funnel mapping |
| `/newsletter` | `content-strategy.md` for pillar topics, repurposing flow (coming soon) |
| `/vsl skool` | `funnel/stages.md`, `membership/benefits.md` |
| `/ads` (congruence) | `funnel/skool-surfaces.md` for ad-to-landing alignment |
| `/organic` (congruence) | `funnel/skool-surfaces.md` for content-to-landing alignment |
| `/site` (congruence) | `funnel/skool-surfaces.md` for site-to-Skool alignment |

---

*Rubric version: 1.2*
*Last updated: 2026-01-29*
