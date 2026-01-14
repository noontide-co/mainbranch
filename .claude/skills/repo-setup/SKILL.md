---
name: Repo Setup
description: |
  Initialize a new business repo with proper context structure. Use when:
  (1) Setting up a new client/business repo from scratch
  (2) User says "set up my repo" or "initialize my business"
  (3) User wants to organize existing business info into context files

  Workflow: User dumps raw context (sales pages, notes, offers) → skill sorts into offer.md, audience.md, angles/, proof/
---

# Repo Setup

Bootstrap a business repo by sorting raw context into structured files.

---

## Philosophy: Active Context Management

**This is not a one-time setup.** Your context files are living documents that evolve as you:

1. Run campaigns and see what resonates
2. Talk to customers and hear new language
3. Test angles and find winners
4. Collect proof and testimonials

The cycle:
```
Dump context → Sort into files → Generate outputs → Learn from results → Update context → Repeat
```

Every ad you run teaches you something. Every customer conversation reveals language. Feed it back into your context files. The system gets smarter because YOU get clearer on your business.

**Start messy. Refine continuously.**

---

## Process

### 1. Check Current State

```bash
ls -la context/ 2>/dev/null || echo "No context folder yet"
```

If context/ exists with files, confirm user wants to overwrite or merge.

### 2. Request Context Dump

Ask user to paste or point to their raw business context:

> Dump everything you have about this business - sales pages, offer details, testimonials, notes, whatever exists. I'll sort it into the right files.

Accept any format:
- Pasted text
- File paths to read
- URLs to fetch
- "Read my existing [file]"

### 3. Create Folder Structure

```
context/
├── offer.md
├── audience.md
├── proof/
│   └── testimonials.md
└── angles/
    └── [angle-name].md
```

### 4. Sort Content

Extract and organize into:

**offer.md**
- Product/service name
- Price points
- What's included
- Mechanism (how it works)
- Transformation promise

**audience.md**
- Who they are (demographics, psychographics)
- Current state (pains, frustrations)
- Desired state (goals, dreams)
- Objections and fears
- Language they use

**proof/testimonials.md**
- Customer results and quotes
- Case studies
- Before/after stories
- Note: preserve exact quotes, add source if known

**angles/** (one file per angle)
- Distinct messaging entry points found in the content
- Name each angle file descriptively: `price-anchor.md`, `mechanism.md`, `community.md`

### 5. Flag Gaps

After sorting, note what's missing:

| File | Status |
|------|--------|
| offer.md | ✅ Complete / ⚠️ Missing [X] |
| audience.md | ✅ Complete / ⚠️ Missing [X] |
| proof/testimonials.md | ✅ Has content / ❌ Empty |
| angles/ | ✅ [N] angles / ⚠️ None identified |

Ask user to provide missing pieces or note for later.

---

## File Templates

### offer.md

```markdown
# [Business Name] Offer

## Product
[Name and one-line description]

## Price
[Price point(s)]

## What's Included
- [Item 1]
- [Item 2]

## Mechanism
[How it works - the unique approach]

## Transformation
[Before state] → [After state]
```

### audience.md

```markdown
# [Business Name] Audience

## Who They Are
[Demographics, role, situation]

## Current State
- [Pain 1]
- [Pain 2]
- [Frustration]

## Desired State
- [Goal 1]
- [Goal 2]
- [Dream outcome]

## Objections
- [Objection 1]
- [Objection 2]

## Their Language
[Phrases they use, how they describe the problem]
```

### testimonials.md

```markdown
# Testimonials

## [Customer Name/Type]
> "[Exact quote]"

**Result:** [Specific outcome if stated]
**Source:** [Where this came from]

---

[Repeat for each testimonial]
```

### angles/[angle-name].md

```markdown
# [Angle Name]

## Hook
[The entry point / attention grabber]

## Core Idea
[What this angle emphasizes]

## Best For
[When to use this angle]
```

---

## Notes

- Preserve original language when possible - don't over-polish
- If content is thin, create files with what exists + TODO markers
- Angles emerge from the content - don't force categories
- v1 is just the start - come back after every campaign with new learnings

---

## When to Run Again

Use this skill anytime you have new context to sort:

- "I just wrote a new sales page, update my context"
- "Here's feedback from 10 customer calls"
- "This angle crushed it, let's document why"
- "Got 5 new testimonials this month"

The skill merges new content into existing files, preserving what's there.
