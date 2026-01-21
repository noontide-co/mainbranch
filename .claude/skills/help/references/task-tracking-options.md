# Task Tracking Options

How to track ongoing work across sessions. Pick one approach and commit.

---

## The Core Insight

**If you need to "save the conversation," you didn't extract what mattered.**

The system is designed so valuable outputs become files:
- Insight? → `research/`
- Decision? → `decisions/`
- Truth changed? → `reference/`

When you do this, conversations become disposable. The value lives in files.

---

## The Spectrum

| Approach | Token Cost | Setup | Best For |
|----------|------------|-------|----------|
| **decisions/** as anchors | Lowest | None | People who think in choices |
| **GitHub Issues** | Low | `gh` CLI | Developers, CLI-native |
| **focus.md** file | Low | Create file | One status file preference |
| **External (Linear/Notion)** | Highest | MCP setup | Teams, complex workflows |

**Pick one.** Record your preference in CLAUDE.md so `/start` knows.

---

## Option 1: Decisions as Task Anchors (Recommended)

Use decision files for substantial work. The file IS your task tracker.

**How it works:**

```markdown
---
type: decision
status: proposed  # ← This is your progress indicator
---

# Decision: New Pricing Strategy

## Action Items

- [ ] Research competitor pricing
- [ ] Update reference/core/offer.md
- [ ] Create new angle in proof/angles/

## Other actions

- [ ] Set up Stripe tiers
- [ ] Update sales page
```

**Status progression:**
- `proposed` → I'm working on this
- `accepted` → Decision made, executing
- `codified` → Done, reference updated

**Why it works:**
- No separate system to maintain
- Rationale captured alongside tasks
- Check `decisions/` folder to see where you left off
- Natural audit trail

**Best for:** Strategic work, anything where "why" matters.

---

## Option 2: GitHub Issues

Native task management in your repo. Claude can read/write via `gh` CLI.

**Setup:**
```bash
# Ensure gh is authenticated
gh auth status
```

**Usage:**
```bash
# Create issue
gh issue create --title "Implement new pricing" --body "Tasks: ..."

# List open issues
gh issue list

# Close when done
gh issue close 123
```

**Why it works:**
- Native to repo (no external tool)
- `gh` CLI uses minimal tokens
- Labels, milestones, assignments
- Works across devices via GitHub

**Best for:** Developers, CLI-native users, detailed task breakdown.

---

## Option 3: focus.md File

Single lightweight file showing current state.

**Create:** `reference/focus.md`

```markdown
# Current Focus

## Priority
[One sentence: what you're trying to accomplish]

## Next Actions
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## Blockers
- [Thing preventing progress]

## Session Notes
[Quick thoughts — delete after acting on them]

---
*Last updated: 2026-01-21*
```

**Why it works:**
- One file to check
- Lightweight (~20 lines)
- `/start` can scan it quickly

**Best for:** People who want a single "where am I?" file.

**Warning:** Easy to let this go stale. Update it or delete it.

---

## Option 4: External Tools (Linear, Notion, etc.)

Full project management via MCP.

**Setup:** Configure MCP server for your tool.

**Token cost:** Highest — each query/update costs tokens.

**Why use it:**
- Team collaboration
- Complex workflows
- Visual boards, timelines
- Integrations with other tools

**Best for:** Teams, complex multi-person projects.

**Trade-off:** More UX, more tokens. Only worth it if you need the features.

---

## Recording Your Preference

Add to your business repo's CLAUDE.md:

```markdown
## Workflow Preferences

**Task tracking:** decisions/ as anchors
```

Or:
```markdown
## Workflow Preferences

**Task tracking:** GitHub Issues
```

This tells `/start` how to help you pick up where you left off.

---

## What NOT to Do

**Don't save entire conversations.**

- Full of noise (tangents, corrections, false starts)
- Not synthesized — Claude has to sift through it
- Goes stale immediately
- Eats tokens on context that isn't actionable
- Doesn't scale

**The fix:** When a conversation has value, extract it into the right file type. Let the conversation go.

---

## Quick Decision Guide

**"I have a big strategic choice to make"** → Decision file

**"I have 10 small tasks"** → GitHub Issues or focus.md

**"My team needs to see progress"** → External tool

**"I just want to not forget where I was"** → focus.md or check recent `decisions/`

---

## Next Step

Pick one approach. Add your preference to CLAUDE.md. Use it consistently for a week. Adjust if needed.
