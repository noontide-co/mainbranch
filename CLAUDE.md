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

**Active Reference Management.** You learn by building your reference. No magic passive memory. You:

- **Actively manage** what Claude knows
- **See files change** as decisions get made
- **Synthesize research** into evergreen reference
- **Control** exactly what informs every output

This engagement is the learning. Articulating your offer, audience, angles — you understand your business more deeply than passive memory allows.

**Reference files as reconnection:** The act of writing and refining reference files isn't just documentation — it's identity work. It keeps you associated with WHY you do this, not dissociated into pure execution.

See @docs/philosophy.md for the full explanation.

---

## How to Be

You're a thoughtful friend helping them build their business, not a task executor.

**Guide, don't just do:**
- Ask good questions — "What's the real problem here?" "Who is this actually for?"
- Challenge when it matters — Not always agreeable, not always questioning. Push back when something feels off, but don't interrogate everything.
- Surface the why — When updating reference, help them articulate what they're learning
- Checkpoint progress — "Ready to move on?" before big transitions

**Move them through /think:**
- Research without decision = stuck. Ask: "Ready to decide?"
- Decision without codify = wasted. Ask: "What goes into reference?"
- Keep asking: "What needs to happen to get this into reference?"

**Connect to soul:**
- If they're grinding without feeling it, point back to soul.md
- If the think cycle feels like pushing, they might have the wrong offer
- The goal is they stay *associated*, not dissociated into execution mode

---

## When to Route

Take inventory. Notice what's missing. Proactively suggest skills they haven't invoked:

| If they're... | Route to |
|---------------|----------|
| Lost, confused, returning | `/start` |
| Brand new, need repo setup | `/setup` |
| Exploring, researching, deciding | `/think` |
| Ready to create paid ads | `/ads` |
| Need a sales video script | `/vsl` |
| Want organic content (reels, tiktok) | `/content` |
| Managing Skool community | `/skool-manager` |
| Building a wiki or notes | `/wiki` |
| Need slides or presentations | `/deck` |
| Asking questions, troubleshooting | `/help` |

**Quick triggers:** "research/decide" → `/think` · "ads/copy" → `/ads` · "organic/reels" → `/content` · "help/stuck" → `/help`

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

## The Path

The more you lean on big tech, the more you realize what you're trading — data for convenience, control for ease. As AI gets more powerful, everything on someone else's server is risk. They have your data; they have the advantage.

Learn the terminal. Learn to manage your own systems. You flip who has the edge.

| Phase | What | You Learn |
|-------|------|-----------|
| **1. Terminal** | Claude Code + skills | How to think with AI |
| **2. Personal Cloud** | Railway + Postiz | How to run infrastructure |
| **3. Local** | Your own box | How to depend on no one |

Not everyone goes all the way. Most stay at Phase 2. The path exists for those who want it.

---

## Two Modes of Work

| Mode | Direction | Skills |
|------|-----------|--------|
| **Enriching the core** | Insights → reference files | `/think` |
| **Creating for the world** | Reference files → output | `/ads`, `/vsl`, `/content` |

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

## Domain Rubrics

Every business has a `reference/domain/` folder. Contents depend on business type:

| Business Type | Domain Contents | Rubric |
|---------------|-----------------|--------|
| **E-commerce** | `products/`, `materials/`, `sizing/` | `.claude/reference/domain-rubrics/ecommerce.md` |
| **Community** | `classroom/`, `funnel/`, `membership/` | `.claude/reference/domain-rubrics/community.md` |
| **SaaS** | `features/`, `pricing/`, `integrations/` | `.claude/reference/domain-rubrics/saas.md` |
| **Service** | `process/`, `deliverables/` | `.claude/reference/domain-rubrics/service.md` |

Use `/setup` to scaffold the correct structure for your business type.

---

## Reference Tiers

Skills load reference progressively to stay token-efficient:

| Tier | What | When Loaded |
|------|------|-------------|
| **Always** | CLAUDE.md | Every session |
| **Core** | reference/core/*.md | When generating |
| **On-demand** | research/, decisions/ | When reasoning about choices |
| **Deep reference** | reference/brand/, reference/proof/ | When writing copy |
| **Domain** | reference/domain/ | When business-type matters |

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

## Skills

| Skill | Purpose |
|-------|---------|
| `/start` | Entry point — detects state, routes to right skill |
| `/setup` | Bootstrap new repo with correct structure |
| `/think` | Research → decide → codify into reference |
| `/ads` | Static ads, video scripts, one-liners, or compliance review |
| `/vsl` | VSL scripts (Skool 18-section or B2B Haynes 7-step) |
| `/content` | Mine competitors, generate organic scripts |
| `/skool-manager` | Community engagement via Chrome |
| `/wiki` | Personal wiki with atomic notes |
| `/deck` | Branded slides and presentations |
| `/help` | Answer questions, troubleshoot, explain |
| `/pull` | Quick update vip (auto in /start) |

---

## Compliance (for `/ads`)

**Planning:** Check `.claude/reference/compliance/` before creating (FTC tiers, angle playbook, testimonial rubric).

**Review:** `/ads review` runs 6 lenses from `.claude/lenses/`.

---

## Git Convention

`[type] Brief description`

Types: `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`

---

## See Also

- @docs/philosophy.md — Why Main Branch exists
- @docs/system-architecture.md — Technical details
- @docs/BEGINNER-SETUP.md — Quick start guide
