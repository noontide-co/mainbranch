---
name: mb-start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens Main Branch without a task, or needs triage. Routes to /mb-setup, /mb-think, /mb-bet, /mb-ads, /mb-vsl, /mb-organic, /mb-wiki, /mb-help."
loops: [sense, decide]
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Start Claude in your business repo, run `/mb-start`. It handles everything. Main Branch is loaded through `additionalDirectories`, with bridge links as a compatibility fallback for skill discovery.

**Status facts first:** Once the business repo path is known, run
`mb status --json --peek` before asking setup or routing questions. Treat that
JSON as the source of truth for update severity, readiness, drift, onboarding,
integrations, GitHub tasks/proposals, bets, dirty git, since-last-check, and
`ranked_actions`. Do not duplicate those checks with ad hoc shell probes unless
the status report says a section is unavailable.

**Continuity facts:** Use `since_last_check`, dirty-git, and recent GitHub/git
activity from status to explain "where we left off." The checkpoint CLI is
future v0.3.x work; do not ask current PyPI users to run it.

**Provider facts first:** When setup or routing depends on GitHub, Cloudflare,
Google/Workspace, Meta Ads, or Apify, read the status `integrations` facts
first. If the operator needs a provider choice or repair explanation, run
`mb connect plan` or `mb connect doctor --json` and use the cited
`next_command` / `repair_command`. Do not ask for tokens or provider setup in
prose before the CLI has named the missing step.

**Paid-traffic facts first:** When routing a paid-traffic minisite, Google Ads,
GTM, retargeting, or "ready to launch" request, load
`docs/google-ads-gtm-conversion-rubric.md`. If a site repo is known, run
`mb site check "$SITE_REPO" --business-repo "$REPO_PATH" --json` before routing
to `/mb-site` or `/mb-ads` launch advice. Treat `blocked` as stop, `ready_for_preview`
as preview-only, and `ready_for_operator_review` as manual review before
launch. Do not publish GTM, mutate Google Ads, upload conversions, or ask for
tokens in prose. Do not invent `ready_for_launch`; the valid readiness states
are `missing`, `blocked`, `ready_for_preview`, `ready_for_operator_review`, and
`ready`.

---

## CRITICAL: Repo Selection Rules

**CWD-first wins.** If `core/` or legacy `reference/core/` exists in CWD, the user is already in their business repo — no selection needed. Just confirm: "Working in **[repo-name]**."

**Only ask which repo when CWD is NOT a business repo** (fallback to config). In that case, list ALL validated repos from `recent_repos`:

> "Found your repos:
>
> 1. [default-repo-name] (saved default)
> 2. [other-repo-name]
> 3. Switch to different repo
>
> (hit a number)"

**If only one repo in config:**

> "Found your saved repo:
>
> 1. [saved-repo-name] (saved)
> 2. Switch to different repo
>
> (hit a number)"

**DO NOT skip this question when in fallback mode.** Users have multiple repos. The saved default is a suggestion, not automatic.

**Exceptions (skip selection entirely):**
- CWD has `core/` or legacy `reference/core/` — user chose their repo by cd'ing into it
- User explicitly ran `/mb-start [repo-name]` with a specific path

**After user selects a repo:** If the selected repo is not the current `default_repo`, ask: "Want me to save [repo-name] as your default? (faster startup next time)" If yes, update `default_repo` in `~/.config/vip/local.yaml`.

---

## Numbered Options Pattern

Always use numbered lists for multi-choice. User replies with just a number.

Apply to: business repo selection, skill routing, any multiple choice.

---

## Detection Flow

```
/mb-start [optional: repo-name] [optional: offer-name]
│
├── Check context level ──────────────→ Fresh? Full load. Heavy? Warn user.
│
├── Detect business repo ─────────────→ CWD-first detection (see Step 2)
│   ├── CWD has core/ or legacy reference/core/? → This IS the repo. Proceed.
│   ├── CWD has .claude/skills/? ─────→ User is in the engine repo (old workflow). Trigger migration.
│   └── Neither? ────────────────────→ Check config, then ask user.
│
├── Read status facts ────────────────→ `mb status --json --peek`
│   ├── ranked_actions? ──────────────→ show top recommendation before menu
│   ├── readiness/drift blockers? ────→ use cited status repair commands
│   └── unavailable section? ─────────→ use only the documented fallback for that section
│
├── Check engine updates ──────────────→ Use status update severity and `mb update`
│
├── Load config ──────────────────────→ See [config-system.md](references/config-system.md)
│   ├── ~/.config/vip/local.yaml ─────→ legacy engine path + default_repo + user identity
│   └── [repo]/.vip/config.yaml ──────→ Team settings, MCP requirements
│
├── Verify Main Branch loaded ────────→ Use status runtime.skill_wiring facts
│   └── Missing? ────────────────────→ Run the repair command cited by status
│
├── MCP pre-flight ───────────────────→ See [mcp-preflight.md](references/mcp-preflight.md)
│   └── Provider/tool missing? ───────→ Use `mb connect plan` / status repair facts
│
├── No business repo found? ──────────→ /mb-setup (creates repo, saves path)
│
├── Pull business repo updates ───────→ (your repo, silently)
│
├── Onboarding progress check ────────→ Use status onboarding facts
│   ├── missing core reference? ──────→ collect only current missing inputs
│   └── complete? ───────────────────→ continue to readiness/menu
│
├── Offer detection ──────────────────→ (multi-offer only, see Step 8)
│   ├── offers/ exists? ─────────────→ Prompt or restore from .vip/local.yaml
│   └── no offers/ ──────────────────→ Single-offer mode, skip
│
├── Has repo but thin? ───────────────→ /mb-think codify
│   (reference files exist but incomplete)
│
├── Present menu ────────────────────→ status readiness gates which options show
│   (option 1 = triage, recommended)
│
├── User picks option 1? ───────────→ Spawn triage agents (see triage-agent.md)
│
├── Ready to work? ───────────────────→ Route by intent:
│   │
│   ├── "research" / "decide" ────────→ /mb-think
│   ├── "bet" / "launch test" ─────────→ /mb-bet (new/update/close/list/narrate)
│   ├── "ads" / "copy" ───────────────→ /mb-ads (triages to static/video/review)
│   ├── "vsl" / "sales video" ────────→ /mb-vsl (triages to skool/b2b)
│   ├── "content" / "organic" ────────→ /mb-organic
│   ├── "newsletter" / "email" ───────→ /newsletter (coming soon — route to /mb-think for now)
│   ├── "content strategy" / "pillars"→ /mb-think
│   ├── "wiki" / "notes" ─────────────→ /mb-wiki
│   ├── "help" / questions ───────────→ /mb-help
│   ├── "done" / "wrapping up" ──────→ /mb-end
│   └── unclear ──────────────────────→ Show options + mention /mb-help
│
├── "confused" / "stuck" ─────────────→ /mb-help
│
└── "done" / "end my day" ───────────→ /mb-end
```

---

## Step 0: Read Status Facts

After repo selection, run:

```bash
mb status --json --peek
```

Use this report before asking additional questions:

- `ranked_actions` is the deterministic top-three next-action list. Surface
  the first action as the recommendation, including its reason and cited signal
  summaries.
- `readiness` gates whether setup/repair work must happen before output skills.
- `drift.items` names stale or broken status signals and repair commands.
- `onboarding.summary` and `onboarding.checklist` replace separate onboarding
  probes unless the status report is unavailable.
- `integrations.github`, `integrations.providers`, `github.sections`,
  `measurement`, `brain.bets`, and `since_last_check` supply the continuity
  facts for routing and triage.

Only run a narrower fallback command such as `mb onboard status --json`,
`mb doctor`, `mb validate --cross-refs`, or `mb connect doctor --json` when status
points at that section as unavailable, degraded, or needing repair.

## Step 1: Pull Engine Updates

Use the `update` section from `mb status --json --peek`. **Do NOT silently
swallow required updates.** Users on stale code get broken features.

For normal users, updating is not a menu of package-manager commands. Do the
update through the Main Branch product path: route to `/mb-update` when the user
asked about updating, or run `mb update --repo . --json` yourself during
`/mb-start` when status says the update is required. Only mention
`pipx upgrade mainbranch` as a bootstrap fallback when `mb update` is
unavailable or the installed version is `0.1.x`.

If `update.severity` is `required` or the top ranked action is an update action,
run the cited command. When status does not cite a narrower command, use:

```bash
mb update --repo . --json
```

Then run `mb status --json --peek` again before routing.

---

## Step 2: Detect Business Repo (CWD-First)

The user starts Claude in their business repo. Check CWD first before falling back to config.

**Quick gist:**

```
1. test -d "core" || test -d "reference/core"  → THIS IS the business repo. Skip to config.
2. test -f ".claude/skills/mb-start/SKILL.md"  → user is in the engine repo; migrate.
3. Otherwise → fall back to ~/.config/vip/local.yaml.
```

See **[references/repo-detection.md](references/repo-detection.md)** for the full flow: CWD detection, migration guidance for users in the engine repo, config loading, multi-repo selection, the discovery algorithm when no config exists, the canonical `REPO_PATH` variable, and the Main Branch wiring verification block.

---

## Step 3: Pull Business Repo Updates

Once business repo is confirmed, pull its latest updates from `REPO_PATH`. See **[references/pull-engine-updates.md](references/pull-engine-updates.md)** "Pull Business Repo Updates" section for the pull command and the result-handling table.

---

## Step 3a: Resume Onboarding Progress

Prefer the `onboarding` section from `mb status --json --peek`. If status is
unavailable or the operator specifically asks for onboarding detail, run:

```bash
mb onboard status --repo "$REPO_PATH" --json
```

Use the JSON envelope as the source of truth for onboarding progress:

- `summary.next_recommended_action` tells you what to do next
- `checklist[].missing_inputs` names the bounded inputs to collect
- `profile.team_size` distinguishes solo, small-team, and larger-team setup
- `boundaries.defer_until_needed` names data to avoid collecting in the first context window

If `core_reference` is pending, collect only enough to draft the missing core
files. Do not ask for full finances, credentials, raw customer/member exports,
or exhaustive operations details before the core reference exists.

If the user's team size or current success stage is missing, ask briefly and
update the plan:

```bash
mb onboard plan --repo "$REPO_PATH" --team-size solo --success-stage working
```

---

## Step 4: Provider And Tool Pre-Flight (Not Full Research Detection)

Check provider and MCP readiness only for skills the user might invoke. See
[mcp-preflight.md](references/mcp-preflight.md).

Start from CLI facts:

```bash
mb status --json --peek
mb connect plan
mb connect doctor --json
```

Use the status and connect JSON before checking runtime tool presence. The
operator-facing pattern is:

> "This action needs [business capability].
>
> 1. Set up [provider] now — `[exact command]`
> 2. Skip for this session — [specific limitation]"

**Full research tool detection still happens in /mb-think** — deferred to when user actually needs research. This keeps /mb-start fast and avoids checking tools user might not use this session.

**What /mb-start DOES check:**
- Provider readiness from `mb status --json --peek` and `mb connect plan`
- MCPs that a selected skill depends on when provider status says runtime tools are still unknown
- Critical blockers (missing config, broken paths)

**What /mb-start DOES NOT do here:**
- Full research tool scan (Gemini, Grok, whisper, etc.) — /mb-think handles this
- Full document tool scan (markitdown, pandoc, marker) — /mb-think handles this

**Why defer:** Most sessions don't use all tools. Checking everything upfront wastes time and clutters the greeting. /mb-think detects tools when user's intent requires them and surfaces setup options at the right moment.

If user's stated intent involves research, route to /mb-think. It will use
`mb` provider facts first, then detect only the runtime tools needed for the
selected research path.

---

## Step 5: Tool Status Audit (Deterministic Facts First)

Run a lightweight provider/readiness audit before routing:

- Use `mb status --json --peek` facts already gathered.
- Run `mb connect doctor --json` when a provider section is degraded, missing,
  or selected by the operator.
- Quote the CLI's `next_command` / `repair_command`.
- Do not re-probe provider credentials from prose or mutate `.vip/config.yaml`.

See [tool-status-audit.md](references/tool-status-audit.md) for the full procedure and messaging rules.

---

## Step 6: Readiness Assessment

Use `readiness` and `ranked_actions` from `mb status --json --peek` before
routing. The legacy scoring rubric below is fallback detail for gaps that status
does not expose yet.

See [readiness-assessment.md](references/readiness-assessment.md) for complete scoring rubric, session state checks, soul health check, skill-specific requirements, and display format.

### Quick summary:

1. **Score reference files** (soul, offer, audience, voice, testimonials, angles) on 0-3 scale each. Composite max = 18. Multi-offer: score active offer's files, not just core.
2. **Check session state** — recent commits, open decisions, uncodified research. Surface what's in progress.
3. **Soul health check** — for returning users (last commit >3 days ago), read soul.md and ask: "Is your current work feeling like pull or push?" Skip for active or first-time users.
4. **Gate routing** based on composite score:

| Score | Status | Action |
|-------|--------|--------|
| 0-3 | EMPTY | Route to `/mb-setup` |
| 4-7 | MINIMAL | Block output skills, route to `/mb-think` |
| 8-11 | THIN | Warn before output skills, suggest `/mb-think` first |
| 12-14 | GOOD | All skills, note gaps |
| 15-18 | FULL | All skills available |

Adapt display to `user.experience` level (beginner = full breakdown, advanced = score only). See reference file for details.

---

## Step 7: Defer Full Context Loading

**Do NOT read full reference files into main.** Readiness (Step 6) already scored them — that's enough for routing. Full context loading happens in the selected skill or triage agents, not here.

**Why:** Reading soul.md + offer.md + audience.md + voice.md into main burns 15-30K tokens that get duplicated when the skill re-reads them. The triage test showed /mb-start hitting 61% context before any work began. Main stays lean; skills/agents load what they need.

**What main knows after Step 6:** Readiness scores, which files exist, composite score, gaps. That's enough to present the menu and gate routing.

**Exception:** Read `[repo]/CLAUDE.md` (the business brain) — it's small and needed for personality/routing awareness. Skip the 4 core reference files.

**Multi-offer context:** If `current_offer` is set (see Step 8), note the active offer for routing. Don't load the offer file — the selected skill will.

---

## Step 8: Offer Detection (Multi-Offer Only)

After loading core context, check for multi-offer:

```bash
find "$REPO_PATH/core/offers" -mindepth 2 -maxdepth 2 -name "offer.md" 2>/dev/null
```

If `core/offers` is absent but legacy `reference/offers` exists and `core/` is
also absent, use `reference/offers` as the fallback. In current repos,
`reference/offers` is a bridge to `core/offers`, not a separate offer tree.

**If no offers/ folder:** Single-offer mode. Skip to Step 2. Everything reads from `core/`.

**If offers/ found:** Multi-offer mode.
1. Check `.vip/local.yaml` for `current_offer`
2. If set: Confirm — "Working on **[offer]**. Continue? (y / type offer name to switch)"
3. If not set: Present numbered list of offers + "all (brand-level work)"
4. Write selection to `.vip/local.yaml`:
   ```bash
   mkdir -p .vip && echo "current_offer: [name]" > .vip/local.yaml
   ```

**Shortcut:** `/mb-start [offer-name]` sets `current_offer` directly and skips the selection prompt. If the argument matches an offer folder name, write it to `.vip/local.yaml` and confirm: "Locked to **[offer-name]**."

**"all" selection:** When user picks "all" or "brand-level work", set `current_offer: null` in `.vip/local.yaml`. Skills will read from `core/` only — appropriate for brand-level thinking, content strategy, and soul/voice work.

---

## Step 9: Detect State and Assess Completeness

Use `readiness`, `onboarding`, `drift.items`, and `ranked_actions` from
`mb status --json --peek` first. If those sections are unavailable, use this
fallback check.

Fallback: check `core/*.md`, then legacy `reference/core/*.md` only when
`core/` is absent. No folder → `/mb-setup`. If two or more
core files are missing/thin, route to `/mb-think codify`; otherwise route by
intent. Use [readiness-assessment.md](references/readiness-assessment.md) for
the exact fallback thresholds.

**Multi-offer completeness:** When status does not expose offer readiness, check
the active offer's `offer.md`; a thin/missing offer-specific file should route
to `/mb-think`.

---

## Step 10: Route by Intent

**Respect readiness gates from Step 6.** If status is MINIMAL or EMPTY, do not offer output skills. If THIN, warn. See [readiness-assessment.md](references/readiness-assessment.md) for skill-specific requirements.

**Show context:** Before presenting options, show: "Business: **[repo name]** | Offer: **[current_offer or 'single']**"

**Surface unread CHANGELOG entries before the menu**, present option 1 (triage), and use the "while you wait" pattern when spawning agents. See **[references/triage-menu.md](references/triage-menu.md)** for the full menu, the CHANGELOG "what's new" banner format (diff'd against `last_seen_version`), the random "while you wait" filler lines, and rules for when to auto-suggest or skip triage.

---

## Step 11: Help Mode

"Help" or confused → route to `/mb-help`. Give quick overview first:

> "1. **Main Branch** = engine (skills + frameworks, linked via setup). 2. **Your repo** = data (offer, audience, voice).
> Daily: `cd your-business-repo && claude` then `/mb-start`.
> For detailed help: `/mb-help` + your question."

---

## Context Awareness

Fresh context gets a fuller load; working context routes directly; heavy context
gets a brief warning; critical context routes to `/mb-end`. Show percentage only
when relevant.

---

## Adapt to Experience

Read `user.experience` from `~/.config/vip/local.yaml` (defaults to `beginner`
if missing): beginner = explain more, intermediate = balanced, advanced = route
fast.

**First-time** (no config, thin reference): Be verbose, route to /mb-setup
**Returning** (config exists): Quick confirmation, route by intent
**Expert** (advanced experience, clear intent): Get out of the way, route fast

**Updating experience:** If user says "I know what I'm doing" or similar, offer to update their experience level in local.yaml.

---

## Intent Keywords

Auto-detect user intent and route. Skills: `/mb-update`, `/mb-help`, `/mb-setup`, `/mb-think`, `/mb-ads`, `/mb-vsl`, `/mb-organic`, `/mb-site`, `/mb-wiki`, `/mb-end`. Some skills spawn parallel subagents automatically.

| Keywords | Route To |
|----------|----------|
| "what should I work on", "help me prioritize", "what to do next", "figure out what to work on", "deep triage" | Option 1 → Triage (see [triage-agent.md](references/triage-agent.md)) |
| "help", "confused", "stuck", "don't understand", "how do I" | `/mb-help` |
| "new", "first time", "get started", "set up" | `/mb-setup` |
| "add", "update", "more context", "new testimonials", "enrich" | `/mb-think codify` |
| "research", "decide", "figure out", "explore", "mine", "mining", "competitors", "transcribe" | `/mb-think` |
| "content strategy", "pillars", "platforms", "cadence", "content plan", "distribution" | `/mb-think` |
| "soul check", "is this still right", "feeling obligated", "pull or push" | `/mb-think codify` (soul.md review) |
| "newsletter", "email", "beehiiv", "weekly email" | `/newsletter` (coming soon — route to `/mb-think` for now) |
| "ads", "copy", "static", "image ads", "video ads", "review", "compliance" | `/mb-ads` |
| "vsl", "sales video", "about page video", "b2b video" | `/mb-vsl` |
| "content", "reels", "tiktok", "organic", "carousel" | `/mb-organic` |
| "site", "landing page", "lander", "minisite", "website", "one-pager", "spin up a site", "deploy site", "put this online", "I need a site", "publish site", "graduate my site", "add a CMS to my site", "/mb-start launch" | `/mb-site` (or `/mb-start launch <offer>` for the speedrun orchestration) |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/mb-wiki` |
| "pull", "update Main Branch", "get latest" | `/mb-update` |
| "done", "wrapping up", "end my day", "closing out", "call it a day", "that's it" | `/mb-end` |

---

## Recovering from Compaction

If re-invoked after compaction: re-read `~/.config/vip/local.yaml` for repo + identity, and `.vip/local.yaml` in the business repo for `current_offer`. Don't re-prompt — confirm: "Restored offer context: **[offer-name]**."

---

## References

- [references/pull-engine-updates.md](references/pull-engine-updates.md) — Step 1 + Step 3 pull scripts and failure warnings
- [references/repo-detection.md](references/repo-detection.md) — Step 2 full CWD detection, migration, multi-repo selection, REPO_PATH, Main Branch wiring verification
- [references/triage-menu.md](references/triage-menu.md) — Step 10 CHANGELOG banner, menu, "while you wait" pattern, auto-suggest/skip rules
- [references/auto-heal.md](references/auto-heal.md) — Bridge link recovery
- [references/config-system.md](references/config-system.md) — Config loading and recovery
- [references/mcp-preflight.md](references/mcp-preflight.md) — MCP pre-flight checks
- [references/readiness-assessment.md](references/readiness-assessment.md) — Step 6 readiness scoring
- [references/tool-status-audit.md](references/tool-status-audit.md) — Step 5 provider/readiness audit
- [references/triage-agent.md](references/triage-agent.md) — Triage agent prompts and synthesis

---

## Remember

Router, not worker. Detect → route → let the skill do the work. One clarifying question max. Skill loads its own context — main stays lean.
