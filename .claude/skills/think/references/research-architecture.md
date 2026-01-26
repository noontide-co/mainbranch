# Research Architecture for /think Skill

**Purpose:** Define how /think routes research tasks to appropriate tools based on user intent and available capabilities.

---

## Design Philosophy

**Progressive enhancement, not hard requirements.**

- /think works with ZERO external tools (codebase-only research)
- Adding API keys unlocks new capabilities
- Skills auto-detect what's available and route accordingly
- Users never blocked — always graceful fallback

---

## Available Research Tools

### Core (Always Available)

| Tool | What | Use For |
|------|------|---------|
| **Codebase search** | Grep, Read | Existing reference/research/decisions |
| **Web search** | WebSearch | General queries, articles, documentation |
| **Web fetch** | WebFetch | Specific URLs, competitor sites |
| **User input** | Direct paste | Voice memos, DMs, emails, screenshots |

### Enhanced (MCP-Based)

| Tool | MCP | What | Use For |
|------|-----|------|---------|
| **YouTube transcripts** | Apify | Extract video transcripts | Mining expert content, competitors, frameworks |
| **Instagram mining** | Apify | Scrape posts, stories, profiles | Competitor content, audience research |
| **X/Twitter sentiment** | xAI Grok | Real-time social search | Sentiment, trends, social proof |
| **Deep research** | Gemini 2.5 | Multi-step web synthesis | Complex research requiring reasoning |
| **Local transcription** | whisper-mcp | Transcribe audio/video files | User's own recordings, voice memos |

---

## Detection Logic

### 1. Check Available Tools (Once per Session)

On first `/think` invocation or when routing to research:

```bash
# Check for MCP tools
# Store results in session memory to avoid re-checking

APIFY_AVAILABLE=false
GROK_AVAILABLE=false
GEMINI_AVAILABLE=false
WHISPER_AVAILABLE=false

# Detection via tool presence
if mcp__apify__* tools exist → APIFY_AVAILABLE=true
if XAI_API_KEY env exists OR mcp__xai__* tools exist → GROK_AVAILABLE=true
if GOOGLE_API_KEY env exists → GEMINI_AVAILABLE=true
if mcp__whisper__* tools exist → WHISPER_AVAILABLE=true
```

**Store in session context:**
```
Available research capabilities:
✓ Codebase search
✓ Web search
✓ YouTube transcripts (Apify)
✓ X/Twitter sentiment (Grok)
✗ Deep research (Gemini not configured)
✓ Local transcription (whisper-mcp)
```

### 2. Route by Intent

Parse user's natural language to determine research type:

| User Says | Intent | Preferred Tool | Fallback |
|-----------|--------|----------------|----------|
| "transcribe this video", "pull down this YouTube" | YouTube mining | Apify YouTube Actor | Ask for manual transcript |
| "what are people saying about...", "sentiment on X" | Social sentiment | Grok X search | Web search for X posts |
| "research [complex topic]", "deep dive on..." | Deep research | Gemini 2.5 | Web search + synthesis |
| "transcribe this file", user shares .mp4/.m4a | Local transcription | whisper-mcp | ffmpeg + CLI fallback |
| "mine competitors", "what's [handle] posting" | Social mining | Apify Instagram Actor | Manual scraping guidance |
| "research [specific question]" | General research | Codebase → Web → Ask user | Always works |

### 3. Fallback Patterns

**Never block research.** If preferred tool unavailable:

```
Preferred tool missing → Inform user + offer fallback
User accepts fallback → Proceed with alternative
User declines → Offer setup guide (one-time)
```

**Example:**
```
User: "What are people saying about Skool on X?"

If GROK_AVAILABLE:
  → Use grok_search_posts

If !GROK_AVAILABLE:
  → "X/Twitter sentiment research works best with Grok MCP (one-time 5-min setup).

     1. Set up Grok now (I'll guide you)
     2. Use web search instead (less real-time)
     3. Skip this research"
```

---

## Intent Detection Patterns

### YouTube Mining

**Triggers:**
- YouTube URL in message
- "transcribe this video"
- "pull down this YouTube"
- "what does [creator] say about..."
- "research this video"

**Routing:**
```
If APIFY_AVAILABLE:
  → Use starvibe/youtube-video-transcript
  → Fetch with fields: "title,channel_name,transcript_text"
  → Synthesize immediately (don't dump raw)
  → Save to: research/YYYY-MM-DD-topic-yt-mining.md

If !APIFY_AVAILABLE:
  → "YouTube transcript mining needs Apify MCP. Set up now or paste transcript manually?"
```

**Cost estimate:** ~$0.005 per video (negligible)

### X/Twitter Social Research

**Triggers:**
- "what are people saying about..."
- "sentiment on X"
- "Twitter discourse about..."
- "social proof for..."
- "trending in [niche]"

**Routing:**
```
If GROK_AVAILABLE:
  → Use grok_search_posts with timeWindow
  → For multi-angle, use grok_analyze_topic
  → For trends, use grok_get_trends
  → Save to: research/YYYY-MM-DD-topic-x-social.md

If !GROK_AVAILABLE:
  → Use WebSearch with "site:x.com [query]"
  → Note: Less structured, no sentiment analysis
  → Save to: research/YYYY-MM-DD-topic-web.md
```

**Cost estimate:** ~$0.002-0.005 per query

### Deep Research

**Triggers:**
- "deep dive on..."
- "comprehensive research about..."
- "research everything about..."
- Complex multi-faceted questions
- Topic requiring synthesis across many sources

**Routing:**
```
If GEMINI_AVAILABLE:
  → Build structured prompt for Gemini 2.5
  → Include: question, context from reference files, desired depth
  → Process response and synthesize
  → Save to: research/YYYY-MM-DD-topic-gemini.md

If !GEMINI_AVAILABLE:
  → Use WebSearch + manual synthesis
  → Multiple queries → synthesize findings
  → Save to: research/YYYY-MM-DD-topic-claude-code.md
```

**Note:** Gemini deep research best for when Claude Code needs external reasoning. Don't use for simple questions.

### Local Transcription

**Triggers:**
- User shares local file path (.mp4, .mov, .m4a, .wav)
- "transcribe this recording"
- "process this voice memo"
- "transcribe my Loom"

**Routing:**
```
If WHISPER_AVAILABLE:
  → Use whisper-mcp transcribe_audio tool
  → Save to: research/YYYY-MM-DD-topic-local-mining.md

If !WHISPER_AVAILABLE:
  → Check for ffmpeg + whisper CLI
  → If available: Use CLI workflow (see local-transcription.md)
  → If not: "Local transcription needs whisper-mcp or CLI tools. Set up now?"
```

### Instagram Mining

**Triggers:**
- Instagram handle provided
- "mine [handle]"
- "what's [handle] posting"
- "research competitors on Instagram"

**Routing:**
```
If APIFY_AVAILABLE:
  → Use apify/instagram-profile-scraper
  → Limit posts (estimate tokens: 10 posts ≈ 3-5k tokens)
  → Ask: "Quick scan (5 posts) or deep mine (20 posts)?"
  → Save to: research/YYYY-MM-DD-topic-ig-mining.md

If !APIFY_AVAILABLE:
  → "Instagram mining needs Apify. Set up now or manual research?"
```

**Token management:** Warn if requesting >20 posts per competitor

### Codebase Research

**Triggers:**
- "what do we know about..."
- "check existing research on..."
- "have we decided..."
- Questions about internal state

**Routing:**
```
Always available (no external dependencies)

1. Search research/ for topic
2. Search decisions/ for related choices
3. Search reference/ for current state
4. Synthesize findings
5. Save to: research/YYYY-MM-DD-topic-claude-code.md
```

---

## File Naming Conventions

### Research Output Files

Format: `research/YYYY-MM-DD-topic-[source].md`

| Suffix | Source | When Used |
|--------|--------|-----------|
| `-yt-mining.md` | YouTube via Apify | Transcribed YouTube videos |
| `-x-social.md` | X/Twitter via Grok | Social sentiment research |
| `-gemini.md` | Gemini 2.5 deep research | Complex multi-step research |
| `-ig-mining.md` | Instagram via Apify | Instagram content mining |
| `-local-mining.md` | Local files via whisper | User's own video/audio |
| `-voice-mining.md` | Voice memos via whisper | User's voice recordings |
| `-claude-code.md` | This Claude Code session | General research using available tools |
| `-web.md` | Web search fallback | When MCP unavailable |
| (no suffix) | Mixed or manual sources | User provided data |

**Why source suffixes:**
- Provenance tracking (know where data came from)
- Reproducibility (can re-run with same tool)
- Cost attribution (know which tools used)
- Skill routing (some skills prefer certain sources)

---

## Token Management

> **Note:** Token estimates throughout this document are approximate and may vary based on model updates and actual content. Adjust based on your usage patterns.

### Problem

Research tools return data that becomes Claude tokens. Large outputs can:
- Exceed MAX_MCP_OUTPUT_TOKENS (default 25k)
- Burn context unnecessarily
- Slow down sessions

### Solutions

#### 1. Limit at Source

| Tool | How to Limit |
|------|--------------|
| YouTube (Apify) | Use `fields` parameter: only get `transcript_text`, `title` |
| Instagram (Apify) | Limit `resultsLimit` parameter (e.g., 10 posts not 50) |
| Grok X search | Set `limit` to 20-30 posts, not default 50 |
| Gemini | Structure prompt to request concise findings |

#### 2. Estimate Before Running

Show user token estimate:

```
"Mining 20 posts from 3 competitors will be ~15-20k tokens (about 10% of our context window).

Alternatives:
- Quick scan: 5 posts each = ~5k tokens
- Deep mine: 30 posts each = ~30k tokens (will need synthesis pass)"
```

#### 3. Synthesize Immediately

**Never dump raw output into research files.**

```
Raw transcript → Extract key points → Save synthesis
Not: Raw transcript → Save everything → Try to work with it later
```

#### 4. Progressive Depth

Offer quick scan first:

```
"Let's start with a quick scan (5 posts, ~3k tokens). If you want deeper, we can mine more."
```

---

## Setup Guides

### When to Offer Setup

```
Tool missing + User wants that research type → Offer setup once per session

"This research works best with [Tool]. Not set up on this machine.

1. Set up now (5-10 min, one-time)
2. Use [Fallback] instead
3. Skip this research"
```

### Setup Guide Locations

| Tool | Guide Path |
|------|------------|
| Apify | `.claude/skills/content/references/apify-setup.md` |
| Grok | `.claude/skills/think/references/grok-setup.md` |
| Gemini | `.claude/skills/think/references/gemini-setup.md` |
| whisper-mcp | `.claude/skills/think/references/local-transcription.md` |

---

## Research Workflow Architecture

### Standard Flow (All Research Types)

```
1. Detect Intent
   └─> Determine research type from user message

2. Check Capabilities
   └─> Is preferred tool available?

3. Route
   ├─> If available: Use preferred tool
   └─> If not: Offer setup or fallback

4. Execute
   ├─> Gather data (with token limits)
   └─> Estimate cost/tokens before running

5. Synthesize (REQUIRED)
   ├─> One-sentence summary (20 words max)
   ├─> Key findings (5-10 bullets)
   └─> Implications for reference files

6. Save
   └─> research/YYYY-MM-DD-topic-[source].md

7. Checkpoint
   └─> "Ready to make a decision, or need more research?"
```

### Multi-Source Research

For complex questions requiring multiple tools:

```
1. Define question clearly
2. Identify needed sources (e.g., social + web + codebase)
3. Spawn parallel research subagents
4. Each subagent → separate research file
5. Create synthesis research file combining all
6. Save individual files + combined synthesis
```

**Example:**
```
Question: "Should we add a guarantee? What type?"

Sources:
- Codebase: Check if we've researched this before
- X/Twitter: What are people saying about guarantees in our niche?
- Competitors: What guarantees do they offer? (Instagram/web)
- Deep research: Guarantee psychology and best practices (Gemini or web)

Output:
- research/2026-01-26-guarantee-x-social.md
- research/2026-01-26-guarantee-competitors.md
- research/2026-01-26-guarantee-psychology-gemini.md
- research/2026-01-26-guarantee-synthesis.md (combines all)
```

---

## Capability Matrix

What each research type can do:

| Research Type | Best For | Requires | Fallback | Cost |
|---------------|----------|----------|----------|------|
| **Codebase** | Internal state | Nothing | N/A | Free |
| **Web search** | General queries | Nothing | N/A | Free |
| **Web fetch** | Specific URLs | Nothing | N/A | Free |
| **YouTube mining** | Video content | Apify MCP | Manual transcript | ~$0.005/video |
| **X sentiment** | Real-time social | Grok MCP | Web search X posts | ~$0.002/query |
| **Deep research** | Complex synthesis | Gemini API | Web + manual synthesis | ~$0.01-0.05/query |
| **Instagram mining** | Visual platform research | Apify MCP | Manual screenshots | ~$0.40-0.50/1K results |
| **Local transcription** | User's own files | whisper-mcp | CLI fallback | Free (local) |

---

## Session Memory Pattern

Don't re-check capabilities every time. Store in session:

```
On first /think:
  Check all capabilities → Store results

On subsequent /think:
  Read stored capabilities → Route immediately

On new session:
  Re-check (capabilities may have changed)
```

---

## Implementation Notes

### Routing Decision Tree

```python
def route_research(user_message, available_tools):
    """Route research request to appropriate tool."""

    # Check for explicit URLs/files first
    if contains_youtube_url(user_message):
        return route_youtube(available_tools)

    if contains_local_file(user_message):
        return route_local_transcription(available_tools)

    # Check for social research triggers
    if contains_social_trigger(user_message):
        if "x" in message or "twitter" in message:
            return route_x_social(available_tools)
        if "instagram" in message or contains_ig_handle(message):
            return route_instagram(available_tools)

    # Check for complexity
    if is_complex_research(user_message):
        return route_deep_research(available_tools)

    # Default: general research (always works)
    return route_general_research()
```

### Tool Priority

When multiple tools could work:

1. **Most specific** tool for the job (e.g., YouTube actor for YouTube URLs)
2. **Highest fidelity** when tie (e.g., Grok > web search for X sentiment)
3. **Lowest friction** when equivalent (e.g., codebase before web if answer might be there)

---

## Error Handling

### MCP Tool Failures

```
Tool exists but fails → Don't retry with same tool
  ├─> Check for known issues (no credits, rate limit)
  ├─> Explain to user what went wrong
  └─> Offer fallback or skip

Never: Keep retrying same tool hoping for different result
```

### Partial Results

```
Tool returns partial results → Accept and synthesize what we got
  ├─> Note limitation in research file
  └─> Document what's missing in "Open Questions"
```

### No Results

```
Tool returns zero results → Inform user, ask to refine query
  ├─> Suggest more specific query
  └─> Offer alternative source
```

---

## Quality Gates

Before marking research as complete:

- [ ] Synthesis section exists
- [ ] One-sentence summary under 20 words
- [ ] 5-10 key findings, each under 15 words
- [ ] Implications for reference files documented
- [ ] Source attributed correctly (suffix + citations)
- [ ] Token usage reasonable (< 25k for output)
- [ ] File saved to correct location with correct naming

---

## Future Enhancements

Potential additions (not implemented yet):

- **Reddit sentiment** — Similar to X/Twitter research
- **LinkedIn research** — Professional sentiment, thought leadership
- **Email mining** — Extract insights from user's own emails (privacy-sensitive)
- **Podcast transcription** — Similar to YouTube but audio-only RSS feeds
- **PDF research** — Extract from research papers, ebooks
- **Competitor ad mining** — Facebook Ad Library scraping via Apify

**How to add new research types:**

1. Add detection pattern to intent routing
2. Create tool-specific guide in `references/`
3. Add fallback pattern
4. Update this architecture doc
5. Add suffix to file naming conventions

---

## See Also

- `research-phase.md` — Detailed research workflow
- `gemini-setup.md` — Gemini API setup guide
- `gemini-deep-research.md` — Deep research workflow with Gemini
- `grok-setup.md` — Grok MCP setup guide
- `grok-social.md` — X/Twitter research specifics
- `local-transcription.md` — Local audio/video workflow
- `apify-discovery.md` — Apify actors and token costs
- `research-template.md` — File template for research output
