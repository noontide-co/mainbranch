# Main Branch Premium

AI-native business operating system. Your reference is the fuel, Claude is the engine.

---

> **FOR CLAUDE: This is the ENGINE repository (vip). Do NOT write files here.**
>
> - Users have READ-ONLY access — they cannot push changes
> - All business data belongs in the USER'S OWN repository
> - If asked to save files, create them in the user's business repo, not here
> - Run `/start` to help users set up their own repo if they don't have one
>
> **For humans:** If you're reading this, your business files should go in YOUR OWN separate repository, not in vip. See `docs/BEGINNER-SETUP.md` for help.

---

## Philosophy: Active Reference Management

**You learn by building your reference.** No magic passive memory. You:

- **Actively manage** what Claude knows
- **See files change** as decisions get made
- **Synthesize research** into evergreen reference
- **Control** exactly what informs every output

This engagement is the learning. Articulating your offer, audience, angles — you understand your business more deeply than passive memory allows.

**Passive memory keeps you shallow.** Active reference is work, but that work IS the thinking.

**Marketing reflects the present moment.** Markets shift. Reference stays current with reality. What worked last quarter might not land today.

---

## Philosophy: Compound Knowledge

**Each piece of reference makes the next output better.**

1. **Research** → Investigate (dated)
2. **Decide** → Choose with rationale (dated, links to research)
3. **Codify** → Update evergreen reference
4. **Generate** → Skills consume reference
5. **Learn** → Outputs inform new research

Your repo IS the truth. Unlike chat that forgets or hallucinates.

---

## How It Works

**Engine + Data = Output**

```
vip (ENGINE)          your-repo (DATA)
├── .claude/skills/                   ├── reference/
├── .claude/lenses/                   │   ├── core/
├── .claude/reference/compliance/       │   │   ├── offer.md
└── .claude/reference/domain-rubrics/   │   │   ├── audience.md
        │                             │   │   └── voice.md
        │                             │   ├── brand/
        │                             │   ├── proof/
        │                             │   └── domain/
        │                             ├── research/
        │                             ├── decisions/
        └──────────────┬──────────────└── outputs/
                       │
               Skills read reference/,
               output to outputs/
```

**Same engine + different data = different outputs per business.**

Like Unity/Unreal — engine provides capabilities, each game provides assets.

---

## Folder Structure

Every business repo follows this structure:

```
[business]/
├── CLAUDE.md              # Always loaded - business summary
│
├── reference/             # Evergreen truth (skills consume this)
│   ├── core/              # REQUIRED - same files every business
│   │   ├── offer.md       # What we sell
│   │   ├── audience.md    # Who buys
│   │   └── voice.md       # How we sound (quick reference)
│   │
│   ├── brand/             # Deep brand systems
│   │   ├── voice-system.md
│   │   ├── guardrails.md
│   │   └── [brand-specific].md
│   │
│   ├── proof/             # Evidence + proven messaging
│   │   ├── testimonials.md
│   │   ├── typicality.md  # FTC outcome data (if paid ads)
│   │   └── angles/        # Proven messaging angles
│   │
│   └── domain/            # Business-type specific
│       └── [see domain rubrics]
│
├── research/              # Dated investigations
│   └── YYYY-MM-DD-topic-[source].md
│
├── decisions/             # Dated choices with rationale
│   └── YYYY-MM-DD-topic.md
│
└── outputs/               # Generated deliverables
    └── [batch-name]/
```

---

## Domain Rubrics

Every business has a `reference/domain/` folder. Contents depend on business type.

| Business Type | Domain Contents | Rubric |
|---------------|-----------------|--------|
| **E-commerce** | `products/`, `materials/`, `sizing/` | `.claude/reference/domain-rubrics/ecommerce.md` |
| **Community** | `classroom/`, `funnel/`, `membership/` | `.claude/reference/domain-rubrics/community.md` |
| **SaaS** | `features/`, `pricing/`, `integrations/` | `.claude/reference/domain-rubrics/saas.md` |
| **Content** | `pillars/`, `editorial/` | `.claude/reference/domain-rubrics/content.md` |
| **Service** | `process/`, `deliverables/` | `.claude/reference/domain-rubrics/service.md` |

Use `/setup` skill to scaffold the correct structure for your business type.

---

## Research Naming Convention

All research files: `YYYY-MM-DD-topic-[source].md`

| Suffix | Source | Example |
|--------|--------|---------|
| `-gemini.md` | Gemini deep research | `2026-01-15-popup-strategy-gemini.md` |
| `-gpt.md` | ChatGPT/GPT-4 | `2026-01-15-brand-positioning-gpt.md` |
| `-claude-code.md` | Claude Code session | `2026-01-16-architecture-claude-code.md` |
| `-claude-web.md` | Claude.ai web | `2026-01-15-brainstorm-claude-web.md` |
| `-mining.md` | Internal data mining | `2026-01-15-email-voice-mining.md` |
| `-audit.md` | Site/system audit | `2026-01-15-live-site-audit.md` |
| (no suffix) | General/mixed | `2026-01-15-competitor-analysis.md` |

**Frontmatter includes source details:**
```yaml
---
type: research
date: 2026-01-16
source: claude-code
model: opus-4.5
status: draft
---
```

---

## Multi-Repo Workflow

1. Open your project/client repo as **primary working directory**
2. Add vip as **additional working directory**
3. Skills and lenses become available
4. All outputs go to your project repo

---

## What Lives Where

| Content | Location | Why |
|---------|----------|-----|
| Skills, lenses, rubrics | Engine | Shared with all members |
| Compliance frameworks | Engine | Shared with all members |
| Your offer, audience, voice | Your repo (`reference/core/`) | Business-specific |
| Your brand systems | Your repo (`reference/brand/`) | Business-specific |
| Your proof and angles | Your repo (`reference/proof/`) | Business-specific |
| Your domain-specific data | Your repo (`reference/domain/`) | Business-specific |
| Your research | Your repo (`research/`) | Business-specific |
| Your decisions | Your repo (`decisions/`) | Business-specific |
| Your generated outputs | Your repo (`outputs/`) | Business-specific |

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

## File Conventions

### Frontmatter

```yaml
---
type: research | decision | reference | output
status: draft | active | complete | archived
date: 2026-01-16
source: gemini | gpt | claude-code | claude-web | mining | audit  # For research
model: opus-4.5 | sonnet-3.5  # When relevant
linked_decisions: []  # For research files
---
```

### Naming

| Type | Format | Example |
|------|--------|---------|
| Core reference | `slug.md` | `offer.md`, `audience.md` |
| Research | `YYYY-MM-DD-slug-[source].md` | `2026-01-16-analysis-gemini.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-16-angle-strategy.md` |
| Output batches | `###_TYPE_name_date.md` | `001_IMG_get-funded_2026-01-16.md` |

### Rules

1. **Frontmatter on all markdown** — type, status, date minimum
2. **Research links to decisions** via `linked_decisions: []` in frontmatter
3. **Decisions reference research** via `## Research` section
4. **Max ~500 lines per file** — split if larger
5. **Edit existing > create new**
6. **Flat > deep** — max 2 levels of folder nesting

---

## The Flow

```
RESEARCH (investigate)
    ↓
DECISIONS (choose with rationale)
    ↓
REFERENCE (update evergreen truth)
    ↓
OUTPUTS (generate via skills)
    ↓
PLATFORM (publish)
    ↓
MINE PERFORMANCE → back to RESEARCH
```

---

## Skills Available

| Skill | Domain | Description |
|-------|--------|-------------|
| `/start` | Onboarding | Main entry point — detects user state, routes to right skill |
| `/setup` | Onboarding | Bootstrap repo with correct structure for your business type |
| `/think` | Knowledge | Research, decide, codify — includes adding context to reference |
| `/ads` | Marketing | Generate ads — routes to static, video, or review mode |
| `/vsl` | Marketing | VSL scripts — routes to Skool 18-section or B2B Haynes 7-step |
| `/content` | Marketing | Mine competitors, generate organic Reels/TikTok/carousel scripts |
| `/skool-manager` | System Ops | Community engagement with Chrome |

---

## Lenses Available

Review criteria for `/ads review` mode:

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

Pre-campaign planning resources in `.claude/reference/compliance/`:

| File | Purpose |
|------|---------|
| `ftc-scrutiny-categories.md` | Which industries get extra FTC attention (Tier 1/2/3) |
| `angle-playbook.md` | 10 persuasion angles with compliance rules for each |
| `testimonial-decision-rubric.md` | When outcome testimonials are worth the risk |
| `typicality/README.md` | How to collect FTC-required outcome data |

---

## Git Commit Convention

`[type] Brief description` — Types: `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`

---

## See Also

- `docs/system-architecture.md` — Technical details
- `.claude/reference/domain-rubrics/` — Business type templates
