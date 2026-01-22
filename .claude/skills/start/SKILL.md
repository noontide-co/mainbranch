---
name: start
description: Main entry point for Main Branch. Detects user state and routes to the right skill. Use when: (1) User says "start", "help", "what can I do", "begin" (2) User is new, returning, lost, or confused (3) User opens vip without a specific task in mind (4) Session starts and user needs triage. Routes to /setup (new users), /enrich (thin repos), /think (research/decide), /ad-static, /ad-video-scripts, /ad-review, /content, /skool-manager, /skool-vsl-scripts, /help.
---

# Start

Single entry point for Main Branch. Detect user state, route to the right skill.

**Recommended workflow:** Always start Claude in vip, run `/start`. It handles everything.

---

## Numbered Options Pattern

Always use numbered lists for multi-choice. User replies with just a number.

Apply to: business repo selection, skill routing, any multiple choice.

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

2+ empty/missing → `/enrich`. Complete → route by intent.

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
| `/enrich` | Add context to existing repo |
| `/think` | Research topics, make decisions |
| `/ad-static` | Generate image ad copy |
| `/ad-video-scripts` | Generate video ad scripts |
| `/ad-review` | Check ads for compliance |
| `/content` | Mine competitors, generate organic scripts |
| `/skool-manager` | Manage community engagement |
| `/skool-vsl-scripts` | Write video sales letters |

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

## Remember

Router, not worker. Detect state → route → let the target skill do the work. One clarifying question max.
