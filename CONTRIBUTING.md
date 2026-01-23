# Contributing to Main Branch Premium

Welcome! We're excited you want to contribute.

---

## Who Can Contribute

Main Branch Premium is a **private repository** for VIP members. To contribute:

1. Be an active VIP member
2. Have used the system and understand how it works
3. Have an idea that helps the community

**Not a VIP yet?** Join at [skool.com/main](https://www.skool.com/main)

---

## How to Contribute

### 1. Create an Issue First (Required)

**Every branch must start from a GitHub issue.** This keeps work tracked and linked.

1. Go to [Issues](https://github.com/mainbranch-ai/vip/issues)
2. Create a new issue describing what you want to do
3. Use the **"Create a branch"** button on the issue (right sidebar)
4. GitHub auto-links the branch to the issue

**Why?** Branch names like `42-add-notion-export-skill` automatically link to issue #42. PRs that merge the branch can auto-close the issue.

### 2. Make Your Changes

Follow the existing patterns:
- Skills go in `.claude/skills/`
- Keep SKILL.md under 500 lines
- Use `references/` for detailed docs
- Test your changes before submitting

**Commit convention:** `[type] Brief description`
- `[add]` - New feature
- `[update]` - Enhancement to existing feature
- `[fix]` - Bug fix
- `[remove]` - Removal
- `[refactor]` - Code restructure without behavior change

### 3. Run Regression Tests (Admins)

Before opening a PR, admins should run:

```bash
bash ~/.claude/skills/test-skills/test-skills.sh
```

All 54 tests must pass. If tests fail after refactoring, you may have removed critical content.

### 4. Open a Pull Request

Push your branch and open a PR against `main`.

**PR checklist:**
- [ ] Issue linked (happens automatically if you used "Create a branch")
- [ ] Regression tests pass (admins)
- [ ] Description explains what changed and why
- [ ] Tested the changes work as expected

**Post test results as PR comment:**
```bash
gh pr comment [PR#] --body "## Test Results

54/54 passed

[paste output]"
```

---

## What We're Looking For

**Great contributions:**
- New skills that solve real problems you've faced
- Improvements to existing skills based on actual usage
- Bug fixes
- Better documentation
- Templates and examples

**Before you build:**
- Check if someone else is working on it (open issues/PRs)
- Consider if it belongs in VIP or the free tier
- Think about how beginners will use it

---

## Contribution Levels

We recognize contributors based on impact:

| Level | What It Means |
|-------|---------------|
| **First PR** | You've contributed! Welcome to the builder club. |
| **Skill Creator** | You've created a skill that shipped. |
| **Core Contributor** | Multiple accepted PRs, deep system understanding. |

*More details on contributor recognition coming soon.*

---

## Skills: Shared vs Admin

There are two skill locations:

| Location | Who | What |
|----------|-----|------|
| `vip/.claude/skills/` | Everyone | Shared skills (`/ads`, `/think`, `/start`, etc.) |
| `noontide-projects/.claude/skills/` | Admins only | Admin tools (`/test-skills`, `/skill-creator`) |

**Shared skills** go through PR review. **Admin skills** are managed by Devon, Joe, and core contributors.

### Becoming an Admin

Admins have access to:
- `noontide-projects` repo (admin skills with git history)
- Regression test suite
- Direct merge permissions

To become an admin: demonstrate consistent contributions and deep system understanding.

---

## Code Style

- Follow existing patterns in the codebase
- Keep skills beginner-friendly
- Use clear, simple language
- Document the "why" not just the "what"

### Skill Structure

```
.claude/skills/my-skill/
├── SKILL.md              # Main file (under 500 lines)
└── references/           # Detailed docs, examples, templates
    ├── getting-started.md
    └── advanced.md
```

**Keep in SKILL.md:**
- Core workflow and philosophy
- Quick reference tables
- Essential commands

**Move to references:**
- Detailed implementation steps
- Edge cases and troubleshooting
- Long examples

---

## Questions?

Ask in the [Main Branch Skool community](https://www.skool.com/main) or tag Devon in your PR.

---

*Thank you for making Main Branch better for everyone.*
