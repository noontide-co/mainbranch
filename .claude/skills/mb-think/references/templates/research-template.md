# Research Template

Copy this template when creating research files.

---

## Filename Convention

```
research/YYYY-MM-DD-topic-[source].md
```

**Source suffixes:**
- `-gemini.md` — Gemini deep research
- `-gpt.md` — ChatGPT research
- `-claude-code.md` — Claude Code session (this tool)
- `-claude-web.md` — Claude.ai web interface
- `-x-social.md` — X/Twitter social research (Grok MCP)
- `-yt-mining.md` — YouTube transcript mining (Apify)
- `-ig-mining.md` — Instagram mining (Apify or manual)
- `-local-mining.md` — Local video/audio transcription
- `-voice-mining.md` — Voice memo transcription
- `-competitor-mining.md` — Competitor site mining
- `-internal-mining.md` — Internal data (emails, DMs, reviews)
- `-audit.md` — Site or system audit
- (no suffix) — General or mixed sources

---

## Template

```markdown
---
type: research
date: YYYY-MM-DD
source: claude-code
source_url:                    # Optional: Gemini/GPT share link for provenance
model: opus-4.5
status: draft
linked_decisions: []
---

# [Topic] Research

## Question

[1-3 sentences: What you're trying to learn. Be specific.]

---

## Methodology

[2-4 sentences: How you approached this research. What tools, what context provided, what attachments. Not the full prompt — just enough to reproduce or audit.]

---

## Sources Checked

| Source | What We Found |
|--------|---------------|
| [Source 1] | [Brief summary] |
| [Source 2] | [Brief summary] |
| [Source 3] | [Brief summary] |

---

## Raw Findings

### [Finding Area 1]

[Detailed notes, quotes, data]

### [Finding Area 2]

[Detailed notes, quotes, data]

### [Finding Area 3]

[Detailed notes, quotes, data]

---

## Synthesis (REQUIRED)

### One-Sentence Summary (20 words max)

[Force yourself to distill the core insight]

### Key Findings (5-10 bullets, 15 words each)

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]
4. [Finding 4]
5. [Finding 5]

### Implications for Reference Files

| File | Potential Update |
|------|------------------|
| `reference/core/offer.md` | [What might change] |
| `reference/core/audience.md` | [What might change] |
| `reference/proof/angles/` | [What might change] |

### Open Questions

- [What we still don't know]
- [What needs follow-up research]

---

## Citations

- [Source 1 with link if available]
- [Source 2]
- [Source 3]
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `draft` | Research in progress, not yet synthesized |
| `complete` | Synthesis done, ready to inform decisions |
| `codified` | Findings have been applied to reference files |
| `superseded` | Newer research replaces this |

---

## Linking to Decisions

When a decision uses this research, update the frontmatter:

```yaml
linked_decisions:
  - decisions/2026-01-17-pricing-strategy.md
  - decisions/2026-01-18-guarantee-policy.md
```

This creates a bidirectional link (research links forward to decisions, decisions link back to research).

---

## Quality Checklist

Before marking research as `complete`:

- [ ] Question is specific and answerable
- [ ] At least 3 sources checked
- [ ] Raw findings are detailed
- [ ] Synthesis section is complete
- [ ] One-sentence summary exists and is under 20 words
- [ ] Key findings are 5-10 bullets, each under 15 words
- [ ] Implications for reference files are explicit
- [ ] Open questions documented
- [ ] Citations included

---

## Example: Completed Research

```markdown
---
type: research
date: 2026-01-17
source: claude-code
model: opus-4.5
status: complete
linked_decisions: []
---

# Pricing Tier Strategy Research

## Question

What pricing tier structure should we use for the community membership?

**Why this matters:** Currently one tier at $97/month. Considering adding free tier or premium tier. Need data to decide.

---

## Sources Checked

| Source | What We Found |
|--------|---------------|
| Competitor analysis (5 communities) | $47-197/month range, most have 2-3 tiers |
| Skool pricing norms | Free tier common for lead gen, paid starts at $47-97 |
| Past member feedback | 3 members mentioned wanting "advanced" content |
| Industry benchmarks (SaaS pricing research) | 3 tiers is optimal, middle tier gets 60% of signups |

---

## Raw Findings

### Competitor Pricing

- Community A: Free / $67/month / $197/month
- Community B: $97/month only (premium positioning)
- Community C: Free / $47/month (high volume)
- Community D: $147/month / $297/month (ultra-premium)
- Community E: Free / $97/month / $497/year

### Member Feedback

[Detailed quotes and feedback...]

### Industry Data

[Pricing psychology research, conversion data...]

---

## Synthesis

### One-Sentence Summary (20 words max)

Three-tier pricing with free/paid/premium maximizes reach while creating natural upgrade paths for committed members.

### Key Findings

1. Two-tier (free/paid) is minimum viable for lead generation
2. Three-tier captures both budget-conscious and power users
3. Middle tier gets 60%+ of signups in most communities
4. Annual pricing increases retention 30-40% vs monthly
5. Premium tier should be 2-3x base price, not 1.5x
6. Free tier converts 5-15% to paid within 60 days
7. "Investment" framing outperforms "deal" framing for our audience

### Implications for Reference Files

| File | Potential Update |
|------|------------------|
| `reference/core/offer.md` | Add tier descriptions, pricing logic |
| `reference/core/audience.md` | Segment by tier (free seeker vs committed buyer) |
| `reference/proof/angles/value.md` | Update ROI math for each tier |

### Open Questions

- What should the free tier include to create desire for paid?
- Should premium be monthly or annual-only?
- How do we position the upgrade without devaluing free?

---

## Citations

- [Competitor A sales page URL]
- [Pricing research article URL]
- Member feedback: Slack #feedback channel, Jan 2026
```
