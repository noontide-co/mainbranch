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

Search working directories for `reference/core/`. Skip vip (has `.claude/skills/`).

**ONE found:** Use it. "Using [name]. Ready to work."

**MULTIPLE found:** Always include options 3 and 4:

> "I found these business repos:
>
> 1. [first-repo-name]
> 2. [second-repo-name]
> 3. Another one (tell me the path)
> 4. Create new (`/setup`)
>
> Which one? (hit a number)"

**NONE found:** Check nested folders, then route to `/setup`.

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
| No `reference/core/` | Add via `/add-dir` |
| Nested repo | Search parent folders |
| Multiple repos | Ask which one |
| Repo exists but not added | Get path, tell them `/add-dir` |

Search working directories each session (don't persist paths).

---

## Daily Workflow

`cd vip && claude` → `/start`. Pulls updates, loads repo, routes.

---

## Don't Overthink

Router, not worker. Detect state → route → let that skill work. If uncertain, one clarifying question, then route.
