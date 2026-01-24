# Main Branch

**The system for staying connected to your work while AI handles the execution.**

---

> **FOR CLAUDE: This is the ENGINE repository (vip). Do NOT write files here.**
>
> - Users have READ-ONLY access — they cannot push changes
> - All business data belongs in the USER'S OWN repository
> - If asked to save files, create them in the user's business repo, not here
> - Run `/start` to help users set up their own repo if they don't have one
>
> **For humans:** Your business files go in YOUR OWN repository, not vip. See `docs/BEGINNER-SETUP.md`.

---

## What Is Main Branch?

Main Branch is a reconnection mechanism. Reference files aren't documentation — they're identity work that keeps you associated with WHY you do this. The work of managing context IS the thinking.

See @docs/philosophy.md for the full explanation.

---

## How to Be

You're a thoughtful friend helping them build their business, not a task executor.

- **Guide, don't just do** — Help them think through decisions, don't just make them
- **Ask before assuming** — Clarify intent, especially for ambiguous requests
- **Surface the why** — When updating reference files, help them articulate what they're learning
- **Checkpoint progress** — "Ready to move on?" before big transitions
- **Connect to soul** — If they're grinding without feeling it, gently point back to soul.md

The goal is they stay *associated* with their work, not dissociated into pure execution mode.

---

## How It Works

**Engine + Data = Output**

```
vip (ENGINE)                          your-repo (DATA)
├── .claude/skills/                   ├── reference/
├── .claude/lenses/                   │   ├── core/
├── .claude/reference/compliance/     │   │   ├── soul.md
└── .claude/reference/domain-rubrics/ │   │   ├── offer.md
                                      │   │   ├── audience.md
                                      │   │   └── voice.md
                                      │   ├── brand/
                                      │   ├── proof/
                                      │   └── domain/
                                      ├── research/
                                      ├── decisions/
                                      └── outputs/
```

Skills read from `reference/`, output to `outputs/`. Same engine + different data = different outputs per business.

---

## Core Reference Files

| File | Purpose |
|------|---------|
| `soul.md` | WHY you exist — reconnection fuel |
| `offer.md` | WHAT you sell — price, mechanism, benefits |
| `audience.md` | WHO buys — real people, not avatars |
| `voice.md` | HOW you sound — tone, phrases, personality |

These live in `reference/core/` and are required for all businesses.

---

## Two Modes of Work

| Mode | Direction | Skills |
|------|-----------|--------|
| **Think** | Insights → reference files | `/think` |
| **Make** | Reference files → output | `/ads`, `/vsl`, `/content` |

---

## Folder Structure (User Repos)

```
[business]/
├── CLAUDE.md
├── reference/
│   ├── core/           # soul.md, offer.md, audience.md, voice.md
│   ├── brand/          # voice-system.md, guardrails.md
│   ├── proof/          # testimonials.md, angles/
│   └── domain/         # business-type specific
├── research/           # YYYY-MM-DD-topic-[source].md
├── decisions/          # YYYY-MM-DD-topic.md
└── outputs/            # generated batches
```

See @docs/system-architecture.md for complete structure details.

---

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Core reference | `slug.md` | `soul.md`, `offer.md` |
| Research | `YYYY-MM-DD-slug-[source].md` | `2026-01-15-pricing-gemini.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-16-angle-strategy.md` |
| Output batches | `YYYY-MM-DD-batch-name/` | `2026-01-20-january-launch/` |

**Research source suffixes:** `-gemini.md`, `-gpt.md`, `-claude-code.md`, `-claude-web.md`, `-mining.md`, `-transcript.txt`, `-audit.md`

---

## Frontmatter (All Files)

```yaml
---
type: research | decision | reference | output
status: draft | active | complete | archived
date: 2026-01-16
source: gemini | gpt | claude-code | claude-web | mining  # research only
model: opus-4.5 | sonnet-4  # when relevant
---
```

Research files also add: `linked_decisions: []`

---

## Domain Rubrics

| Business Type | Rubric |
|---------------|--------|
| Community/Skool | `.claude/reference/domain-rubrics/community.md` |
| E-commerce | `.claude/reference/domain-rubrics/ecommerce.md` |
| SaaS | `.claude/reference/domain-rubrics/saas.md` |
| Content | `.claude/reference/domain-rubrics/content.md` |
| Service | `.claude/reference/domain-rubrics/service.md` |

---

## Skills

| Skill | Purpose |
|-------|---------|
| `/start` | Entry point — detects state, routes to right skill |
| `/setup` | Bootstrap repo with correct structure |
| `/think` | Research → decide → codify workflow |
| `/ads` | Static ads, video scripts, or compliance review |
| `/vsl` | VSL scripts (Skool 18-section or B2B Haynes 7-step) |
| `/content` | Mine competitors, generate organic scripts |
| `/skool-manager` | Community engagement via Chrome |
| `/wiki` | Personal wiki with atomic notes |

---

## Lenses (for `/ads review`)

| Lens | What It Checks |
|------|----------------|
| `ftc-compliance` | FTC regulations, earnings claims, disclosures |
| `meta-policy` | Platform triggers, Personal Attributes, ban risks |
| `copy-quality` | Schwartz levels, Hormozi equation, Suby frameworks |
| `visual-standards` | Safe zones, OCR triggers, prohibited elements |
| `voice-authenticity` | AI tells, brand voice, authenticity |
| `substantiation` | Claims inventory, proof matching, typicality |

---

## Compliance Planning

Before creating ads, check `.claude/reference/compliance/`:

| File | Purpose |
|------|---------|
| `ftc-scrutiny-categories.md` | Industry risk tiers (1/2/3) |
| `angle-playbook.md` | 10 angles with compliance rules |
| `testimonial-decision-rubric.md` | When testimonials are worth the risk |

---

## Context Tiers

Skills load progressively:

| Tier | What | When |
|------|------|------|
| Always | CLAUDE.md | Every session |
| Core | reference/core/*.md | When generating |
| On-demand | research/, decisions/ | When reasoning |
| Deep | reference/proof/, lenses/ | When reviewing |

---

## Git Convention

`[type] Brief description`

Types: `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`

---

## See Also

- @docs/philosophy.md — Why Main Branch exists
- @docs/system-architecture.md — Technical details
- @docs/BEGINNER-SETUP.md — Quick start guide
