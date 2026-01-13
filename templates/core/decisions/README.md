# Decisions

Business decisions with reasoning.

## Why

You don't relitigate. Six months later, you know *why* you chose this path.

## Format

```markdown
---
date: 2026-01-13
decision: Short decision statement
status: decided | superseded | archived
tags: [tag1, tag2]
---

# Decision Title

## Context
[What prompted this decision]

## Decision
[The choice, one sentence]

## Options Considered
1. **Option A** - pros/cons
2. **Option B** - pros/cons

## Reasoning
[Why this option won]

## Consequences
- What this enables
- What this prevents
```

## Naming

`YYYY-MM-DD-decision-slug.md`

Example: `2026-01-13-stripe-over-square.md`

## Status Lifecycle

- `decided` — Active, use this
- `superseded` — Replaced (link to replacement)
- `archived` — No longer relevant
