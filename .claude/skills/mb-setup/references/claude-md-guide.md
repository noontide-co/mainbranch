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

This repo contains your **business data**. It's powered by **Main Branch** (the engine).

**Setup:**
1. Clone Main Branch: `git clone https://github.com/noontide-co/mainbranch.git`
2. Start Claude in THIS folder (your business repo) and run `/mb-start`
3. Main Branch is linked via `.claude/settings.local.json` (with bridge links as compatibility fallback)

**How it works:**
- Engine (Main Branch): Contains skills, lenses, frameworks. You pull updates but never edit.
- Data (this repo): Contains your business context. You own and edit this.
- Skills read from `core/`, `research/`, and `decisions/`, then write coordinated work to `pushes/`.

**If `/mb-start` isn't available:** Skills may need bridge links. Find the Main Branch path from `.claude/settings.local.json` (the `additionalDirectories` array), then read `[engine-path]/.claude/skills/mb-start/references/auto-heal.md` and follow the repair steps. After repair, tell the user to restart Claude.

---

## Folder Structure

```
[business-name]/
├── CLAUDE.md              # Always loaded - business brain
├── README.md              # Human-readable overview
│
├── core/                  # Evergreen business brain
│   ├── offer.md
│   ├── audience.md
│   ├── voice.md
│   ├── content-strategy.md
│   ├── brand/             # Deep brand systems
│   ├── proof/
│   │   ├── testimonials.md
│   │   └── angles/
│   └── operations/        # Business-type specific
│
├── research/              # Dated investigations
├── decisions/             # Dated choices with rationale
└── pushes/                # Coordinated work records and generated output
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

**Full profile:** `core/audience.md`

---

## Voice (Quick Reference)

**Tone:** [Primary tone]
**Cadence:** [How it flows]
**Key phrases:**
- "[Phrase 1]"
- "[Phrase 2]"

**Full system:** `core/voice.md`

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
| **Core** | core/*.md | When generating content |
| **On-demand** | research/, decisions/ | When reasoning about choices |
| **Deep reference** | core/brand/, core/proof/ | When writing copy |
| **Domain** | core/operations/ | When business-type matters |

---

## Workflow Preferences

**Task tracking:** [decisions/ | GitHub Issues | focus.md | External: ___]

This tells `/mb-start` how you prefer to track ongoing work.
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
- Complete product catalog (put in `core/operations/products/`)
- Deep voice system (put in `core/brand/voice-system.md`)
- Research content (put in `research/`)

---

## Progressive Disclosure

CLAUDE.md is **Tier 1** — always loaded, so keep it lean.

Pattern:
1. **Summary in CLAUDE.md** — Quick reference
2. **Pointer to full file** — "Full system: `core/voice.md`"
3. **Claude loads on-demand** — When actually needed

Example:
```markdown
## Voice (Quick Reference)

**Tone:** Calm, grounded, never preachy
**Key phrases:** "Wearable notes to self", "Stay awake. Stay happy."

**Full system:** `core/voice.md`
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
