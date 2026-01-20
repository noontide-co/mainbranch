---
name: start
description: |
  Main entry point for Main Branch. Detects user state, routes to right skill. Use when new, returning, lost, or says "start", "help", "what can I do". Routes to /setup, /enrich, /think, /ad-static, /ad-video-scripts, /ad-review, /content, /skool-manager, /skool-vsl-scripts.
---

# Start

Entry point. Detect state, route to skill.

**Daily workflow:** Start Claude in vip → `/start`. It handles everything.

---

## Numbered Options

Always use numbered lists for choices. Users reply with just a number.

```
1. Option one
2. Option two
3. Another one (tell me)
4. Create new (/setup)

(hit a number)
```

---

## Detection Flow

```
/start
├── git pull origin main (silent)
├── Find business repo (has reference/core/)
│   ├── None → /setup
│   ├── Multiple → Ask which (numbered)
│   └── One → Use it
├── Check completeness
│   ├── 2+ core files empty → /enrich
│   └── Complete → Route by intent
└── Confused? → /help
```

---

## Step 0: Pull Updates

```bash
git pull origin main 2>/dev/null || true
```

Silent. Don't block on network issues.

---

## Step 1: Find Business Repo

Search all working directories for `reference/core/*.md`. Skip vip (has `.claude/skills/`).

**One found:** Use it. "Using [name]. Ready to work."

**Multiple found:**
```
I found these business repos:
1. [repo-name-1]
2. [repo-name-2]
3. Another one (tell me the path)
4. Create new (/setup)

Which one? (hit a number)
```

**None found:** Route to `/setup`

Note: `/add-dir` is Claude Code command, not bash.

---

## Step 2: Check Completeness

| File | Complete If |
|------|-------------|
| offer.md | >50 lines or has "Price" |
| audience.md | >30 lines or has "Pains" |
| voice.md | >20 lines or has "Tone" |

2+ files empty/missing → Suggest `/enrich`

---

## Step 3: Route by Intent

```
What would you like to do?

1. Research a topic → /think
2. Create ad copy → /ad-static or /ad-video-scripts
3. Review ads → /ad-review
4. Create organic content → /content
5. Write VSL → /skool-vsl-scripts
6. Manage Skool → /skool-manager
7. Add more context → /enrich
8. Get help → /help

(hit a number)
```

If intent already stated, route directly.

---

## Intent Keywords

| Keywords | Route |
|----------|-------|
| help, confused, stuck, how do I | /help |
| new, first time, set up | /setup |
| add, update, more context | /enrich |
| research, decide, explore | /think |
| ads, copy, static, primaries | /ad-static |
| video ads, ad scripts, hooks | /ad-video-scripts |
| review, compliance, ftc | /ad-review |
| content, reels, tiktok, organic, mine, carousel | /content |
| skool, community, posts | /skool-manager |
| vsl, sales video | /skool-vsl-scripts |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No reference/core/ | User needs `/add-dir` for business repo |
| Nested repo | Search inside parent folders |
| Multiple repos | Ask which one |
| Repo not added | Ask path, tell user to `/add-dir` |

---

## Skills Reference

| Skill | What |
|-------|------|
| /pull | Pull latest vip updates |
| /help | Answers, troubleshooting |
| /setup | Create business repo |
| /enrich | Add context to existing |
| /think | Research → decide → codify |
| /ad-static | Image ad copy |
| /ad-video-scripts | Video scripts |
| /ad-review | Compliance check |
| /content | Mine competitors, organic |
| /skool-manager | Community engagement |
| /skool-vsl-scripts | VSL scripts |
