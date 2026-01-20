---
name: pull
description: |
  Quick pull latest vip updates from GitHub. Use when:
  (1) User wants to update vip without running /start
  (2) User says "pull", "update", "get latest"
  (3) User wants to see what changed in recent updates
---

# Pull

Pull latest updates from GitHub.

---

## Usage

```
/pull
```

---

## What It Does

```bash
git pull origin main
```

**Updated:** "Pulled latest. Changes: [list]"

**Current:** "Already up to date."

**Error:** "Couldn't pull: [error]. Try again later."

---

## When to Use

- Quick update check
- After Devon announces features in Skool

Note: `/start` pulls automatically, so skip `/pull` if running `/start` next.
