---
name: ads
description: "Create and review Meta/Facebook/Instagram ads. Flexible entry points: full pipeline (copy + images), copy only, images only, creative variations (hook library), video scripts, video repurpose, compliance review, or ad account check (Pipeboard). Use when asked to create ads, ad copy, image prompts, video scripts, creative variations, or review ads. Say /ads or describe what you need."
---

# Ads Skill

Create ads, generate creative variations, review for compliance, and check ad account performance.

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

## Pipeboard Detection (Lazy)

Check for Meta ad account access on first /ads invocation when topic is ads-related. Same pattern as Gemini/Grok/whisper detection -- config-first, probe unknowns, cache results.

### Detection Flow

```
1. Read .vip/config.yaml → tools.pipeboard
2. If status: true → note available, skip detection
3. If status: false AND last_checked < 30 days → skip
4. If status: null OR missing OR stale false:
   a. Check for mcp__pipeboard__* tools in session
   b. If found: probe with get_ad_accounts (lightweight)
   c. If probe succeeds: write status: true to config
   d. If not found or probe fails: write status: false to config
5. Never block on detection failure
```

### Config Update (REQUIRED after detection)

```yaml
tools:
  pipeboard:
    status: true              # detection result
    method: mcp
    tier: free                # free | pro (self-reported)
    notes: "meta-ads MCP configured via remote URL"
    last_checked: 2026-02-10
    weekly_calls_used: 0      # lightweight tracking (Phase 1.5)
```

**Graceful degradation:** If Pipeboard is not configured, skip all account-related features. The skill works fully without it. Pipeboard is additive, not required.

### User-Facing Display

**Never assume the user knows what Pipeboard is.** In all user-facing messages, describe the CAPABILITY (connecting your Meta ad account), not the tool name. Use "Pipeboard" only in parentheses as a reference, never as the lead.

**Pre-flight status line (add after Nano Banana check):**

If configured:
> `Ad account:   ✓ connected (I can check what's performing before we create)`

If not configured:
> `Ad account:   — not connected (optional — lets me see your live Meta ad performance to inform new ads)`

**Never say:** "Pipeboard: not configured (no account check — that's fine)" — this means nothing to a new user.

**If user asks what this means:**
> "You can optionally connect your Meta/Facebook ad account so I can pull live performance data — what's spending, what's winning, CPAs, creative that's working. This helps me create ads that fit your account structure and build on what's already performing. It uses a tool called Pipeboard (free tier: 30 calls/week). Want to set it up, or skip and work from your reference files?"

---

## Triage (Flexible Intent Detection)

Detect what the user wants from natural language. Route internally to the right component pipeline. See [references/entry-points.md](references/entry-points.md) for the complete entry point detection table and component composition.

### Intent Detection

| User Says | Entry Point | What Happens |
|-----------|-------------|-------------|
| "static ads", "full from scratch", "image ads" | Full Pipeline | Copy + compliance + images (classic flow) |
| "I already have images, just need copy" | Copy Only | Skip image gen, primaries + headlines |
| "Just need images for existing copy" | Image Only | Nano Banana image gen only |
| "creative variations", "hook library", "one-liners", "50 hooks" | Hook Library | Bulk creative variations (flexible quantity) |
| "video scripts", "ad scripts", "spoken word" | Video Scripts | Spoken-word script pipeline |
| "I'm repurposing a video", "I shot a video" | Video Repurpose | Transcribe + extract hooks + copy variants |
| "I want ideas for an ad", "brainstorm" | Ideation | Account check (if available) + concept generation |
| "Check my ad performance", "what's working" | Account Check | Pipeboard read-only (requires Pipeboard) |
| "Give me 5 variations of this winning ad" | Performance Iteration | Pull winner + generate variants (requires Pipeboard) |
| "What's working before we create?" | Pre-Gen Account Check | Account overview + creative audit (requires Pipeboard) |
| "review", "audit", "compliance check" | Review | 6-lens compliance review |

**Also accepts:** "static", "static ads", "video", "video scripts", "one-liners", "review" -- these route to the same pipelines.

**If unclear,** ask: "What do you have and what do you need? (e.g., 'I have images, just need copy' or 'full from scratch')"

### Proactive Account Awareness

If Pipeboard is configured (tools.pipeboard.status: true in config):

**Before generating:** Suggest checking the account first. Explain the value briefly — don't assume the user knows what this does:
> "Your Meta ad account is connected. Want me to pull your live performance data first? I can see what's spending, which creative has the best CPA, and use that to inform what we create. (Takes ~30 seconds.)"

If user says yes, run Account Check component (see [references/pipeboard-integration.md](references/pipeboard-integration.md)):
- Pull active campaigns and top performers
- Surface winning patterns (angles, hooks, images with low CPA)
- Extract naming conventions so new ads match
- Show where new creative fits in existing structure

If user says no, proceed to generation with reference files only.

**After generating:** If Pipeboard is available, show account context:
> "Here's what's currently live. Your new creative could fit as [suggested placement]."

Account awareness is currently read-only. Write operations (duplicate + swap) are on the roadmap -- see [references/pipeboard-integration.md](references/pipeboard-integration.md).

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
| Ad Account Access | `.vip/config.yaml` → `tools.pipeboard.status` | Optional (enables live performance data) |

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
| Text Overlay | Background-only for text overlay (used with creative variation copy) |

**Format pair: 1:1 + 9:16** — Facebook Ads Manager accepts exactly these two formats per ad. Design 9:16 first with critical content in center 1:1 safe zone. Center-crop for square. One design → two uploads.

See [references/static-output-template.md](references/static-output-template.md) for full output format.
See [references/image-prompt-templates.md](references/image-prompt-templates.md) for template library.
See [references/image-generation-workflow.md](references/image-generation-workflow.md) for Nano Banana integration.

---

## Mode: Hook Library (Creative Variations)

Generate punchy, truly diversified creative variations for static image ads that feed Meta's Andromeda algorithm. Users can request any quantity -- "give me 5" or "give me 50" -- not fixed batches.

Also called "one-liners" -- same methodology, same pipeline. Both trigger words route here.

### Why This Mode Exists

Meta's Andromeda algorithm (July 2025) rewards TRUE creative diversification - not surface variations. Each creative variation is a different psychological conversation, anchored in offer-specific details.

### 6-Step Process

1. **Core Outcome:** Single transformation every buyer achieves
2. **Extract Specifics:** Roles, timelines, niche pains, value props, failed alternatives, proof points
3. **Reasons to Buy:** 15-20 fundamentally different reasons (the protein supplement exercise)
4. **Hook Categories:** Ensure variety across problem agitation, emotional state, transformation, contrarian, identity callout, etc.
5. **Generate:** 30 creative variations, each with at least one specific anchor
6. **Output:** Simple numbered list, ready to copy

### The Anchor Rule (Non-Negotiable)

Every variation **MUST** include at least one specific element:
- A specific role, outcome, or company (DevOps Engineer, AWS, 60k)
- A specific niche pain (service desk 2+ years, no CS degree)
- A specific value prop (mock interviews with Principal Engineers)
- A specific timeline or proof point (8 weeks, 500+ community)

**The Specificity Test:** If this variation could sell a gym membership, a life coaching program, or a generic course - it fails. Rewrite it.

### Input Modes

| Mode | How to Detect | What to Pull |
|------|---------------|--------------|
| **Has business repo** | Reference files exist | Resolved `offer.md`, resolved `audience.md`, `reference/core/voice.md`, testimonials |
| **No repo** | Nothing found | Ask user for materials |

### Output Format

**Save to file, not chat.** This enables review to edit the file directly.

1. Ask for campaign name (required)
2. Confirm quantity: "How many? A few to test (5-10) or a full batch (30+)?" -- or use the number they already specified
3. Create folder: `outputs/YYYY-MM-DD-creative-variations-[offer]-{campaign}/` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
4. Save full generation context + creative variations to: `creative-variations-batch-001.md`
5. Tell user: "Saved {N} creative variations. Running automatic post-generation pipeline..."
6. Run the **Automatic Post-Generation Pipeline** (see below). This handles git commit, compliance review, and image generation automatically.

**creative-variations-batch-001.md format:**

```markdown
---
type: output
subtype: creative-variations
date: YYYY-MM-DD
status: draft
review_status: null
---

# Creative Variations: {Campaign Name}

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

[Which categories each variation uses - for diversity check]

---

## Creative Variations

1. [variation]
2. [variation]
...
{N}. [variation]
```

**Why save the full context:**
- **Anchor verification:** Reviewers can check each variation has a specific from the extraction
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

**Every generation entry point (Full Pipeline, Copy Only, Hook Library, Video Scripts) runs this pipeline automatically after saving output.** Do not ask the user whether to run compliance review -- it is automatic.

See **[references/post-generation-pipeline.md](references/post-generation-pipeline.md)** for the complete pipeline: git commit pre-review, lens tier selection, Nano Banana check, parallel agent spawning (compliance + image), synthesis, unified report, and post-review commit.

**Quick summary:** Commit pre-review state, spawn 5-6 compliance agents + optional image agents in parallel, synthesize P1/P2/P3 findings, auto-apply P2/P3 fixes, surface P1 to user, present unified report, commit post-review.

**"While You Wait" pattern:** When spawning parallel agents that take >30 seconds, show a brief note so the user knows what's happening:
> "Running compliance review across 6 lenses + generating images in parallel. This takes about 2-3 minutes. These run as sub-agents so they won't eat into your session context."

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
| **Anchor specificity** | Every hook/variation has at least one offer-specific anchor |
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
2. **What entry point?** Full pipeline, copy only, hook library, video scripts, review, account check
3. **What stage?** Planning angles, writing hooks, generating prompts, reviewing, pulling account data
4. **What's done?** Check outputs/ folder for partial work
5. **Pipeboard status?** Read `.vip/config.yaml` for `tools.pipeboard.status`
6. **Resume:** Continue from the last completed step

For full pipeline: Did we finish image prompts (Part 1) before copy (Part 2)?
For hook library: How many variations generated out of requested quantity?
For video: How many of 15-30 scripts are done?
For review: Which lenses completed?

---

## Quick Reference

**Full pipeline (static ads):** 5-6 concepts x 5 primaries x 5 headlines x 3 image prompts
**Hook library (creative variations):** Flexible quantity (default 30), Andromeda-optimized
**Video scripts:** 15-30 diverse scripts, spoken-word optimized
**Review:** 6 lenses, P1/P2/P3 report, fix suggestions
**Account check:** Pipeboard read-only -- campaigns, performance, creative audit (requires Pipeboard)
