---
name: mb-start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens Main Branch without a task, needs triage, or wants to launch an offer. Routes to /mb-setup, /mb-think, /mb-bet, /mb-site, /mb-ads, /mb-vsl, /mb-organic, /mb-wiki, /mb-help."
loops: [sense, decide]
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Start Claude in your business repo, run `/mb-start`. It handles everything. Claude Code discovers Main Branch through project-local `.claude/skills/mb-*` bridge links; `additionalDirectories` grants file access to the engine.

## Output destinations and operator vocabulary

This skill routes to other skills; it does not write coordinated work itself.
When summarizing repo state, count records under `pushes/` (canonical) and
flag `campaigns/` separately as legacy compatibility — `mb status` and
`mb doctor` already do this. If `core/vocabulary.md` defines display words
(e.g. `terms.push.singular: drop`), speak the operator's word in
conversation while still referring to canonical paths in any commands.

If the repo has legacy `campaigns/` records, surface the doctor warning
and recommend `mb migrate campaigns --plan` as a triage option before
routing the operator into a skill that creates new push work.

**Status facts first:** Once the business repo path is known, run
`mb status --json --peek` before asking setup or routing questions. Treat that
JSON as the source of truth for update severity, readiness, drift, onboarding,
integrations, GitHub issue/proposal facts, bets, dirty git, since-last-check, and
`ranked_actions`. Do not duplicate those checks with ad hoc shell probes unless
the status report says a section is unavailable.

**Continuity facts:** Use `since_last_check.journal`, top-level `journal`,
dirty-git, GitHub activity, and `checkpoint` from status to explain "where we
left off." Do not run raw `git log` unless status says journal facts are
unavailable. If the operator asks to save progress, run `mb checkpoint --plan
--json`, validate with `mb checkpoint --validate "..." --json`, then after
approval run `mb checkpoint --message "..." --yes`.

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

**Offer launch path:** When the operator asks to launch an offer, use
[references/launch-orchestration.md](references/launch-orchestration.md).
The path is skill orchestration: keyword-gate with `/mb-think`, create/select a
canonical launch push, build/check the lander with `/mb-site`, prepare or check
ads with `/mb-ads`, and checkpoint approved artifacts.

**Primitive routing:** When an operator brings a live idea and it is unclear
whether it is a bet, offer, push, proof, or decision, load
`.claude/reference/business-primitives/offer-bet-push-proof.md` from the engine
and route by business meaning before suggesting file moves. In short: offers
are what the business may keep selling, bets are time-boxed wagers, pushes are
coordinated execution, proof is evidence, and decisions explain durable changes.
Ask before renaming, deleting, merging, or moving offer folders.

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

**After user selects a repo from legacy fallback config:** If the selected repo
is not the current `default_repo`, ask: "Want me to save [repo-name] as your
default? (faster startup next time)" If yes, merge-update `default_repo` in
`~/.config/vip/local.yaml`. Do not create or update `.vip/config.yaml`.

---

## Numbered Options Pattern

Always use numbered lists for multi-choice: business repo selection, skill
routing, launch blockers, and provider setup.

Use one active choice namespace per turn. If top recommendations are numbered,
do not also number offers or skill routes in the same response. Use offer
slugs/names (`community`, `newsletter`, `all`) or letters for the secondary
set, and make the prompt explicit:

> "Reply `1` for the top recommendation, or reply with an offer slug like
> `community`."

Never present two visible choices where the same number means different
actions. If the operator replies with an ambiguous number, ask what they meant
before taking action.

---

## Detection Flow

1. Detect repo CWD-first; use config only when CWD is not a business repo.
2. Run `mb status --json --peek`; status facts gate updates, repair, readiness,
   onboarding, ranked actions, and continuity.
3. Use status-cited repair/update commands before routing into output work.
4. Resume onboarding from status facts; in rich repos, read existing `core/`
   before asking bounded missing-profile questions.
5. Resolve multi-offer context without reusing numbered choices or silently
   writing local state.
6. Present one clear route set or infer intent: `/mb-think`, `/mb-bet`,
   `/mb-ads`, `/mb-vsl`, `/mb-organic`, `/mb-site`, `/mb-wiki`, `/mb-help`, or
   `/mb-end`.

---

## Step 0: Read Status Facts

After repo selection, run:

```bash
mb status --json --peek
```

Use this report before asking additional questions:

- `ranked_actions` is the deterministic list of one to three business moves.
  Surface the first action as the recommendation, including its reason and
  cited signal summaries.
- `readiness` gates whether setup/repair work must happen before output skills.
- `drift.items` names stale or broken status signals and repair commands.
- `onboarding.summary` and `onboarding.checklist` replace separate onboarding
  probes unless the status report is unavailable.
- `journal`, `since_last_check.journal`, `integrations.github`,
  `integrations.providers`, `github.sections`, `measurement`, and
  `brain.bets` supply continuity facts for routing and triage.

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
3. Otherwise → fall back to `~/.config/vip/local.yaml` only as legacy
   machine-local repo memory.
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
or exhaustive operations details before the core files exist.

If the repo already has substantive current `core/` files, read and summarize
those facts before asking onboarding questions. Mine `core/offer.md`,
`core/audience.md`, `core/voice.md`, `core/soul.md`, and `core/proof/` when
present; include `core/offers/*/offer.md` names in multi-offer repos. Propose
answers for bounded missing inputs from existing repo truth, cite which files
informed the proposal, and ask the operator only to confirm or correct the
facts that remain uncertain.

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

1. **Score core files** (soul, offer, audience, voice, testimonials, angles) on 0-3 scale each. Composite max = 18. Multi-offer: score active offer's files, not just core.
2. **Check continuity state** -- status journal activity, active decisions, uncodified research, and saved/unsaved work.
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

**Exception:** Read `[repo]/CLAUDE.md` (the business brain) — it's small and needed for personality/routing awareness. Skip the 4 full core files.

**Onboarding exception:** When onboarding is incomplete and current `core/`
files already exist, read enough of those files to avoid asking for facts the
repo already contains. Keep this bounded: summarize the existing facts and ask
only for confirmation or missing profile fields.

**Multi-offer context:** If CLI facts or the current session identify an
active offer, note it for routing; the selected skill loads the offer file.

---

## Step 8: Offer Detection (Multi-Offer Only)

Use the active-offer resolution contract in
`.claude/reference/business-primitives/offer-bet-push-proof.md`.

```bash
find "$REPO_PATH/core/offers" -mindepth 2 -maxdepth 2 -name "offer.md" 2>/dev/null
```

If `core/offers` is absent and `core/` is also absent, legacy
`reference/offers` is fallback only. In current repos it bridges to
`core/offers`.

**If no offers/ folder:** Single-offer mode. Skip to Step 2. Everything reads from `core/`.

**If offers/ found:** Multi-offer mode.
1. Check current CLI status facts first. If a future `mb` JSON field exposes
   active-offer local state, prefer that. Do not silently route from
   `.vip/local.yaml`.
2. If legacy active-offer state is present, do not treat it as canonical. Say:
   "This repo has old active-offer session state. Continue with that offer,
   work brand-level, or switch?" Avoid echoing raw `.vip` values unless the
   user asks to inspect the file.
3. If no active offer is set, present offers by slug/name, not numbers when
   ranked actions or routes are already numbered:
   - `community` — paid community
   - `newsletter` — newsletter
   - `all` — brand-level work from `core/`
4. Treat the user's selection as session-scoped until they explicitly confirm
   persistence. Say what will happen before writing local state:
   "For this session I'll use **[offer]**. Save that as the active offer for
   future sessions too?"
5. Keep the selection session-scoped. Do not write `.vip/local.yaml` as the
   active-offer mechanism. If a future `mb` command exposes an explicit
   session-state contract, use that only after confirmation.

**Shortcut:** `/mb-start [offer-name]` selects that offer for this session after
validating the folder exists. Ask before saving future active-offer state.

**"all" selection:** Use brand-level `core/` context for this session. Ask
before persisting any future local state that clears an active offer.

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

**Show context:** Before presenting options, show: "Business: **[repo name]** | Offer: **[active offer or 'single']**"

**Surface unread CHANGELOG entries before the menu**, present the triage route
without reusing a number from recommendations or offers, and use the "while you
wait" pattern when spawning agents. See
**[references/triage-menu.md](references/triage-menu.md)** for the full menu,
the CHANGELOG "what's new" banner format (diff'd against `last_seen_version`),
the random "while you wait" filler lines, and rules for when to auto-suggest or
skip triage.

---

## Step 11: Help Mode

"Help" or confused → route to `/mb-help`. Give quick overview first:

> "1. **Main Branch** = engine. 2. **Your repo** = business data. Daily:
> `cd your-business-repo && claude` then `/mb-start`. Details: `/mb-help`."

---

## Context And Experience

Fresh context gets a fuller load; working context routes directly; heavy context
gets a brief warning; critical context routes to `/mb-end`. If legacy
`~/.config/vip/local.yaml` has `user.experience`, use it as a machine-local
fallback: beginner explains more, returning confirms quickly, expert routes
fast. If the user asks for a faster mode, offer to update local experience.

---

## Intent Keywords

Auto-detect user intent and route. Skills: `/mb-update`, `/mb-help`, `/mb-setup`, `/mb-think`, `/mb-ads`, `/mb-vsl`, `/mb-organic`, `/mb-site`, `/mb-wiki`, `/mb-end`. Some skills spawn parallel subagents automatically.

| Keywords | Route To |
|----------|----------|
| "what should I work on", "help me prioritize", "what to do next", "figure out what to work on", "deep triage" | Triage route (see [triage-agent.md](references/triage-agent.md)) |
| "help", "confused", "stuck", "don't understand", "how do I" | `/mb-help` |
| "new", "first time", "get started", "set up" | `/mb-setup` |
| "add", "update", "more context", "new testimonials", "enrich" | `/mb-think codify` |
| "research", "decide", "figure out", "explore", "mine", "mining", "competitors", "transcribe" | `/mb-think` |
| "content strategy", "pillars", "platforms", "cadence", "content plan", "distribution" | `/mb-think` |
| "soul check", "is this still right", "feeling obligated", "pull or push" | `/mb-think codify` (soul.md review) |
| "newsletter", "email", "beehiiv", "weekly email" | `/mb-think` for content strategy, then `/mb-organic` for social repurposing |
| "ads", "copy", "static", "image ads", "video ads", "review", "compliance" | `/mb-ads` |
| "vsl", "sales video", "about page video", "b2b video" | `/mb-vsl` |
| "content", "reels", "tiktok", "organic", "carousel" | `/mb-organic` |
| "launch offer", "keyword gate then build", "offer launch", "/mb-start launch <offer>" | Use [references/launch-orchestration.md](references/launch-orchestration.md), then route to `/mb-think`, `/mb-site`, and `/mb-ads` as each step becomes current |
| "site", "landing page", "lander", "minisite", "website", "one-pager", "spin up a site", "deploy site", "put this online", "I need a site", "publish site", "graduate my site", "add a CMS to my site" | `/mb-site` |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/mb-wiki` |
| "pull", "update Main Branch", "get latest" | `/mb-update` |
| "done", "wrapping up", "end my day", "closing out", "call it a day", "that's it" | `/mb-end` |

---

## Recovering from Compaction

If re-invoked after compaction: use CWD and `mb status --json --peek` first;
read `~/.config/vip/local.yaml` only as legacy fallback for repo + identity;
treat business `.vip/local.yaml` as audit input only, and do not write it.

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
- [references/launch-orchestration.md](references/launch-orchestration.md) — guided offer-launch path

## Remember

Router, not worker. Detect → route → let the skill do the work. One clarifying question max. Skill loads its own context — main stays lean.
