---
name: pull
description: |
  Quick pull latest vip updates from GitHub. Use when:
  (1) User wants to update vip without running /start
  (2) User says "pull", "update", "get latest"
  (3) User wants to see what changed in recent updates
---

# Pull

Pull latest updates from GitHub. Fast and simple.

---

## Usage

```
/pull
```

---

## What It Does

1. Runs `git pull origin main` in vip
2. Shows what changed (files modified, new skills, etc.)
3. Done

---

## Implementation

```bash
# Pull latest
git pull origin main
```

**If changes pulled:**
> "Pulled latest updates. Changes:
> - [list of changed files/folders]"

**If already up to date:**
> "Already up to date."

**If error (network, etc.):**
> "Couldn't pull updates: [error]. You can try again later or continue working."

---

## When to Use

- Quick update check
- Before starting a work session
- After Devon announces new features in Skool

**Note:** `/start` also pulls automatically, so you don't need `/pull` if you're about to run `/start`.
