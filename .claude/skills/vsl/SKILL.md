---
name: vsl
description: Write high-converting Video Sales Letter scripts for any offer type. Routes to appropriate framework based on context. Use when: (1) Creating VSL scripts for Skool communities or membership offers (2) Writing sales videos for B2B high-ticket services ($3K-$50K+) (3) User says "VSL", "video sales letter", "sales video script", "about page video" (4) Need structured frameworks: 18-section for Skool/membership or 7-step Haynes for B2B. Produces camera-ready scripts optimized for spoken delivery. Never invents facts.
---

# VSL Script Writer

Routes to the right framework based on your offer type.

---

## Pull Latest Updates

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

---

## Critical Rule: Never Invent Facts

Before writing ANY VSL, verify you have explicit confirmation for every claim.

- Do NOT invent statistics, numbers, or credentials
- Do NOT assume pricing, years in business, or client counts
- Do NOT fabricate testimonials or results
- If information is missing, ASK for it before proceeding

After gathering context, re-read every factual claim and verify against source material.

---

## Triage: Which Framework?

| Signal | Framework | Reference |
|--------|-----------|-----------|
| Skool community, membership, $47-$497/month | **Skool 18-Section** | `references/frameworks/skool-18-section.md` |
| B2B, agency, high-ticket ($3K-$50K+), affluent buyers | **B2B Haynes 7-Step** | `references/frameworks/b2b-haynes.md` |

**Keyword triggers:**
- "Skool", "community", "membership", "about page" → Skool framework
- "B2B", "agency", "high-ticket", "affluent", "service provider" → B2B framework

If unclear, ask: "Is this for a Skool/membership community ($47-$497/month) or a B2B high-ticket service ($3K+)?"

---

## Reference Required (Both Frameworks)

| File | Purpose | Required |
|------|---------|----------|
| `reference/core/offer.md` | What you sell, price, inclusions, guarantee | Yes |
| `reference/core/audience.md` | Who buys, their pains, objections | Yes |
| `reference/core/origin.md` | Founder backstory for intro/epiphany bridge | Recommended |
| `reference/proof/testimonials.md` | Success stories with specifics | Yes |

**origin.md usage:** Use heavily in Epiphany Bridge (Section 2), light elsewhere. See `vip/.claude/skills/origin/references/usage-guide.md` for full guidance.

**If required files missing:** Ask user to provide or run `/think` first.
**If origin.md missing and using Epiphany Bridge:** Suggest `/origin` — that section needs a real founder story to work.

---

## Framework Quick Summaries

### Skool 18-Section Framework

For community/membership offers. Full reference: `references/frameworks/skool-18-section.md`

**Flow:** Hook → Epiphany Bridge → Peek Plan → Features/Soft CTA → The Plan → Answer Questions → Stack Proof → Change Tone → Zoom Out → Price Anchor → Low Effort/High Reward → Recap Obstacles → Address Objections → Roadmap → Worst/Best Case → Hard CTA → Risk Reversal → Final CTA

**Key principles:**
- Hook creates pain recognition ("that's exactly how I feel")
- Epiphany bridge shows your journey from struggle to solution
- Social proof covers diverse backgrounds
- CTAs progress: soft → soft → hard
- Risk reversal makes joining feel safer than not joining

---

### B2B Haynes 7-Step Framework

For high-ticket B2B services. Full reference: `references/frameworks/b2b-haynes.md`

**Flow:** 60-90 Second Summary → Hook → Why (Legitimacy) → Market Drivers → Offer & Price → Objection Handling → Qualification → CTA

**Example:** See `references/examples/b2b-ijanitorial.md`

**Key principles:**
- Tweet version (first 90 seconds) covers entire pitch
- State price upfront (trains pixel on qualified buyers)
- For affluent: direct, conservative claims, no hype
- Clear qualification: who it IS and ISN'T for
- Vocabulary control (no "money", "guaranteed", "savings")

---

## Process

1. **Triage** — Determine framework from offer type
2. **Gather context** — Verify you have required reference files
3. **Get campaign name** — Ask: "What should we call this VSL? (e.g., 'skool-about', 'agency-pitch')"
4. **Load framework** — Read the appropriate reference file
5. **Write script** — Follow framework structure
6. **Verify facts** — Check every claim against source material
7. **Optimize for spoken delivery** — Contractions, short sentences, natural flow
8. **Save and commit prompt** — Save to output path, ask: "Saved to [path]. Want me to commit this to git?"

---

## Output Path

**Standard:** `outputs/YYYY-MM-DD-vsl-{campaign}/vsl-script.md`

Campaign name is REQUIRED. Ask user if not provided. Examples: `skool-about`, `agency-pitch`, `membership-sales`.

**Files:**
- `vsl-script.md` — The full VSL script
- `review-log.md` — Created if compliance reviewed

---

## Output Format

Both frameworks produce scripts with:
- Header: Target audience, transformation, runtime estimate
- Sections with timestamps/chapter markers
- Delivery/production notes
- Quality checklist verification

---

## Recovery from Compaction

When conversations get long, Claude's memory compresses. This helps resume VSL sessions.

### For Users

Just say `/vsl` again and describe where you were:
- "We were working on the Skool VSL, got through section 5"
- "Continue the B2B script for my agency"
- "Where was I on the sales video?"

### For Claude

1. **Check for in-progress scripts:**

```bash
ls -ltd outputs/*-vsl-*/ 2>/dev/null | head -3
```

2. **Re-read key files:**

| File | What It Provides |
|------|------------------|
| This SKILL.md | Triage logic, critical rules |
| `references/frameworks/skool-18-section.md` | Full 18-section template |
| `references/frameworks/b2b-haynes.md` | Full 7-step B2B framework |
| User's `reference/core/offer.md` | Offer details for script |
| User's `reference/proof/testimonials.md` | Proof for script |

3. **Confirm with user:**

> "I see you were working on [framework] VSL. You're at [section]. Continue from here?"

---

## When NOT to Use

- Static image ads (use `/ads`)
- Short-form video scripts under 60 seconds (use `/ads` video scripts)
- General copywriting or landing pages
- Content without sales intent

Use `/vsl` when creating structured 5-20 minute sales video scripts.
