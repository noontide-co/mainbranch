---
name: start
description: |
  Main entry point for Main Branch. Detects user state and routes to the right skill. Use when user is new, returning, lost, or says "start", "help", "what can I do". Routes to /setup, /enrich, /think, /ad-static, /ad-video-scripts, /ad-review, /content, /skool-manager, /skool-vsl-scripts.
---

# Start

Single entry point for Main Branch. Detect user state, route to the right skill.

**Recommended workflow:** Always start Claude in vip, run `/start`. It handles everything.

---

## Numbered Options Pattern

**Always use numbered lists for multi-choice prompts.** This lets users reply with just a number.

```
1. Option one
2. Option two
3. Option three

(hit a number to reply)
```

Apply this pattern to: business repo selection, skill routing, any multiple choice.

---

## Detection Flow

```
/start
│
├── Pull latest vip updates ──────────→ (always, silently)
│
├── Load business repo automatically ─→ (from settings.local.json)
│
├── No business repo configured? ─────→ /setup (creates repo, saves path)
│
├── Has repo but thin? ───────────────→ /enrich
│   (reference files exist but incomplete)
│
├── Ready to work? ───────────────────→ Route by intent:
│   │
│   ├── "research" / "decide" ────────→ /think
│   ├── "ads" / "copy" ───────────────→ /ad-static or /ad-video-scripts
│   ├── "review" / "compliance" ──────→ /ad-review
│   ├── "content" / "organic" ────────→ /content
│   ├── "skool" / "community" ────────→ /skool-manager
│   ├── "vsl" / "sales video" ────────→ /skool-vsl-scripts
│   ├── "help" / questions ───────────→ /help
│   └── unclear ──────────────────────→ Show options + mention /help
│
└── "confused" / "stuck" ─────────────→ /help
```

---

## Step -1: Pull Latest Updates (Always Do This)

**Before anything else, ensure vip has the latest skills:**

```bash
# If we're in vip:
if [ -f ".claude/skills/start/SKILL.md" ]; then
  git pull origin main 2>/dev/null || true
fi
```

**If updates were pulled:**
> "Pulled latest updates from vip."

**If already up to date or offline:** Continue silently (don't block on network issues).

---

## Step 0: Find Business Repo

**Search all working directories for business repos (folders with `reference/core/`).**

1. List working directories (vip + any added via `/add-dir`)
2. For each, check if `reference/core/*.md` exists
3. Skip vip (has `.claude/skills/`, not `reference/core/`)

**If ONE business repo found:** Use it. Confirm briefly: "Using [name]. Ready to work."

**If MULTIPLE business repos found:** Number the options so user can reply with just a number:
> "I found these business repos:
> 1. [repo-name-1]
> 2. [repo-name-2]
> 3. Another one (tell me the path)
> 4. Create new (/setup)
>
> Which one? (hit a number to reply)"

**If NONE found:**
- Check if user has a parent folder with multiple businesses inside (like `noontide-projects/main-branch/`)
- If found nested, use that
- If truly none, route to `/setup`

**Note:** `/add-dir` is a Claude Code command, not bash. Don't try to run it via Bash tool. The user adds directories through the Claude Code interface or it's already in their workspace.

---

## Step 1: Detect State

Check for business repo structure:

```bash
# Check if reference folder exists with content
ls reference/core/*.md 2>/dev/null | head -3
```

**If no reference/ folder:** User is new → Route to `/setup`

**If reference/ exists:** Check completeness by reading core files.

---

## Step 2: Assess Completeness

If repo exists, quick-scan key files:

| Check | How |
|-------|-----|
| offer.md exists and has content | >50 lines or has "Price" section |
| audience.md exists and has content | >30 lines or has "Pains" section |
| voice.md exists and has content | >20 lines or has "Tone" section |

**If 2+ files are empty/missing:** Suggest `/enrich` to fill gaps

**If files look complete:** Ready to work — ask what they want to do

---

## Step 3: Route by Intent

If user is ready to work, ask or infer intent. **Use numbered options:**

> "Your reference files look good. What would you like to do?
>
> 1. Research a topic → `/think`
> 2. Create ad copy → `/ad-static` or `/ad-video-scripts`
> 3. Review ads for compliance → `/ad-review`
> 4. Create organic content → `/content`
> 5. Write a VSL script → `/skool-vsl-scripts`
> 6. Manage Skool community → `/skool-manager`
> 7. Add more context → `/enrich`
> 8. Get help → `/help`
>
> (hit a number to reply, or just tell me what you need)"

If user already stated intent, route directly without asking.

---

## Step 4: Help Mode

If user says "help" or seems confused, route to `/help` for comprehensive answers.

Quick overview to give before routing:

> "Main Branch works like this:
>
> 1. **vip** is the engine (skills, templates) — you always start here
> 2. **Your business repo** has your data (offer, audience, voice, proof)
> 3. **`/start`** loads your business repo automatically and routes you
>
> **Daily workflow:**
> ```
> cd ~/Documents/GitHub/vip && claude
> /start
> ```
>
> **For detailed help:** Type `/help` followed by your question. It has comprehensive answers about Terminal basics, the two-repo model, troubleshooting, skills, and more.
>
> What would you like to do?"

---

## Skill Quick Reference

| Skill | What It Does | When to Use |
|-------|--------------|-------------|
| `/pull` | Pull latest vip updates | Quick update check |
| `/help` | Get answers, troubleshoot, learn | Confused, stuck, have questions |
| `/setup` | Create business repo from scratch | First-time users |
| `/enrich` | Add context to existing repo | Returning users with gaps |
| `/think` | Research topics, make decisions | Before committing to an approach |
| `/ad-static` | Generate image ad copy | Need Meta ad copy |
| `/ad-video-scripts` | Generate video ad scripts | Need 15-60s video scripts |
| `/ad-review` | Check ads for compliance | Before running ads |
| `/content` | Mine competitors, generate organic scripts | Reels, TikTok, carousels |
| `/skool-manager` | Manage community engagement | Daily Skool tasks |
| `/skool-vsl-scripts` | Write video sales letters | Need VSL for about page |

---

## Intent Keywords

Use these to auto-detect what user wants:

| Keywords | Route To |
|----------|----------|
| "help", "confused", "stuck", "don't understand", "how do I" | `/help` |
| "new", "first time", "get started", "set up" | `/setup` |
| "add", "update", "more context", "new testimonials" | `/enrich` |
| "research", "decide", "figure out", "explore" | `/think` |
| "ads", "copy", "static", "image ads", "primaries" | `/ad-static` |
| "video ads", "ad scripts", "hooks", "ugc" | `/ad-video-scripts` |
| "review", "compliance", "ftc", "check" | `/ad-review` |
| "content", "reels", "tiktok", "organic", "mine", "competitors", "carousel" | `/content` |
| "skool", "community", "posts", "respond" | `/skool-manager` |
| "vsl", "sales video", "about page video" | `/skool-vsl-scripts` |

---

## Troubleshooting: Business Repo Not Found

| Problem | Solution |
|---------|----------|
| No `reference/core/` found | User needs to add their business repo via `/add-dir` in Claude Code |
| Business repo nested (e.g., `projects/main-branch/`) | Search inside parent folders for `reference/core/` |
| Multiple business repos | Ask which one to use for this session |
| User has repo but not added | Ask for the path, then tell them to `/add-dir` it |

**Key insight:** Don't try to persist paths to settings.json (strict schema). Just search working directories each session.

---

## Daily Workflow (Tell Users This)

```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's it. `/start` pulls updates, loads the business repo, and routes to the right skill.

---

## Don't Overthink

This skill is a router, not a worker.

- Detect state quickly
- Route to the right skill
- Let that skill do the heavy lifting

If uncertain, ask one clarifying question, then route.
