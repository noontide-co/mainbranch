---
name: mb-ads
description: "Create and review ads, and prepare provider-safe launch plans/checks. Flexible entry points: full pipeline (copy + images), copy only, images only, creative variations (hook library), video scripts, video repurpose, compliance review, launch-plan, check, or optional Meta ad account check. Use when asked to create ads, ad copy, image prompts, video scripts, creative variations, review ads, plan paid traffic, or check launch performance. Say /mb-ads or describe what you need."
loops: [ship, reflect]
---

# Ads Skill

Create ads, generate creative variations, review for compliance, and check ad account performance.

## Output destinations and operator vocabulary

This skill writes new coordinated work to `pushes/<YYYY-MM-DD-slug>/` (the
canonical engine primitive). Examples below say "push" for the wrapping
record; this is the engine's word. If `core/vocabulary.md` defines a
display word — for example `terms.push.singular: drop` — speak the
operator's word ("drop") in conversation while still writing canonical
files (`pushes/...`, `type: push`, `linked_pushes`). Never rename folders,
frontmatter, link fields, JSON keys, or commands based on vocabulary.

If the repo still has legacy `campaigns/` records, preview the migration
**before** creating new push work:

```text
mb doctor                       # confirms legacy campaigns/ drift
mb migrate campaigns --plan     # read-only preview of moves
```

The word "campaign" elsewhere in this skill refers to Meta Ads campaigns
(the provider's term for its object) — not the Main Branch primitive.

When creating `push.md`, include the validator-required frontmatter and fill
the values from repo truth or operator answers:

```yaml
---
type: push
slug: YYYY-MM-DD-slug
kind: launch
status: planned
health: unknown
goal: { metric: "", target: "", by: YYYY-MM-DD }
owner: ""
audience: ""
offer: core/offers/<offer>/offer.md
promise: ""
---
```

If the push is tied to a bet, decision, research file, playbook, or outcome,
add the appropriate typed frontmatter link (`linked_bets`,
`linked_decisions`, `linked_research`, `linked_playbooks`,
`linked_outcomes`). Mirror frontmatter links in `## Related links` with
Markdown relative links, or preview `mb doctor repair --plan` and ask before
applying the repair. Do not infer frontmatter links from body-only references.

When an ad-adjacent workflow needs a resource-delivery plan, provider setup
recipe, launch checklist, or external automation approval record, draft it as
`pushes/<YYYY-MM-DD-slug>/playbooks/<playbook>.md` with `type: playbook`.
Treat playbooks as plans and approval records only. Do not publish, schedule,
DM, reply, mutate ad accounts, or claim a provider is supported unless `mb`
and a shipped provider adapter prove that path with docs, tests, approval
gates, and smoke evidence.

## Step 0: Pre-Flight Readiness

**Before triage, find the business repo, read deterministic Main Branch facts,
then score ad-specific reference depth only when needed.** This prevents
generating generic ads from thin reference without duplicating repo-health or
provider checks that `mb` already owns.

### 0a. Find Business Repo (REQUIRED — do this first)

**NEVER search the filesystem. NEVER use Explore or Task agents to find repos. NEVER scan ~/Documents/GitHub/.**

**CWD-first:** If `core/` or legacy `reference/core/` exists in CWD, you're already in the business repo — use it.

If CWD is NOT a business repo:

Run:

```bash
mb status --json --peek
```

- If status identifies a usable business repo, ask the user to confirm it.
- If status cannot identify a repo, ask: "Which business repo should I use?
  Give me the path."
- If `/mb-ads` was invoked from `/mb-start`, the repo is already identified —
  use it without asking.

**Always confirm the repo before proceeding.** Never assume.

After the repo is confirmed, run `mb status --json --peek` from that repo. Use
`readiness`, `drift.items`, `integrations`, `measurement`, and `ranked_actions`
as the source of truth for setup, stale context, GitHub, provider readiness, and
repair commands. Only run the direct scoring below for ad-specific creative
depth when status is unavailable or lacks the needed ad-specific detail.

### 0b. Score Reference Files (fast — direct Read only, NO agents)

**NEVER spawn Explore or Task agents for pre-flight.** Read files directly at the known repo path. Pre-flight should complete in under 10 seconds.

At the repo path, resolve offer context first with
`.claude/reference/business-primitives/offer-bet-push-proof.md`, then check
these files and count lines:

```
[resolved offer.md]          → 0 (missing), 1 (<20 lines), 2 (20-80), 3 (80+)
[resolved audience.md]       → same scoring
core/voice.md                → same scoring
core/proof/testimonials.md → same scoring
core/proof/angles/*.md  → count .md files EXCLUDING README.md: 0=0, 1=1, 2-3=2, 4+=3
core/brand/visual-style.md → same scoring (optional)
```

In multi-offer mode, score the offer-specific `offer.md` and `audience.md` (resolved via path resolution), not the brand-level `core/offer.md`.

Composite = sum of all 6 scores (max 18).

### 0c. Route on Score

| Composite | Status | Action |
|-----------|--------|--------|
| **12-18** | GREEN | Proceed to triage |
| **8-11** | YELLOW | Warn user, show gaps, allow override |
| **4-7** | RED | Route to `/mb-think` with enrichment targets |
| **0-3** | BLOCKED | Route to `/mb-setup` |

Display the readiness report, then proceed. See [references/preflight-algorithm.md](references/preflight-algorithm.md) for gap guidance and smart mix recommendations.

### 0d. Check Image Generation Readiness

```bash
mb connect doctor --json
```

Use status/connect facts first for Google/Workspace readiness. Only check local
environment variables when image generation is actually selected and the CLI
does not report that capability. Never ask the operator to paste API keys into
chat or public issue text.

### 0e. Paid-Traffic Measurement Gate

If this ad work is for Google Ads, paid traffic to a site/minisite/lander, retargeting, or any request that asks whether a campaign is ready to launch, check measurement readiness before saying "launch."

1. Load `docs/google-ads-gtm-conversion-rubric.md`.
2. Run `mb connect plan` or `mb connect doctor --json` from the business repo when provider readiness matters.
3. If a site repo is known, run:

```bash
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
```

Use the returned `state`:

- `blocked`: do not recommend launch; list the blocked checks and exact next command/manual step.
- `ready_for_preview`: ads can be drafted, but traffic should not launch; tell the operator to run GTM Preview/Tag Assistant and finish provider metadata/approvals.
- `ready_for_operator_review`: ads can be prepared for review, but launch still needs explicit operator approval for GTM publication, conversion actions, consent posture, budget, billing, and spend.
- `ready`: local readiness checks passed, but do not mutate accounts or launch campaigns.

Do not invent `ready_for_launch` or treat `ready` as campaign launch permission. Main Branch can prepare and review; the operator launches manually.

Never ask the operator to paste Google Ads/GTM tokens, OAuth secrets, conversion uploads, or customer data into chat. Quote `mb connect` repair commands instead.

---

## Meta Ad Account Readiness (Lazy)

Check Meta ad account access only when the user's request needs live ad account
context. Do not duplicate provider setup or health checks in prose.

### Readiness Flow

```
1. Read `mb status --json --peek` → integrations/providers/measurement facts.
2. If the operator needs setup choices, run `mb connect plan`.
3. If something looks broken, run `mb connect doctor --json`.
4. Only after `mb` says Meta Ads account context is ready or repairable, check
   whether the current Claude Code session exposes the required read-only MCP
   tools.
5. Never block generation on missing ad account access.
```

**Graceful degradation:** If Meta Ads account context is not ready, skip all
account-related features. The skill works fully from repo reference files.

### User-Facing Display

In user-facing messages, describe the capability: connecting a Meta ad account,
pulling live performance, or auditing active campaigns. Do not mention connector
vendor names or unsupported setup paths.

**Pre-flight status line (add after Nano Banana check):**

If ready:
> `Ad account:   ✓ connected (I can check what's performing before we create)`

If not ready:
> `Ad account:   — not connected (optional — lets me see your live Meta ad performance to inform new ads)`

**Never say:** "provider tool not configured" or name an implementation detail
the user does not need. Keep the status line capability-first.

**If user asks what this means:**
> "You can optionally connect your Meta/Facebook ad account so I can pull live performance data — what's spending, what's winning, CPAs, creative that's working. This helps me create ads that fit your account structure and build on what's already performing. Want to run `mb connect plan`, or skip and work from your reference files?"

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
| "research winning ads", "mine reviews", "analyze competitors first" | Research / Mining | Route to `/mb-think` winning-ad research before generation |
| "launch ads", "paid traffic plan", "Google Ads launch", "$X/day for Y days" | Launch Plan | Provider-safe plan/check mode, no account mutation |
| "check launch", "how are ads doing", "continue or kill" | Launch Check | Read status/outcomes/operator exports, recommend continue/change/stop |
| "Check my ad performance", "what's working" | Account Check | Read-only Meta Ads context if `mb connect` and runtime tools are ready |
| "Give me 5 variations of this winning ad" | Performance Iteration | Pull winner + generate variants if account context is ready |
| "What's working before we create?" | Pre-Gen Account Check | Account overview + creative audit if account context is ready |
| "review", "audit", "compliance check" | Review | 6-lens compliance review |

**Also accepts:** "static", "static ads", "video", "video scripts", "one-liners", "review" -- these route to the same pipelines.

**If unclear,** ask: "What do you have and what do you need? (e.g., 'I have images, just need copy' or 'full from scratch')"

**If research/mining is requested before generation:** Route to `/mb-think` and
load `mb-think/references/winning-ad-research.md`. Customer language, review
mining, competitor gap maps, comment mining, and winning script teardown should
save to `research/` and codify into `core/` before this skill generates ads.
Do not paste raw review/comment dumps or copied prompt libraries into ad output.
If the selected research file has `brief_format: grok-8`, use its downstream
handoff first: business/offering for the promise, ICP for hooks, journey for
funnel stage, competitive landscape for differentiation, brand story for voice,
content/assets for proof and creative inputs, and metrics/constraints for the
review bar. If the brief names a resource-delivery or provider workflow, draft
or update a push playbook as a plan only; do not execute provider mutation.

**If launch/check is requested for paid traffic:** Load
[references/launch-plan-check.md](references/launch-plan-check.md). Prepare
campaign materials, policy findings, measurement readiness, manual provider
steps, and approval records; do not mutate ad accounts or start spend.

### Proactive Account Awareness

If `mb status --json --peek` / `mb connect doctor --json` reports Meta Ads
ready and the current runtime exposes the read-only ad account tools:

**Before generating:** Suggest checking the account first. Explain the value briefly — don't assume the user knows what this does:
> "Your Meta ad account is connected. Want me to pull your live performance data first? I can see what's spending, which creative has the best CPA, and use that to inform what we create. (Takes ~30 seconds.)"

If user says yes, run Account Check component (see [references/meta-ads-integration.md](references/meta-ads-integration.md)):
- Pull active campaigns and top performers
- Surface winning patterns (angles, hooks, images with low CPA)
- Extract naming conventions so new ads match
- Show where new creative fits in existing structure

If user says no, proceed to generation with reference files only.

**After generating:** If Meta Ads account context is available, show account context:
> "Here's what's currently live. Your new creative could fit as [suggested placement]."

Account awareness is currently read-only. Write operations are on the roadmap
and require explicit operator approval gates -- see
[references/meta-ads-integration.md](references/meta-ads-integration.md).

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

Before loading reference files, resolve active offer context with
`.claude/reference/business-primitives/offer-bet-push-proof.md`:

1. If a future `mb` JSON field exposes active offer state, use it.
2. Do not treat `.vip/local.yaml` as canonical active-offer state. If legacy
   state exists, confirm the offer with the user instead of silently routing.
3. If an offer is selected and `core/offers/[offer]/offer.md` exists, load it as the active offer.
4. If no offer is selected AND `core/offers/` exists: ask which offer.
5. If no `core/offers/` folder: use `core/offer.md` (single-offer mode)
6. Legacy fallback: if the repo does not have `core/`, read the old
   `reference/core/` and `reference/offers/` paths.

In current repos, `reference/core` and `reference/offers` are compatibility
bridges to `core/` and `core/offers/`. Treat them as aliases, not duplicate
files: read through them only as fallback, and never ask the user to update both
paths.

**Always-core files:** `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files:** `offer.md`, `audience.md`
**Proof files:** company-wide proof in `core/proof/testimonials.md`,
`core/proof/typicality.md`, and `core/proof/angles/`; offer-specific proof in
matching files under `core/offers/[active]/proof/`. Read older offer
testimonial files as compatibility context only.

**Offer argument:** `/mb-ads [mode] [offer] [campaign]` — e.g., `/mb-ads static community january-launch`
If offer specified, it selects the offer for this run only.

---

## Reference Required (All Modes)

Before creating ads, the business repo must have:

| File | Path | Required |
|------|------|----------|
| Offer | `core/offers/[active]/offer.md` or `core/offer.md` (resolved via path resolution) | Yes |
| Audience | `core/offers/[active]/audience.md` or `core/audience.md` (resolved via path resolution) | Yes |
| Voice | `core/voice.md` (always core) | Yes |
| Testimonials/proof | `core/proof/testimonials.md` + `core/offers/[active]/proof/testimonials.md` when present | Yes |
| Typicality | `core/proof/typicality.md` + offer-specific typicality when present | Recommended |
| Angles | `core/proof/angles/*.md` | Yes (at least 1) |
| Visual Style | `core/brand/visual-style.md` | Optional (affects image gen) |
| Content Strategy | `core/content-strategy.md` (always brand-level) | Optional (improves topic selection) |
| Skool Surfaces | `core/operations/funnel/skool-surfaces.md` | Optional (congruence check) |
| Ad Account Access | `mb status --json --peek` + `mb connect doctor --json` | Optional (enables live performance data) |

If required files are missing, Step 0 pre-flight catches this and routes appropriately.

**Content funnel awareness:** Ads are the "immediate ROI" pillar of the two-pillar value prop (ads + content). In the content pipeline, ads drive newsletter signups, newsletter nurtures, Skool trial converts, revenue follows. If `content-strategy.md` exists, use content pillars to inform angle selection, metrics to understand what performs organically (ads amplify top-performing organic content), and funnel mapping to determine whether ads should target awareness, consideration, or conversion.

**Skool surface congruence:** If `core/operations/funnel/skool-surfaces.md` exists, check it before finalizing any batch. Ad copy must not promise anything not visible on the Skool about page or pricing cards. Pricing mentioned in ads must match current tier structure. Language and framing should echo (not contradict) the about page positioning. The about page is the FIXED surface — ads are the VARIABLE surface.

**Angle library note:** Angles are NOT locked. They evolve as understanding deepens. Every `/mb-think` session may surface new angles. The angle library is additive — new angles supplement, never replace. When selecting angles for a batch, mix established angles with any newly codified ones.

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

Review ads through 6 compliance and quality lenses before shipping (FTC, Meta Policy, Copy Quality, Visual Standards, Voice Authenticity, Substantiation). Spawns 6 parallel Task agents (read-only), synthesizes a unified P1/P2/P3 report, presents proposed P2/P3 copy changes as a diff, and applies them only after explicit approval.

See **[references/mode-review.md](references/mode-review.md)** for the full lens table, review process, severity levels, and status determination.

---

## Automatic Post-Generation Pipeline

**Every generation entry point (Full Pipeline, Copy Only, Hook Library, Video Scripts) runs this pipeline automatically after saving output.** Do not ask the user whether to run compliance review -- it is automatic.

See **[references/post-generation-pipeline.md](references/post-generation-pipeline.md)** for the complete pipeline: checkpoint pre-review, lens tier selection, Nano Banana check, parallel agent spawning (compliance + image), synthesis, proposed-change approval gate, unified report, and post-review checkpoint.

**Quick summary:** Save a checkpoint for the pre-review state after operator approval, spawn 5-6 compliance agents + optional image agents in parallel, synthesize P1/P2/P3 findings, surface P1 to user, show proposed P2/P3 copy edits as a dry-run diff, apply copy edits only after explicit approval, present unified report, and offer a post-review checkpoint.

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

1. **Which offer?** Use a future `mb` JSON active-offer field if present; otherwise ask the user to restore offer context. Do not silently route from `.vip/local.yaml`.
2. **What entry point?** Full pipeline, copy only, hook library, video scripts, review, account check
3. **What stage?** Planning angles, writing hooks, generating prompts, reviewing, pulling account data
4. **What's done?** Check `pushes/` (and legacy `campaigns/` on unmigrated repos) for partial work
5. **Ad account status?** Re-run `mb status --json --peek`; if needed, run `mb connect doctor --json`
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
**Account check:** read-only Meta Ads context -- campaigns, performance, creative audit when `mb connect` and runtime tools are ready
**Launch plan/check:** provider-safe Google Ads/GTM/paid-traffic plan or outcome check; no account mutation without a shipped adapter and explicit approval
