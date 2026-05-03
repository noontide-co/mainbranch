---
name: start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens vip without a task, or needs triage. Routes to /setup, /think, /ads, /vsl, /organic, /wiki, /help."
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Start Claude in your business repo, run `/start`. It handles everything. vip is loaded through `additionalDirectories`, with bridge links as a compatibility fallback for skill discovery.

---

## CRITICAL: Repo Selection Rules

**CWD-first wins.** If `reference/core/` or `core/` exists in CWD, the user is already in their business repo — no selection needed. Just confirm: "Working in **[repo-name]**."

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
- CWD has `reference/core/` or `core/` — user chose their repo by cd'ing into it
- User explicitly ran `/start [repo-name]` with a specific path

**After user selects a repo:** If the selected repo is not the current `default_repo`, ask: "Want me to save [repo-name] as your default? (faster startup next time)" If yes, update `default_repo` in `~/.config/vip/local.yaml`.

---

## Numbered Options Pattern

Always use numbered lists for multi-choice. User replies with just a number.

Apply to: business repo selection, skill routing, any multiple choice.

---

## Detection Flow

```
/start [optional: repo-name] [optional: offer-name]
│
├── Check context level ──────────────→ Fresh? Full load. Heavy? Warn user.
│
├── Detect business repo ─────────────→ CWD-first detection (see Step 2)
│   ├── CWD has reference/core/ or core/? → This IS the repo. Proceed.
│   ├── CWD has .claude/skills/? ─────→ User is in vip (old workflow). Trigger migration.
│   └── Neither? ────────────────────→ Check config, then ask user.
│
├── Pull engine updates ──────────────→ Resolve vip path, pull THAT dir (not CWD)
│
├── Load config ──────────────────────→ See [config-system.md](references/config-system.md)
│   ├── ~/.config/vip/local.yaml ─────→ vip_path + default_repo + user identity
│   └── [repo]/.vip/config.yaml ──────→ Team settings, MCP requirements
│
├── Verify vip loaded ────────────────→ Check additionalDirectories has vip
│   └── Missing? ────────────────────→ Offer to run /setup to configure
│
├── MCP pre-flight ───────────────────→ See [mcp-preflight.md](references/mcp-preflight.md)
│   └── Missing required MCP? ────────→ Offer setup or skip
│
├── No business repo found? ──────────→ /setup (creates repo, saves path)
│
├── Pull business repo updates ───────→ (your repo, silently)
│
├── Offer detection ──────────────────→ (multi-offer only, see Step 8)
│   ├── offers/ exists? ─────────────→ Prompt or restore from .vip/local.yaml
│   └── no offers/ ──────────────────→ Single-offer mode, skip
│
├── Has repo but thin? ───────────────→ /think codify
│   (reference files exist but incomplete)
│
├── Present menu ────────────────────→ Readiness gates which options show
│   (option 1 = triage, recommended)
│
├── User picks option 1? ───────────→ Spawn triage agents (see triage-agent.md)
│
├── Ready to work? ───────────────────→ Route by intent:
│   │
│   ├── "research" / "decide" ────────→ /think
│   ├── "ads" / "copy" ───────────────→ /ads (triages to static/video/review)
│   ├── "vsl" / "sales video" ────────→ /vsl (triages to skool/b2b)
│   ├── "content" / "organic" ────────→ /organic
│   ├── "newsletter" / "email" ───────→ /newsletter (coming soon — route to /think for now)
│   ├── "content strategy" / "pillars"→ /think
│   ├── "wiki" / "notes" ─────────────→ /wiki
│   ├── "help" / questions ───────────→ /help
│   ├── "done" / "wrapping up" ──────→ /end
│   └── unclear ──────────────────────→ Show options + mention /help
│
├── "confused" / "stuck" ─────────────→ /help
│
└── "done" / "end my day" ───────────→ /end
```

---

## Step 1: Pull Engine Updates

Pull vip updates. CWD is the business repo — resolve vip path first. **Do NOT silently swallow failures.** Users on stale code get broken features.

See **[references/pull-engine-updates.md](references/pull-engine-updates.md)** for the canonical pull script, result handling table, the failure warning to surface, and the matching Step 3 business-repo pull logic.

---

## Step 2: Detect Business Repo (CWD-First)

The user starts Claude in their business repo. Check CWD first before falling back to config.

**Quick gist:**

```
1. test -d "reference/core" || test -d "core"  → THIS IS the business repo. Skip to config.
2. test -f ".claude/skills/start/SKILL.md"  → user is in vip; migrate.
3. Otherwise → fall back to ~/.config/vip/local.yaml.
```

See **[references/repo-detection.md](references/repo-detection.md)** for the full flow: CWD detection, migration guidance for users in vip, config loading, multi-repo selection, the discovery algorithm when no config exists, the canonical `REPO_PATH` variable, and the verify-vip-is-loaded block (config + bridge links).

---

## Step 3: Pull Business Repo Updates

Once business repo is confirmed, pull its latest updates from `REPO_PATH`. See **[references/pull-engine-updates.md](references/pull-engine-updates.md)** "Pull Business Repo Updates" section for the pull command and the result-handling table.

---

## Step 4: MCP Pre-Flight (Not Full Research Detection)

Check for MCPs required by skills user might invoke. See [mcp-preflight.md](references/mcp-preflight.md).

**Full research tool detection still happens in /think** — deferred to when user actually needs research. This keeps /start fast and avoids checking tools user might not use this session.

**What /start DOES check:**
- MCPs that skills depend on (Apify for /organic, etc.)
- Critical blockers (missing config, broken paths)

**What /start DOES NOT do here:**
- Full research tool scan (Gemini, Grok, whisper, etc.) — /think handles this
- Full document tool scan (markitdown, pandoc, marker) — /think handles this

**Why defer:** Most sessions don't use all tools. Checking everything upfront wastes time and clutters the greeting. /think detects tools when user's intent requires them and surfaces setup options at the right moment.

If user's stated intent involves research, route to /think — it will handle tool detection with config-first logic (reads `.vip/config.yaml`, only probes unknowns, updates config with results).

---

## Step 5: Tool Status Audit (Lightweight Self-Heal)

Run a lightweight `.vip/config.yaml` audit before readiness to repair stale `status: false` entries and normalize missing `last_checked` values.

- Re-probe only stale false entries (missing/invalid/old `last_checked`)
- Write updates immediately when status or metadata is repaired
- Notify only when status changes (`false → true` or `true → false`)

See [tool-status-audit.md](references/tool-status-audit.md) for the full procedure and messaging rules.

---

## Step 6: Readiness Assessment

**Run AFTER MCP pre-flight and tool-status audit, BEFORE routing.** Scores reference files, checks session state, and gates routing so users don't jump into output skills with thin context.

See [readiness-assessment.md](references/readiness-assessment.md) for complete scoring rubric, session state checks, soul health check, skill-specific requirements, and display format.

### Quick summary:

1. **Score reference files** (soul, offer, audience, voice, testimonials, angles) on 0-3 scale each. Composite max = 18. Multi-offer: score active offer's files, not just core.
2. **Check session state** — recent commits, open decisions, uncodified research. Surface what's in progress.
3. **Soul health check** — for returning users (last commit >3 days ago), read soul.md and ask: "Is your current work feeling like pull or push?" Skip for active or first-time users.
4. **Gate routing** based on composite score:

| Score | Status | Action |
|-------|--------|--------|
| 0-3 | EMPTY | Route to `/setup` |
| 4-7 | MINIMAL | Block output skills, route to `/think` |
| 8-11 | THIN | Warn before output skills, suggest `/think` first |
| 12-14 | GOOD | All skills, note gaps |
| 15-18 | FULL | All skills available |

Adapt display to `user.experience` level (beginner = full breakdown, advanced = score only). See reference file for details.

---

## Step 7: Defer Full Context Loading

**Do NOT read full reference files into main.** Readiness (Step 6) already scored them — that's enough for routing. Full context loading happens in the selected skill or triage agents, not here.

**Why:** Reading soul.md + offer.md + audience.md + voice.md into main burns 15-30K tokens that get duplicated when the skill re-reads them. The triage test showed /start hitting 61% context before any work began. Main stays lean; skills/agents load what they need.

**What main knows after Step 6:** Readiness scores, which files exist, composite score, gaps. That's enough to present the menu and gate routing.

**Exception:** Read `[repo]/CLAUDE.md` (the business brain) — it's small and needed for personality/routing awareness. Skip the 4 core reference files.

**Multi-offer context:** If `current_offer` is set (see Step 8), note the active offer for routing. Don't load the offer file — the selected skill will.

---

## Step 8: Offer Detection (Multi-Offer Only)

After loading core context, check for multi-offer:

```bash
find "$REPO_PATH/reference/offers" -mindepth 2 -maxdepth 2 -name "offer.md" 2>/dev/null
```

**If no offers/ folder:** Single-offer mode. Skip to Step 2. Everything reads from `core/`.

**If offers/ found:** Multi-offer mode.
1. Check `.vip/local.yaml` for `current_offer`
2. If set: Confirm — "Working on **[offer]**. Continue? (y / type offer name to switch)"
3. If not set: Present numbered list of offers + "all (brand-level work)"
4. Write selection to `.vip/local.yaml`:
   ```bash
   mkdir -p .vip && echo "current_offer: [name]" > .vip/local.yaml
   ```

**Shortcut:** `/start [offer-name]` sets `current_offer` directly and skips the selection prompt. If the argument matches an offer folder name, write it to `.vip/local.yaml` and confirm: "Locked to **[offer-name]**."

**"all" selection:** When user picks "all" or "brand-level work", set `current_offer: null` in `.vip/local.yaml`. Skills will read from `core/` only — appropriate for brand-level thinking, content strategy, and soul/voice work.

---

## Step 9: Detect State and Assess Completeness

Check `reference/core/*.md`. No folder → `/setup`. Exists → check completeness:

| File | Complete If |
|------|------------|
| soul.md | >30 lines or "Beliefs" section |
| offer.md | >50 lines or "Price" section |
| audience.md | >30 lines or "Pains" section |
| voice.md | >20 lines or "Tone" section |

2+ empty/missing → `/think codify`. Complete → route by intent.

**Multi-offer completeness:** When `offers/` exists, also check the active offer's `offer.md` for substance. A thin offer file (< 20 lines) means `/think` should be recommended to flesh it out. Don't count brand-level `core/offer.md` as a substitute for a missing offer-specific file.

---

## Step 10: Route by Intent

**Respect readiness gates from Step 6.** If status is MINIMAL or EMPTY, do not offer output skills. If THIN, warn. See [readiness-assessment.md](references/readiness-assessment.md) for skill-specific requirements.

**Show context:** Before presenting options, show: "Business: **[repo name]** | Offer: **[current_offer or 'single']**"

**Surface unread CHANGELOG entries before the menu**, present option 1 (triage), and use the "while you wait" pattern when spawning agents. See **[references/triage-menu.md](references/triage-menu.md)** for the full menu, the CHANGELOG "what's new" banner format (diff'd against `last_seen_version`), the random "while you wait" filler lines, and rules for when to auto-suggest or skip triage.

---

## Step 11: Help Mode

"Help" or confused → route to `/help`. Give quick overview first:

> "1. **vip** = engine (skills + frameworks, linked via setup). 2. **Your repo** = data (offer, audience, voice).
> Daily: `cd your-business-repo && claude` then `/start`.
> For detailed help: `/help` + your question."

---

## Context Awareness

| Level | Action |
|-------|--------|
| Fresh (0-20%) | Full load, explain briefly |
| Working (20-70%) | Route to task |
| Heavy (70-85%) | Warn: "Finish this, then new session" |
| Critical (85%+) | "Context nearly full. Wrap up." |

Show percentage when relevant: "You're at ~60% — plenty of room."

---

## Adapt to Experience

Read `user.experience` from `~/.config/vip/local.yaml` (defaults to `beginner` if missing).

| Experience | Behavior |
|------------|----------|
| `beginner` | Verbose explanations, show context tips, more hand-holding |
| `intermediate` | Balanced — explain when relevant, skip basics |
| `advanced` | Minimal — get out of the way, route fast |

**First-time** (no config, thin reference): Be verbose, route to /setup
**Returning** (config exists): Quick confirmation, route by intent
**Expert** (advanced experience, clear intent): Get out of the way, route fast

**Updating experience:** If user says "I know what I'm doing" or similar, offer to update their experience level in local.yaml.

---

## Intent Keywords

Auto-detect user intent and route. Skills: `/pull`, `/help`, `/setup`, `/think`, `/ads`, `/vsl`, `/organic`, `/newsletter`, `/site`, `/wiki`, `/end`. Some skills spawn parallel subagents automatically.

| Keywords | Route To |
|----------|----------|
| "what should I work on", "help me prioritize", "what to do next", "figure out what to work on", "deep triage" | Option 1 → Triage (see [triage-agent.md](references/triage-agent.md)) |
| "help", "confused", "stuck", "don't understand", "how do I" | `/help` |
| "new", "first time", "get started", "set up" | `/setup` |
| "add", "update", "more context", "new testimonials", "enrich" | `/think codify` |
| "research", "decide", "figure out", "explore", "mine", "mining", "competitors", "transcribe" | `/think` |
| "content strategy", "pillars", "platforms", "cadence", "content plan", "distribution" | `/think` |
| "soul check", "is this still right", "feeling obligated", "pull or push" | `/think codify` (soul.md review) |
| "newsletter", "email", "beehiiv", "weekly email" | `/newsletter` (coming soon — route to `/think` for now) |
| "ads", "copy", "static", "image ads", "video ads", "review", "compliance" | `/ads` |
| "vsl", "sales video", "about page video", "b2b video" | `/vsl` |
| "content", "reels", "tiktok", "organic", "carousel" | `/organic` |
| "site", "landing page", "lander", "minisite", "website", "one-pager", "spin up a site", "deploy site", "put this online", "I need a site", "publish site", "graduate my site", "add a CMS to my site", "/start launch" | `/site` (or `/start launch <offer>` for the speedrun orchestration) |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/wiki` |
| "pull", "update vip", "get latest" | `/pull` |
| "done", "wrapping up", "end my day", "closing out", "call it a day", "that's it" | `/end` |

---

## Recovering from Compaction

If re-invoked after compaction: re-read `~/.config/vip/local.yaml` for repo + identity, and `.vip/local.yaml` in the business repo for `current_offer`. Don't re-prompt — confirm: "Restored offer context: **[offer-name]**."

---

## References

- [references/pull-engine-updates.md](references/pull-engine-updates.md) — Step 1 + Step 3 pull scripts and failure warnings
- [references/repo-detection.md](references/repo-detection.md) — Step 2 full CWD detection, migration, multi-repo selection, REPO_PATH, vip-loaded verification
- [references/triage-menu.md](references/triage-menu.md) — Step 10 CHANGELOG banner, menu, "while you wait" pattern, auto-suggest/skip rules
- [references/auto-heal.md](references/auto-heal.md) — Bridge link recovery
- [references/config-system.md](references/config-system.md) — Config loading and recovery
- [references/mcp-preflight.md](references/mcp-preflight.md) — MCP pre-flight checks
- [references/readiness-assessment.md](references/readiness-assessment.md) — Step 6 readiness scoring
- [references/tool-status-audit.md](references/tool-status-audit.md) — Step 5 self-heal
- [references/triage-agent.md](references/triage-agent.md) — Triage agent prompts and synthesis

---

## Remember

Router, not worker. Detect → route → let the skill do the work. One clarifying question max. Skill loads its own context — main stays lean.
