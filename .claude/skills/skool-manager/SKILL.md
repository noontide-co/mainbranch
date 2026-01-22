---
name: skool-manager
description: Manage Skool community engagement with Chrome browser automation. Use when: (1) Responding to member posts in your community (2) Doing daily community management rounds (3) Checking the Skool feed for new posts needing replies (4) Drafting responses that match your voice profile (5) User says "check skool", "respond to posts", "community management". Requires Chrome extension and Skool login. Reads voice profile from reference/core/voice.md.
---

# Skool Manager

Draft and post community responses with Chrome MCP.

**Need help?** Type `/help` + your question anytime.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Where Files Go

**All drafts save to YOUR business repo, not the engine (vip).**

```
your-business-repo/
├── reference/core/voice.md    <- Read for tone
└── outputs/community/         <- Drafts saved here

vip/ (engine)
└── .claude/skills/skool-manager/  <- This skill lives here
```

---

## Prerequisites

- Claude in Chrome extension installed and connected
- Logged into Skool in Chrome
- Voice profile in `reference/core/voice.md` (run `/setup` or `/enrich` if missing)

## Quick Start

```
/skool-manager "Check the feed and draft responses"
```

---

## Modes

### `/skool-manager` (Full Flow - Default)

Check feed, draft responses, wait for approval, post.

### `/skool-manager check`

Scan feed only. Report what needs attention without drafting.

### `/skool-manager post`

Post previously approved drafts from `outputs/community/inbox-*.md`.

---

## Full Flow Workflow

1. Navigate to Skool community URL
2. `read_page depth=8` to scan feed
3. Find: unanswered questions, new intros, member wins
4. Read voice profile from `reference/core/voice.md`
5. Draft responses to `outputs/community/inbox-{date}.md`
6. **STOP** - present drafts with numbered options:
   ```
   Drafts ready for review:
   1. Approve all and post
   2. Review individually (I'll show each)
   3. Edit drafts first
   4. Save for later (don't post)
   ```
7. Post approved responses, like relevant posts

## Daily Target

15-20 activities: 8-10 likes, 4-6 comments, 1-2 posts

## Draft Output Format

```markdown
# Community Inbox - [DATE]

## Pending Responses

### [Post Title]
**Link:** [URL]
**Type:** Question / Intro / Win
**Draft:**
[Response]

---

## Suggested Likes
- [Post] - [reason]

## Notes
[Community observations]
```

## Chrome MCP Quick Reference

```
read_page       → Get page structure (preferred)
navigate        → Go to URL
computer        → Click, scroll, type
form_input      → Fill forms
find            → Find elements by description
```

Use refs from `read_page` output to interact with elements.

## Voice Profile

Use `reference/core/voice.md` in your business repo. If missing:
- Run `/setup` for new users
- Run `/enrich` to add voice context to existing repo

If no voice profile exists, use neutral helpful tone and flag this to user.

---

## Guidelines

- Always draft before posting (human approval required)
- Prioritize questions over general posts
- Keep response queue manageable (5-10 drafts max)
- Flag posts needing owner attention
- Use numbered options for any multi-choice

---

## Transparency

Before saving drafts: show file path.
Before posting: show exactly what will be posted.
