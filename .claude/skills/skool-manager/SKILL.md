---
name: skool-manager
description: Manage Skool community engagement with Chrome browser automation. Use when responding to members, doing daily community management, checking the Skool feed, or drafting responses to posts.
---

# Skool Manager

Draft and post community responses with Chrome MCP.

## Prerequisites

- Claude in Chrome extension installed and connected
- Logged into Skool in Chrome
- Voice profile configured (see [references/voice-profile-template.md](references/voice-profile-template.md))

## Quick Start

```
/skool-manager "Check the feed and draft responses"
```

## Workflow

1. Navigate to Skool community URL
2. `read_page depth=8` to scan feed
3. Find: unanswered questions, new intros, member wins
4. Read voice profile from `reference/core/voice.md` (if exists)
5. Draft responses to `outputs/community/inbox-{date}.md`
6. **STOP** - wait for approval
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

Use `reference/core/voice.md` in your business repo. Copy template from [references/voice-profile-template.md](references/voice-profile-template.md) if starting fresh.

If no voice profile exists, use neutral helpful tone.

## Guidelines

- Always draft before posting (human approval required)
- Prioritize questions over general posts
- Keep response queue manageable (5-10 drafts max)
- Flag posts needing owner attention
