---
name: mb-start
description: "Main Branch business router. Detects repo facts, save/sync state, updates, readiness, and live operator intent, then routes to the right skill or CLI contract. Use when the user starts/returns, asks what to do, needs setup, bookkeeping/books, provider setup, save/checkpoint/sync help, repair/update guidance, launch routing, or help."
loops: [sense, decide]
---

# Start

Single entry point for Main Branch. Detect business state, current intent, save/sync posture, and the smallest useful next route.

**Recommended workflow:** Start Claude in your business repo, run `/mb-start`. It handles everything. Claude Code discovers Main Branch through project-local `.claude/skills/mb-*` bridge links; `additionalDirectories` grants file access to the installed package or source checkout.

## Router and language contract

This skill routes; it is not the worker for coordinated output. Use
[references/router-and-language.md](references/router-and-language.md) as the
business router before presenting a menu.

Business language comes first. Say saved checkpoint, unsaved local work, catch
up, sync, reconcile, shared repo, workspace, and provider readiness. Keep raw
git terms, checkpoint ids, branch names, `origin`, `ahead`, `behind`, `rebase`,
and `commit` out of the first response unless the user asks for technical detail
or the exact command must be shown.

When summarizing repo state, count records under `pushes/` (current) and flag
`campaigns/` separately as legacy compatibility. If `core/vocabulary.md` defines
display words, speak the operator's word in conversation while still using
actual file paths in commands.

**CLI facts first:** Once the business repo path is known, run
`mb status --json --peek` before asking setup or routing questions. Treat JSON
as source of truth for update severity, readiness, drift, onboarding,
integrations, GitHub, bets, dirty git, since-last-check, `content_strategy`,
`money_path`, and `ranked_actions`. Parse the full JSON once; do not slice
status output with `head` or `sed` in the normal path.

**Continuity facts:** Use `since_last_check.journal`, top-level `journal`,
GitHub activity, and `checkpoint` from status to explain "where we left off."
Do not run raw `git log` unless status says journal facts are unavailable. If
the operator asks to save progress, run `mb checkpoint --plan --json`, validate
with `mb checkpoint --validate "..." --json`, then after approval run
`mb checkpoint --message "..." --yes`.

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
launch push, build/check the lander with `/mb-site`, prepare or check
ads with `/mb-ads`, and checkpoint approved artifacts.

**Primitive routing:** When a live idea could be a bet, offer, push, proof, or
decision, load `.claude/reference/business-primitives/offer-bet-push-proof.md`
and `.claude/reference/business-primitives/setup-patterns.md`; route by business
meaning before suggesting file moves.

**Books/finance routing:** When the user mentions bookkeeping, books, finance,
accounting, ledgers, statements, P&L, chart of accounts, tax, payroll, hledger,
or a restricted `finance` child repo, run `mb books check "$REPO_PATH" --json`
before drafting files. Keep raw private finance records out of the
team-safe hub repo; use the books contract, `storage_mode`, and topology
visibility (`restricted` or `local_only`) to route raw records.

**Slug/destructive-operation guardrails:** Load
`.claude/reference/business-primitives/slug-conventions.md` before naming
business objects or topology entries, and
`.claude/reference/business-primitives/destructive-operations.md` before
renaming, deleting, merging, archiving, migrating, publishing, mutating
providers, spending money, changing topology, or creating checkpoints.

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

**After user selects a repo from legacy fallback config:** Treat the selected
repo as session-scoped unless a current `mb` command exposes an explicit
persistence path. Do not write `default_repo` into `~/.config/vip/local.yaml`,
and do not create or update `.vip/config.yaml`.

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
4. Route live intent through [references/router-and-language.md](references/router-and-language.md)
   before showing a generic menu.
5. Resume onboarding from status facts; in rich repos, read existing `core/`
   before asking bounded missing-profile questions.
6. Resolve multi-offer context without reusing numbered choices or silently
   writing local state.
7. Present one clear route set or infer intent: `/mb-think`, `/mb-bet`,
   `/mb-ads`, `/mb-organic`, `/mb-site`, `/mb-wiki`, `/mb-help`, or
   `/mb-end`. Conversion-script requests route through the owning workflow,
   not a standalone skill.

---

## Status Preamble: Read Status Facts

After repo selection, run:

```bash
mb status --json --peek
```

Use this report before asking additional questions:

- `ranked_actions` is the deterministic list of one to three business moves.
  Surface the first action as the recommendation, including its reason and
  cited signal summaries.
- `money_path` maps customer progress, offer, proof, CTA, channel, push,
  playbook, page readiness, and outcome feedback. Use levels, objects, and
  ranked actions as evidence; do not call the offer "good" or "will convert."
  For proof, cite `money_path.objects.proof.quality` facts: generic testimonials, outcomes, offer linkage, typicality, and outcome feedback.
- `content_strategy` maps the simple file and optional layers before markdown parsing.
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

## Step 1: Check Main Branch Updates

Use the `update` section from `mb status --json --peek`. **Do not bury available
updates inside a general status wall.** Users on stale code get broken
features, and normal operators will miss a one-line version note.

If `update.severity` is `required` or the top ranked action is an update action,
run the cited command. When status does not cite a narrower command, use:

```bash
mb update --repo . --json
```

Then run `mb status --json --peek` again before routing.

If `update.severity` is `recommended`, stop there. Do not show ranked actions
or business recommendations yet; those may change after the update. Ask whether
to update now, then rerun `mb status --json --peek` before routing. Use
[references/router-and-language.md](references/router-and-language.md) for
operator-facing wording and fallback details.

---

## Step 2: Detect Business Repo (CWD-First)

The user starts Claude in their business repo. Check CWD first before falling back to config.

**Quick gist:**

```
1. test -d "core" || test -d "reference/core"  → THIS IS the business repo. Skip to config.
2. test -f ".claude/skills/mb-start/SKILL.md"  → user is in a Main Branch source checkout; migrate.
3. Otherwise → fall back to `~/.config/vip/local.yaml` only as legacy
   machine-local repo memory.
```

See **[references/repo-detection.md](references/repo-detection.md)** for the full flow: CWD detection, migration guidance for users in a source checkout, config loading, multi-repo selection, the discovery algorithm when no config exists, the required `REPO_PATH` variable, and the Main Branch wiring verification block.

---

## Step 3: Read Save/Sync State

Once the business repo is confirmed, use status `git`, `checkpoint`, and
`since_last_check` facts to explain whether work is saved locally, unsaved
locally, synced to the shared repo, or waiting for reconciliation. Do not
blindly pull or rebase the business repo from `/mb-start`. See
[references/router-and-language.md](references/router-and-language.md) for the
save/sync vocabulary.

---

## Onboarding Preamble: Resume Onboarding Progress

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

**What /mb-start checks:** provider readiness from `mb status --json --peek`
and `mb connect plan`, selected-skill MCPs when provider status says runtime
tools are unknown, and critical blockers such as missing config or broken paths.
Leave full research/document tool scans to `/mb-think`; most sessions do not
need every tool checked upfront.

If user's stated intent involves research, route to /mb-think. It will use
`mb` provider facts first, then detect only the runtime tools needed for the
selected research path.

---

## Step 5: Tool Status Audit (Deterministic Facts First)

Run a lightweight provider/readiness audit:

- Use `mb status --json --peek` facts already gathered.
- Run `mb connect doctor --json` when a provider section is degraded, missing,
  or selected by the operator.
- Quote the CLI's `next_command` / `repair_command`.
- Do not re-probe provider credentials from prose or mutate `.vip/config.yaml`.

See [tool-status-audit.md](references/tool-status-audit.md) for the full procedure and messaging rules.

---

## Step 6: Readiness Assessment

Use `readiness`, `money_path`, and `ranked_actions` from
`mb status --json --peek` before routing. The reference below is fallback detail
for gaps that status does not expose yet.

See [readiness-assessment.md](references/readiness-assessment.md) for complete scoring rubric, session state checks, soul health check, skill-specific requirements, and display format.

Quick summary: status readiness gates setup, repair, and output skills; fallback
scoring only fills missing detail. Adapt display to `user.experience` level
without making the repo feel audited or behind.

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
`.claude/reference/business-primitives/offer-bet-push-proof.md`; load
`setup-patterns.md` and `slug-conventions.md` from that same directory when
setup shape or naming is unclear.

```bash
find "$REPO_PATH/core/offers" -mindepth 2 -maxdepth 2 -name "offer.md" 2>/dev/null
```

If `core/offers` is absent and `core/` is also absent, legacy
`reference/offers` is fallback only. In current repos it bridges to
`core/offers`.

**If no offers/ folder:** Single-offer mode. Skip to Step 2. Read from `core/`.

**If offers/ found:** Multi-offer mode.
1. Check current CLI status facts first. If a future `mb` JSON field exposes
   active-offer local state, prefer that. Do not silently route from
   `.vip/local.yaml`.
2. If legacy active-offer state is present, do not treat it as the source of truth. Say:
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

Use `readiness`, `onboarding`, `drift.items`, `money_path`, and `ranked_actions`
from status first. Prefer `money_path.ranked_actions` for path gaps unless the
top-level ranked action already incorporates it.

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

**Show context:** "Business: **[repo name]** | Offer: **[active offer or 'single']**"

If the user stated intent, route directly using
[references/router-and-language.md](references/router-and-language.md). If the
session is open-ended, surface the top ranked action, update recommendation, top
non-duplicated MoneyPath action, or compact route menu. Use
[references/triage-menu.md](references/triage-menu.md) only for prioritization
or deep triage.

---

## Step 11: Help Mode

"Help" or confused → route to `/mb-help`. Give quick overview first:

> "Open your business folder, start Claude, then run `/mb-start`. Main Branch
> uses the `mb` CLI for facts and skills for judgment. Details: `/mb-help`."

---

## Context And Experience

Fresh context gets a fuller load; working context routes directly; heavy context
gets a brief warning; critical context routes to `/mb-end`. If legacy
`~/.config/vip/local.yaml` has `user.experience`, use it as a machine-local
fallback: beginner explains more, returning confirms quickly, expert routes
fast. If the user asks for a faster mode, offer to update local experience.

---

## Intent Keywords

Auto-detect user intent through
[references/router-and-language.md](references/router-and-language.md). Key
clusters: save/checkpoint/sync, bookkeeping/books/finance, provider/tool setup,
repair/update/drift, decide/codify/research, bets, launches, sites, ads, organic,
wiki, and help.

Generic "set up" is not enough to route. Use the noun: repo setup routes to
`/mb-setup`, bookkeeping setup runs `mb books check`, provider setup reads
`mb connect`, and decision/tool setup routes to `/mb-think`.

---

## Recovering from Compaction

If re-invoked after compaction: use CWD and `mb status --json --peek` first;
read `~/.config/vip/local.yaml` only as legacy fallback for repo + identity;
treat business `.vip/local.yaml` as audit input only, and do not write it.

---

## References

- [references/router-and-language.md](references/router-and-language.md) — business router, save/sync language, update posture, and intent clusters
- [references/pull-engine-updates.md](references/pull-engine-updates.md) — Step 1 Main Branch update handling
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
