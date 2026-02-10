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

Your repo is a precision instrument, not a dumping ground. The purpose is not to cram everything in — it's to filter context so LLMs produce great outcomes. Every file should earn its place.

Two pillars power every business: **ads that convert** (immediate ROI) and **content that runs itself** (long game). Both are driven by the same reference files -- your offer, audience, voice, and proof inform everything from a static ad to a newsletter-first content pipeline.

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

**Write reference in enduring language:**
- Core beliefs, offer thesis, audience truths — these read like they've always been true
- Never write reference that reacts to a specific event, tool, or session
- Event-specific context goes in evolution markers (soul.md) and decision files
- Test: would this line make sense to someone reading it in 6 months with no context?

**Connect to soul:**
- If they're grinding without feeling it, point back to soul.md
- If the think cycle feels like pushing, they might have the wrong offer
- The goal is they stay *associated*, not dissociated into execution mode

**Connect to content strategy:**
- If they have reference files but no content strategy, suggest building one through /think
- If they're creating content without a plan, route to /think to build content-strategy.md first

---

## When to Route

Take inventory. Notice what's missing. Proactively suggest skills they haven't invoked:

| If they're... | Route to |
|---------------|----------|
| Lost, confused, returning | `/start` |
| Brand new, need repo setup | `/setup` |
| Exploring, researching, deciding | `/think` |
| Building content pillars, planning platforms | `/think` |
| Ready to create paid ads | `/ads` |
| Need a sales video script | `/vsl` |
| Want organic content (reels, tiktok) | `/organic` |
| Want to write a newsletter | `/newsletter` (coming soon -- use `/think` for now) |
| Building a wiki or notes | `/wiki` |
| Need a landing page or website | `/site` |
| Asking questions, troubleshooting | `/help` |
| Wrapping up, done for today, closing out | `/end` |

**Quick triggers:** "research/decide" → `/think` · "ads/copy" → `/ads` · "organic/reels" → `/organic` · "newsletter/email" → `/newsletter` · "site/landing page/website" → `/site` · "content strategy/pillars" → `/think` · "help/stuck" → `/help` · "done/wrapping up/end my day" → `/end`

---

## How It Works

**Engine + Data = Output**

```
vip (ENGINE)                          your-repo (DATA)
├── .claude/skills/                   ├── .vip/
├── .claude/lenses/                   │   ├── config.yaml        # User preferences (git-tracked)
├── .claude/reference/compliance/     │   └── local.yaml         # Session state (git-ignored)
└── .claude/reference/domain-rubrics/ ├── reference/
                                      │   ├── core/
                                      │   │   ├── soul.md
                                      │   │   ├── offer.md
                                      │   │   ├── audience.md
                                      │   │   └── voice.md
                                      │   ├── offers/               # (multi-offer only)
                                      │   │   └── [name]/
                                      │   │       └── offer.md
                                      │   ├── brand/
                                      │   ├── proof/
                                      │   └── domain/
                                      │       ├── product-ladder.md  # (multi-offer only)
                                      │       └── content-strategy.md
                                      ├── research/
                                      ├── decisions/
                                      └── outputs/
```

Skills read from `reference/`, output to `outputs/`. Some skills (`/wiki`, `/site`) produce separate repos instead of writing to `outputs/`. Same engine + different data = different outputs per business.

---

## Multi-Offer vs Multi-Business

**Multi-offer** = multiple products under one brand, one repo. A coaching community and a digital course sold under the same brand share `soul.md` and `voice.md`, so they live together. Each offer gets its own `offers/[name]/offer.md` with offer-specific details.

**Multi-business** = separate brands with separate souls, separate repos. A coaching practice and an unrelated e-commerce store have different identities, different audiences, different voices. They need separate repos.

**The test:** If products share `soul.md` and `voice.md`, one repo. Otherwise separate repos.

Single-offer repos work exactly as before -- no `offers/` folder, everything in `core/`. Multi-offer is additive, not breaking. See `.claude/reference/domain-rubrics/multi-offer.md` for the complete rubric.

---

## Core Reference Files

| File | Purpose |
|------|---------|
| `soul.md` | WHY you exist — reconnection fuel |
| `offer.md` | WHAT you sell — brand-level thesis (see `offers/` for per-offer details in multi-offer setups) |
| `audience.md` | WHO buys — real people, not avatars |
| `voice.md` | HOW you sound — tone, phrases, personality |
| `content-strategy.md` | HOW you distribute — pillars, platforms, cadence, metrics (domain -- emerges through /think, not required at setup) |
| `product-ladder.md` | HOW offers relate — strategic relationship between products (domain -- multi-offer only) |
| `skool-surfaces.md` | WHAT cold traffic sees — live Skool about page + pricing card copy (domain/funnel -- congruence anchor for ads, organic, VSLs) |

First four live in `reference/core/` and are required for all businesses. `content-strategy.md` and `product-ladder.md` live in `reference/domain/`. `skool-surfaces.md` lives in `reference/domain/funnel/` (Skool communities only). All emerge over time.

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
| **Enriching the core** | Insights → reference files (including content-strategy.md — your distribution backbone) | `/think` |
| **Creating for the world** | Reference files → output | `/ads`, `/vsl`, `/organic`, `/site` |

---

## Folder Structure (User Repos)

```
[business]/
├── CLAUDE.md
├── .vip/
│   └── local.yaml      # Session state (git-ignored)
├── reference/
│   ├── core/           # soul.md, offer.md, audience.md, voice.md
│   ├── offers/         # (multi-offer only) [name]/offer.md, [name]/audience.md
│   ├── brand/          # voice-system.md, guardrails.md
│   ├── proof/          # testimonials.md, angles/
│   └── domain/         # business-type specific + product-ladder.md
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
| **Multi-Offer** | `offers/`, `product-ladder.md` | `.claude/reference/domain-rubrics/multi-offer.md` |

Use `/setup` to scaffold the correct structure for your business type.

---

## Reference Tiers

Skills load reference progressively to stay token-efficient:

| Tier | What | When Loaded |
|------|------|-------------|
| **Always** | CLAUDE.md | Every session |
| **Core** | reference/core/*.md | When generating |
| **On-demand** | research/, decisions/, content-strategy.md, skool-surfaces.md, offers/[active]/ | When reasoning about choices or generating content |
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
| `/ads` | Create and review ads with flexible entry points: static, video, video repurpose, creative variations, copy-only, images-only, account check, or compliance review |
| `/vsl` | VSL scripts (Skool 18-section or B2B Haynes 7-step) |
| `/organic` | Generate organic content from reference + research |
| `/wiki` | Personal wiki with atomic notes |
| `/site` | Generate and deploy landing pages from reference files |
| `/help` | Answer questions, troubleshoot, explain |
| `/newsletter` | Generate weekly newsletter from thinking work (coming soon) |
| `/end` | Close session intentionally — summary, crystallize, commit |
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
