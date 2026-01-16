---
name: Repo Setup
description: |
  Initialize a new business repo with proper reference structure. Use when:
  (1) Setting up a new client/business repo from scratch
  (2) User says "set up my repo" or "initialize my business"
  (3) User wants to organize existing business info into reference files

  Workflow: User dumps raw context (sales pages, notes, offers) → skill sorts into reference/core/, reference/proof/, etc.
---

# Repo Setup

Bootstrap a business repo by sorting raw context into structured reference files.

---

## Philosophy: Active Reference Management

**This is not a one-time setup.** Marketing is a reflection of the present moment.

Times change. Seasons change. Markets shift. Your audience's problems evolve. What worked last quarter might not land today. Your reference files need to stay current with reality - not just accumulate history.

Your reference files are living documents that evolve as:

1. You run campaigns and see what resonates
2. You talk to customers and hear new language
3. The market shifts and new pains emerge
4. Your offer matures and positioning sharpens
5. Seasons change and timely angles appear

The cycle:
```
Research → Decide → Codify reference → Generate outputs → Learn from results → Repeat
```

Every ad you run teaches you something. Every customer conversation reveals language. Every market shift creates new angles. Feed it back into your reference files.

The system gets smarter because YOU stay present with your business.

**Start messy. Refine continuously. Stay current.**

---

## Process

### 1. Check Current State

```bash
ls -la reference/ 2>/dev/null || echo "No reference folder yet"
```

If reference/ exists with files, confirm user wants to overwrite or merge.

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
reference/
├── core/
│   ├── offer.md
│   ├── audience.md
│   └── voice.md
├── brand/
│   └── [brand-specific].md
├── proof/
│   ├── testimonials.md
│   └── angles/
│       └── [angle-name].md
└── domain/
    └── [business-type-specific]/
```

### 4. Sort Content

Extract and organize into:

**core/offer.md**
- Product/service name
- Price points
- What's included
- Mechanism (how it works)
- Transformation promise

**core/audience.md**
- Who they are (demographics, psychographics)
- Current state (pains, frustrations)
- Desired state (goals, dreams)
- Objections and fears
- Language they use

**core/voice.md**
- Tone and cadence
- Vocabulary patterns
- Core phrases
- What to avoid

**proof/testimonials.md**
- Customer results and quotes
- Case studies
- Before/after stories
- Note: preserve exact quotes, add source if known

**proof/angles/** (one file per angle)
- Distinct messaging entry points found in the content
- Name each angle file descriptively: `price-anchor.md`, `mechanism.md`, `community.md`

### 5. Flag Gaps

After sorting, note what's missing:

| File | Status |
|------|--------|
| core/offer.md | ✅ Complete / ⚠️ Missing [X] |
| core/audience.md | ✅ Complete / ⚠️ Missing [X] |
| core/voice.md | ✅ Complete / ⚠️ Missing [X] |
| proof/testimonials.md | ✅ Has content / ❌ Empty |
| proof/angles/ | ✅ [N] angles / ⚠️ None identified |

Ask user to provide missing pieces or note for later.

---

## File Templates

### core/offer.md

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

### core/audience.md

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

### core/voice.md

```markdown
# [Business Name] Voice

## Tone
[Calm, energetic, professional, casual, etc.]

## Cadence
[Short sentences, long flowing prose, etc.]

## Vocabulary
[Words to use, words to avoid]

## Core Phrases
- [Phrase 1]
- [Phrase 2]
```

### proof/testimonials.md

```markdown
# Testimonials

## [Customer Name/Type]
> "[Exact quote]"

**Result:** [Specific outcome if stated]
**Source:** [Where this came from]

---

[Repeat for each testimonial]
```

### proof/angles/[angle-name].md

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

- "I just wrote a new sales page, update my reference"
- "Here's feedback from 10 customer calls"
- "This angle crushed it, let's document why"
- "Got 5 new testimonials this month"

The skill merges new content into existing files, preserving what's there.
