---
name: start
description: |
  Main entry point for Main Branch. Use when:
  (1) User is new and doesn't know where to begin
  (2) User returns and wants guidance on next steps
  (3) User says "start", "help", "what can I do", "get started"
  (4) User seems lost or unsure which skill to use

  Routes to: /setup (new users), /enrich (add context), /think (research/decide),
  /ad-static, /ad-video-scripts, /ad-review, /skool-manager, /skool-vsl-scripts
---

# Start

Single entry point for Main Branch. Detect user state, route to the right skill.

---

## Detection Flow

```
/start
│
├── In vip (engine) repo? ─────────→ STOP — need user's business repo
│   (.claude/skills/ exists)
│
├── No business repo? ──────────────→ /setup
│   (no reference/ folder)
│
├── Has repo but thin? ─────────────→ /enrich
│   (reference files exist but incomplete)
│
├── Ready to work? ─────────────────→ Route by intent:
│   │
│   ├── "research" / "decide" ──────→ /think
│   ├── "ads" / "copy" ─────────────→ /ad-static or /ad-video-scripts
│   ├── "review" / "compliance" ────→ /ad-review
│   ├── "skool" / "community" ──────→ /skool-manager
│   ├── "vsl" / "sales video" ──────→ /skool-vsl-scripts
│   └── unclear ────────────────────→ Show options
│
└── "help" / confused? ─────────────→ Explain concepts
```

---

## Step 0: Check Location (CRITICAL)

**Before doing anything else, check if we're in the vip (engine) repo:**

```bash
# If this succeeds, we're in vip — don't write here
ls .claude/skills/start/SKILL.md 2>/dev/null
```

**If we're in vip:**

> "You're currently in the **vip** repository — that's the engine.
>
> I can't save your business files here because:
> 1. You only have read-only access (you can't push changes)
> 2. Your business data should live in YOUR OWN separate repo
>
> **To fix this:**
> - Create a new folder for your business (e.g., `~/my-business`)
> - Run `claude` from that folder
> - Use `/add-dir` to add vip so you still have access to skills
>
> Or if you already have a business repo, navigate there first.
>
> Need help? See `docs/BEGINNER-SETUP.md` in this repo."

**Do not proceed with setup or file creation if we're in vip.**

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

If user is ready to work, ask or infer intent:

> "Your reference files look good. What would you like to do?
>
> - **Research a topic** → `/think`
> - **Create ad copy** → `/ad-static` (images) or `/ad-video-scripts` (video)
> - **Review ads for compliance** → `/ad-review`
> - **Manage Skool community** → `/skool-manager`
> - **Write a VSL script** → `/skool-vsl-scripts`
> - **Add more context** → `/enrich`"

If user already stated intent, route directly without asking.

---

## Step 4: Help Mode

If user says "help" or seems confused, explain the system:

> "Main Branch works like this:
>
> 1. **Your business repo** has reference files (offer, audience, voice, proof)
> 2. **Skills** read those files and generate outputs
> 3. **Better reference = better outputs**
>
> **Getting started:**
> - New here? Run `/setup` to create your business repo
> - Have a repo? Run `/enrich` to add more context
> - Ready to generate? Try `/ad-static` or `/think`
>
> What would you like to do?"

---

## Skill Quick Reference

| Skill | What It Does | When to Use |
|-------|--------------|-------------|
| `/setup` | Create business repo from scratch | First-time users |
| `/enrich` | Add context to existing repo | Returning users with gaps |
| `/think` | Research topics, make decisions | Before committing to an approach |
| `/ad-static` | Generate image ad copy | Need Meta ad copy |
| `/ad-video-scripts` | Generate video ad scripts | Need 15-60s video scripts |
| `/ad-review` | Check ads for compliance | Before running ads |
| `/skool-manager` | Manage community engagement | Daily Skool tasks |
| `/skool-vsl-scripts` | Write video sales letters | Need VSL for about page |

---

## Intent Keywords

Use these to auto-detect what user wants:

| Keywords | Route To |
|----------|----------|
| "new", "first time", "get started", "set up" | `/setup` |
| "add", "update", "more context", "new testimonials" | `/enrich` |
| "research", "decide", "figure out", "explore" | `/think` |
| "ads", "copy", "static", "image ads", "primaries" | `/ad-static` |
| "video", "scripts", "hooks", "ugc" | `/ad-video-scripts` |
| "review", "compliance", "ftc", "check" | `/ad-review` |
| "skool", "community", "posts", "respond" | `/skool-manager` |
| "vsl", "sales video", "about page video" | `/skool-vsl-scripts` |

---

## Don't Overthink

This skill is a router, not a worker.

- Detect state quickly
- Route to the right skill
- Let that skill do the heavy lifting

If uncertain, ask one clarifying question, then route.
