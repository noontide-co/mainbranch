# Gemini Deep Research

When and how to use Gemini for comprehensive research.

---

## When to Use Gemini

**Trigger phrases:**
- "deep dive on..."
- "comprehensive research about..."
- "research everything about..."
- "best practices for..."
- "what does the research say about..."
- "industry analysis of..."

**Best for:**
- Complex questions requiring synthesis across many sources
- Competitive analysis
- Industry trends and market research
- Best practices research
- Academic-style investigation
- Strategic questions requiring nuanced answers

**Not for:**
- Quick factual lookups (use WebSearch)
- Real-time social data (use Grok)
- YouTube/video transcripts (use Apify)
- Simple questions with obvious answers (just answer)

---

## How It Works

Gemini Deep Research:
1. Analyzes your question for complexity
2. Searches across multiple web sources
3. Synthesizes findings into coherent analysis
4. Provides structured output with key findings

**Typical time:** 30-60 seconds for comprehensive research

**Token output:** 5-10K tokens (fits comfortably in context)

---

## Quick Start

**Check if Gemini is available:**

```bash
echo $GOOGLE_API_KEY
```

If empty, offer setup: "Deep research works better with Gemini. 3-min setup?"

1. Yes -> Guide through [gemini-setup.md](gemini-setup.md)
2. No -> Fall back to WebSearch + manual synthesis
3. Skip -> Proceed with available tools

---

## Workflow from /think

When user triggers deep research:

```
1. Detect intent (complex research question)
2. Check: Is GOOGLE_API_KEY set?
   ├─> If no: "Deep research works best with Gemini. Set up now (3 min)?"
   └─> If yes: Continue
3. Construct research prompt with context
4. Call Gemini for comprehensive research
5. Synthesize response (don't dump raw)
6. Save to: research/YYYY-MM-DD-topic-gemini.md
7. Checkpoint: "Ready to decide, or need more research?"
```

---

## Prompt Patterns

### For Competitive Analysis

```
Research [competitor] in the [industry] space. Focus on:
- Pricing model and tiers
- Key features and positioning
- Customer sentiment and reviews
- Strengths and weaknesses vs alternatives

Provide specific examples and data where available.
```

### For Industry Research

```
Deep research on [industry/trend]. Cover:
- Key players and market landscape
- Recent developments (last 12 months)
- Where this is heading (predictions)
- Opportunities and risks

Include sources for key claims.
```

### For Strategic Questions

```
Research best practices for [topic]. What do experts recommend?
- What approaches have proven successful?
- What are common mistakes to avoid?
- What data supports different strategies?
- How does this apply to [specific context]?
```

### For Problem Exploration

```
Research: [problem or question]

Context from our business:
- Offer: [brief description]
- Audience: [who we serve]
- Current approach: [what we do now]

What does the research suggest for our situation?
```

---

## Output Format

Save to: `research/YYYY-MM-DD-topic-gemini.md`

**Template:**

```markdown
---
type: research
date: YYYY-MM-DD
source: gemini
model: gemini-2.5-flash  # Check https://ai.google.dev/models for latest
status: complete
topics: [topic1, topic2]
linked_decisions: []
---

# [Topic] — Deep Research

## One-Sentence Summary
[20 words max — the key insight]

## Research Question
[What were we trying to learn?]

## Key Findings

### Finding 1: [Title]
[2-3 sentences explaining this finding]

### Finding 2: [Title]
[2-3 sentences]

### Finding 3: [Title]
[2-3 sentences]

[Continue as needed, typically 5-10 findings]

## Synthesis
[1-2 paragraphs connecting the findings into a coherent picture]

## Implications for Reference Files
- **offer.md:** [How this affects our offer]
- **audience.md:** [What we learned about our audience]
- **voice.md:** [Tone/messaging implications]
- **angles/:** [New angles or refinements]

## Open Questions
- [What follow-up research is needed?]
- [What remains uncertain?]

## Sources
- [Key sources cited in research]
```

---

## Combining with Other Tools

**Grok + Gemini workflow:**

1. **Grok first:** What are people saying RIGHT NOW? (real-time sentiment)
2. **Gemini second:** Deep research on patterns found (structured analysis)
3. **Synthesize:** Combine real-time sentiment with comprehensive research

**Example:**
```
User: "Research what people think about guarantees in coaching"

1. Grok: "What are people saying about guarantees on X?" (current sentiment)
2. Gemini: "Best practices for guarantees in coaching" (structured research)
3. Create synthesis combining both perspectives
```

**WebSearch + Gemini workflow:**

1. **WebSearch:** Quick facts and recent articles
2. **Gemini:** Deeper analysis on the core question
3. **Synthesize:** Fact-check Gemini with specific sources

---

## Cost & Token Management

**Costs (Google AI Studio free tier):**

| Usage Level | Daily Queries | Cost |
|-------------|---------------|------|
| Light | 10-20 | Free |
| Moderate | 50-100 | Free |
| Heavy | 100+ | May hit limits |

**Typical query costs (pay-as-you-go):**

| Query Type | Approx Tokens | Approx Cost |
|------------|---------------|-------------|
| Simple deep research | ~5K | ~$0.01 |
| Complex multi-faceted | ~10K | ~$0.02-0.03 |
| Comprehensive analysis | ~15K | ~$0.04-0.05 |

**Manage tokens by:**

1. **Be specific:** "Guarantees in online coaching" vs just "guarantees"
2. **Provide context:** Include relevant info from reference files
3. **Limit scope:** "Focus on pricing" vs "research everything"
4. **Synthesize immediately:** Extract key findings, don't save raw dumps

---

## Fallback (No Gemini)

If user doesn't have Gemini set up and doesn't want to:

1. **WebSearch synthesis:** Multiple WebSearch queries + manual synthesis
   - Save to: `research/YYYY-MM-DD-topic-web.md`
   - Note: Less comprehensive, requires more queries

2. **Apify RAG Browser:** Use `apify/rag-web-browser` for web research
   - Good middle ground between WebSearch and Gemini
   - Save to: `research/YYYY-MM-DD-topic-claude-code.md`

3. **Skip:** Note that deep research was skipped, proceed with available info

Don't block research just because Gemini isn't available — adapt and continue.

---

## Quality Checklist

Before saving Gemini research file:

- [ ] One-sentence summary (20 words max)
- [ ] 5-10 key findings, each with clear title
- [ ] Synthesis connecting findings
- [ ] Implications for reference files documented
- [ ] Open questions captured
- [ ] Sources noted where relevant
- [ ] File named correctly: `YYYY-MM-DD-topic-gemini.md`

---

## See Also

- [gemini-setup.md](gemini-setup.md) — Setup guide
- [grok-social.md](grok-social.md) — X/Twitter research (complementary)
- [research-architecture.md](research-architecture.md) — Full routing logic
- [research-template.md](templates/research-template.md) — File template
