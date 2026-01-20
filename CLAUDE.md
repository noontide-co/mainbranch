# Main Branch Premium

AI-native business OS. Reference = fuel, Claude = engine.

---

> **ENGINE REPO (vip). Do NOT write files here.**
> - Users have READ-ONLY access
> - Business data → user's OWN repo(s)
> - `/start` → set up user repo

---

## Architecture

```
vip (ENGINE)                    your-repo (DATA)
├── .claude/skills/             ├── reference/
├── .claude/lenses/             │   ├── core/ (offer, audience, voice)
├── .claude/reference/          │   ├── brand/, proof/, domain/
│   ├── compliance/             ├── research/
│   └── domain-rubrics/         ├── decisions/
                                └── outputs/
```

Same engine + different data = different outputs per business.

---

## Business Repo Structure

```
[business]/
├── CLAUDE.md              # Always loaded
├── reference/
│   ├── core/              # REQUIRED
│   │   ├── offer.md
│   │   ├── audience.md
│   │   └── voice.md
│   ├── brand/             # voice-system.md, guardrails.md
│   ├── proof/             # testimonials.md, typicality.md, angles/
│   └── domain/            # Business-type specific
├── research/              # YYYY-MM-DD-topic-[source].md
├── decisions/             # YYYY-MM-DD-topic.md
└── outputs/               # Generated deliverables
```

---

## Domain Rubrics

| Type | Domain Contents | Rubric |
|------|-----------------|--------|
| E-commerce | products/, materials/, sizing/ | domain-rubrics/ecommerce.md |
| Community | classroom/, funnel/, membership/ | domain-rubrics/community.md |
| SaaS | features/, pricing/, integrations/ | domain-rubrics/saas.md |
| Content | pillars/, editorial/ | domain-rubrics/content.md |
| Service | process/, deliverables/ | domain-rubrics/service.md |

`/setup` scaffolds correct structure.

---

## Research Naming

Format: `YYYY-MM-DD-topic-[source].md`

| Suffix | Source |
|--------|--------|
| `-gemini.md` | Gemini deep research |
| `-gpt.md` | ChatGPT/GPT-4 |
| `-claude-code.md` | Claude Code session |
| `-claude-web.md` | Claude.ai web |
| `-mining.md` | Internal data mining |
| `-audit.md` | Site/system audit |
| (none) | General/mixed |

---

## Reference Loading

| Tier | Files | When |
|------|-------|------|
| Always | CLAUDE.md | Every session |
| Core | reference/core/*.md | Generating |
| On-demand | research/, decisions/ | Reasoning |
| Deep | brand/, proof/ | Writing copy |
| Domain | reference/domain/ | Business-type matters |

---

## File Rules

**Frontmatter (all .md):**
```yaml
type: research | decision | reference | output
status: draft | active | complete | archived
date: 2026-01-16
source: gemini | gpt | claude-code | claude-web | mining | audit
```

**Naming:**
| Type | Format |
|------|--------|
| Core reference | `slug.md` |
| Research | `YYYY-MM-DD-slug-[source].md` |
| Decisions | `YYYY-MM-DD-slug.md` |
| Outputs | `###_TYPE_name_date.md` |

**Rules:**
- Frontmatter required (type, status, date minimum)
- Research → `linked_decisions: []`
- Decisions → `## Research` section
- Max ~500 lines/file
- Edit existing > create new
- Max 2 folder levels

---

## The Flow

```
RESEARCH → DECIDE → CODIFY → GENERATE → PUBLISH → MINE → RESEARCH
```

---

## Skills

| Skill | What |
|-------|------|
| `/start` | Entry point — detect state, route |
| `/setup` | Bootstrap repo structure |
| `/enrich` | Add context, fill gaps |
| `/think` | Research → decide → codify |
| `/ad-static` | Static ad copy |
| `/ad-video-scripts` | Video scripts (15-60s) |
| `/ad-review` | Compliance review (6 lenses) |
| `/content` | Mine competitors, organic scripts |
| `/skool-manager` | Community engagement |
| `/skool-vsl-scripts` | VSL scripts |

---

## Lenses (for /ad-review)

| Lens | Checks |
|------|--------|
| ftc-compliance | FTC regs, earnings claims, disclosures |
| meta-policy | Platform triggers, ban risks |
| copy-quality | Schwartz, Hormozi, Suby frameworks |
| visual-standards | Safe zones, OCR triggers |
| voice-authenticity | AI tells, brand consistency |
| substantiation | Claims vs proof matching |

---

## Compliance Resources

`.claude/reference/compliance/`:
- `ftc-scrutiny-categories.md` — Industry risk tiers
- `angle-playbook.md` — 10 angles + rules
- `testimonial-decision-rubric.md` — When outcomes worth risk
- `typicality/` — FTC outcome data collection

---

## Commits

```
[type] Brief description
```

Types: `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`
