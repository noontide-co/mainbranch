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

### Initial Setup

1. Install free plugin: `claude /plugin install main-branch`
2. Clone this repo locally for advanced skills
3. Create your own project repo (or client repos)

### Multi-Repo Workflow

**Main-branch-premium is an "operating system" that works across your other repos.**

When using Claude Code:
1. Open your project/client repo as primary working directory
2. Add main-branch-premium as an additional working directory
3. Skills and lenses from main-branch-premium become available
4. Client-specific outputs go to your project repo

```
YOUR WORKFLOW:
┌─────────────────────────────────────────────────────────┐
│  main-branch-premium (additional working directory)     │
│  ├── .claude/skills/      → Generic skills              │
│  ├── .claude/lenses/      → Review criteria             │
│  └── context/compliance/  → Templates & frameworks      │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Skills read frameworks,
                          │ output goes to your repo
                          ▼
┌─────────────────────────────────────────────────────────┐
│  your-project-repo (primary working directory)          │
│  ├── .claude/context/     → Your offer, audience, etc.  │
│  ├── campaigns/           → Your ad outputs             │
│  └── compliance/typicality/ → Your client-specific data │
└─────────────────────────────────────────────────────────┘
```

### What Lives Where

| Content Type | Location | Why |
|--------------|----------|-----|
| Generic skills (ad-static, ad-review) | main-branch-premium | Shared with all members |
| Review lenses (FTC, Meta, etc.) | main-branch-premium | Shared with all members |
| Compliance frameworks/templates | main-branch-premium | Shared with all members |
| Your offer.md, audience.md | Your repo | Client-specific |
| Your campaign outputs | Your repo | Client-specific |
| Your typicality data | Your repo | Client-specific |
| Your testimonials/proof | Your repo | Client-specific |

### Adding main-branch-premium in Claude Code

In your Claude Code settings, add main-branch-premium as an additional working directory. The skills will automatically become available when you work in any repo.

## Skills Available

| Skill | Domain | Description |
|-------|--------|-------------|
| ad-review | Compliance | Multi-lens review (FTC, Meta, Copy, Visual, Voice, Substantiation) |
| skool-manager | System Ops | Community engagement with Chrome |
| ad-static | Marketing | Static image ads + AI prompts |
| ad-video-scripts | Marketing | Video ad scripts (15-30+) |
| skool-vsl-scripts | Marketing | VSL scripts (18-section) |

## Lenses Available

Review criteria for the ad-review skill:

| Lens | What It Checks |
|------|----------------|
| ftc-compliance | FTC regulations, earnings claims, disclosures |
| meta-policy | Platform triggers, Personal Attributes, bans |
| copy-quality | Schwartz, Hormozi, Suby frameworks |
| visual-standards | Safe zones, OCR triggers, prohibited visuals |
| voice-authenticity | AI tells, brand voice consistency |
| substantiation | Claims inventory, proof matching, typicality |

## Compliance References

Pre-campaign planning resources in `context/compliance/`:

| File | Purpose |
|------|---------|
| ftc-scrutiny-categories.md | Which industries get extra FTC attention |
| angle-playbook.md | 10 persuasion angles with rules for each |
| testimonial-decision-rubric.md | When outcome testimonials are worth it |
| typicality/README.md | How to collect FTC-required outcome data |

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
