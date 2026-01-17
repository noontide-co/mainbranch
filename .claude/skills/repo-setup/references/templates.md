# File Templates

Copy and customize these templates when creating reference files.

---

## reference/core/offer.md

```markdown
---
type: context
status: active
---

# The Offer

## What We Sell

[One paragraph: What is this product/service?]

**Core proposition:** "[The main promise in customer language]"

---

## Products/Services

### [Product/Service 1]
- **Price:** $X
- **What's included:** [List]
- **Delivery:** [How they get it]

### [Product/Service 2]
...

---

## The Mechanism

How it works — the unique approach that delivers the transformation:

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Transformation

**Before:** [Current state - pains, frustrations]
**After:** [Desired state - outcomes, feelings]

---

## Pricing Philosophy

[Why this price? What does it signal?]

---

## Objections & Responses

| Objection | Response |
|-----------|----------|
| "[Common objection 1]" | [How to address it] |
| "[Common objection 2]" | [How to address it] |
```

---

## reference/core/audience.md

```markdown
---
type: context
status: active
---

# The Audience

## Core Insight

[One sentence: Who are they really?]

---

## Demographics

- **Age:**
- **Gender:**
- **Income:**
- **Location:**
- **Education/Role:**

---

## Psychographics

### Who They Are
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]

### Their Internal State
- [What they're feeling]
- [What they're dealing with]
- [What they're seeking]

### What They Believe
- [Belief 1]
- [Belief 2]
- [Belief 3]

---

## Buying Triggers

### When They Buy
- [Trigger 1]
- [Trigger 2]
- [Trigger 3]

### What Converts Them
- [Conversion factor 1]
- [Conversion factor 2]

---

## Pain Points

| Pain | How We Address It |
|------|-------------------|
| "[Pain 1]" | [Our solution] |
| "[Pain 2]" | [Our solution] |

---

## Their Language

Words and phrases they use to describe their problem:
- "[Phrase 1]"
- "[Phrase 2]"
- "[Phrase 3]"

---

## Where They Hang Out

**Online:** [Platforms, communities, content they consume]
**Offline:** [Places, events, contexts]
```

---

## reference/core/voice.md

```markdown
---
type: context
status: active
---

# Brand Voice

## The Essence

[2-3 sentences describing the voice]

---

## Tone

**Default:** [Primary tone - calm, energetic, professional, casual, etc.]
**Range:** [When it shifts and how]

---

## Cadence

[Short sentences? Long flowing prose? Punchy? Musical?]

---

## Vocabulary

**Use:**
- [Word/phrase to use]
- [Word/phrase to use]

**Avoid:**
- [Word/phrase to avoid]
- [Word/phrase to avoid]

---

## Core Phrases

Signature phrases that define the brand:
- "[Phrase 1]"
- "[Phrase 2]"
- "[Phrase 3]"

---

## Quality Test

Before shipping copy, ask:
1. Can I see it in my head? (Concrete > Abstract)
2. Could someone call BS on it? (Specific > Vague)
3. Could a competitor copy-paste this? (Distinctive > Generic)

---

## Channel Variations

| Channel | Voice Adjustment |
|---------|------------------|
| Email | [How it shifts] |
| Social | [How it shifts] |
| Ads | [How it shifts] |
| Support | [How it shifts] |
```

---

## reference/proof/testimonials.md

```markdown
---
type: context
status: active
---

# Testimonials

## Best Quotes

### [Customer Name/Type]
> "[Exact quote - preserve their words]"

**Result:** [Specific outcome if stated]
**Source:** [Where this came from]
**Date:** [When received]

---

### [Customer Name/Type]
> "[Quote]"

**Result:**
**Source:**
**Date:**

---

## Themes

Common words/phrases customers use:
- "[Theme 1]" — appears in X reviews
- "[Theme 2]" — appears in X reviews
- "[Theme 3]" — appears in X reviews
```

---

## reference/proof/angles/[angle-name].md

```markdown
---
type: angle
status: active
---

# [Angle Name]

## Hook

[The entry point / attention grabber]

## Core Idea

[What this angle emphasizes — the central insight]

## Proof

[Evidence that validates this angle]
- [Review quote or data point]
- [Review quote or data point]

## Best For

[When to use this angle — audience state, channel, timing]

## Example Copy

[Sample headline or hook using this angle]
```

---

## decisions/YYYY-MM-DD-topic.md

```markdown
---
type: decision
date: YYYY-MM-DD
status: active
---

# Decision: [Topic]

## Situation

[What's happening, what prompted this decision]

## Research

[Summary of research that informed this]
See: `research/YYYY-MM-DD-topic.md`

## Options Considered

### Option A: [Name] (selected)
**Pros:**
**Cons:**

### Option B: [Name] (rejected)
**Pros:**
**Cons:**

## Decision

[The actual choice with rationale]

## Action Items

- [ ] [Action 1]
- [ ] [Action 2]
```

---

## research/YYYY-MM-DD-topic-[source].md

```markdown
---
type: research
date: YYYY-MM-DD
source: [gemini | claude-code | web | expert | mining]
topics: [topic1, topic2]
status: complete
---

# [Research Topic]

## Question

[What we were trying to learn]

## Key Findings

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## Implications

[What this means for the business]

## Next Steps

- [ ] [Action this research suggests]

---

## Raw Notes

[Detailed findings, quotes, data]
```

---

## README.md

```markdown
# [Business Name]

[One sentence: What this business does]

---

## About

[2-3 sentences about the business]

**URL:** [Website]

---

## This Repo

This is the **data repo** (knowledge base) for [Business Name].

It uses [vip](https://github.com/mainbranch-ai/vip) as the **engine** — skills, lenses, and frameworks that generate content from your data.

### Setup

1. **Clone the engine** (if you haven't):
   ```bash
   git clone https://github.com/mainbranch-ai/vip.git
   ```

2. **In Claude Code**, add vip as an additional working directory

3. **Work in this repo** as your primary directory

### How It Works

```
ENGINE (vip)     +     DATA (this repo)     =     OUTPUT
├── Skills                             ├── reference/            ├── Ads
├── Lenses                             ├── research/             ├── Emails
└── Pull updates, don't edit           └── You own this          └── Content
```

Skills from the engine read your `reference/` files and generate content to `outputs/`.

---

## Quick Stats

- **[Metric 1]:** [Value]
- **[Metric 2]:** [Value]
- **[Metric 3]:** [Value]
```
