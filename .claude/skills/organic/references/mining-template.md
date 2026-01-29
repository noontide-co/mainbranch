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

> **Remember:** Mining is INPUT. Reference is OUTPUT. The goal is to enrich your reference files, not just collect content.

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

**Framework Analysis (Human Judgment Required):**

| Dimension | What AI Observes | Why It Worked (YOUR Analysis) |
|-----------|------------------|-------------------------------|
| **Visual** | [Format type, production style, visual patterns] | [Your interpretation of WHY this visual approach connects] |
| **Audible** | [Energy level, pacing, vocal patterns] | [Your interpretation of WHY this delivery resonates] |
| **Emotional** | [Primary emotion triggered, controversial element] | [Your interpretation of the identity/emotion play] |

**Framework Transfer Notes (Human Work):**

This is where the real value lives. AI showed you WHAT worked. Now you decide WHY and WHETHER it transfers.

- **Why did this work?** [Your interpretation — not AI's guess]
- **Does it fit my energy?** [Can you authentically deliver this?]
- **Does it fit my audience?** [Will YOUR people respond to this approach?]
- **Transfer verdict:** [Use as-is / Adapt heavily / Skip — and why]

**Adaptation potential:** [High / Medium / Low]
[Specific notes on how to make it yours — or why it doesn't fit]

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

**This is the whole point.** Mining isn't complete until something goes into reference.

| File | Potential Update |
|------|------------------|
| reference/proof/angles/*.md | [New angles discovered — create or update angle files] |
| reference/core/voice.md | [Voice patterns to adopt/avoid] |
| reference/core/audience.md | [New understanding of what resonates with them] |
| reference/brand/guardrails.md | [Patterns to avoid, anti-patterns spotted] |

### Before You Generate: Update Reference First

The path is: Mining → Human Synthesis → Reference Update → THEN Content Generation

**Don't skip straight to scripts.** Extract what you learned, codify it, then generate from enriched reference.

### Next Steps

- [ ] **REQUIRED:** Update at least one reference file with insights from this mining
- [ ] Review frameworks with human judgment (Visual/Audible/Emotional)
- [ ] Codify winning patterns via `/think codify` (see `think/references/codify-phase.md`)
- [ ] THEN generate scripts from concepts (not before)

---

## Raw Data (Optional)

If extracted via Apify or other tools, include raw JSON or CSV here for reference.

```json
[Raw data if available]
```
```

---

## What AI Can and Cannot Do

> "AI can show WHAT worked. Human must judge WHY." — Koston Williams

### AI CAN:
- Collect posts and metrics
- Transcribe video content
- Identify engagement patterns
- Extract hooks and structure
- Note format distribution
- Surface patterns across competitors

### AI CANNOT:
- Tell you WHY something actually worked
- Judge framework transferability to YOUR niche
- Determine if a format fits YOUR personality
- Know if an angle aligns with YOUR offer
- Feel the emotional resonance

### YOUR JOB:
1. **Extract frameworks** — Visual, Audible, Emotional dimensions
2. **Judge transferability** — Does this fit YOUR voice, energy, offer?
3. **Apply to your niche** — Same framework, different execution
4. **Update reference files** — Winning patterns become evergreen

**The goal is reference files.** Mining is INPUT. Reference is OUTPUT. Content generation happens AFTER reference is enriched.

---

## The 6M View Insight

This framework extraction methodology comes from Koston Williams, who used it to create a video with 6 million views. The insight:

**AI can collect and display data. Only you can extract the framework that transfers.**

A competitor's video worked for THEM. The Visual/Audible/Emotional dimensions were calibrated to THEIR audience, THEIR personality, THEIR offer. Your job is to:

1. See the framework beneath the content
2. Judge whether it transfers to your context
3. Adapt it to your voice and audience
4. Codify what you learned into reference files

The skill isn't copying. The skill is framework transfer — same underlying pattern, different execution.

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
3. Generate scripts via `/organic video` or `/organic carousel`
4. (Optional) Codify winning angles via `/think codify`
