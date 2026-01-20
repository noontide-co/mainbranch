# Competitor Content Mining Template

Use this template when saving mining research to `research/YYYY-MM-DD-competitor-mine.md`.

---

## Frontmatter

```yaml
---
type: research
date: YYYY-MM-DD
source: competitor-mine
status: draft
competitors_analyzed:
  - "@handle1"
  - "@handle2"
linked_decisions: []
---
```

---

## Template

```markdown
---
type: research
date: YYYY-MM-DD
source: competitor-mine
status: draft
competitors_analyzed:
  - "@handle1"
  - "@handle2"
linked_decisions: []
---

# Competitor Content Mining

Mining date: YYYY-MM-DD
Competitors analyzed: X accounts
Posts reviewed: X total
Top performers extracted: X concepts

---

## Competitors Analyzed

### @handle1
- **Niche:** [Their specific focus]
- **Follower count:** [Approximate]
- **Post frequency:** [Daily/3x week/etc.]
- **Primary format:** [Reels/Carousels/Mixed]
- **Why included:** [Direct competitor / Adjacent / Aspirational]

### @handle2
- **Niche:** [Their specific focus]
- **Follower count:** [Approximate]
- **Post frequency:** [Daily/3x week/etc.]
- **Primary format:** [Reels/Carousels/Mixed]
- **Why included:** [Direct competitor / Adjacent / Aspirational]

[Repeat for each competitor]

---

## Data Collection Method

[How data was gathered]

- [ ] Apify Instagram Profile Scraper
- [ ] Manual review of top posts
- [ ] Screenshots provided by user
- [ ] Other: [specify]

**Time period:** [Last 30 days / Last 90 days / etc.]

**Engagement threshold:** [Top 20% by engagement rate / etc.]

---

## Top Performing Concepts

### Concept 1: [Title/Theme]

**Source:** @handle - [Post date or link]

**Engagement:**
- Likes: X
- Comments: X
- Engagement rate: X%

**Hook:**
> "[Exact hook text or first 3 seconds transcribed]"

**Format:** [Talking head / Carousel / Text overlay / etc.]

**Topic:** [Core subject matter]

**Angle:** [Emotional entry point - curiosity, pain, desire, identity]

**Structure:**
1. [Hook approach]
2. [Middle content approach]
3. [Ending/CTA approach]

**Why it worked:**
[Analysis of what made this perform]

**Adaptation potential:** [High / Medium / Low]
[Notes on how to adapt for user's brand]

---

### Concept 2: [Title/Theme]

[Same structure as above]

---

### Concept 3: [Title/Theme]

[Same structure as above]

---

[Continue for 10-20 concepts]

---

## Patterns Observed

### Content Patterns

| Pattern | Frequency | Example |
|---------|-----------|---------|
| [Pattern 1] | [How often seen] | [Brief example] |
| [Pattern 2] | [How often seen] | [Brief example] |
| [Pattern 3] | [How often seen] | [Brief example] |

### Hook Patterns

Most effective hook types observed:

1. **[Hook type]** - [Why it works in this niche]
2. **[Hook type]** - [Why it works in this niche]
3. **[Hook type]** - [Why it works in this niche]

### Format Distribution

| Format | % of Top Performers |
|--------|---------------------|
| Talking head | X% |
| Carousel | X% |
| Text overlay | X% |
| B-roll + voiceover | X% |
| Other | X% |

### Posting Insights

- **Best performing days:** [If observable]
- **Caption length trend:** [Short / Medium / Long]
- **CTA style:** [What CTAs top performers use]
- **Hashtag usage:** [Heavy / Light / None]

---

## Gaps and Opportunities

### What competitors are NOT doing:

1. [Gap 1]
2. [Gap 2]
3. [Gap 3]

### Underserved angles in the niche:

1. [Angle 1]
2. [Angle 2]

### Differentiation opportunities:

1. [How user can stand out]
2. [Unique perspective user has]

---

## Synthesis

### One-Sentence Summary
[Distilled insight from this mining session - 20 words max]

### Key Findings (5-10 bullets)
- [Finding 1]
- [Finding 2]
- [Finding 3]
- [Finding 4]
- [Finding 5]

### Top 5 Concepts to Adapt

| Priority | Concept | Adaptation Idea |
|----------|---------|-----------------|
| 1 | [Concept title] | [How to make it yours] |
| 2 | [Concept title] | [How to make it yours] |
| 3 | [Concept title] | [How to make it yours] |
| 4 | [Concept title] | [How to make it yours] |
| 5 | [Concept title] | [How to make it yours] |

### Implications for Reference Files

| File | Potential Update |
|------|------------------|
| reference/proof/angles/*.md | [New angles discovered] |
| reference/core/voice.md | [Voice patterns to adopt/avoid] |
| reference/competitors/handles.md | [New competitors to add] |

### Next Steps

- [ ] Generate scripts from concepts 1, 2, 3
- [ ] Save winning angles to reference
- [ ] [Other actions]

---

## Raw Data (Optional)

If extracted via Apify or other tools, include raw JSON or CSV here for reference.

```json
[Raw data if available]
```
```

---

## Usage Notes

### When to Mine

- Starting a new content strategy
- Content feels stale, need fresh ideas
- Entering a new platform
- Quarterly refresh of angles

### How Often

- **Full mining session:** Monthly or quarterly
- **Quick check:** Weekly scan of top performers
- **Reactive mining:** When a competitor goes viral

### What to Do After

1. Review concepts with user
2. Select 3-5 to adapt
3. Generate scripts via `/content video` or `/content carousel`
4. (Optional) Codify winning angles via `/think codify`
