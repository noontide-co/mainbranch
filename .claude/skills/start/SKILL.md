---
name: start
description: Main entry point for Main Branch. Detects user state, context level, and experience to route to the right skill. Use when: (1) User says "start", "help", "what can I do", "begin" (2) User is new, returning, lost, or confused (3) User opens vip without a specific task in mind (4) Session starts and user needs triage. Routes to /setup (new users), /think (research/decide/enrich), /ads (static/video/review), /vsl (skool/b2b), /content, /skool-manager, /wiki, /help.
---

# Start

Router for Main Branch. Detect state → load business → route to skill.

**Core job:** Orient Claude to the user's business, then route fast.

---

## Detection Flow

```
/start
│
├── Check context level ──────────────→ Fresh? Full load. Heavy? Warn user.
│
├── Pull vip updates ─────────────────→ (silently)
│
├── Load config ──────────────────────→ See [config-system.md](references/config-system.md)
│   ├── ~/.config/vip/local.yaml ─────→ Default repo for this machine
│   └── [repo]/.vip/config.yaml ──────→ User preferences
│
├── MCP pre-flight ───────────────────→ See [mcp-preflight.md](references/mcp-preflight.md)
│   └── Missing required MCP? ────────→ Offer setup or skip
│
├── Load business repo ───────────────→ Discovery if no config
│
├── No repo? ─────────────────────────→ /setup
├── Repo but thin? ───────────────────→ /think codify
│
└── Ready? ───────────────────────────→ Route by intent (below)
```

---

## Route by Intent

| Keywords | Route |
|----------|-------|
| "help", "confused", "stuck", "how do I" | `/help` |
| "new", "first time", "set up" | `/setup` |
| "add context", "enrich", "new testimonials" | `/think codify` |
| "research", "decide", "figure out" | `/think` |
| "ads", "copy", "static", "video ads", "compliance" | `/ads` |
| "vsl", "sales video" | `/vsl` |
| "content", "reels", "tiktok", "mine competitors" | `/content` |
| "skool", "community" | `/skool-manager` |
| "wiki", "notes" | `/wiki` |

If unclear → show numbered options.

---

## Numbered Options Pattern

Always use numbered lists. User replies with just a number.

**Repo selection:**
> 1. [found-repo]
> 2. Another (tell me the path)
> 3. Create new (/setup)
> 4. I'm confused (/help)

**Task selection:**
> 1. Research → /think
> 2. Ads → /ads
> 3. VSL → /vsl
> 4. Content → /content
> 5. Skool → /skool-manager
> 6. Wiki → /wiki
> 7. Add context → /think codify
> 8. Help → /help

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

**First-time** (no config, thin reference): Be verbose, route to /setup
**Returning** (config exists): Quick confirmation, route by intent
**Expert** (clear intent, short messages): Get out of the way, route fast

---

## Find Business Repo

**Config path (fast):** Read `~/.config/vip/local.yaml` → `default_repo`

**Discovery (fallback):**
1. Check additional working directories for `reference/core/`
2. `find ~/Documents/GitHub -maxdepth 3 -name "reference" -exec test -d "{}/core" \;`
3. Ask user

**Skip vip** — paths with `.claude/skills/` are engine, not business.

**Verify with Read:** `[path]/reference/core/offer.md`

---

## Assess Completeness

| File | Complete If |
|------|------------|
| offer.md | >50 lines or "Price" section |
| audience.md | >30 lines or "Pains" section |
| voice.md | >20 lines or "Tone" section |

2+ incomplete → `/think codify`

---

## Skill Reference

| Skill | Purpose |
|-------|---------|
| `/setup` | Create business repo |
| `/think` | Research, decide, codify |
| `/ads` | Image ads, video scripts, compliance review |
| `/vsl` | Video sales letters |
| `/content` | Mine competitors, organic scripts |
| `/skool-manager` | Community engagement |
| `/wiki` | Atomic notes, publish |
| `/help` | Troubleshoot, learn |
| `/pull` | Update vip |

---

## Remember

Router, not worker. One clarifying question max.

**Three jobs:**
1. Orient Claude to business
2. Understand what user needs
3. Route to the right skill
