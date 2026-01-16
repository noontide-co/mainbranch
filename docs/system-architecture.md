# System Architecture

Complete technical reference for how Main Branch Premium works as an AI-native business operating system.

---

## Core Concept: Engine + Data

Main Branch Premium operates on a fundamental separation:

```
ENGINE (main-branch-premium)     +     DATA (your business repo)     =     OUTPUT
├── Skills                             ├── Reference                       ├── Ads
├── Lenses                             ├── Research                        ├── Scripts
└── Frameworks                         ├── Decisions                       └── Outputs
                                       └── Compliance
```

**The engine is business-agnostic.** It doesn't know about any specific offer, audience, or proof. It expects to find that information in standardized locations within whatever business repo it's pointed at.

**The data is engine-agnostic.** Business repos don't contain skills or logic. They contain context that any compatible engine can consume.

This is analogous to:
- A game engine (Unity) + game assets = a game
- A CMS engine (WordPress) + content = a website
- Main Branch Premium + your reference = your marketing

---

## Why This Architecture

### Problem: Chat Memory is Passive

Traditional AI chat interfaces (ChatGPT, Claude.ai) offer "memory" features that passively accumulate context. This feels convenient but creates problems:

1. **Opacity** — You can't see what the AI "remembers"
2. **Hallucination risk** — AI may misremember or confuse contexts
3. **No synthesis** — Raw memories accumulate without being refined
4. **No learning** — You never have to articulate what matters

### Solution: Active Context Management

Main Branch Premium inverts this:

1. **Transparency** — Context lives in files you can read and edit
2. **Truth** — The repo IS the truth, not AI's interpretation of it
3. **Synthesis required** — You must refine research into decisions into context
4. **Learning built-in** — Articulating context IS understanding your business

**The insight:** The "work" of managing context is not overhead — it's the actual thinking that makes marketing effective.

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

## Action Items
- [x] Update offer.md with new pricing
- [ ] Create ads for new price point
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

---

## Folder Structure: Business Repos

```
your-business/
├── CLAUDE.md                    # Instructions + engine reference
│
├── reference/                   # EVERGREEN — What skills consume
│   ├── core/                    # REQUIRED — Fundamental context
│   │   ├── offer.md             # What you sell
│   │   ├── audience.md          # Who you sell to
│   │   └── voice.md             # How you sound
│   ├── brand/                   # Deep brand systems
│   ├── proof/
│   │   ├── testimonials.md      # Approved testimonials
│   │   ├── typicality.md        # FTC outcome data
│   │   └── angles/              # Messaging entry points
│   │       └── [angle-name].md
│   └── domain/                  # Business-type specific
│
├── research/                    # DATED — Point-in-time exploration
│   └── YYYY-MM-DD-slug.md
│
├── decisions/                   # DATED — Choices with rationale
│   └── YYYY-MM-DD-slug.md
│
└── outputs/                     # OUTPUT — Generated content
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
main-branch-premium/
├── CLAUDE.md                        # Philosophy + reference
├── docs/
│   └── system-architecture.md       # This file
│
├── .claude/
│   ├── skills/                      # Invokable capabilities
│   │   ├── ad-static/
│   │   │   └── SKILL.md
│   │   ├── ad-video-scripts/
│   │   │   └── SKILL.md
│   │   ├── ad-review/
│   │   │   └── SKILL.md
│   │   └── ...
│   │
│   ├── lenses/                      # Review criteria for ad-review
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
│           └── community.md
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
name: ad-static
description: Generate static image ad copy from business context. Use when creating Facebook/Instagram image ads.
---

# Ad Static

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
| Offer | `reference/core/offer.md` | Yes |
| Audience | `reference/core/audience.md` | Yes |
| Voice | `reference/core/voice.md` | Recommended |
| Angles | `reference/proof/angles/*.md` | At least one |
| Testimonials | `reference/proof/testimonials.md` | Recommended |
| Typicality | `reference/proof/typicality.md` | For outcome claims |

Skills should fail gracefully with clear errors if required context is missing.

---

## How Lenses Work

Lenses are review criteria used by the `/ad-review` skill. Each lens is a markdown file containing:

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

The `/ad-review` skill spawns parallel agents, one per lens:

```
┌─────────────────────────────────────────────────────────┐
│                    /ad-review                           │
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
| **On-demand** | research/, decisions/ | When reasoning | Medium |
| **Deep reference** | reference/proof/, lenses/ | When reviewing | High |

**Why this matters:** Token efficiency. Don't load everything upfront. Load what's needed when it's needed.

---

## Multi-Repo Workflow

### Setup

1. Clone main-branch-premium locally
2. Create or clone your business repo
3. In Claude Code, add main-branch-premium as additional working directory
4. Work in your business repo as primary directory

### In Practice

```
Claude Code Session:
├── Primary: ~/projects/my-business/
│   ├── reference/
│   ├── outputs/
│   └── ...
│
└── Additional: ~/main-branch-premium/
    ├── .claude/skills/
    ├── .claude/lenses/
    └── ...
```

When you invoke `/ad-static`:
1. Claude loads skill from main-branch-premium
2. Skill reads context from my-business/reference/
3. Output goes to my-business/outputs/
4. Review uses lenses from main-branch-premium

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
## Action Items
- [x] Update reference/core/offer.md with new pricing
- [x] Add new angle to reference/proof/angles/value-stack.md
```

This creates a traceable chain: Research → Decision → Context → Output

---

## Naming Conventions

| Content Type | Format | Example |
|--------------|--------|---------|
| Core context | `slug.md` | `offer.md`, `audience.md`, `voice.md` |
| Research | `YYYY-MM-DD-slug.md` | `2026-01-10-competitor-analysis.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-11-pricing-strategy.md` |
| Output batches | `YYYY-MM-DD-batch-name/` | `2026-01-15-january-launch/` |
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
type: research | decision | context | campaign
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
status: complete
---
```

### Decision Files

```yaml
---
type: decision
date: 2026-01-11
status: active | closed
urgency: low | normal | high | critical
---
```

### Context Files

```yaml
---
type: context
status: active
updated: 2026-01-13
---
```

---

## Access Tiers (Noontide Internal)

| Tier | Repo | Who | Contains |
|------|------|-----|----------|
| **Public** | main-branch | Everyone | Free Claude plugin |
| **Members** | main-branch-premium | Paying members | Engine (skills, lenses, frameworks) |
| **Team** | noontide-projects | Employees, contractors | Internal project work |
| **Owners** | noontide-ops | Founders | Legal, accounting, sensitive |

Client repos (BDC, autism-rewired) are separate — can be handed off independently.

---

## Summary

1. **Engine + Data separation** — Skills in engine, context in business repos
2. **Active context management** — You build and maintain the context, learning as you go
3. **Compound context cycle** — Research → Decide → Codify → Generate → Learn
4. **Flat structure** — Max 2 levels, semantic names, first-timer friendly
5. **File linking** — Research links to decisions, decisions link to context
6. **Progressive loading** — Context tiers for token efficiency
7. **Compliance layers** — Planning, review, and data layers
8. **Multi-repo workflow** — Engine as additional directory, business repo as primary
