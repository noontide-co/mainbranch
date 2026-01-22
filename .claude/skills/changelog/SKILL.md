---
name: changelog
description: Create and maintain a business metrics changelog. Use when: (1) Setting up a new business repo and want to track metrics (2) User wants to track business progress over time (3) User says "changelog", "metrics", "track progress", "track growth" (4) Adding a new metrics entry to existing changelog. Creates CHANGELOG.md in user's business repo root.
---

# Changelog

Track your business metrics and milestones over time.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

---

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Where Files Go

**CHANGELOG.md goes in YOUR business repo root, not the engine (vip).**

```
your-business-repo/          <- CHANGELOG.md created here
├── CHANGELOG.md              <- This skill creates/updates this
├── reference/
├── research/
├── decisions/
└── outputs/

vip/ (engine)                 <- Never modified by /changelog
└── .claude/skills/changelog/ <- This skill lives here
```

Make sure your business repo is the primary working directory.

---

## Modes

### Setup Mode (First Run)

When no `CHANGELOG.md` exists in the business repo root:
1. Ask business type
2. Show default metrics
3. Ask simple vs extended
4. Ask update cadence
5. Create CHANGELOG.md with first entry

### Update Mode (Subsequent Runs)

When `CHANGELOG.md` already exists:
1. Read existing file
2. Extract metric names
3. Ask for current values
4. Append new dated entry

---

## Setup Mode Workflow

### 1. Detect Mode

```bash
# Check if CHANGELOG.md exists in business repo
ls CHANGELOG.md 2>/dev/null
```

If exists: Switch to Update Mode.
If not: Continue with Setup Mode.

### 2. Ask Business Type

> "What type of business is this? (Choose a number)"
>
> 1. **Skool Community** — Membership, community, courses
> 2. **E-commerce** — Physical or digital products
> 3. **Coaching/Services** — 1:1 or group coaching, consulting
> 4. **SaaS** — Software as a service
> 5. **Agency** — Client services, retainers

**Do not guess.** Always ask the user to select.

### 3. Show Default Metrics

Based on business type, show the simple (default) metrics:

| Business Type | Simple Metrics (default) |
|---------------|--------------------------|
| Skool Community | MRR, Members, Churn |
| E-commerce | Revenue, Orders, AOV |
| Coaching/Services | Revenue, Clients, Close rate |
| SaaS | MRR, Users, Churn |
| Agency | Revenue, Clients, Retainer value |

> "For a [business type], I recommend tracking: **[metrics]**
>
> Want to keep it simple (recommended), or add extended metrics?"

### 4. Offer Extended Metrics (Optional)

If user wants extended:

| Business Type | Extended Metrics |
|---------------|------------------|
| Skool Community | + Conversion rate, Retention %, Engagement score |
| E-commerce | + Traffic, Conversion rate, ROAS |
| Coaching/Services | + Calls booked, Show rate, LTV |
| SaaS | + Trial conversion, NPS, CAC |
| Agency | + Pipeline value, Win rate, Utilization |

### 5. Ask Update Cadence

> "How often do you want to log metrics?"
>
> 1. **Weekly** — Best for fast-moving businesses
> 2. **Monthly** (recommended) — Standard cadence for most businesses
> 3. **Quarterly** — For slower-moving metrics

### 6. Gather First Entry Values

Ask for each metric value:

> "Let's record your first entry. What are your current numbers?"
>
> - MRR: $_____
> - Members: _____
> - Churn: _____

### 7. Create CHANGELOG.md

Use template from [references/changelog-templates.md](references/changelog-templates.md).

Create at business repo root: `CHANGELOG.md`

### 8. Confirm Success

> "Created CHANGELOG.md with your first entry.
>
> **To add future entries:** Just run `/changelog` again and I'll prompt you for the latest numbers.
>
> **Tip:** Set a calendar reminder for [cadence] to update your metrics."

---

## Update Mode Workflow

### 1. Read Existing Changelog

```bash
# Read the file to extract structure
cat CHANGELOG.md
```

Parse:
- Business type (from header)
- Metrics being tracked (from table)
- Last entry date (to calculate delta)
- Last entry values (to calculate change)

### 2. Ask for Current Values

> "Time for a new entry! What are your current numbers?"
>
> | Metric | Last value | Current |
> |--------|------------|---------|
> | MRR | $X,XXX | $_____ |
> | Members | XXX | _____ |
> | Churn | X | _____ |

### 3. Calculate Deltas

For each metric, calculate change from last entry:
- Absolute change (e.g., +$500, -3 members)
- Percentage if relevant

### 4. Ask for Notes (Optional)

> "Any notes about this period? (Press enter to skip)"
>
> Examples:
> - "Launched new ad campaign"
> - "Holiday slow period"
> - "Hit 1,000 members milestone!"

### 5. Append New Entry

Add new dated section to CHANGELOG.md, maintaining the existing structure.

### 6. Confirm Success

> "Added [Month Year] entry to your changelog.
>
> **Highlights:**
> - [Metric] [direction]: [change]
> - ...
>
> Keep it up! See you next [cadence]."

---

## CHANGELOG.md Format

See [references/changelog-templates.md](references/changelog-templates.md) for full template.

Basic structure:

```markdown
# Business Changelog

Track record of [Business Name] metrics and milestones.

**Cadence:** Monthly
**Business Type:** Skool Community

---

## Metrics Tracked

| Metric | Description |
|--------|-------------|
| MRR | Monthly recurring revenue |
| Members | Total active members |
| Churn | Members lost this period |

---

## 2026

### January 2026

**Date:** 2026-01-22

| Metric | Value | Change |
|--------|-------|--------|
| MRR | $5,000 | -- |
| Members | 150 | -- |
| Churn | 3 | -- |

**Notes:**
- First changelog entry

---
```

---

## Business Type Reference

### Skool Community

**Simple (default):**
- **MRR** — Monthly recurring revenue from memberships
- **Members** — Total active paying members
- **Churn** — Members who cancelled this period

**Extended (optional):**
- **Conversion rate** — Free to paid conversion %
- **Retention %** — Members retained month-over-month
- **Engagement score** — Community activity metric

### E-commerce

**Simple (default):**
- **Revenue** — Total sales this period
- **Orders** — Number of orders placed
- **AOV** — Average order value

**Extended (optional):**
- **Traffic** — Site visitors
- **Conversion rate** — Visitors to buyers %
- **ROAS** — Return on ad spend

### Coaching/Services

**Simple (default):**
- **Revenue** — Total revenue this period
- **Clients** — Active paying clients
- **Close rate** — % of calls that convert

**Extended (optional):**
- **Calls booked** — Discovery/sales calls scheduled
- **Show rate** — % of calls that happen
- **LTV** — Lifetime value per client

### SaaS

**Simple (default):**
- **MRR** — Monthly recurring revenue
- **Users** — Total active users
- **Churn** — Users lost this period

**Extended (optional):**
- **Trial conversion** — Trial to paid %
- **NPS** — Net promoter score
- **CAC** — Customer acquisition cost

### Agency

**Simple (default):**
- **Revenue** — Total revenue this period
- **Clients** — Active retainer clients
- **Retainer value** — Average monthly retainer

**Extended (optional):**
- **Pipeline value** — Value of prospects in pipeline
- **Win rate** — % of proposals that close
- **Utilization** — Billable hours %

---

## Recovering from Compaction

If conversation compacts mid-changelog:

**For the user:** Type `/changelog` again:
- "I was setting up my changelog"
- "I need to add a new entry"

**For Claude:** When resuming:
1. Check if CHANGELOG.md exists
2. If exists: Update mode
3. If not: Setup mode
4. Confirm with user what they need

---

## When NOT to Use

- For project task tracking (use `/think` decisions instead)
- For one-time business events (just note in decisions/)
- For financial accounting (use proper accounting software)

Use `/changelog` for periodic business health snapshots.

---

## References

- [references/changelog-templates.md](references/changelog-templates.md) — Full templates for each business type
