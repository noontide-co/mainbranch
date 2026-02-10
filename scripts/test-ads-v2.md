# /ads v2 Manual Smoke Tests

Integration testing checklist for flexible entry points, Pipeboard detection, and creative variations rename.

**How to run:** Type each prompt exactly as shown into Claude Code with a business repo loaded. Check expected behavior. Mark pass/fail.

**Pre-requisites:**
- Business repo with GREEN pre-flight (composite 12+)
- vip as additional working directory
- `.vip/config.yaml` accessible in business repo

---

## Group 1: Backward Compatibility

Old triggers must still route correctly. No regressions.

### 1.1 `/ads static`

**Prompt:** `/ads static`

**Expected:**
- Pre-flight runs (readiness score displayed)
- Pipeboard detection runs (lazy, first invocation)
- Routes to Full Pipeline (copy + images)
- Asks for campaign name
- Selects 5-6 angles from reference
- Generates image prompts (Part 1) then ad copy (Part 2)

**Pass:** Full Pipeline executes. Output saved to `outputs/YYYY-MM-DD-static-ads-{campaign}/`.

---

### 1.2 `/ads video scripts`

**Prompt:** `/ads video scripts`

**Expected:**
- Pre-flight runs
- Routes to Video Scripts mode
- Generates 15-30 spoken-word scripts
- Asks for campaign name
- Post-gen pipeline fires (commit + compliance, no image gen)

**Pass:** Video scripts saved to `outputs/YYYY-MM-DD-video-ads-{campaign}/`.

---

### 1.3 `/ads one-liners`

**Prompt:** `/ads one-liners`

**Expected:**
- Pre-flight runs
- Routes to Hook Library (creative variations)
- Asks for quantity ("How many? A few to test or a full batch?")
- Asks for campaign name
- Generates creative variations with anchor specificity
- Post-gen pipeline fires

**Pass:** Output saved to `outputs/YYYY-MM-DD-creative-variations-{campaign}/`. File named `creative-variations-batch-001.md`, NOT `one-liners-batch-001.md`.

---

### 1.4 `/ads review`

**Prompt:** `/ads review`

**Expected:**
- Skips pre-flight (review mode)
- Asks which batch/ads to review
- Spawns 6 parallel lens agents
- Returns P1/P2/P3 report

**Pass:** Review report generated with findings from all 6 lenses.

---

### 1.5 `/ads static community january-test`

**Prompt:** `/ads static community january-test`

**Expected:**
- Pre-flight runs against `offers/community/` context (multi-offer resolution)
- Routes to Full Pipeline
- Uses "community" as offer, "january-test" as campaign name (does NOT re-ask)
- Output path includes offer slug: `outputs/YYYY-MM-DD-static-ads-community-january-test/`

**Pass:** Offer resolved to community. Campaign name accepted from arguments. Output path correct.

---

## Group 2: New Entry Points

Natural language intent detection. No slash-command required.

### 2.1 Copy Only

**Prompt:** `I already have images, just need copy`

**Expected:**
- Intent detected: Copy Only
- Pre-flight runs
- Skips image generation entirely
- Generates primaries + headlines only
- Asks for campaign name
- Post-gen pipeline fires (commit + compliance, no image gen)

**Pass:** No image prompts in output. Copy saved to `outputs/YYYY-MM-DD-static-ads-{campaign}/`.

---

### 2.2 Image Only

**Prompt:** `just need images for my existing copy`

**Expected:**
- Intent detected: Image Only
- Lite pre-flight runs
- Checks Nano Banana availability (GOOGLE_API_KEY)
- Generates image prompts only (no copy)
- If Nano Banana available, generates images

**Pass:** Image prompts generated. No ad copy in output.

---

### 2.3 Creative Variations (quantity specified)

**Prompt:** `give me 10 creative variations`

**Expected:**
- Intent detected: Hook Library
- Pre-flight runs
- Quantity set to 10 (does NOT ask for quantity -- user specified)
- Asks for campaign name
- Runs 6-step process (core outcome, extract specifics, reasons to buy, hook categories, generate, output)
- Post-gen pipeline fires

**Pass:** Exactly 10 variations saved. Output file is `creative-variations-batch-001.md`.

---

### 2.4 Ideation

**Prompt:** `I want to brainstorm some ad ideas`

**Expected:**
- Intent detected: Ideation
- Lite pre-flight
- If Pipeboard configured: offers account check first
- Generates ad concepts (not full copy)
- No post-gen pipeline (ideation is lightweight)

**Pass:** Concepts presented. No full batch generated. No compliance review triggered.

---

### 2.5 Video Repurpose

**Prompt:** `I shot a video and want to turn it into ads`

**Expected:**
- Intent detected: Video Repurpose
- Pre-flight runs
- Asks for video file or transcript
- Extracts hooks from transcript
- Generates copy variants from video content
- Post-gen pipeline fires

**Pass:** Routes to Video Repurpose, not Video Scripts. Asks for video/transcript input.

---

### 2.6 Ambiguous Intent

**Prompt:** `help me with ads`

**Expected:**
- Intent unclear
- Asks clarifying question: "What do you have and what do you need?" (or similar)
- Does NOT assume a mode
- Does NOT start generating

**Pass:** Clarifying question asked. No generation started.

---

## Group 3: No Pipeboard (Graceful Degradation)

Pipeboard not configured. Skill works fully without it.

### 3.1 Standard Flow Without Pipeboard

**Setup:** Remove `tools.pipeboard` from `.vip/config.yaml` (or ensure it doesn't exist).

**Prompt:** `/ads static`

**Expected:**
- Pre-flight runs
- Pipeboard detection runs: checks config, finds nothing, probes for `mcp__pipeboard__*` tools, finds none
- Writes `status: false` to `.vip/config.yaml` under `tools.pipeboard`
- Does NOT offer "check what's working" prompt
- Proceeds directly to Full Pipeline generation
- No error messages about Pipeboard

**Pass:** Full Pipeline executes without interruption. Config updated with `status: false` and `last_checked` date.

---

### 3.2 Account Check Without Pipeboard

**Setup:** Pipeboard not configured or `status: false`.

**Prompt:** `check my ad performance`

**Expected:**
- Intent detected: Account Check
- Pipeboard required but missing
- Shows message: "This needs ad account access." Offers setup guidance or skip option.
- Does NOT crash or throw unhandled error

**Pass:** Clear message about missing Pipeboard. Offers alternative path.

---

### 3.3 Config Persists After Failed Detection

**Setup:** Remove `tools.pipeboard` from config. Run `/ads static` once (triggers detection, writes `status: false`).

**Verification:** Read `.vip/config.yaml`.

**Expected:**
```yaml
tools:
  pipeboard:
    status: false
    last_checked: 2026-02-10  # today's date
```

**Pass:** Config contains `status: false` with today's date.

---

### 3.4 Second Invocation Skips Re-Detection

**Setup:** Config already has `status: false` and `last_checked` within 30 days.

**Prompt:** `/ads static`

**Expected:**
- Reads config, finds `status: false` with recent `last_checked`
- Skips detection entirely (no tool probing)
- Proceeds directly to pre-flight and generation
- Faster startup than first invocation

**Pass:** No detection probe. Proceeds immediately.

---

## Group 4: With Pipeboard

Pipeboard MCP configured and responding.

### 4.1 Fresh Detection with MCP Available

**Setup:** Remove `tools.pipeboard` from config. Pipeboard MCP is configured in session.

**Prompt:** `/ads static`

**Expected:**
- Reads config, finds no Pipeboard entry
- Checks for `mcp__pipeboard__*` tools in session -- finds them
- Probes with `get_ad_accounts` (lightweight)
- Probe succeeds: writes `status: true` to config
- Offers: "Want me to check what's working in your ad account before we create?"

**Pass:** Detection succeeds. Config updated with `status: true`. Proactive suggestion offered.

---

### 4.2 Account Check

**Prompt:** `what's working in my account?`

**Expected:**
- Intent detected: Account Check
- Pipeboard `status: true` in config
- Runs Account Overview pattern (2-3 calls): `get_campaigns`, `get_insights`
- Surfaces active campaigns, spend, CPA/ROAS
- Presents results in readable format
- Does NOT start generating ads

**Pass:** Account data displayed. No generation triggered.

---

### 4.3 Proactive Suggestion (Accept)

**Setup:** Pipeboard configured, `status: true`.

**Prompt:** `/ads static`

**Expected:**
- Pre-flight runs
- Before generation, suggests: "Want me to check what's working in your ad account before we create?"

**Follow-up:** `yes`

**Expected:**
- Runs Creative Audit pattern (5-8 calls)
- Surfaces winning patterns, angles, hooks, naming conventions
- Then proceeds to Full Pipeline generation informed by account data

**Pass:** Account check runs first. Generation follows with account context.

---

### 4.4 Proactive Suggestion (Decline)

**Setup:** Pipeboard configured, `status: true`.

**Prompt:** `/ads static`

**Expected:**
- Pre-flight runs
- Suggests account check

**Follow-up:** `no, just generate`

**Expected:**
- Skips account check entirely
- Proceeds to Full Pipeline from reference files only
- Does NOT re-suggest account check during this pipeline

**Pass:** No account check. Generation proceeds from reference only. No repeated suggestions.

---

## Group 5: Edge Cases

### 5.1 Empty /ads With No Follow-Up

**Prompt:** `/ads`

**Expected:**
- Pre-flight runs
- Intent unclear (no mode specified)
- Asks: "What do you have and what do you need?" (or similar clarifying question)
- Waits for response

**Pass:** Does not default to any mode. Asks for clarification.

---

### 5.2 Contradictory Signals

**Prompt:** `I need video scripts but also static image prompts`

**Expected:**
- Detects conflicting intent
- Asks for clarification: which to do first, or whether to do both sequentially
- Does NOT merge modes into a hybrid pipeline

**Pass:** Clarification requested. Does not crash or silently pick one mode.

---

### 5.3 Mode Switch Mid-Flow

**Setup:** Start with `/ads static`, get past pre-flight.

**Prompt (mid-flow):** `actually, let's do creative variations instead`

**Expected:**
- Acknowledges change: "No problem. What would you like instead?" or similar
- Re-detects intent: Hook Library
- Asks for quantity
- Does NOT continue static pipeline

**Pass:** Graceful switch. No partial static output mixed with hook library.

---

### 5.4 Legacy Phrasing With Quantity

**Prompt:** `30 one-liners`

**Expected:**
- Intent detected: Hook Library (creative variations)
- Quantity detected: 30 (does NOT re-ask)
- Pre-flight runs
- Asks for campaign name
- Generates 30 creative variations

**Pass:** Routes to Hook Library. Quantity 30 accepted. Output file is `creative-variations-batch-001.md`.

---

## Group 6: Post-Generation Pipeline

### 6.1 Pipeline After Static Ads

**Setup:** Complete a static ads generation (Group 1.1).

**Expected (automatic after save):**
- Message: "Running compliance review across 6 lenses + generating images in parallel..."
- Git commit pre-review: `[output] static ads batch pre-review`
- 6 compliance agents spawn in parallel
- If Nano Banana available: image generation agents spawn in parallel
- P1/P2/P3 findings synthesized
- P2/P3 auto-applied to batch file
- P1 surfaced to user
- Unified report presented
- Git commit post-review: `[review] static ads batch - N fixes applied`

**Pass:** Both git commits exist. Compliance report shown. P2/P3 fixes applied to file.

---

### 6.2 Pipeline After Hook Library

**Setup:** Complete a hook library generation (Group 2.3).

**Expected (automatic after save):**
- Message about running compliance review
- Git commit pre-review: `[output] creative variations batch pre-review`
- Compliance agents spawn (may be fewer lenses -- visual standards less relevant for text-only)
- Findings synthesized
- Post-review commit

**Pass:** Git commits exist. Compliance review ran on creative variations.

---

### 6.3 Git Commit Format

**Verification:** After any generation + pipeline, check git log.

**Expected commit messages:**
- Pre-review: `[output] {type} batch pre-review`
- Post-review: `[review] {type} batch - N fixes applied`

Where `{type}` is one of: `static ads`, `creative variations`, `video ads`, `video repurpose`.

**Pass:** Commit messages follow `[type] description` convention. No default "Update files" messages.

---

## Results Tracking

| # | Test | Pass | Fail | Notes |
|---|------|------|------|-------|
| 1.1 | `/ads static` | | | |
| 1.2 | `/ads video scripts` | | | |
| 1.3 | `/ads one-liners` | | | |
| 1.4 | `/ads review` | | | |
| 1.5 | `/ads static community january-test` | | | |
| 2.1 | Copy Only | | | |
| 2.2 | Image Only | | | |
| 2.3 | Creative Variations (qty) | | | |
| 2.4 | Ideation | | | |
| 2.5 | Video Repurpose | | | |
| 2.6 | Ambiguous Intent | | | |
| 3.1 | No Pipeboard standard flow | | | |
| 3.2 | Account Check without Pipeboard | | | |
| 3.3 | Config persists after failed detection | | | |
| 3.4 | Second invocation skips detection | | | |
| 4.1 | Fresh detection with MCP | | | |
| 4.2 | Account Check with Pipeboard | | | |
| 4.3 | Proactive suggestion (accept) | | | |
| 4.4 | Proactive suggestion (decline) | | | |
| 5.1 | Empty `/ads` | | | |
| 5.2 | Contradictory signals | | | |
| 5.3 | Mode switch mid-flow | | | |
| 5.4 | Legacy phrasing with quantity | | | |
| 6.1 | Pipeline after static ads | | | |
| 6.2 | Pipeline after hook library | | | |
| 6.3 | Git commit format | | | |
