---
name: start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens vip without a task, or needs triage. Routes to /setup, /think, /ads, /vsl, /organic, /wiki, /help."
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Start Claude in your business repo, run `/start`. It handles everything. Skills load automatically from vip via `additionalDirectories`.

---

## CRITICAL: Repo Selection Rules

**CWD-first wins.** If `reference/core/` exists in CWD, the user is already in their business repo — no selection needed. Just confirm: "Working in **[repo-name]**."

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
- CWD has `reference/core/` — user chose their repo by cd'ing into it
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
├── Detect business repo ─────────────→ CWD-first detection (see Step 0)
│   ├── CWD has reference/core/? ─────→ This IS the repo. Proceed.
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

## Step -1: Pull Engine Updates

Pull vip updates. CWD is the business repo — resolve vip path first. **Do NOT silently swallow failures.** Users on stale code get broken features.

```bash
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

**Handle the result:**

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "Updating..." / files changed | "Pulled latest engine updates." |
| VIP_PATH empty (not found) | "Couldn't find vip. Run `/setup` to configure, or check `~/.config/vip/local.yaml`." |
| Any error (auth, network) | Show the warning below |

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

## Step 0: Detect Business Repo (CWD-First)

The user starts Claude in their business repo. Check CWD first before falling back to config.

### CWD Detection (Primary — Fast Path)

```
1. Check CWD for business repo fingerprint:
   test -d "reference/core"
   ├── YES → This IS the business repo. Use CWD. Skip to config loading.
   └── NO → Continue to step 2.

2. Check CWD for vip fingerprint (old workflow):
   test -f ".claude/skills/start/SKILL.md"
   ├── YES → User is in vip (old workflow). Trigger migration guidance.
   └── NO → Continue to step 3.

3. Fall back to config:
   Read ~/.config/vip/local.yaml → default_repo + recent_repos
   ├── Found valid repo(s)? → Present options (see below)
   └── Nothing valid? → Discovery or /setup
```

**Migration guidance (step 2 — user is in vip):**

> "It looks like you're running Claude inside the vip engine folder. The recommended workflow is now to run Claude from your business repo instead.
>
> 1. **Quick switch:** Close this session, `cd [their-repo-path]` then `claude` then `/start`
> 2. **Need setup help?** `/setup` will configure everything
> 3. **Continue here anyway** (some features may need manual paths)"
>
> If `~/.config/vip/local.yaml` has `default_repo`, show that path in option 1.

### Config Loading

Once business repo is identified (from CWD or config), load settings:

```
1. Read ~/.config/vip/local.yaml
   ├── Found? → Get vip_path + default_repo + recent_repos + user identity
   └── Missing? → Acceptable if CWD is the repo; config gets created by /setup

2. Read [repo]/.vip/config.yaml
   ├── Found? → Get team settings, MCP requirements
   └── Missing? → Use defaults, offer to create later
```

### Multi-Repo Selection (When CWD Is NOT a Business Repo)

If CWD detection fails (step 3 above), present options from config:

**Validate EVERY path in config before showing it to the user.** Never present a dead path as an option. For each path in `default_repo` and `recent_repos`, check `test -d "[path]/reference/core"`. If invalid, attempt recovery (check sibling folders for a renamed repo) and auto-prune dead entries. See [config-system.md](references/config-system.md) for the full recovery algorithm.

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

**Discovery algorithm (when no config):** Use fallbacks in order:

1. **Scan additionalDirectories** for paths containing `reference/core/`
2. **Use bash to find repos** (if step 1 fails)
   ```bash
   find ~/Documents/GitHub -maxdepth 3 -type d -name "reference" -exec test -d "{}/core" \; -print 2>/dev/null
   ```
3. **Ask the user** (if nothing found)

**Verify with Read, not Glob:** Use `Read` on `[path]/reference/core/soul.md` to confirm it's a business repo. `soul.md` is always in `core/` (even multi-offer repos).

**Skip vip** — any path containing `.claude/skills/start/SKILL.md` is the engine, not a business repo.

### When CWD IS the Business Repo (Happy Path)

No repo selection needed. Confirm briefly and move on:

> "Working in **[repo-name]**."

If `~/.config/vip/local.yaml` doesn't have this repo saved, offer to save:

> "Want me to save [repo-name] as your default? (faster startup next time)"

If yes, update `~/.config/vip/local.yaml`:

```yaml
vip_path: /path/to/vip
default_repo: /full/path/to/repo
recent_repos:
  - /full/path/to/repo
user:
  name: "[ask if not set]"
  experience: "[ask if not set]"  # beginner | intermediate | advanced
```

**If user.name or user.experience missing:** Ask once, save for future sessions.

### Verify vip Is Loaded (Config + Compatibility Links)

After detecting the business repo, confirm vip is accessible and `/start` bridge exists:

```bash
# 1. Check additionalDirectories config
VIP_PATH=$(test -f ".claude/settings.local.json" && python3 -c "
import json, os
with open('.claude/settings.local.json') as f:
    dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
for d in dirs:
    if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
        print(d); break
" 2>/dev/null)

# 2. Check /start bridge exists in local .claude/skills
test -e ".claude/skills/start" && echo "START_BRIDGE_OK"
```

**If `additionalDirectories` missing:** Run `/setup` to configure.

**If bridge links missing** (but `additionalDirectories` exists): Repair without replacing local folders:
```bash
mkdir -p .claude/skills .claude/lenses .claude/reference

for d in "$VIP_PATH"/.claude/skills/*; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -e ".claude/skills/$n" ] || ln -s "$d" ".claude/skills/$n"
done

for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
  [ -e "$p" ] || continue
  base=$(basename "$p")
  parent=$(basename "$(dirname "$p")")
  [ -e ".claude/$parent/$base" ] || ln -s "$p" ".claude/$parent/$base"
done
```
Tell the user: "Repaired missing vip bridge links. Local custom skills are preserved."

**Why both are needed:**
- `additionalDirectories` = file access (read reference files, compliance docs)
- Bridge links = compatibility fallback for skill discovery in environments where settings-based discovery is inconsistent

---

## Step 0.5: Pull Business Repo Updates

Once business repo is confirmed, pull its latest updates. Since CWD IS the business repo, just pull directly:

```bash
git pull origin main 2>&1
```

**Handle the result:**

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "Updating..." / files changed | "Pulled latest updates for [repo-name]." |
| "fatal: 'origin' does not appear to be a git repo" | Say nothing — local-only repo, no remote configured |
| Any other error | Show the warning below |

**If pull fails (and repo has a remote):**

> "Couldn't pull updates for [repo-name]. You may be working on older reference files.
>
> Try: Open GitHub Desktop → select [repo-name] → click 'Fetch origin'"

**Why both repos:**
- Engine (vip) → new skills, playbooks, compliance frameworks
- Business repo → your reference files, decisions, research

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

> "1. **vip** = engine (skills, loaded automatically). 2. **Your repo** = data (offer, audience, voice).
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
