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

**CWD-first:** If `reference/core/` exists in CWD, you're already in the business repo — use it.

If CWD is NOT a business repo:

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
reference/visual-identity/visual-style.md → same scoring (optional)
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
3. If status: false AND last_checked is valid and <30 days old → skip
4. If status: null OR missing OR stale false:
   a. Check for mcp__pipeboard__* tools in session
   b. If found: probe with get_ad_accounts (lightweight)
   c. If probe succeeds: write status: true to config
   d. If not found or probe fails: write status: false to config
5. Never block on detection failure
```

`stale false` means: `status: false` and `last_checked` is missing, invalid, or >=30 days old.

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
| Visual Style | `reference/visual-identity/visual-style.md` | Optional (affects image gen) |
| Content Strategy | `reference/domain/content-strategy.md` (always brand-level) | Optional (improves topic selection) |
| Skool Surfaces | `reference/domain/funnel/skool-surfaces.md` | Optional (congruence check) |
| Ad Account Access | `.vip/config.yaml` → `tools.pipeboard.status` | Optional (enables live performance data) |

If required files are missing, Step 0 pre-flight catches this and routes appropriately.

**Content funnel awareness:** Ads are the "immediate ROI" pillar of the two-pillar value prop (ads + content). In the content pipeline, ads drive newsletter signups, newsletter nurtures, Skool trial converts, revenue follows. If `content-strategy.md` exists, use content pillars to inform angle selection, metrics to understand what performs organically (ads amplify top-performing organic content), and funnel mapping to determine whether ads should target awareness, consideration, or conversion.

**Skool surface congruence:** If `reference/domain/funnel/skool-surfaces.md` exists, check it before finalizing any batch. Ad copy must not promise anything not visible on the Skool about page or pricing cards. Pricing mentioned in ads must match current tier structure. Language and framing should echo (not contradict) the about page positioning. The about page is the FIXED surface — ads are the VARIABLE surface.

**Angle library note:** Angles are NOT locked. They evolve as understanding deepens. Every `/think` session may surface new angles. The angle library is additive — new angles supplement, never replace. When selecting angles for a batch, mix established angles with any newly codified ones.

---

## Mode: Static Ads

Create campaign batches with image prompts + ad copy. Each batch = 5-6 angles, each angle = 3 image creatives (graphic, lo-fi, interrupt). Hook = 123-135 chars, no questions, no "you/your" in first 3 lines, no emojis. 5 ad styles (Deep, UGC, DR, Pattern Interrupt, Testimonial). Format pair: 1:1 + 9:16.

See **[references/mode-static-ads.md](references/mode-static-ads.md)** for the full workflow: campaign structure, hook formulas, copywriting batch sequence, ad styles by length, image prompt types, and the file save convention.

---

## Mode: Hook Library (Creative Variations)

Generate punchy, truly diversified creative variations for static image ads (Andromeda-optimized). Users can request any quantity. Also called "one-liners" — same methodology, same pipeline.

**The core rule:** Every variation must include at least one specific anchor (role, niche pain, value prop, or proof point). The Specificity Test: if it could sell a gym membership, it fails.

See **[references/mode-hook-library.md](references/mode-hook-library.md)** for the full 6-step process, anchor rule, input modes, output file format with full generation context, and links to one-liner-methodology.md / one-liner-examples.md.

---

## Mode: Video Scripts

Create diverse spoken-word scripts for camera delivery. 15-30 scripts across 3-4 buyer avatars, ~5th grade reading level, contractions, fragments. Each ad = a fundamentally different reason to buy.

See **[references/mode-video-scripts.md](references/mode-video-scripts.md)** for the 6-step process, script structure (Hook / Body / CTA), spoken delivery optimization, and save convention.

---

## Mode: Review

Review ads through 6 compliance and quality lenses before shipping (FTC, Meta Policy, Copy Quality, Visual Standards, Voice Authenticity, Substantiation). Spawns 6 parallel Task agents (read-only), synthesizes a unified P1/P2/P3 report, applies P2/P3 fixes, asks before committing.

See **[references/mode-review.md](references/mode-review.md)** for the full lens table, review process, severity levels, and status determination.

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
| **Save-ability** | Would someone save this ad to reference later? Educational, actionable hooks drive purchase intent |
| **Enemy framing** | Does at least one concept use a named enemy from voice.md? Enemy-driven contrast creates identity alignment |

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
