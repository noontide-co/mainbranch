# CLAUDE.md Guide

How to draft an effective CLAUDE.md for a business repo.

---

## Purpose

Your entire repo is a precision instrument for LLM context quality. Every file should earn its place. CLAUDE.md is the lightest layer — summaries and pointers, not full content.

CLAUDE.md is the **always-loaded business brain**. Claude reads this file at the start of every session. It should contain:

- Enough context to work effectively
- Pointers to deeper reference files
- Current state and key decisions

**Not too much** — keep it scannable. Put deep details in reference files.

---

## Structure

```markdown
# [Business Name]

[One sentence: What this business is]

---

## Engine

This repo contains your **business data**. It's powered by **vip** (the engine).

**Setup:**
1. Clone vip: `git clone https://github.com/mainbranch-ai/vip.git`
2. Start Claude in the vip folder and run `/start`
3. Work in THIS repo as your primary data directory

**How it works:**
- Engine (vip): Contains skills, lenses, frameworks. You pull updates but never edit.
- Data (this repo): Contains your business context. You own and edit this.
- Skills read from your `reference/` and output to your `outputs/`

---

## Folder Structure

```
[business-name]/
├── CLAUDE.md              # Always loaded - business brain
├── README.md              # Human-readable overview
│
├── reference/             # Evergreen truth
│   ├── core/              # REQUIRED
│   │   ├── offer.md
│   │   ├── audience.md
│   │   └── voice.md
│   ├── brand/             # Deep brand systems
│   ├── proof/
│   │   ├── testimonials.md
│   │   └── angles/
│   └── domain/            # Business-type specific
│
├── research/              # Dated investigations
├── decisions/             # Dated choices with rationale
└── outputs/               # Generated content
```

---

## The Business ([Month Year])

**What it is:** [Brief description]

**Current state:**
- [Key metric 1]
- [Key metric 2]
- [Current situation/phase]

**Key assets:**
- [Asset 1]
- [Asset 2]

---

## The Customer

[2-3 sentences about who buys]

**Who they are:**
- [Characteristic 1]
- [Characteristic 2]

**Full profile:** `reference/core/audience.md`

---

## Voice (Quick Reference)

**Tone:** [Primary tone]
**Cadence:** [How it flows]
**Key phrases:**
- "[Phrase 1]"
- "[Phrase 2]"

**Full system:** `reference/core/voice.md`

---

## Key Decisions

| Decision | File |
|----------|------|
| [Decision 1] | `decisions/YYYY-MM-DD-topic.md` |
| [Decision 2] | `decisions/YYYY-MM-DD-topic.md` |

---

## Reference Tiers

| Tier | What | When Loaded |
|------|------|-------------|
| **Always** | This CLAUDE.md | Every session |
| **Core** | reference/core/*.md | When generating content |
| **On-demand** | research/, decisions/ | When reasoning about choices |
| **Deep reference** | reference/brand/, reference/proof/ | When writing copy |
| **Domain** | reference/domain/ | When business-type matters |

---

## Workflow Preferences

**Task tracking:** [decisions/ | GitHub Issues | focus.md | External: ___]

This tells `/start` how you prefer to track ongoing work.
```

---

## What to Include

### Must Have
- Business one-liner
- Engine reference
- Folder structure
- Current state summary
- Customer quick reference
- Voice quick reference
- Reference tiers

### Should Have (if exists)
- Key decisions index
- Workflow preferences (task tracking approach)
- Best sellers / top products
- Current strategy
- Known gaps
- Tools in use

### Avoid
- Full testimonials (put in `proof/testimonials.md`)
- Complete product catalog (put in `domain/products/`)
- Deep voice system (put in `brand/voice-system.md`)
- Research content (put in `research/`)

---

## Progressive Disclosure

CLAUDE.md is **Tier 1** — always loaded, so keep it lean.

Pattern:
1. **Summary in CLAUDE.md** — Quick reference
2. **Pointer to full file** — "Full system: `reference/core/voice.md`"
3. **Claude loads on-demand** — When actually needed

Example:
```markdown
## Voice (Quick Reference)

**Tone:** Calm, grounded, never preachy
**Key phrases:** "Wearable notes to self", "Stay awake. Stay happy."

**Full system:** `reference/core/voice.md`
```

---

## Length Guidelines

- **Ideal:** 100-300 lines
- **Maximum:** 500 lines
- **If longer:** Move content to reference files

CLAUDE.md shares context window with everything else. Keep it tight.

---

## Update Cadence

Update CLAUDE.md when:
- Business state changes significantly
- New major decisions are made
- Strategy shifts
- Key metrics update (quarterly)

Don't update for:
- Every small change
- New research (goes in `research/`)
- New testimonials (goes in `proof/`)
