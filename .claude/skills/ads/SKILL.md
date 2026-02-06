---
name: ads
description: "Create and review Meta/Facebook/Instagram ads. Routes to: static image ads (copy + AI image prompts), video scripts (15-30 spoken-word scripts), one-liners (30 diversified copy lines for static images), or multi-lens compliance review. Use when asked to create ads, ad copy, image prompts, video scripts, or review ads. Say /ads or ask for static ads, video scripts, one-liners, or ad review."
---

# Ads Skill

Create static ads, video scripts, one-liners, or review ads for compliance.

## Step 0: Pre-Flight Readiness

**Before triage, find the business repo and score reference file depth.** This prevents generating generic ads from thin reference.

### 0a. Find Business Repo (REQUIRED — do this first)

**NEVER search the filesystem. NEVER use Explore or Task agents to find repos. NEVER scan ~/Documents/GitHub/.**

Do this instead — one step:

```bash
cat ~/.config/vip/local.yaml 2>/dev/null
```

- If `default_repo:` exists → **ask user to confirm:** "Found saved repo: [name]. Use this? (y/n)"
- If no config or no default_repo → **ask the user:** "Which business repo should I use? Give me the path."
- If the command returns nothing or errors → **that is fine. Just ask the user. Do NOT search for repos.**
- If `/ads` was invoked from `/start`, the repo is already identified — use it without asking.

**Always confirm the repo before proceeding.** Never assume.

### 0b. Score Reference Files (fast — direct Read only, NO agents)

**NEVER spawn Explore or Task agents for pre-flight.** Read files directly at the known repo path. Pre-flight should complete in under 10 seconds.

At the repo path, resolve offer context first (see Offer Context Resolution above), then check these files and count lines:

```
[resolved offer.md]          → 0 (missing), 1 (<20 lines), 2 (20-80), 3 (80+)
[resolved audience.md]       → same scoring
reference/core/voice.md      → same scoring
reference/proof/testimonials.md → same scoring
reference/proof/angles/*.md  → count .md files EXCLUDING README.md: 0=0, 1=1, 2-3=2, 4+=3
reference/brand/visual-style.md → same scoring (optional)
```

In multi-offer mode, score the offer-specific `offer.md` and `audience.md` (resolved via path resolution), not the brand-level `core/offer.md`.

Composite = sum of all 6 scores (max 18).

### 0c. Route on Score

| Composite | Status | Action |
|-----------|--------|--------|
| **12-18** | GREEN | Proceed to triage |
| **8-11** | YELLOW | Warn user, show gaps, allow override |
| **4-7** | RED | Route to `/think` with enrichment targets |
| **0-3** | BLOCKED | Route to `/setup` |

Display the readiness report, then proceed. See [references/preflight-algorithm.md](references/preflight-algorithm.md) for gap guidance and smart mix recommendations.

### 0d. Check Nano Banana

```bash
source ~/.config/vip/env.sh 2>/dev/null; echo "GOOGLE_API_KEY=${GOOGLE_API_KEY:+set}"
```

If set, note it for Batch 4 image generation after copy is saved.

---

## Triage

Determine mode from user request:

| Mode | Triggers | Output |
|------|----------|--------|
| **Static** | "static ads", "image ads", "primaries", "headlines", "image prompts" | 5-6 concepts, each with 5 primaries + 5 headlines + 3 image prompts |
| **Video** | "video scripts", "ad scripts", "spoken word", "camera scripts" | 15-30 diverse scripts for spoken delivery |
| **One-Liner** | "one-liners", "30 one-liners", "Andromeda", "diversified static copy" | 30 diversified copy lines for static image ads (Andromeda-optimized) |
| **Review** | "review", "check", "audit", "compliance", "before launch" | P1/P2/P3 report across 6 lenses |

If unclear, ask: "Do you want static image ads, video scripts, one-liners, or a compliance review?"

---

## Pre-Flight: Special Ad Categories

**Before generating any ads, ask:**

> "Will this campaign run as a Meta Special Ad Category? (Housing, Employment, Credit, or Social Issues/Politics)"

If **Employment** (job training, career coaching, hiring, job boards):

1. **Load additional rules:** See Meta Policy lens → Employment section
2. **Warn user:** "Employment category has strict restrictions. I'll avoid salary assertions, 'if you've been...' patterns, and job-seeking status claims."
3. **Tag the output:** Add `special_ad_category: employment` to frontmatter

### Employment Category Quick Rules

These patterns that work in standard ads will get rejected in Employment:

| Pattern | Why It Fails | Alternative |
|---------|--------------|-------------|
| "If you've been stuck at £30k..." | Asserts current employment status | "DevOps engineers can reach £60k+" |
| "Still getting rejected after interviews?" | Personal attribute (job-seeking status) | "Interview preparation that works" |
| "Tired of your dead-end job?" | Asserts job dissatisfaction | "Career advancement strategies" |
| Salary numbers as pain (£30k, $50k) | Implies current salary = personal attribute | Salary as aspiration only |

**The rule:** In Employment, ANY assertion about current status (job, salary, employment state) = Personal Attributes violation. Aspirational framing only.

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. Check `.vip/local.yaml` for `current_offer`
2. If set: load `reference/offers/[current_offer]/offer.md` as the active offer
3. If not set AND `reference/offers/` exists: ask which offer
4. If no `offers/` folder: use `reference/core/offer.md` (single-offer, backward compatible)

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

**Offer argument:** `/ads [mode] [offer] [campaign]` — e.g., `/ads static community january-launch`
If offer specified, overrides session `current_offer` for this run.

---

## Reference Required (All Modes)

Before creating ads, the business repo must have:

| File | Path | Required |
|------|------|----------|
| Offer | `offers/[active]/offer.md` or `core/offer.md` (resolved via path resolution) | Yes |
| Audience | `offers/[active]/audience.md` or `core/audience.md` (resolved via path resolution) | Yes |
| Voice | `reference/core/voice.md` (always core) | Yes |
| Testimonials | `reference/proof/testimonials.md` + `offers/[active]/testimonials.md` (accumulate) | Yes |
| Angles | `reference/proof/angles/*.md` | Yes (at least 1) |
| Visual Style | `reference/brand/visual-style.md` | Optional (affects image gen) |
| Content Strategy | `reference/domain/content-strategy.md` (always brand-level) | Optional (improves topic selection) |
| Skool Surfaces | `reference/domain/funnel/skool-surfaces.md` | Optional (congruence check) |

If required files are missing, Step 0 pre-flight catches this and routes appropriately.

**Content funnel awareness:** Ads are the "immediate ROI" pillar of the two-pillar value prop (ads + content). In the content pipeline, ads drive newsletter signups, newsletter nurtures, Skool trial converts, revenue follows. If `content-strategy.md` exists, use content pillars to inform angle selection, metrics to understand what performs organically (ads amplify top-performing organic content), and funnel mapping to determine whether ads should target awareness, consideration, or conversion.

**Skool surface congruence:** If `reference/domain/funnel/skool-surfaces.md` exists, check it before finalizing any batch. Ad copy must not promise anything not visible on the Skool about page or pricing cards. Pricing mentioned in ads must match current tier structure. Language and framing should echo (not contradict) the about page positioning. The about page is the FIXED surface — ads are the VARIABLE surface.

---

## Mode: Static Ads

Create campaign batches with image prompts + ad copy.

### Campaign Structure

Each batch = 5-6 angles. Each angle = 3 image creatives (graphic, lo-fi, interrupt).

```
Campaign Batch 001
├── Angle 1: 001_01 (graphic), 001_02 (lo-fi), 001_03 (interrupt)
├── Angle 2: 001_04, 001_05, 001_06
└── [etc.]
```

### Hook Rules (Non-Negotiable)

**Hook = 123-135 characters** (visible before "See more" on Facebook).

- No questions (binary "no" response)
- No "you/your" in first 3 lines
- No emojis
- Pack customer language into the hook

**Hook Formulas:**
1. **Transformation:** "How [Resonance] go from [Pain] to [Benefit] using [Approach]"
2. **Even Without:** "Here's how even [Resonance] (without [Challenge]) are [Benefit]"
3. **Eliminates:** "This [Approach] eliminates [Pain 1], [Pain 2], without [Challenge]"

### Workflow

**Batch 1: Copywriting**

1. Read project context (offer, audience, proof, angles)
2. Ask for campaign name (required)
3. Select 5-6 angles for the batch — **reference `.claude/reference/compliance/angle-playbook.md`** for angle types, compliance burden, and selection matrix
4. **Write ALL image prompts first** (Part 1)
5. **Write ALL ad copy second** (Part 2)
6. **Cold traffic language check:** Every hook must pass the 3-second comprehension test — no insider jargon, no assumed context. Translate community language to customer language. See Joel's cold traffic guidance in [references/one-liner-methodology.md](references/one-liner-methodology.md).
7. Save to `outputs/YYYY-MM-DD-static-ads-[offer]-{campaign}/static-ads-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
8. Tell user: "Copy saved. Running automatic post-generation pipeline..."
9. Run the **Automatic Post-Generation Pipeline** (see below). This handles git commit, compliance review, and image generation automatically.

### Ad Styles (5 per concept)

| Style | Length |
|-------|--------|
| Deep Ad | 500-800 words |
| UGC/Native | 100-300 words |
| Direct Response | 100-400 words |
| Pattern Interrupt | Under 100 words |
| Testimonial | 200-400 words |

### Image Prompt Types

| Type | Use Case |
|------|----------|
| Graphic | Typography-focused, frameworks, authority |
| Lo-fi | UGC style, authenticity, social proof |
| Interrupt | Pattern interrupt, scroll-stopping, contrarian |
| One-liner | Background-only for text overlay (used with one-liner copy) |

**Format pair: 1:1 + 9:16** — Facebook Ads Manager accepts exactly these two formats per ad. Design 9:16 first with critical content in center 1:1 safe zone. Center-crop for square. One design → two uploads.

See [references/static-output-template.md](references/static-output-template.md) for full output format.
See [references/image-prompt-templates.md](references/image-prompt-templates.md) for template library.
See [references/image-generation-workflow.md](references/image-generation-workflow.md) for Nano Banana integration.

---

## Mode: One-Liner

Generate 30 punchy, truly diversified one-liners for static image ads that feed Meta's Andromeda algorithm.

### Why This Mode Exists

Meta's Andromeda algorithm (July 2025) rewards TRUE creative diversification - not surface variations. 30 one-liners = 30 different psychological conversations, each anchored in offer-specific details.

### 6-Step Process

1. **Core Outcome:** Single transformation every buyer achieves
2. **Extract Specifics:** Roles, timelines, niche pains, value props, failed alternatives, proof points
3. **Reasons to Buy:** 15-20 fundamentally different reasons (the protein supplement exercise)
4. **Hook Categories:** Ensure variety across problem agitation, emotional state, transformation, contrarian, identity callout, etc.
5. **Generate:** 30 one-liners, each with at least one specific anchor
6. **Output:** Simple numbered list, ready to copy

### The Anchor Rule (Non-Negotiable)

Every one-liner **MUST** include at least one specific element:
- A specific role, outcome, or company (DevOps Engineer, AWS, 60k)
- A specific niche pain (service desk 2+ years, no CS degree)
- A specific value prop (mock interviews with Principal Engineers)
- A specific timeline or proof point (8 weeks, 500+ community)

**The Specificity Test:** If this one-liner could sell a gym membership, a life coaching program, or a generic course - it fails. Rewrite it.

### Input Modes

| Mode | How to Detect | What to Pull |
|------|---------------|--------------|
| **Has business repo** | Reference files exist | Resolved `offer.md`, resolved `audience.md`, `reference/core/voice.md`, testimonials |
| **No repo** | Nothing found | Ask user for materials |

### Output Format

**Save to file, not chat.** This enables review to edit the file directly.

1. Ask for campaign name (required)
2. Create folder: `outputs/YYYY-MM-DD-one-liners-[offer]-{campaign}/` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
3. Save full generation context + one-liners to: `one-liners-batch-001.md`
4. Tell user: "Saved 30 one-liners. Running automatic post-generation pipeline..."
5. Run the **Automatic Post-Generation Pipeline** (see below). This handles git commit, compliance review, and image generation offer automatically.

**one-liners-batch-001.md format:**

```markdown
---
type: output
subtype: one-liners
date: YYYY-MM-DD
status: draft
review_status: null
---

# One-Liners: {Campaign Name}

## Core Outcome

[Single sentence: the transformation every buyer achieves]

## Extracted Specifics

| Category | Specifics |
|----------|-----------|
| **Roles/Outcomes** | [roles, job titles, results] |
| **Timelines** | [how fast results happen] |
| **Niche Pains** | [pains SPECIFIC to this audience] |
| **Value Props** | [what makes THIS offer different] |
| **Failed Alternatives** | [what they've tried] |
| **Proof Points** | [numbers, stats, community size] |

## Reasons to Buy

[Numbered list of 15-20 fundamentally different reasons]

## Hook Categories

[Which categories each one-liner uses - for diversity check]

---

## One-Liners

1. [one-liner]
2. [one-liner]
...
30. [one-liner]
```

**Why save the full context:**
- **Anchor verification:** Reviewers can check each one-liner has a specific from the extraction
- **Resume capability:** Don't re-extract specifics if generating more
- **Understanding:** Why certain hooks were chosen
- **Quality control:** Can verify all reasons to buy are covered

See [references/one-liner-methodology.md](references/one-liner-methodology.md) for the complete 6-step process, hook categories, and quality checklist.

See [references/one-liner-examples.md](references/one-liner-examples.md) for real examples by offer type.

---

## Mode: Video Scripts

Create diverse spoken-word scripts for camera delivery.

### 6-Step Process

1. **Core Outcome:** Single result every buyer achieves
2. **Avatars:** 3-4 buyer personas with situation, frustration, desires
3. **Angles Per Avatar:** Map angles from project context
4. **Generate Ads:** 15-30 scripts across all avatars
5. **Optimize for Spoken:** ~5th grade reading level, contractions, fragments
6. Ask for campaign name (required)
7. **Save Output:** `outputs/YYYY-MM-DD-video-ads-[offer]-{campaign}/video-ads-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
8. Tell user: "Video scripts saved. Running automatic post-generation pipeline..."
9. Run the **Automatic Post-Generation Pipeline** (see below). This handles git commit and compliance review automatically. (No image generation for video scripts.)

### Script Structure

**Hook** (1-2 sentences): Lead with pain, desire, or belief. Create curiosity.

**Body** (4-8 sentences): Why problem exists. Position offer. Include proof.

**CTA** (2-3 sentences): Clear instruction. What happens after click.

**CRITICAL**: Each ad = fundamentally different reason to buy.

### Spoken Delivery Optimization

- Contractions: you're, don't, can't, won't
- Fragments: "Not theory. Patterns."
- Simple words: "use" not "utilize"

See [references/video-templates-hooks.md](references/video-templates-hooks.md) for templates and hook bank.

---

## Mode: Review

Review ads through 6 compliance and quality lenses before shipping.

### The 6 Lenses

| Lens | Location | What It Checks |
|------|----------|----------------|
| FTC Compliance | `.claude/lenses/ftc-compliance.md` | Federal regulations, earnings claims |
| Meta Policy | `.claude/lenses/meta-policy.md` | Platform triggers, Personal Attributes |
| Copy Quality | `.claude/lenses/copy-quality.md` | Schwartz, Hormozi, Suby frameworks |
| Visual Standards | `.claude/lenses/visual-standards.md` | Safe zones, OCR, prohibited visuals |
| Voice Authenticity | `.claude/lenses/voice-authenticity.md` | AI tells, brand voice |
| Substantiation | `.claude/lenses/substantiation.md` | Claims inventory, proof matching |

### Review Process

1. Gather input (single ad, batch, or component)
2. Git commit current state (preserves original): `[output] {type} batch pre-review`
3. Spawn 6 parallel Task agents — one per lens. Use `subagent_type: "general-purpose"`. Each agent:
   - Reads the ad batch/copy being reviewed
   - Reads its assigned lens file from `.claude/lenses/`
   - Evaluates every ad against that lens's checklist
   - Returns P1/P2/P3 findings with specific line references
   - Does NOT fix anything — just reports findings (read-only pattern, no write risk)
4. When all 6 agents return, synthesize findings into a unified P1/P2/P3 report (deduplicate where lenses overlap)
5. Apply P2/P3 fixes directly to the batch file
6. Create `review-log.md` documenting what changed
7. Tell user: "Fixes applied. Want me to commit these changes to git?"
8. If yes, commit: `[review] {type} batch - N fixes applied`

### Severity Levels

| Level | Meaning |
|-------|---------|
| **P1** | Blocks launch (legal/platform risk) |
| **P2** | Fix before launch (reduces performance or risk) |
| **P3** | Nice to have (optimization) |

### Status Determination

- **BLOCKED:** Any P1 issues
- **REVIEW REQUIRED:** Multiple P2 or borderline P1
- **CLEAR:** No P1, minimal P2

See [references/review-workflow.md](references/review-workflow.md) for full report format.

---

## Automatic Post-Generation Pipeline

**Every generation mode (Static, One-Liner, Video) runs this pipeline automatically after saving output.** Do not ask the user whether to run compliance review -- it is automatic.

See **[references/post-generation-pipeline.md](references/post-generation-pipeline.md)** for the complete pipeline: git commit pre-review, lens tier selection, Nano Banana check, parallel agent spawning (compliance + image), synthesis, unified report, and post-review commit.

**Quick summary:** Commit pre-review state, spawn 5-6 compliance agents + optional image agents in parallel, synthesize P1/P2/P3 findings, auto-apply P2/P3 fixes, surface P1 to user, present unified report, commit post-review.

---

## Compliance (All Modes)

**Never say:**
- Cures/treats/heals [condition]
- Guaranteed results
- Will eliminate [problem]

**Safe to say:**
- Many have found this helpful
- Supports/complements existing approach
- Framework for understanding
- Education and guidance

---

## Quality Checklist (All Copy Modes)

Before saving any batch, verify:

| Check | Requirement |
|-------|-------------|
| **Anchor specificity** | Every hook/one-liner has at least one offer-specific anchor |
| **Cold traffic language** | No insider jargon — would a stranger understand in 3 seconds? |
| **Hook length** | 123-135 characters for static ad hooks |
| **No questions** | Hooks don't start with yes/no questions |
| **No you/your** | First 3 lines avoid direct address |
| **Angle diversity** | Each concept uses a genuinely different psychological entry point |
| **Voice match** | Copy matches `voice.md` tone (if available) |
| **Compliance** | No banned claims, proper testimonial attribution |
| **Skool congruence** | Claims match live about page + pricing cards (if `skool-surfaces.md` exists) |

---

## Recovery from Compaction

If context was compacted mid-task, check:

1. **Which offer?** Read `.vip/local.yaml` for `current_offer` to restore offer context
2. **What mode?** Static, Video, or Review
3. **What stage?** Planning angles, writing hooks, generating prompts, reviewing
4. **What's done?** Check outputs/ folder for partial work
5. **Resume:** Continue from the last completed step

For static: Did we finish image prompts (Part 1) before copy (Part 2)?
For video: How many of 15-30 scripts are done?
For review: Which lenses completed?

---

## Quick Reference

**Static ads:** 5-6 concepts x 5 primaries x 5 headlines x 3 image prompts
**Video scripts:** 15-30 diverse scripts, spoken-word optimized
**Review:** 6 lenses, P1/P2/P3 report, fix suggestions
