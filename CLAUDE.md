# Main Branch Premium

AI-native business operating system. Your context is the fuel, Claude is the engine.

---

## Philosophy: Active Context Management

**You learn your business by building your context.**

This is not passive memory like ChatGPT. There is no magic background system remembering things for you. Instead:

- **You actively manage** what Claude knows about your business
- **You see files change** as decisions get made
- **You synthesize research** into evergreen context
- **You discuss and refine** until the context is right
- **You control** exactly what informs every output

This active engagement is the learning. By forcing yourself to articulate your offer, your audience, your angles — you understand your business more deeply than you would if a chat just "remembered" things automatically.

**The insight:** Passive memory feels convenient but keeps you shallow. Active context management is work, but that work IS the thinking that makes your marketing effective.

---

## Philosophy: Compound Context

**Each piece of context you save makes the next output better.**

The cycle:
1. **Research** → Explore questions, gather information (dated)
2. **Decide** → Make choices with rationale (dated, links to research)
3. **Codify** → Update evergreen context (offer, audience, angles)
4. **Generate** → Skills consume context, produce outputs
5. **Learn** → Outputs inform new research

Your business knowledge compounds. The more you feed it, the better it performs. Unlike a chat that forgets or hallucinates context, your repo IS the truth.

---

## How It Works

**Engine + Data = Output**

```
main-branch-premium (ENGINE)          your-repo (DATA)
├── .claude/skills/                   ├── context/
├── .claude/lenses/                   │   ├── offer.md
└── .claude/context/compliance/       │   ├── audience.md
        │                             │   ├── proof/
        │                             │   └── angles/
        │                             ├── research/
        │                             ├── decisions/
        │                             ├── campaigns/
        └──────────────┬──────────────└── compliance/
                       │
               Skills read context/,
               output to campaigns/,
               enforce compliance/
```

**Same engine + different data = different outputs for each business.**

This is like a game engine (Unity, Unreal) — the engine provides capabilities, each game provides its own assets. Main Branch Premium is the engine. Your business repo is the game.

---

## Multi-Repo Workflow

1. Open your project/client repo as **primary working directory**
2. Add main-branch-premium as **additional working directory**
3. Skills and lenses from the engine become available
4. All outputs go to your project repo

```bash
# In Claude Code settings, add main-branch-premium as additional directory
# Then work in your business repo - skills are automatically available
```

---

## What Lives Where

| Content | Location | Why |
|---------|----------|-----|
| Skills (ad-static, ad-review) | Engine | Shared with all members |
| Lenses (FTC, Meta, Copy) | Engine | Shared with all members |
| Compliance frameworks | Engine | Shared with all members |
| Your offer, audience, angles | Your repo | Business-specific |
| Your research and decisions | Your repo | Business-specific |
| Your campaign outputs | Your repo | Business-specific |
| Your testimonials/proof | Your repo | Business-specific |
| Your typicality data | Your repo | Business-specific |

---

## Context Tiers

Skills load context progressively to stay token-efficient:

| Tier | What | When Loaded |
|------|------|-------------|
| **Always** | CLAUDE.md | Every session |
| **Just-in-time** | context/*.md | When generating |
| **On-demand** | research/, decisions/ | When reasoning about choices |
| **Deep reference** | compliance/typicality/ | When reviewing outcome claims |

---

## File Conventions

### Frontmatter

All markdown files should have frontmatter:

```yaml
---
type: research | decision | context | campaign
status: draft | active | complete | archived
date: 2026-01-13
linked_decisions: []  # For research files
---
```

### Naming

| Type | Format | Example |
|------|--------|---------|
| Evergreen context | `slug.md` | `offer.md`, `audience.md` |
| Research | `YYYY-MM-DD-slug.md` | `2026-01-13-competitor-analysis.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-13-angle-strategy.md` |
| Campaign batches | `YYYY-MM-DD-batch-name/` | `2026-01-13-january-launch/` |

### Rules

1. **Frontmatter on all markdown** — type, status, date minimum
2. **Research links to decisions** via `linked_decisions: []` in frontmatter
3. **Decisions reference research** via `## Research` section
4. **Max ~500 lines per file** — split if larger
5. **Edit existing > create new**
6. **Flat > deep** — max 2 levels of folder nesting

---

## Skills Available

| Skill | Domain | Description |
|-------|--------|-------------|
| `/ad-static` | Marketing | Generate static image ad copy from context |
| `/ad-video-scripts` | Marketing | Generate video ad scripts (15-60s) |
| `/ad-review` | Compliance | Multi-lens review (FTC, Meta, Copy, Visual, Voice, Substantiation) |
| `/skool-manager` | System Ops | Community engagement with Chrome |
| `/skool-vsl-scripts` | Marketing | VSL scripts (18-section structure) |

---

## Lenses Available

Review criteria for the `/ad-review` skill:

| Lens | What It Checks |
|------|----------------|
| `ftc-compliance` | FTC regulations, earnings claims, required disclosures |
| `meta-policy` | Platform triggers, Personal Attributes policy, ban risks |
| `copy-quality` | Schwartz awareness levels, Hormozi value equation, Suby frameworks |
| `visual-standards` | Safe zones, OCR triggers, prohibited visual elements |
| `voice-authenticity` | AI tells, brand voice consistency, authenticity markers |
| `substantiation` | Claims inventory, proof matching, typicality requirements |

---

## Compliance Frameworks

Pre-campaign planning resources in `.claude/context/compliance/`:

| File | Purpose |
|------|---------|
| `ftc-scrutiny-categories.md` | Which industries get extra FTC attention (Tier 1/2/3) |
| `angle-playbook.md` | 10 persuasion angles with compliance rules for each |
| `testimonial-decision-rubric.md` | When outcome testimonials are worth the risk |
| `typicality/README.md` | How to collect FTC-required outcome data |

---

## The Three Domains

| Domain | What Skills Handle |
|--------|-------------------|
| **Marketing** | Ads, content, emails, campaigns |
| **System Ops** | Community management, tools, automation |
| **Biz Ops** | Finance, compliance, bookkeeping |

Research weaves through all domains.

---

## Git Commit Convention

```
[type] Brief description

- Detail 1
- Detail 2

Context: Why this change was made
```

**Types:** `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`

---

## See Also

- `docs/system-architecture.md` — Full technical explanation of how the system works
- `templates/modules/business-repo-scaffold/` — Template for creating new business repos
