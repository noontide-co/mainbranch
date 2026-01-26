# X/Twitter Social Research

Real-time social intelligence using Grok X Insights MCP.

---

## When to Use

**Trigger phrases:**
- "what are people saying about..."
- "sentiment on X about..."
- "what's trending in..."
- "social proof for..."
- "X/Twitter research on..."
- "real-time opinions about..."

**Best for:**
- Understanding current sentiment around a topic
- Finding social proof and real opinions
- Researching what your audience actually talks about
- Trend discovery in your niche
- Competitive intelligence (what are people saying about competitors?)

**Not for:**
- Historical research (use Gemini/web search)
- Deep technical research (use Gemini)
- Content that lives in articles/blogs (use web search)

---

## Quick Start

**Check if Grok MCP is available:**

Ask user: "Do you have Grok X Insights MCP set up? (One-time 5-min setup)"

1. Yes → proceed with Grok tools
2. No → offer setup guide ([grok-setup.md](grok-setup.md))
3. Skip → fall back to web search (less real-time)

---

## Tools Reference

### 1. grok_search_posts

Search and analyze X posts about any topic.

```json
{
  "query": "AI-native business tools",
  "timeWindow": "24hr",
  "limit": 50,
  "analysisType": "both"
}
```

**Parameters:**
- `query` (required): Search query or topic
- `timeWindow`: "15min", "1hr", "4hr", "24hr", "7d" (default: "4hr")
- `limit`: 1-50 posts (default: 50)
- `analysisType`: "sentiment", "themes", "both" (default: "both")

**Returns:**
- Summary of findings
- Themes identified
- Sentiment breakdown (positive/negative/neutral/mixed)
- Notable observations
- Citations (links to actual posts)

---

### 2. grok_analyze_topic

Deep analysis with customizable aspects.

```json
{
  "topic": "Skool communities",
  "aspects": [
    "common complaints",
    "what people love",
    "competitor comparisons",
    "pricing sentiment"
  ],
  "timeWindow": "7d"
}
```

**Use when:** You need specific angles analyzed, not just general sentiment.

**Good aspects to analyze:**
- "common complaints"
- "what people love"
- "key influencers"
- "controversy points"
- "pricing sentiment"
- "competitor comparisons"
- "emerging trends"
- "use cases people share"

---

### 3. grok_get_trends

Identify what's trending in a category.

```json
{
  "category": "AI tools",
  "limit": 50
}
```

**Returns:**
- Trending topics with volume (high/medium/low)
- Sentiment per trend
- Key themes
- Citations

**Use when:** You want to discover what's hot, not research a specific topic.

---

### 4. grok_chat

General chat with Grok, optionally grounded in live X data.

```json
{
  "prompt": "What's the current discourse around community-based businesses?",
  "enableSearch": true,
  "searchLimit": 50,
  "temperature": 0.3
}
```

**Use when:** You want conversational exploration, not structured analysis.

---

## Workflow Patterns

### Pattern 1: Sentiment Check

User: "What are people saying about Skool?"

```
1. grok_search_posts with query "Skool" timeWindow "7d"
2. Extract: overall sentiment, common themes, notable posts
3. Synthesize findings
4. Save to research/YYYY-MM-DD-skool-sentiment-x-social.md
```

### Pattern 2: Competitive Intelligence

User: "What do people say about [competitor] vs us?"

```
1. grok_analyze_topic with aspects: ["complaints", "what people love", "comparisons"]
2. Run for competitor AND for your brand
3. Compare findings
4. Save to research/YYYY-MM-DD-competitive-x-social.md
```

### Pattern 3: Trend Discovery

User: "What's trending in the coaching space?"

```
1. grok_get_trends with category "coaching" or "online business"
2. Identify relevant trends
3. For top 2-3 trends, run grok_search_posts for deeper analysis
4. Save to research/YYYY-MM-DD-coaching-trends-x-social.md
```

### Pattern 4: Social Proof Mining

User: "Find social proof about [topic] for my messaging"

```
1. grok_search_posts with topic, timeWindow "7d", analysisType "themes"
2. Extract actual quotes/opinions from citations
3. Identify patterns in how people describe the problem/solution
4. Save quotes and patterns to research/
5. Consider codifying strong angles to reference/proof/angles/
```

---

## Output Format

Save X/Twitter research to: `research/YYYY-MM-DD-[topic]-x-social.md`

**Template:**

```markdown
---
type: research
date: YYYY-MM-DD
source: grok-x-social
status: complete
topics: [topic1, topic2]
linked_decisions: []
---

# [Topic] — X/Twitter Social Research

## One-Sentence Summary
[20 words max — what did you learn?]

## Query Details
- **Search:** [query used]
- **Time window:** [timeframe]
- **Posts analyzed:** [count]

## Sentiment Overview
- **Overall:** [positive/negative/neutral/mixed]
- **Distribution:** [breakdown]

## Key Themes
1. [Theme 1]
2. [Theme 2]
...

## Notable Quotes
> "[Actual quote from X post]"
> — [@handle](link)

> "[Another quote]"
> — [@handle](link)

## Implications for Reference Files
- [Which files should be updated based on this?]

## Open Questions
- [What follow-up research is needed?]

## Citations
- [Links to source posts]
```

---

## Cost & Token Management

**Typical costs per operation (Grok 4.1 Fast):**

| Operation | Approx Tokens | Approx Cost |
|-----------|---------------|-------------|
| Simple sentiment search | ~7K total | ~$0.002 |
| Deep topic analysis | ~15K total | ~$0.005 |
| Trend discovery | ~10K total | ~$0.003 |

**$5 gets you:** ~1,500-2,500 research queries

**Manage tokens by:**

1. **Start narrow:** Use shorter timeWindow (4hr vs 7d)
2. **Limit posts:** Start with 20-30, increase if needed
3. **Specific queries:** "Skool pricing complaints" vs just "Skool"
4. **Synthesize immediately:** Don't dump raw output into files

---

## Combining with Other Research

**Grok + Gemini workflow:**

1. **Grok first:** What are people saying RIGHT NOW?
2. **Gemini second:** Deep research on the patterns you found
3. **Synthesize:** Combine real-time sentiment with structured research

**Example:**
> "Research email list transition strategies"
> 1. Grok: "What are people saying about email list rebrands?" (real sentiment)
> 2. Gemini: "Best practices for email list transitions" (structured research)
> 3. Combine into comprehensive research file

---

## Fallback (No Grok MCP)

If user doesn't have Grok set up and doesn't want to:

1. **Web search:** Use WebSearch for X/Twitter discussions (less structured)
2. **Manual:** Ask user to share screenshots of relevant X posts
3. **Skip:** Note that social research was skipped, proceed with other sources

Don't block research just because Grok isn't available — adapt and continue.
