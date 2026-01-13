# Main Branch Premium

Private skills library and business OS scaffold for Main Branch members.

## What This Repo Is

This is the full toolkit for Main Branch. Members clone this locally to access skills and templates.

**This is not a project repo.** This is a tools/templates repo that members use to build their own project repos.

## Folder Structure

```
.claude/skills/     → Skills Claude can invoke
templates/
  modules/          → Optional add-ons (marketing, clients, etc.)
```

**Note:** `templates/core/` (Business OS scaffold) is now in the free plugin. Install via:
```bash
claude /plugin install main-branch
```

## How Members Use This

1. Install free plugin: `claude /plugin install main-branch`
2. Clone this repo locally for advanced skills
3. Copy `templates/core/` from free plugin to start a new project
4. Add modules from `templates/modules/` as needed
5. Skills from both repos become available in Claude Code

## Skills Available

| Skill | Domain | Description |
|-------|--------|-------------|
| skool-manager | System Ops | Community engagement with Chrome |
| ad-static | Marketing | Static image ads + AI prompts |
| ad-video-scripts | Marketing | Video ad scripts (15-30+) |
| skool-vsl-scripts | Marketing | VSL scripts (18-section) |

## The Three Domains

| Domain | What AI Handles |
|--------|-----------------|
| **Marketing** | Ads, content, emails, campaigns |
| **System Ops** | Community, tools, automation |
| **Biz Ops** | Finance, compliance, bookkeeping |

Research is interwoven into all domains.

## Git Commit Convention

Use this format for all commits:

```
[type] Brief description

- Detail 1
- Detail 2

Context: Why this change was made
```

**Types:**
- `[add]` — New content
- `[update]` — Improved existing
- `[fix]` — Corrected error
- `[remove]` — Deleted content
- `[refactor]` — Reorganized

**Example:**
```
[add] New ad-review agent for compliance checking

- FTC compliance lens
- Industry-specific lens (configurable)
- Voice/culture match lens

Context: Multi-lens review pattern from Compound Engineering
```

## Contributing (VIP Only)

VIP members have write access. Submit PRs to improve skills or add new ones.
