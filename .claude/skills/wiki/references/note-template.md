# Atomic Note Guidelines

Guidelines for creating evergreen notes following Andy Matuschak's principles.

---

## Core Principles

### 1. Atomic — One Idea Per Note

Each note contains **one complete idea**. If you can't summarize it in a single sentence, split it.

**Good:**
- "Evergreen notes should be concept-oriented"
- "Manual file management is high-friction waste"

**Bad:**
- A note combining productivity + focus + calendars + meetings

### 2. Concept-Oriented — Timeless Ideas

Notes are about **concepts**, not events, projects, or people.

**Good:**
- "Prefer associative ontologies to hierarchical taxonomies"
- "Deep work requires uninterrupted time blocks"

**Bad:**
- "My thoughts on note-taking" (vague, personal)
- "2026-01-21 Notes" (date-based)
- "What I learned from reading Deep Work" (event-based)

### 3. API-Style Titles

Titles are **sharp concept handles** that make content predictable.

**Good:**
- "Evergreen notes should be atomic" (you know exactly what it covers)
- "Defaulting to no protects deep work"

**Bad:**
- "Thoughts on productivity" (vague)
- "Interesting idea" (uninformative)

### 4. Densely Linked

**Minimum:** 3 WikiLinks per note
**Target:** 1 link per 30-50 words

Links create **associative connections**, not hierarchies.

**WikiLink format:**
```markdown
[[Note Title]]           → Standard link
[[Note Title|Custom]]    → Custom display text (use sparingly)
```

---

## Word Count Targets

| Status | Target | Max | Description |
|--------|--------|-----|-------------|
| **seed** | 50-150 | 200 | Rough capture, needs work |
| **growing** | 100-200 | 300 | Being developed, iterating |
| **evergreen** | 150-250 | 350 | Stable, refined, heavily linked |

Only exceed 350 words with explicit justification.

---

## Frontmatter Template

```yaml
---
title: "Note Title as Concept Statement"
created: 2026-01-21
visibility: public
status: seed | growing | evergreen
summary: "1-2 sentence summary for previews and hover cards"
tags: [topic1, topic2]
aliases: ["alternative name", "shorthand"]
---
```

**Required fields:**
- `title` — Concept-oriented statement
- `created` — Date created
- `visibility` — public, private, or draft
- `status` — seed, growing, or evergreen
- `summary` — 1-2 sentences for previews

**Optional fields:**
- `tags` — Categorization (use sparingly, prefer links)
- `aliases` — Alternative names for WikiLink resolution
- `updated` — Date last modified

---

## Content Structure

### Opening

Start with the core claim. No preamble.

**Good:**
> Digital gardens are cool, but managing them sucks. This is different.

**Bad:**
> In today's fast-paced world, note-taking has become increasingly important...

### Body

Dense insights with WikiLinks woven naturally.

**Example (150 words, 5 links):**
```markdown
[[Atomic Notes]] are the foundation of [[Evergreen Notes]]. Each note
contains **one complete idea**. This approach is inspired by the
[[Zettelkasten Method]] but adapted for modern tools.

Unlike traditional note-taking, atomic notes prioritize
[[Associative Linking Over Hierarchies]]. Instead of folders,
[[Personal Knowledge Graphs]] emerge organically from connections.
```

### Closing

No summary needed. End when the idea is complete.

---

## Voice Guidelines

Write like yourself, not like generic AI.

**Good (direct, technical, confident):**
> Most companies drown in Slack noise. The fix isn't better search—it's an agent that knows what you're working on.

> Unscheduled 'quick calls' destroy flow states. The calendar is a battlefield.

**Bad (generic AI):**
- "Many experts believe that..."
- "It's interesting to consider..."
- "In conclusion, we can see that..."

**Rule:** If it sounds like a blog post intro, rewrite it.

---

## Common Pitfalls

| Pitfall | Example | Fix |
|---------|---------|-----|
| Vague title | "Thoughts on productivity" | "Defaulting to no protects deep work" |
| Too broad | Note covering 4+ concepts | Split into separate notes |
| Event-based | "What I learned from X" | "Deep work requires time blocks" |
| Under-linked | 0-1 WikiLinks | Add min 3 links |
| Over-explained | Long preamble | Get to the point |

---

## Example Note

```yaml
---
title: "Externalizing thought builds cognitive scaffold"
created: 2026-01-21
visibility: public
status: evergreen
summary: "Writing ideas down frees working memory and reveals gaps in thinking."
tags: [thinking, writing, cognition]
---
```

Writing isn't just recording—it's **thinking made visible**. When you externalize ideas, you free working memory for new connections. This is why [[Atomic Notes]] work better than mental storage.

The act of writing reveals gaps. You think you understand something until you try to explain it. [[Evergreen Notes]] force clarity by demanding you capture **one complete idea** in 150-250 words.

This is also why [[Build in Public]] accelerates learning. Publishing creates accountability. Your future self (and others) will read this, so you write more carefully.

The best thinkers aren't those with better memories—they're those who externalize effectively. See [[Zettelkasten Method]] for the historical precedent.

---

*175 words, 5 WikiLinks*

---

## Quality Checklist

Before marking note as `evergreen`:

- [ ] Title is concept-oriented (not event-based or vague)
- [ ] Content is atomic — one complete idea
- [ ] Word count is 150-250 words (max 350 with justification)
- [ ] Minimum 3 WikiLinks included
- [ ] Link density ~1 per 30-50 words
- [ ] Summary field is 1-2 sentences
- [ ] No preamble — opens with core claim
- [ ] Voice is direct, not generic AI
- [ ] Status reflects actual state (seed → growing → evergreen)
