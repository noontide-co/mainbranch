# Git Workflow

GitHub CLI best practices for Main Branch repos.

---

## Always Use Git

Every Main Branch business repo should be version controlled. Git provides:

- History of all changes
- Ability to revert mistakes
- Collaboration with team members
- Backup of your business knowledge

---

## Initial Setup

```bash
# If starting fresh
git init
git add -A
git commit -m "[init] Bootstrap business repo with Main Branch structure"

# Connect to GitHub (optional but recommended)
gh repo create [business-name] --private --source=. --push
```

---

## Commit Message Format

Always use this format:

```
[type] Brief description (50 chars max)

- Detail 1
- Detail 2
- Detail 3

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Types

| Type | Use For |
|------|---------|
| `[init]` | Initial repo setup |
| `[add]` | New files, features, content |
| `[update]` | Changes to existing files |
| `[fix]` | Bug fixes, corrections |
| `[refactor]` | Restructuring without changing behavior |
| `[docs]` | Documentation only changes |
| `[remove]` | Deleting files |
| `[research]` | Adding research files |
| `[decision]` | Adding decision files |

### Examples

**Initial setup:**
```
[init] Bootstrap business repo with Main Branch structure

- Created reference/core/ (offer, audience, voice)
- Created reference/proof/ (testimonials, angles)
- Created reference/domain/products/
- Drafted CLAUDE.md and README.md

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Adding content:**
```
[add] Customer testimonials from Q4 reviews

- Added 12 new testimonials to proof/testimonials.md
- Created 2 new angles: gift-giving.md, comfort-fit.md
- Updated audience.md with new customer language

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Research:**
```
[research] Pinterest strategy analysis

- Added research/2026-01-15-pinterest-strategy-gemini.md
- Key finding: CTR below benchmark, needs content diversification

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Decision:**
```
[decision] Adopt lunar email calendar

- Added decisions/2026-01-15-lunar-email-strategy.md
- Decided: New/Full moon timing for campaigns
- Rejected: Traditional sale calendar

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Using HEREDOC for Commits

Always use HEREDOC for multi-line commit messages to ensure proper formatting:

```bash
git commit -m "$(cat <<'EOF'
[type] Brief description

- Detail 1
- Detail 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Why HEREDOC?**
- Preserves line breaks
- Handles special characters
- Works reliably across systems

---

## Staging Best Practices

```bash
# Stage everything
git add -A

# Stage specific files
git add reference/core/offer.md reference/core/audience.md

# Stage by folder
git add reference/proof/

# Check what's staged
git status
```

---

## Common Workflows

### After Context Dump Session

```bash
git add -A
git status  # Review changes
git commit -m "$(cat <<'EOF'
[update] Incorporate new business context

- Updated offer.md with new pricing
- Added 5 testimonials from customer calls
- Created mechanism.md angle

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### After Research Session

```bash
git add research/
git commit -m "$(cat <<'EOF'
[research] Competitor analysis for Q1

- Added research/2026-01-20-competitor-analysis-gemini.md
- Analyzed 5 competitors' positioning
- Identified gap in [specific area]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### After Output Generation

```bash
git add outputs/
git commit -m "$(cat <<'EOF'
[add] January email campaign batch

- Generated 4 welcome sequence emails
- Created 2 promotional emails for lunar drop
- All using Devon Voice system

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Safety Rules

1. **Never force push to main** — Protect your history
2. **Commit frequently** — Small, logical commits
3. **Check status before commit** — Review what's staged
4. **Use descriptive messages** — Future you will thank you
5. **Include Co-Authored-By** — Credit AI assistance

---

## GitHub CLI Reference

```bash
# Check authentication
gh auth status

# Create private repo and push
gh repo create [name] --private --source=. --push

# View repo in browser
gh repo view --web

# Create pull request (if using branches)
gh pr create --title "Title" --body "Description"
```

---

## .gitignore Recommendations

```gitignore
# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/

# Environment
.env
*.env.local

# Temporary
*.tmp
*.log

# Large media (store elsewhere)
*.mp4
*.mov
```
