# System Architecture

> **Status:** Legacy architecture reference. This file still contains
> pre-package-era paths such as `reference/core/` and `.vip/local.yaml`.
> For the current public repo shape, use `mb onboard`, `mb status`, and
> the tree in `README.md`. Treat this document as historical design context
> until it is rewritten around the shipped `core/`, `research/`,
> `decisions/`, `log/`, `campaigns/`, and `documents/` taxonomy.

Complete technical reference for how Main Branch works as an AI-native business operating system.

---

## Core Concept: Engine + Data

Main Branch operates on a fundamental separation:

```
ENGINE (mainbranch)     +     DATA (your business repo)     =     OUTPUT
├── Skills                             ├── Reference                       ├── Ads, Scripts, Content (outputs/)
├── Lenses                             │   (incl. content-strategy.md)     ├── Wiki (separate repo)
└── Frameworks                         ├── Research                        └── Site (separate repo)
                                       ├── Decisions
                                       └── Compliance
```

**The engine is business-agnostic.** It doesn't know about any specific offer, audience, or proof. It expects to find that information in standardized locations within whatever business repo it's pointed at.

**The data is engine-agnostic.** Business repos don't contain skills or logic. They contain context that any compatible engine can consume.

---

## Why This Architecture

See `docs/philosophy.md` for the deeper explanation. The short version:

**Passive memory keeps you shallow.** You can't see what AI "remembers," it hallucinates, nothing gets synthesized, you never articulate what matters.

**Active reference is work, but that work IS the thinking.** Files you can read, edit, version control. The repo is truth. Articulating context = understanding your business.

**Curation over collection.** The repo is a precision instrument. Every file earns its place by improving what LLMs can do for you. Research gets synthesized, decisions get distilled, and only the sharpest context survives into reference. Quantity of context hurts; quality compounds.

---

## The Compound Context Cycle

```
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    ▼                                                     │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│Research │───▶│ Decide  │───▶│ Codify  │───▶│Generate │─┘
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
  research/     decisions/     reference/      outputs/
```

### 1. Research (Dated)

Explore questions, gather information. Point-in-time snapshots.

```
research/
├── 2026-01-10-competitor-pricing-analysis.md
├── 2026-01-12-audience-pain-points.md
└── 2026-01-13-testimonial-themes.md
```

**Frontmatter:**
```yaml
---
type: research
date: 2026-01-10
source: gemini | claude | web | expert
topics: [pricing, competitors]
linked_decisions:
  - 2026-01-11-pricing-strategy
status: complete
---
```

### 2. Decide (Dated)

Make choices with rationale. Links to research that informed it.

```
decisions/
├── 2026-01-11-pricing-strategy.md
├── 2026-01-13-primary-angle.md
└── 2026-01-14-testimonial-selection.md
```

**Structure:**
```markdown
---
type: decision
date: 2026-01-11
status: active
---
# Pricing Strategy

## Situation
[What's happening, what prompted this decision]

## Research
### competitor-pricing-analysis
**Date:** 2026-01-10
**Source:** Gemini deep research
[Summary of findings]
See: `research/2026-01-10-competitor-pricing-analysis.md`

## Options

### Option A: Premium pricing (selected)
**Pros:** ...
**Cons:** ...

### Option B: Value pricing (rejected)
**Pros:** ...
**Cons:** ...

## Decision
[The actual choice with rationale]

## What Changes

Reference files affected:
- `reference/core/offer.md` — update pricing section
- New ads needed for updated price point
```

### 3. Codify (Evergreen)

Update permanent context based on decisions. These files are what skills consume.

```
reference/
├── core/
│   ├── offer.md           # What you sell, pricing, mechanism
│   ├── audience.md        # Who you sell to, psychographics
│   └── voice.md           # How you sound
├── brand/                 # Deep brand systems
├── proof/
│   ├── testimonials.md
│   └── angles/
│       ├── overwhelm-to-clarity.md
│       └── professional-credibility.md
└── domain/                # Business-type specific
```

**Evergreen files don't have dates in the filename.** They represent current truth, not point-in-time snapshots.

### 4. Generate (Output)

Skills consume context and produce outputs.

```
outputs/
├── 2026-01-15-january-launch/
│   ├── batch-001-static-ads.md
│   ├── batch-002-video-scripts.md
│   └── review-notes.md
└── 2026-01-20-retargeting/
```

### 5. Learn (Loop Back)

Outputs inform new research. What worked? What didn't? This becomes new research, which informs new decisions, which updates context.

In the Generate step, the **newsletter is the keystone piece** -- long-form thinking that gets adapted into platform-specific content by /organic and amplified by /ads. In the Learn step, performance data flows back into `content-strategy.md` -- updating the hooks library, metrics benchmarks, and pillar effectiveness.

---

## Folder Structure: Business Repos

```
your-business/
├── CLAUDE.md                    # Instructions + engine reference
├── .vip/                        # SESSION STATE — git-ignored
│   └── local.yaml               # Active offer, session config
│
├── reference/                   # EVERGREEN — What skills consume
│   ├── core/                    # REQUIRED — Fundamental context
│   │   ├── soul.md              # Why you exist
│   │   ├── offer.md             # What you sell (or brand thesis if multi-offer)
│   │   ├── audience.md          # Who you sell to
│   │   └── voice.md             # How you sound
│   ├── offers/                  # (MULTI-OFFER ONLY)
│   │   └── [name]/
│   │       ├── offer.md         # Offer-specific details
│   │       └── audience.md      # Offer-specific audience (optional)
│   ├── brand/                   # Deep brand systems
│   ├── proof/
│   │   ├── testimonials.md      # Approved testimonials
│   │   ├── typicality.md        # FTC outcome data
│   │   └── angles/              # Messaging entry points
│   │       └── [angle-name].md
│   └── domain/                  # Business-type specific
│       ├── product-ladder.md    # How offers relate (multi-offer only)
│       └── content-strategy.md  # Pillars, platforms, cadence, metrics
│
├── research/                    # DATED — Point-in-time exploration
│   └── YYYY-MM-DD-slug.md
│
├── decisions/                   # DATED — Choices with rationale
│   └── YYYY-MM-DD-slug.md
│
└── outputs/                     # All generated content — lifecycle via frontmatter status
    └── YYYY-MM-DD-batch-name/
```

### Design Principles

1. **Flat > Deep** — Max 2 levels of nesting. Agents navigate via grep, not directory walking.
2. **Semantic names** — Folder names describe content type, not arbitrary categories.
3. **Dated vs Evergreen** — Dated content uses `YYYY-MM-DD-` prefix. Evergreen doesn't.
4. **First-timer friendly** — Someone new sees: reference, research, decisions, outputs. Self-explanatory.

---

## Folder Structure: Engine Repo

```
mainbranch/
├── CLAUDE.md                        # Philosophy + reference
├── docs/
│   └── system-architecture.md       # This file
│
├── .claude/
│   ├── skills/                      # Invokable capabilities
│   │   ├── ads/
│   │   │   └── SKILL.md
│   │   ├── vsl/
│   │   │   └── SKILL.md
│   │   ├── think/
│   │   │   └── SKILL.md
│   │   ├── site/
│   │   │   └── SKILL.md
│   │   ├── end/
│   │   │   └── SKILL.md
│   │   └── ...
│   │
│   ├── lenses/                      # Review criteria for /ads review
│   │   ├── README.md
│   │   ├── ftc-compliance.md
│   │   ├── meta-policy.md
│   │   ├── copy-quality.md
│   │   ├── visual-standards.md
│   │   ├── voice-authenticity.md
│   │   └── substantiation.md
│   │
│   └── reference/
│       ├── compliance/              # Shared compliance frameworks
│       │   ├── README.md
│       │   ├── ftc-scrutiny-categories.md
│       │   ├── angle-playbook.md
│       │   ├── testimonial-decision-rubric.md
│       │   └── typicality/
│       │       └── README.md
│       └── domain-rubrics/          # Domain-specific folder structures
│           ├── ecommerce.md
│           ├── community.md
│           └── multi-offer.md
│
└── templates/
    └── modules/
        └── brand-style-template.md  # Visual style guide template
```

---

## How Skills Work

Skills are modular capabilities that Claude can invoke. They follow Claude Code's skill specification.

### Skill Structure

```
skills/
└── skill-name/
    ├── SKILL.md           # Required: frontmatter + instructions
    ├── references/        # Optional: detailed docs loaded on-demand
    └── scripts/           # Optional: executable code
```

### SKILL.md Format

```markdown
---
name: ads
description: Generate ad copy and review for compliance. Routes to static, video, or review mode.
---

# Ads

[Instructions for Claude when this skill is invoked]

## What This Skill Does
...

## Context Required
...

## Output Format
...
```

### Context Discovery

Skills expect business context in standardized locations:

| Context Type | Where to Look | Required |
|--------------|---------------|----------|
| Offer | `offers/[active]/offer.md` then `reference/core/offer.md` | Yes |
| Audience | `offers/[active]/audience.md` then `reference/core/audience.md` | Yes |
| Soul | `reference/core/soul.md` (always core) | Yes |
| Voice | `reference/core/voice.md` (always core) | Recommended |
| Angles | `reference/proof/angles/*.md` | At least one |
| Testimonials | `reference/proof/testimonials.md` (+ offer-specific if exists) | Recommended |
| Typicality | `reference/proof/typicality.md` | For outcome claims |
| Content Strategy | `reference/domain/content-strategy.md` (always brand-level) | Recommended for /organic, /newsletter |
| Product Ladder | `reference/domain/product-ladder.md` | Multi-offer only |
| Skool Surfaces | `reference/domain/funnel/skool-surfaces.md` | When generating ads, organic, VSLs, or site copy (congruence) |
| Session State | `.vip/local.yaml` | Multi-offer only |
| Site config | `~/.mainbranch/sites.json` | When building/publishing with /site |

Skills should fail gracefully with clear errors if required context is missing.

---

## How Lenses Work

Lenses are review criteria used by `/ads review` mode. Each lens is a markdown file containing:

1. What to check
2. How to score issues (P1/P2/P3)
3. Examples of violations
4. References to regulations or guidelines

### Lens Structure

```markdown
# FTC Compliance Lens

## What This Lens Checks
[Overview]

## Priority Levels
- **P1 (Blocking):** [Definition]
- **P2 (Should Fix):** [Definition]
- **P3 (Consider):** [Definition]

## Checklist

### Earnings/Income Claims
[Specific checks]

### Testimonials
[Specific checks]

...

## References
[Links to FTC guidance, case law, etc.]
```

### Multi-Lens Review

The `/ads review` mode spawns parallel agents, one per lens:

```
┌─────────────────────────────────────────────────────────┐
│                    /ads review                          │
│                        │                                │
│    ┌───────┬───────┬───────┬───────┬───────┬───────┐   │
│    ▼       ▼       ▼       ▼       ▼       ▼       │   │
│   FTC    Meta    Copy   Visual  Voice  Subst.     │   │
│    │       │       │       │       │       │       │   │
│    └───────┴───────┴───────┴───────┴───────┘       │   │
│                        │                            │   │
│                        ▼                            │   │
│              Synthesized Report                     │   │
│              (P1 → P2 → P3)                         │   │
└─────────────────────────────────────────────────────────┘
```

### Spawning Subagents: Permissions and Durability

**Critical:** When spawning subagents with the Task tool, they inherit limited permissions. If your agent needs to:

- Create folders or move files → **Needs Bash access**
- Write files outside working directories → **Needs explicit paths**
- Run git commands → **Needs Bash access**
- Use MCP tools (Apify, etc.) → **Must run in foreground** (background agents can't access MCP)

**Known bug — subagent writes may not persist:** Claude Code Task tool subagents sometimes report successful file writes via the Write tool, but the files don't appear on disk (GitHub [#4462](https://github.com/anthropics/claude-code/issues/4462), [#9458](https://github.com/anthropics/claude-code/issues/9458), [#13890](https://github.com/anthropics/claude-code/issues/13890)). This is intermittent — writes succeed most of the time, but fail silently when the bug triggers.

**Recommended pattern — write with fallback:**

1. Use `subagent_type: "general-purpose"` (has Write, Edit, Bash, MCP)
2. Agent writes the file
3. Agent verifies the write (Read or ls the file)
4. Agent returns: file path + write status + summary (always), full content (only if write failed)
5. Main conversation checks the file exists; if not, writes from returned content

**Read-only pattern (safest):** For agents that only analyze (like `/ads review` lenses or `/pr-review` checks), agents read + return findings. Main conversation acts on findings. Zero persistence risk.

**Avoid stuck loops:** If an agent keeps retrying the same denied permission, it will loop indefinitely. Instruct agents to report back if permissions are missing rather than retry.

**Do NOT run agents in background if they need MCP tools.** Background agents auto-deny permissions and cannot access MCP servers ([#13254](https://github.com/anthropics/claude-code/issues/13254)).

---

## Compliance Framework

### Three Layers

1. **Planning Layer** (`.claude/reference/compliance/`)
   - FTC scrutiny categories
   - Angle playbook with rules
   - Testimonial decision rubric
   - Used BEFORE creating ads

2. **Review Layer** (`.claude/lenses/`)
   - FTC compliance lens
   - Meta policy lens
   - Used AFTER creating ads

3. **Data Layer** (`compliance/typicality/` in business repos)
   - Actual outcome data for FTC defense
   - Required for outcome testimonials
   - Business-specific

### FTC Scrutiny Tiers

| Tier | Industries | Scrutiny Level |
|------|------------|----------------|
| **Tier 1** | Income/biz opp, weight loss, health cures, financial | Extreme — outcome claims need bulletproof typicality |
| **Tier 2** | Health-adjacent, education, coaching, credit | High — outcome claims need strong typicality |
| **Tier 3** | General consumer, lifestyle, productivity | Normal — standard advertising rules apply |

### Testimonial Decision

Before using outcome testimonials, ask:

1. Do we have typicality data showing what AVERAGE users achieve?
2. Is the industry Tier 1 or Tier 2?
3. Is the testimonial extraordinary or representative?
4. Can we defend this if FTC asks?

Often the answer is: **Use mechanism/community/price angles instead of outcome testimonials.**

---

## Context Tiers

Skills should load context progressively:

| Tier | What | When | Token Cost |
|------|------|------|------------|
| **Always** | CLAUDE.md | Every session | Low |
| **Just-in-time** | reference/core/*.md | When generating | Medium |
| **On-demand** | research/, decisions/, content-strategy.md, skool-surfaces.md | When reasoning or generating content | Medium |
| **Deep reference** | reference/proof/, lenses/ | When reviewing | High |

**Why this matters:** Token efficiency. Don't load everything upfront. Load what's needed when it's needed.

---

## Multi-Repo Workflow

### Setup

1. Clone Main Branch locally
2. Create or clone your business repo
3. Run `/setup` to configure Main Branch linkage (writes `.claude/settings.local.json` and compatibility links when needed)
4. Start Claude in your business repo and run `/start`

### In Practice

```
Claude Code Session:
├── Primary (CWD): ~/projects/my-business/
│   ├── .claude/settings.local.json  ← additionalDirectories points to mainbranch
│   ├── .claude/skills/*             ← bridge links for skill discovery fallback
│   ├── reference/
│   ├── outputs/
│   └── ...
│
└── Additional directory (read-only): ~/Documents/GitHub/mainbranch/
    ├── .claude/skills/              ← canonical skill source
    ├── .claude/lenses/
    └── ...
```

When you invoke `/ads`:
1. Claude loads skill from Main Branch
2. Skill reads context from my-business/reference/
3. Output goes to my-business/outputs/
4. Review uses lenses from Main Branch

Users with a wiki or site have additional repos accessed via config files (`~/.mainbranch/wiki.json`, `~/.mainbranch/sites.json`), not as working directories.

---

## Content Pipeline Architecture

The content pipeline follows a **newsletter-first waterfall**: one keystone piece becomes many platform-adapted outputs.

```
/think → research, decisions, content-strategy.md
    │
    ▼
/newsletter → keystone long-form (weekly email)
    │
    ▼
/organic → platform-adapted social (reels, tiktok, carousels)
    │
    ▼
/ads → paid amplification of top performers
    │
    ▼
/think → performance analysis, strategy updates → content-strategy.md
```

### Infrastructure Layer

Some skills produce infrastructure that sits outside the recurring content cycle — built once, updated when reference changes:

- `/site` — Conversion endpoint (landing pages where pipeline traffic lands)
- `/wiki` — Knowledge base (published notes)

These are destinations the pipeline drives traffic to, not recurring content items.

### Energy-Protected Audience Feedback Loop

The pipeline is designed so the creator **never opens a social app to post**. AI handles adaptation and distribution. The creator's energy stays in thinking and writing -- not scrolling. Audience feedback (metrics, comments, engagement) flows back through /think into content-strategy.md, closing the loop without requiring the creator to be on-platform.

### Output Lifecycle (Frontmatter-Based)

All generated content lives in `outputs/`. Lifecycle is tracked via the `status` field in YAML frontmatter, not folder moves:

- `status: draft` — Work in progress
- `status: scheduled` — Approved, ready to publish
- `status: published` — Live on platform
- `status: final` — Complete, no publishing lifecycle (VSL scripts, reviewed ad batches)

To find all drafts: `grep -rl "^status: draft" outputs/ --include="*.md"`
To find scheduled content: `grep -rl "^status: scheduled" outputs/ --include="*.md"`

This replaces the previous folder-move lifecycle pattern where files moved between subdirectories.

### Skill Connections to Content Pipeline

| Skill | Pipeline Role |
|-------|---------------|
| `/think` | Builds content-strategy.md, analyzes performance |
| `/newsletter` | Generates keystone long-form (coming soon) |
| `/organic` | Adapts keystone into platform-specific formats |
| `/ads` | Amplifies top-performing organic content |
| `/site` | Conversion endpoint — landing pages where pipeline traffic lands |
| `/end` | Session close — summarizes activity, surfaces crystallize moments, commits work |

---

## Multi-Offer Architecture

Some businesses sell multiple products or services under a single brand. Multi-offer architecture handles this without duplicating repos or breaking the single-offer workflow.

### The Shared Soul Test

If products share `soul.md` and `voice.md`, they belong in the same repo. Different souls or voices = different repos. This is the only test that matters.

### Multi-Business Boundary

Separate brands = separate repos. Always. The question during a session is: "Are any other business repos relevant right now?" NOT "Do you have multiple businesses?" Each session works with one business repo at a time.

### Folder Structure (Multi-Offer)

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
└── domain/
    ├── product-ladder.md        # How offers relate (multi-offer only)
    └── content-strategy.md      # Pillars, platforms, cadence (brand-level)
```

### Session Offer Context

The active offer is stored in `.vip/local.yaml` at the business repo root:

```yaml
current_offer: community    # Active offer for this session
```

- Git-ignored (session state, not shared)
- Written by `/start`, read by all skills
- If missing or null: single-offer mode (everything reads from `core/`)

### Canonical Path Resolution

Skills resolve context files using this algorithm:

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

### Resolution Flow Diagram

```
                    ┌──────────────┐
                    │ Skill needs  │
                    │ context file │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ soul.md or   │──── YES ──── core/{type}.md
                    │ voice.md?    │
                    └──────┬───────┘
                           │ NO
                    ┌──────▼───────┐
                    │ content-     │──── YES ──── domain/content-strategy.md
                    │ strategy?    │
                    └──────┬───────┘
                           │ NO
                    ┌──────▼───────┐
                    │ .vip/local   │──── NO ───── core/{type}.md (single-offer)
                    │ .yaml exists │
                    │ w/ offer?    │
                    └──────┬───────┘
                           │ YES
                    ┌──────▼───────┐
                    │ offers/      │
                    │ {offer}/     │──── YES ──── offers/{offer}/{type}.md
                    │ {type}.md    │
                    │ exists?      │
                    └──────┬───────┘
                           │ NO
                           │
                    core/{type}.md (fallback)
```

### Backward Compatibility

No `offers/` folder = single-offer mode. Everything works exactly as before. The resolution algorithm falls through to `core/` at every step when there is no active offer or no `offers/` folder. Existing single-offer repos require zero changes.

### What Never Goes Per-Offer

| File | Rationale |
|------|-----------|
| `soul.md` | Soul is brand identity -- different souls need different repos |
| `voice.md` | Voice is brand personality -- one brand, one voice |
| `content-strategy.md` | Distribution is brand-level, not per-product |
| `brand/*` | Brand systems are unified across all offers |

See `.claude/reference/domain-rubrics/multi-offer.md` for the complete rubric including scaling guidelines, migration path, and skill integration details.

---

## File Linking

### Research → Decision

Research files link to decisions they inform:

```yaml
# In research/2026-01-10-pricing-analysis.md
---
linked_decisions:
  - 2026-01-11-pricing-strategy
---
```

### Decision → Research

Decisions reference research inline:

```markdown
# In decisions/2026-01-11-pricing-strategy.md

## Research

### pricing-analysis
**Date:** 2026-01-10
**Source:** Gemini deep research
[Summary]
See: `research/2026-01-10-pricing-analysis.md`
```

### Decision → Context

Decisions note what context they updated:

```markdown
## What Changes

Reference files affected:
- `reference/core/offer.md` — updated pricing section
- `reference/proof/angles/value-stack.md` — new angle added
```

This creates a traceable chain: Research → Decision → Context → Output

### Decision → Content Strategy

Decisions about content pillars, platforms, or cadence update content-strategy.md:

```markdown
## What Changes

Reference files affected:
- `reference/domain/content-strategy.md` — add "transformation stories" pillar, update platform strategy with Instagram Reels cadence
```

Content strategy links back to the decisions that informed pillar choices, creating the same traceable chain.

---

## Naming Conventions

| Content Type | Format | Example |
|--------------|--------|---------|
| Core context | `slug.md` | `offer.md`, `audience.md`, `voice.md` |
| Content strategy | `slug.md` | `content-strategy.md` |
| Research | `YYYY-MM-DD-slug.md` | `2026-01-10-competitor-analysis.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-11-pricing-strategy.md` |
| Output batches | `YYYY-MM-DD-batch-name/` | `2026-01-15-january-launch/` |
| Output drafts | `YYYY-MM-DD-descriptive.md` | `2026-02-03-newsletter-issue.md` |
| Typicality data | `typicality.md` | `reference/proof/typicality.md` |

### Why Dates in Filenames

- Chronological sorting without metadata parsing
- Grep-friendly (`grep "2026-01" research/`)
- Git history shows evolution
- No ambiguity about "which version"

---

## Frontmatter Standards

### Minimum (All Files)

```yaml
---
type: research | decision | reference | output
status: draft | active | complete | archived
---
```

### Research Files

```yaml
---
type: research
date: 2026-01-10
source: gemini | claude | web | expert | internal
topics: [topic1, topic2]
linked_decisions:
  - decision-id
status: draft | complete | codified | superseded
---
```

### Decision Files

```yaml
---
type: decision
date: 2026-01-11
status: proposed | accepted | codified
urgency: low | normal | high | critical
---
```

### Reference Files

```yaml
---
type: reference
status: active
updated: 2026-01-13
---
```

---

## Summary

1. **Engine + Data separation** — Skills in engine, context in business repos
2. **Active context management** — You build and maintain the context, learning as you go
3. **Compound context cycle** — Research → Decide → Codify → Generate → Learn
4. **Flat structure** — Max 2 levels, semantic names, first-timer friendly
5. **File linking** — Research links to decisions, decisions link to context
6. **Progressive loading** — Context tiers for token efficiency
7. **Compliance layers** — Planning, review, and data layers
8. **Multi-repo workflow** — Engine linked via additional directory + bridge fallback, business repo as primary
9. **Content pipeline** — Newsletter-first waterfall: keystone → organic → ads → learn
10. **Multi-offer support** — Cascading path resolution for businesses with multiple products under one brand
