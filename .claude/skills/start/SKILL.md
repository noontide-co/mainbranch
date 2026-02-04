---
name: start
description: "Main entry point for Main Branch. Detects state and routes to the right skill. Use when: user says start/help/begin, is new/returning/lost, opens vip without a task, or needs triage. Routes to /setup, /think, /ads, /vsl, /organic, /wiki, /help."
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Recommended workflow:** Always start Claude in vip, run `/start`. It handles everything.

---

## CRITICAL: Always Ask Which Repo

**Even if config exists with a saved default, ALWAYS ask the user which repo before proceeding:**

> "Found saved repo:
>
> 1. [saved-repo-name] (saved)
> 2. Switch to different repo
>
> (hit a number)"

Replace `[saved-repo-name]` with the actual folder name from config (e.g., "acme-coaching", "client-project").

**DO NOT skip this question.** Users have multiple repos. The saved default is a suggestion, not automatic.

**Only exception:** User explicitly ran `/start [repo-name]` with a specific path.

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

Run `git pull origin main` on vip silently. Mention only if updates pulled. Don't block on network issues.

```bash
cd ~/Documents/GitHub/vip 2>/dev/null && git pull origin main 2>/dev/null || true
```

---

## Step 0: Load Config and Find Business Repo

### Config Reading Flow

```
1. Read ~/.config/vip/local.yaml
   ├── Found? → Get default_repo + user identity
   │            Validate path exists and has reference/core/
   │            ├── Valid? → STILL ASK (see below)
   │            └── Invalid? → Clear config, fall to discovery
   └── Missing? → Fall to discovery

2. If repo found, read [repo]/.vip/config.yaml
   ├── Found? → Get team settings, MCP requirements
   └── Missing? → Use defaults, offer to create later
```

### CRITICAL: Always Offer Switch Option

**Even with valid config, ALWAYS present numbered options:**

> "Found saved repo:
>
> 1. [saved-repo-name] (saved) ← use this
> 2. Switch to different repo
>
> (hit a number)"

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

**Verify with Read, not Glob:** Once you have a candidate path, use `Read` on `[path]/reference/core/offer.md` to confirm it exists.

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

## Step 1: Load Business Context

Read these files (in order) to prep Claude:

```
[repo]/CLAUDE.md                    - Business brain
[repo]/reference/core/soul.md       - WHY (philosophy, beliefs)
[repo]/reference/core/offer.md      - WHAT (product, pricing)
[repo]/reference/core/audience.md   - WHO (pains, desires)
[repo]/reference/core/voice.md      - HOW (tone, vocabulary)
```

**Missing files?** Skip silently. If 2+ core files missing → `/think codify`.

**Multi-offer context:** If `current_offer` is set (see Step 1.5), also load `reference/offers/[current_offer]/offer.md`. This is the active offer — it takes precedence over `core/offer.md` for offer-specific details. `core/offer.md` becomes the brand-level thesis. If `offers/[current_offer]/audience.md` exists, load it too (offer-specific audience override).

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

## Step 2: Detect State

Check `reference/core/*.md`. No folder → `/setup`. Exists → check completeness.

---

## Step 2: Assess Completeness

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

**Show context:** Before presenting options, show: "Business: **[repo name]** | Offer: **[current_offer or 'single']**"

If user is ready to work, ask or infer intent. **Use numbered options:**

> "Your reference files look good. What would you like to do?
>
> 1. Enrich the core (research, decide, mine) → `/think`
> 2. Create ads (image or video) → `/ads`
> 3. Write a VSL script → `/vsl`
> 4. Create organic content → `/organic`
> 5. Write a newsletter → `/newsletter` (coming soon — use `/think` for now)
> 6. Work on my wiki → `/wiki`
> 7. Add more context → `/think codify`
> 8. Get help → `/help`
>
> (hit a number to reply, or just tell me what you need)"

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
| `/organic` | Mine competitors, generate organic scripts |
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
| "help", "confused", "stuck", "don't understand", "how do I" | `/help` |
| "new", "first time", "get started", "set up" | `/setup` |
| "add", "update", "more context", "new testimonials", "enrich" | `/think codify` |
| "research", "decide", "figure out", "explore", "mine", "mining", "transcribe" | `/think` |
| "content strategy", "pillars", "platforms", "cadence", "content plan" | `/think` |
| "newsletter", "email", "beehiiv", "weekly email" | `/newsletter` (coming soon — route to `/think` for now) |
| "ads", "copy", "static", "image ads", "video ads", "review", "compliance" | `/ads` |
| "vsl", "sales video", "about page video", "b2b video" | `/vsl` |
| "content", "reels", "tiktok", "organic", "mine", "competitors", "carousel" | `/organic` |
| "site", "landing page", "website", "deploy site", "put this online", "I need a site" | `/site` |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/wiki` |
| "pull", "update vip", "get latest" | `/pull` |
| "done", "wrapping up", "end my day", "closing out", "call it a day", "that's it" | `/end` |

---

## Recovering from Compaction

If the conversation compacts and /start is re-invoked:

1. Re-read `~/.config/vip/local.yaml` for `default_repo` and user identity
2. Re-read the business repo's context files
3. **Offer recovery:** Read `.vip/local.yaml` in the business repo for `current_offer` to restore offer context after compaction. Don't re-prompt for offer selection if the file exists — just confirm: "Restored offer context: **[offer-name]**."

---

## Remember

Router, not worker. Detect state → route → let the target skill do the work. One clarifying question max.

**Three jobs:**
1. Orient Claude to the business (load reference)
2. Understand what user needs (ask if unclear)
3. Route to the right skill (fast)
