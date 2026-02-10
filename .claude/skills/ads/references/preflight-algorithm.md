# Pre-Flight Readiness Algorithm

Score reference file depth before generating ads. Prevents thin reference from producing generic output.

---

## When to Run

- **`/ads` Step 0** — Before triage menu appears
- **`/start`** — As part of global gap scan (surfaces priorities)

---

## Scoring Matrix

Score each file 0-3 based on line count + section presence.

| Score | Label | Criteria |
|-------|-------|----------|
| **0** | Missing | File does not exist |
| **1** | Stub | File exists but under 20 lines or only has headers |
| **2** | Adequate | 20-80 lines with key sections populated |
| **3** | Rich | 80+ lines with specifics, examples, or proof |

### Files Scored

Use canonical path resolution for offer and audience files (multi-offer aware):

1. Check `.vip/local.yaml` for `current_offer`
2. If `current_offer` is set and `offers/{current_offer}/offer.md` exists, score that file
3. Otherwise fall back to `reference/core/offer.md`
4. Same resolution for `audience.md`

See `docs/system-architecture.md` (Canonical Path Resolution) for the full algorithm.

| File | Key Sections | Weight |
|------|-------------|--------|
| `offer.md` (resolved) | Price, mechanism, benefits, guarantee | Required |
| `audience.md` (resolved) | Pains, desires, demographics, psychographics | Required |
| `reference/core/voice.md` | Tone, phrases, personality, don'ts | Required |
| `reference/proof/testimonials.md` | Named testimonials with outcomes | Required |
| `reference/proof/angles/` | At least 1 angle file beyond README | Required |
| `reference/brand/visual-style.md` | Colors, typography, mood, prompt fragments | Optional (affects image gen) |

### Scoring Logic

```
Resolve offer.md and audience.md paths first (see above).

For each file:
  if not exists → 0
  if exists and lines < 20 → 1
  if exists and 20 ≤ lines < 80 → 2
  if exists and lines ≥ 80 → 3

For angles/:
  count = number of .md files (excluding README.md)
  if count == 0 → 0
  if count == 1 → 1
  if count == 2-3 → 2
  if count >= 4 → 3

Composite = sum of all 6 scores (max 18)
```

---

## Thresholds

| Composite | Status | Action |
|-----------|--------|--------|
| **12-18** | GREEN | Proceed to triage. Full creative diversity possible. |
| **8-11** | YELLOW | Warn user. Show gaps. Allow override: "I know my reference is thin, proceed anyway." |
| **4-7** | RED | Route to `/think` with specific enrichment targets. Offer parallel agents to fill gaps. |
| **0-3** | BLOCKED | Route to `/setup`. Cannot generate meaningful ads. |

---

## Report Format

Display to user at Step 0:

```
Pre-Flight Check:
  offer.md      ███░ 3/3 (rich — 211 lines)
  audience.md   ███░ 3/3 (rich — 165 lines)
  voice.md      ███░ 3/3 (rich — 230 lines)
  testimonials  ███░ 3/3 (rich — 332 lines)
  angles/       █░░░ 1/3 (stub — 1 file, need 4+)
  visual-style  ░░░░ 0/3 (missing)

  Composite: 13/18 — GREEN
  Gaps: angles thin, no visual style

  Image gen:    ✓ Nano Banana available
  Ad account:   — not connected (optional — lets me see your live Meta ad performance to inform new ads)
```

**Ad account status line:** Always display after the composite score. Describes the capability, not the tool name. See SKILL.md "User-Facing Display" for the exact wording for connected vs not connected states.

---

## Gap Guidance

When gaps are found, explain WHY each matters for ads:

| Gap | Why It Matters |
|-----|----------------|
| **offer.md missing** | Ads will be generic — no specifics about what you sell, price, or mechanism |
| **audience.md missing** | Can't write hooks that resonate — no pains, desires, or language to use |
| **voice.md missing** | Ads will sound generic AI — no brand personality to apply |
| **testimonials missing** | No social proof angles available — limits creative diversity |
| **angles/ empty** | All ads will use the same entry point — Andromeda penalizes repetition |
| **visual-style missing** | Image prompts will be freestyle only — no brand consistency option |

---

## Smart Recommendations

Based on available data, recommend a creative approach:

| visual-style.md | Recommendation |
|-----------------|----------------|
| Rich (3/3) | "60% on-brand, 40% freestyle for variety" |
| Adequate (2/3) | "50/50 on-brand and freestyle — brand style is basic" |
| Stub (1/3) | "Mostly freestyle — brand style needs enrichment" |
| Missing (0/3) | "All freestyle — no brand style file. Want to create one? (3 questions)" |

---

## Quick Scaffold

If visual-style.md is missing, offer inline creation during pre-flight (don't force `/setup`):

> "No visual style file found. I can create one now with 3 questions:
> 1. What's your brand's visual mood? (minimal/bold/editorial/playful/dark)
> 2. What are your brand colors? (hex codes or descriptions)
> 3. What photography style fits? (lifestyle/product/abstract/editorial)
>
> Or skip — all image prompts will be freestyle."

---

## Media Output Path Check

**Not part of composite score.** This is an informational check that runs after scoring, before image generation begins.

### Detection Flow

```
1. Read ~/.config/vip/local.yaml
2. Resolve image path:
   a. media.images → use directly
   b. media.root → {root}/images/
   c. neither → prompt user

3. If path resolved and exists:
   → Confirm: "Images will save to {path}/{campaign}/"

4. If path resolved but doesn't exist:
   → "Output folder doesn't exist: {path}. Create it? (y/n)"
   → If yes: mkdir -p

5. If no path configured:
   → "Where should generated images be saved?"
   → Examples: "~/Google Drive/My Drive/Main Branch/images"
   → Save to ~/.config/vip/local.yaml under media.root
   → mkdir -p {path}
```

**Ask once, save forever.** First `/ads` run with image gen prompts for path. Every subsequent run reads from config and confirms.

**If path is inside git repo:**
→ Warn: "This folder is inside your git repo. Binary images will bloat history. Want me to add a .gitignore entry? (y/n)"

---

## Decisions-Without-Codification Detection

Check for a common stuck state:

```
if decisions/ has 3+ files with status: accepted
AND reference/ has gaps (composite < 12)
THEN surface:
  "You have accepted decisions that haven't been applied to reference.
   Want to run parallel agents to codify them?"
```

---

## Integration Points

- **`/ads`** — Step 0, blocks or warns before triage
- **`/start`** — Global scan, surfaces as priority items
- **`/think codify`** — Uses same scoring to detect what needs enrichment
- **Parallel agents** — When RED, offer to spawn agents that fill gaps from existing research/decisions

---

*Shared algorithm used by /ads (Step 0) and /start (gap scan).*
