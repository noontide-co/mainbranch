---
name: start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens vip without a task, or needs triage. Routes to /setup, /think, /ads, /vsl, /organic, /wiki, /help."
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Always start Claude in vip, run `/start`. It handles everything.

---

## CRITICAL: Always Ask Which Repo

**Even if config exists with a saved default, ALWAYS ask the user which repo before proceeding.** List ALL validated repos from `recent_repos`, not just the default:

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

**DO NOT skip this question.** Users have multiple repos. The saved default is a suggestion, not automatic.

**Only exception:** User explicitly ran `/start [repo-name]` with a specific path.

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
├── Pull engine updates ──────────────→ (vip, always, silently)
│
├── Load config ──────────────────────→ See [config-system.md](references/config-system.md)
│   ├── ~/.config/vip/local.yaml ─────→ Default repo + user identity (name, experience)
│   └── [repo]/.vip/config.yaml ──────→ Team settings, MCP requirements
│
├── MCP pre-flight ───────────────────→ See [mcp-preflight.md](references/mcp-preflight.md)
│   └── Missing required MCP? ────────→ Offer setup or skip
│
├── Find business repo ───────────────→ (from config OR discovery)
│
├── No business repo configured? ─────→ /setup (creates repo, saves path)
│
├── Pull business repo updates ───────→ (your repo, silently)
│
├── Offer detection ──────────────────→ (multi-offer only, see Step 1.5)
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

## Step -1: Pull Updates

Pull vip updates. **Do NOT silently swallow failures.** Users on stale code get broken features.

```bash
# Pull vip updates — capture result
git pull origin main 2>&1
```

**Handle the result:**

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "Updating..." / files changed | "Pulled latest updates." |
| Any error (auth, network, not a repo) | Show the warning below |

**If pull fails, show this warning immediately:**

> "I wasn't able to pull the latest Main Branch updates. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. **GitHub Desktop not running?** Open it and make sure you're signed in
> 2. **Subscription inactive?** Check your Main Branch access in Skool
> 3. **Network issue?** Check your internet connection
> 4. **Try manually:** Open GitHub Desktop → select vip → click 'Fetch origin'
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale vip is the #1 cause of "why doesn't X work" support questions.

---

## Step 0: Load Config and Find Business Repo

### Config Reading Flow

```
1. Read ~/.config/vip/local.yaml
   ├── Found? → Get default_repo + recent_repos + user identity
   │            Validate ALL paths (see Path Validation below)
   │            ├── All valid? → Present valid options
   │            ├── Some invalid? → Attempt recovery, prune dead paths
   │            └── All invalid? → Clear config, fall to discovery
   └── Missing? → Fall to discovery

2. If repo found, read [repo]/.vip/config.yaml
   ├── Found? → Get team settings, MCP requirements
   └── Missing? → Use defaults, offer to create later
```

### Path Validation (Before Presenting Options)

**Validate EVERY path in config before showing it to the user.** Never present a dead path as an option. For each path in `default_repo` and `recent_repos`, check `test -d "[path]/reference/core"`. If invalid, attempt recovery (check sibling folders for a renamed repo) and auto-prune dead entries. See [config-system.md](references/config-system.md) for the full recovery algorithm.

### CRITICAL: Always Offer Switch Option

**Even with valid config, ALWAYS list ALL validated repos from `recent_repos` as numbered options** (see top-level "Always Ask Which Repo" section for templates). Never show just the default — users switch repos and shouldn't have to type paths.

**Why:** Users may have multiple business repos. The saved default is a convenience, not a lock-in. Skipping this question traps users in one repo.

**Only skip the question if:** User explicitly said `/start [repo-name]` with a specific repo.

**Shortcut:** If user says `/start [repo-name]` or mentions a specific repo, validate that path directly with Read. If valid, confirm with user and proceed.

**Config path (fast):** Check `~/.config/vip/local.yaml` for `default_repo` and `user.*`. See [config-system.md](references/config-system.md).

**Why Glob fails:** User may have added subdirectories (like `decisions/` or `research/`) as additional working directories, not the parent repo. Glob from vip can't traverse up to find `reference/core/`.

**Discovery algorithm (when no config):**

1. **Extract parent paths from additional working directories**
   - Look at env info for "Additional working directories"
   - For each path, walk up to find a folder containing `reference/core/`
   - Example: if `main-branch/decisions` is listed, check `main-branch/reference/core/`

2. **Use bash to find repos** (if step 1 fails)
   ```bash
   find ~/Documents/GitHub -maxdepth 3 -type d -name "reference" -exec test -d "{}/core" \; -print 2>/dev/null
   ```

3. **Ask the user** (if nothing found)

**Verify with Read, not Glob:** Once you have a candidate path, use `Read` on `[path]/reference/core/soul.md` to confirm it's a business repo. (Don't check `core/offer.md` — in multi-offer repos, the primary offer details live in `offers/[name]/offer.md` instead. `soul.md` is always in `core/`.)

**Skip vip** — any path containing `.claude/skills/` is the engine, not a business repo.

**ALWAYS present numbered options** — even with ONE repo found:

> "I found this business repo:
>
> 1. [repo-name]
> 2. Another one (tell me the path)
> 3. Create new (`/setup`)
> 4. I'm confused (`/help`)
>
> Which one? (hit a number)"

**MULTIPLE found:** List all, then options 2-4 above.

**NONE found:** Ask user for path, or route to `/setup`.

### After User Selects Repo

**Offer to save to config:**

> "Want me to save [repo-name] as your default? (faster startup next time)"

If yes, update `~/.config/vip/local.yaml`:

```yaml
default_repo: /full/path/to/repo
recent_repos:
  - /full/path/to/repo
user:
  name: "[ask if not set]"
  experience: "[ask if not set]"  # beginner | intermediate | advanced
```

**If user.name or user.experience missing:** Ask once, save for future sessions.

---

## Step 0.5: Pull Business Repo Updates

Once business repo is confirmed, pull its latest updates:

```bash
cd [repo-path] && git pull origin main 2>/dev/null || true
```

**Why both repos:**
- Engine (vip) → new skills, playbooks, compliance frameworks
- Business repo → your reference files, decisions, research

If you work across machines or collaborate, your business repo may have changes. Pull them.

**Mention only if updates:** "Pulled latest updates for [repo-name]" — otherwise stay silent.

---

## Step 0.75: MCP Pre-Flight (Not Research Tools)

Check for MCPs required by skills user might invoke. See [mcp-preflight.md](references/mcp-preflight.md).

**Research tool detection happens in /think** — deferred to when user actually needs research. This keeps /start fast and avoids checking tools user might not use this session.

**What /start DOES check:**
- MCPs that skills depend on (Apify for /organic, etc.)
- Critical blockers (missing config, broken paths)

**What /start DOES NOT check:**
- Research tools (Gemini, Grok, whisper, etc.) — /think handles these
- Document tools (markitdown, pandoc, marker) — /think handles these

**Why defer:** Most sessions don't use all tools. Checking everything upfront wastes time and clutters the greeting. /think detects tools when user's intent requires them and surfaces setup options at the right moment.

If user's stated intent involves research, route to /think — it will handle tool detection with config-first logic (reads `.vip/config.yaml`, only probes unknowns, updates config with results).

---

## Step 0.9: Readiness Assessment

**Run AFTER MCP pre-flight, BEFORE routing.** Scores reference files, checks session state, and gates routing so users don't jump into output skills with thin context.

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

## Step 1: Defer Full Context Loading

**Do NOT read full reference files into main.** Readiness (Step 0.9) already scored them — that's enough for routing. Full context loading happens in the selected skill or triage agents, not here.

**Why:** Reading soul.md + offer.md + audience.md + voice.md into main burns 15-30K tokens that get duplicated when the skill re-reads them. The triage test showed /start hitting 61% context before any work began. Main stays lean; skills/agents load what they need.

**What main knows after Step 0.9:** Readiness scores, which files exist, composite score, gaps. That's enough to present the menu and gate routing.

**Exception:** Read `[repo]/CLAUDE.md` (the business brain) — it's small and needed for personality/routing awareness. Skip the 4 core reference files.

**Multi-offer context:** If `current_offer` is set (see Step 1.5), note the active offer for routing. Don't load the offer file — the selected skill will.

---

## Step 1.5: Offer Detection (Multi-Offer Only)

After loading core context, check for multi-offer:

```bash
ls reference/offers/*/offer.md 2>/dev/null
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

## Step 2: Detect State and Assess Completeness

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

## Step 3: Route by Intent

**Respect readiness gates from Step 0.9.** If status is MINIMAL or EMPTY, do not offer output skills. If THIN, warn. See [readiness-assessment.md](references/readiness-assessment.md) for skill-specific requirements.

**Show context:** Before presenting options, show: "Business: **[repo name]** | Offer: **[current_offer or 'single']**"

If user is ready to work, ask or infer intent. **Use numbered options:**

### Triage (Option 1 — User-Initiated)

**Triage is option 1 on the menu.** It runs when the user selects it or when intent keywords match. It does NOT run automatically every session. This keeps /start fast and preserves context for actual work.

**Why not always-on:** Three parallel agents burn 50-80K tokens. Running them every session means the user starts at 60%+ context before doing anything. /end gates crystallize behind meaningful activity — /start gates triage behind user choice.

**Present the menu:**

> "What would you like to do?
>
> 1. **What should I focus on?** (triage — analyzes your full state) → see [triage-agent.md](references/triage-agent.md)
> 2. Enrich the core (research, decide, codify) → `/think`
> 3. Create ads (image or video) → `/ads`
> 4. Write a VSL script → `/vsl`
> 5. Create organic content → `/organic`
> 6. Work on my wiki → `/wiki`
> 7. Build/update a site → `/site`
> 8. Add more context → `/think codify`
> 9. Get help → `/help`
>
> (hit a number, or just tell me what you need)"

**When user picks option 1:** Spawn triage agents. See [triage-agent.md](references/triage-agent.md) for gating, tiered spawning, agent prompts, and synthesis format.

**While agents work:** Set expectations, then give them something to chew on:

> "Spinning up [1/2/3] analysis agents — this takes about **2-3 minutes**. They're reading your full reference, decisions, git history, and soul alignment so I can give you something actually useful.
>
> **Good news:** These run as sub-agents in their own context windows, so they won't eat into your session. You'll still have plenty of room for whatever comes next.
>
> While we wait: [pick ONE at random per session]
> - *The word 'decide' comes from Latin 'decidere' — literally 'to cut off.' Every decision is choosing what to let go of.*
> - *Hemingway rewrote the ending of A Farewell to Arms 47 times. When asked why, he said: 'Getting the words right.'*
> - *The best time to plant a tree was 20 years ago. The second best time is now.*
> - *Your reference files are like compound interest — small deposits now, massive returns later.*
> - *'If you can't explain it simply, you don't understand it well enough.' — Einstein. That's what codifying does.*
> - *Fun fact: the average person mass-produces 50K+ words a day in their head. You're one of the few who actually filters those into something useful.*"

**Auto-suggest option 1 when:**
- Returning user (last commit >3 days ago) and no stated intent
- Readiness is THIN (8-11) — "Option 1 can help you figure out the highest-leverage gap"
- User says "what should I work on", "help me prioritize", "what to do next"

**Skip triage entirely when:**
- Readiness is EMPTY or MINIMAL (0-7) — answer is obvious: `/setup` or `/think`
- User stated clear intent with `/start ads` or similar

If user already stated intent, route directly without asking.

---

## Step 4: Help Mode

"Help" or confused → route to `/help`. Give quick overview first:

> "1. **vip** = engine (skills). 2. **Your repo** = data (offer, audience, voice).
> Daily: `cd vip && claude` then `/start`.
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

## Skill Quick Reference

| Skill | What It Does |
|-------|--------------|
| `/pull` | Pull latest vip updates |
| `/help` | Get answers, troubleshoot, learn |
| `/setup` | Create business repo from scratch |
| `/think` | Enrich the core — research, decide, codify into reference |
| `/ads` | Generate image ads, video scripts, or review for compliance |
| `/vsl` | Write video sales letters (Skool or B2B frameworks) |
| `/organic` | Generate organic content from reference + research |
| `/newsletter` | Generate weekly newsletter from thinking work (coming soon) |
| `/site` | Generate and deploy landing pages from reference files |
| `/wiki` | Create atomic notes, publish wiki |
| `/end` | Close session — summary, crystallize, commit |

Skills like `/think` and `/ads review` automatically spawn parallel subagents when the task benefits (e.g., multi-source research, 6-lens compliance review). This makes complex work faster and keeps your main context window clean. No action needed on your part.

---

## Intent Keywords

Use these to auto-detect what user wants:

| Keywords | Route To |
|----------|----------|
| "what should I work on", "help me prioritize", "what to do next", "figure out what to work on" | Option 1 → Triage (see [triage-agent.md](references/triage-agent.md)) |
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
| "site", "landing page", "website", "deploy site", "put this online", "I need a site" | `/site` |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/wiki` |
| "pull", "update vip", "get latest" | `/pull` |
| "done", "wrapping up", "end my day", "closing out", "call it a day", "that's it" | `/end` |

---

## Recovering from Compaction

If re-invoked after compaction: re-read `~/.config/vip/local.yaml` for repo + identity, and `.vip/local.yaml` in the business repo for `current_offer`. Don't re-prompt — confirm: "Restored offer context: **[offer-name]**."

---

## Remember

Router, not worker. Detect → route → let the skill do the work. One clarifying question max. Skill loads its own context — main stays lean.
