---
name: start
description: Main entry point for Main Branch. Detects user state, context level, and experience to route to the right skill. Use when: (1) User says "start", "help", "what can I do", "begin" (2) User is new, returning, lost, or confused (3) User opens vip without a specific task in mind (4) Session starts and user needs triage. Routes to /setup (new users), /think (research/decide/enrich), /ads (static/video/review), /vsl (skool/b2b), /content, /skool-manager, /wiki, /help.
---

# Start

Single entry point for Main Branch. Detect user state, context level, experience — route to the right skill.

**Core job:** Orient Claude to the user's business, then route to what they need.

---

## Philosophy: Never Assume

- **Don't assume noob** — Some users know exactly what they want
- **Don't assume expert** — Some users are lost but won't say so
- **Ask ONE clarifying question** when intent is unclear
- **Route fast** when intent is clear

---

## Context Awareness (Critical)

**Users must understand context management.** Teach as you route.

### Check Context State First

Before doing heavy lifting, assess where the session is:

| Context Level | What To Do |
|---------------|------------|
| Fresh (0-10%) | Full load: find repo, load reference, orient |
| Light (10-30%) | Reference may be loaded; verify before reloading |
| Working (30-70%) | Productive zone; route to task, don't reload |
| Heavy (70-85%) | Warn user; finish current work, new session soon |
| Critical (85%+) | "Context is nearly full. Let's wrap up this task, then start fresh." |

**Show context percentage** when relevant: "You're at about 60% context — plenty of room to work."

### Teach Context Management

When context is fresh, briefly explain:
> "I'm starting fresh — I don't have your business context yet. Let me load your reference files so I know your offer, audience, and voice."

When context is heavy, warn:
> "We're at about 80% context. I'd recommend finishing this task, then starting a new conversation for the next one."

---

## Config Check (Two-File System)

**Step 1: Check machine-local settings**

```bash
cat ~/.config/vip/local.yaml 2>/dev/null
```

This tells us which business repo is default on THIS machine:
```yaml
default_repo: ~/Documents/GitHub/my-business
```

**Step 2: Load business repo config**

If we have a repo path, load its config:
```bash
cat [repo]/.vip/config.yaml 2>/dev/null
```

This has all user preferences (synced via git):
- `user.experience` → Adjust verbosity
- `session.auto_load_reference` → Load core/ automatically
- `infrastructure.*` → Connected services

**If no local.yaml exists:** Check for old settings, then discovery flow.
**If repo found but no .vip/config.yaml:** Offer to create it (migration).

---

## Migration Logic (Existing Users)

Existing users may have:
- Old `~/.claude/settings.json` with `business_repo_path`
- Business repo WITHOUT `.vip/` folder

### Step 1: Check for Old Settings

```bash
cat ~/.claude/settings.json 2>/dev/null | grep business_repo_path
```

If found:
1. Extract the path
2. Offer to migrate: "I found your business repo in old settings. Want me to set up the new config system? (faster startups, syncs across machines)"
3. If yes:
   - Create `~/.config/vip/local.yaml` with that path
   - Continue to Step 2

### Step 2: Check for Missing .vip/ in Repo

Once we have a repo path (from local.yaml, old settings, or discovery):

```bash
ls [repo]/.vip/config.yaml 2>/dev/null
```

If `.vip/config.yaml` doesn't exist but repo has `reference/core/`:
> "Your business repo exists but doesn't have VIP config yet. Want me to create it?
> This enables: faster session starts, synced preferences across machines, infrastructure tracking."

If user says yes:
1. Create `.vip/config.yaml` with defaults
2. Ask their experience level (beginner/intermediate/advanced)
3. Save and continue

If user says no:
> "No problem. I'll use discovery mode. You can run `/setup upgrade` anytime to add config."

### Migration is Non-Breaking

| Scenario | What Happens |
|----------|--------------|
| New user, no repo | Normal /setup flow |
| Existing user, no config | Discovery works, offered upgrade |
| Existing user, accepts upgrade | Gets fast path going forward |
| Existing user, declines upgrade | Works exactly as before |

---

## Numbered Options Pattern

Always use numbered lists for multi-choice. User replies with just a number.

Apply to: business repo selection, skill routing, any multiple choice.

---

## Detection Flow

```
/start
│
├── Check context level ──────────────→ (are we fresh or continuing?)
│
├── Pull latest vip updates ──────────→ (always, silently)
│
├── Check local.yaml ─────────────────→ (~/.config/vip/local.yaml)
│   ├── Has default_repo? ────────────→ Load that repo
│   └── No local.yaml? ───────────────→ Check old settings (migration)
│       └── Has ~/.claude/settings.json? → Offer to migrate
│
├── Load repo's .vip/config.yaml ─────→ (user preferences)
│   └── No .vip/config.yaml? ─────────→ Offer to create (upgrade)
│
├── Load business repo ───────────────→ (from config OR discovery)
│
├── No business repo configured? ─────→ /setup (creates repo, saves path)
│
├── Has repo but thin? ───────────────→ /think codify
│   (reference files exist but incomplete)
│
├── Ready to work? ───────────────────→ Route by intent:
│   │
│   ├── "research" / "decide" ────────→ /think
│   ├── "ads" / "copy" ───────────────→ /ads (triages to static/video/review)
│   ├── "vsl" / "sales video" ────────→ /vsl (triages to skool/b2b)
│   ├── "content" / "organic" ────────→ /content
│   ├── "skool" / "community" ────────→ /skool-manager
│   ├── "wiki" / "notes" ─────────────→ /wiki
│   ├── "help" / questions ───────────→ /help
│   └── unclear ──────────────────────→ Show options + mention /help
│
└── "confused" / "stuck" ─────────────→ /help
```

---

## Step -1: Pull Updates (Always)

Run `git pull origin main` silently. Mention only if updates pulled. Don't block on network issues.

---

## Step 0: Find Business Repo

**Shortcut:** If user says `/start [repo-name]` or mentions a specific repo, validate that path directly with Read. If valid, confirm with user and proceed.

**Why Glob fails:** User may have added subdirectories (like `decisions/` or `research/`) as additional working directories, not the parent repo. Glob from vip can't traverse up to find `reference/core/`.

**Discovery algorithm (when no repo specified):**

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

---

## Step 1: Detect State

Check `reference/core/*.md`. No folder → `/setup`. Exists → check completeness.

---

## Step 2: Assess Completeness

| File | Complete If |
|------|------------|
| offer.md | >50 lines or "Price" section |
| audience.md | >30 lines or "Pains" section |
| voice.md | >20 lines or "Tone" section |

2+ empty/missing → `/think codify`. Complete → route by intent.

---

## Step 3: Route by Intent

If user is ready to work, ask or infer intent. **Use numbered options:**

> "Your reference files look good. What would you like to do?
>
> 1. Research a topic → `/think`
> 2. Create ads (image or video) → `/ads`
> 3. Write a VSL script → `/vsl`
> 4. Create organic content → `/content`
> 5. Manage Skool community → `/skool-manager`
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

## Skill Quick Reference

| Skill | What It Does |
|-------|--------------|
| `/pull` | Pull latest vip updates |
| `/help` | Get answers, troubleshoot, learn |
| `/setup` | Create business repo from scratch |
| `/think` | Research, decide, codify (includes adding context) |
| `/ads` | Generate image ads, video scripts, or review for compliance |
| `/vsl` | Write video sales letters (Skool or B2B frameworks) |
| `/content` | Mine competitors, generate organic scripts |
| `/skool-manager` | Manage community engagement |
| `/wiki` | Create atomic notes, publish wiki |

---

## Intent Keywords

Use these to auto-detect what user wants:

| Keywords | Route To |
|----------|----------|
| "help", "confused", "stuck", "don't understand", "how do I" | `/help` |
| "new", "first time", "get started", "set up" | `/setup` |
| "add", "update", "more context", "new testimonials", "enrich" | `/think codify` |
| "research", "decide", "figure out", "explore" | `/think` |
| "ads", "copy", "static", "image ads", "video ads", "review", "compliance" | `/ads` |
| "vsl", "sales video", "about page video", "b2b video" | `/vsl` |
| "content", "reels", "tiktok", "organic", "mine", "competitors", "carousel" | `/content` |
| "skool", "community", "posts", "respond" | `/skool-manager` |
| "wiki", "notes", "atomic", "wikilinks", "publish wiki" | `/wiki` |

---

## Adapting to User Experience

### First-Time Users (Detected: no config, thin reference)

Be more verbose. Explain what's happening:
> "Welcome to Main Branch! I'm going to help you set up your business repo. This is a one-time setup that teaches me about your offer, audience, and voice."

Route to `/setup` with encouragement.

### Returning Users (Detected: config exists, reference complete)

Be efficient. Quick confirmation:
> "Found your business: [name]. What are we working on today?"

Then numbered options or route by stated intent.

### Confused Users (Detected: "help", "stuck", "don't understand")

Don't assume what they're confused about. Ask:
> "Happy to help! What specifically is unclear?
> 1. How this system works
> 2. What to do next
> 3. Something technical isn't working
> 4. Something else"

Route to `/help` with context.

### Expert Users (Detected: clear intent, short messages)

Get out of the way. If they say "ads for my launch", don't ask 5 questions — route to `/ads` and let that skill handle details.

---

## Context Management Tips to Share

When appropriate, teach users these concepts:

1. **"Fresh session = fresh context"** — I don't remember previous conversations
2. **"/start loads your business"** — Run it first thing each session
3. **"Context fills up"** — Long sessions need to end and restart
4. **"Your reference is your memory"** — What's in those files is what I know

Don't lecture. Mention naturally when relevant.

---

## Remember

Router, not worker. Detect state → route → let the target skill do the work. One clarifying question max.

**Three jobs:**
1. Orient Claude to the business (load reference)
2. Understand what user needs (ask if unclear)
3. Route to the right skill (fast)
