# Research Phase

Detailed workflow for research mode in `/think`.

**See also:** [research-architecture.md](research-architecture.md) for full routing and tool selection logic.

---

## Workflow

1. **Define the question** — What specifically are you trying to learn?
2. **Detect intent & route** — Determine which research tools to use (see [research-routing-quick-ref.md](research-routing-quick-ref.md))
3. **Check capabilities** — Are preferred tools available? Offer setup or fallback if not
4. **Gather findings** — Execute with token management and cost awareness
5. **Synthesize** (required) — Distill findings into actionable insight
6. **Save** — Write to `research/YYYY-MM-DD-topic-[source].md`

---

## Defining Good Questions

**Good research questions:**
- "What pricing tier structure should we use?"
- "Which messaging angle resonates with cold traffic?"
- "Should we add a guarantee? What kind?"

**Bad questions (too vague):**
- "How do I grow?"
- "What should I do next?"

---

## Source Suffixes

| Suffix | Source |
|--------|--------|
| `-gemini.md` | Gemini deep research |
| `-gpt.md` | ChatGPT research |
| `-claude-code.md` | This Claude Code session |
| `-claude-web.md` | Claude.ai web interface |
| `-x-social.md` | X/Twitter social research (Grok MCP) |
| `-yt-mining.md` | YouTube transcript mining (Apify) |
| `-ig-mining.md` | Instagram mining (Apify or manual) |
| `-local-mining.md` | Local video/audio transcription |
| `-voice-mining.md` | Voice memo transcription |
| `-competitor-mining.md` | Competitor site mining |
| `-internal-mining.md` | Internal data (emails, DMs, reviews) |
| `-transcript.txt` | Raw transcript (use specific `-mining.md` for synthesized) |
| `-audit.md` | Site or system audit |
| (none) | General or mixed sources |

---

## Content Strategy Research Routing

When the user's research topic involves content pillars, platform selection, content cadence, or content performance, check `reference/domain/content-strategy.md` first. If it exists, read it to understand current strategy before researching.

**Trigger topics:** content pillars, which platforms, content plan, cadence, content mix, repurposing, hooks, content frameworks, content metrics, newsletter strategy

**Research flow for content strategy topics:**
1. Read existing `reference/domain/content-strategy.md` (if present) to understand current state
2. Read `reference/core/soul.md` + `offer.md` + `audience.md` for pillar derivation context
3. Conduct research (web, mining, competitor analysis)
4. Synthesize into a research file as usual
5. In the **Implications for Reference Files** section, note which sections of `content-strategy.md` should be updated

If `content-strategy.md` does not exist, the research output should recommend creating it as an action item.

---

## Sources to Check

1. **Codebase** — Existing reference files, past decisions, research
2. **Web** — Competitors, industry benchmarks, expert perspectives
3. **X/Twitter** — Real-time sentiment, trending topics (see [grok-social.md](grok-social.md))
4. **User input** — "What else do you know about this?"
5. **YouTube transcripts** — When researching topics with video content (see below)
6. **Local video/audio** — User's own recordings, voice memos, Loom exports (see [local-transcription.md](local-transcription.md))

---

## YouTube Transcript Research

When user wants to research video content, use **Apify** (`starvibe/youtube-video-transcript`).

**IMPORTANT:** Never fall back to browser automation for transcripts. If Apify fails, troubleshoot the MCP — don't open Chrome. Browser automation for transcripts is slow, unreliable, and defeats the purpose of having MCPs.

**Trigger phrases:**
- "pull down this YouTube video"
- "transcribe this video"
- "what does [creator] say about..."
- "research this YouTube link"

**How to use:**

```
mcp__apify__call-actor
  actor: "starvibe/youtube-video-transcript"
  input: {
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "en",
    "include_transcript_text": true
  }
```

Then fetch results with `mcp__apify__get-actor-output` using the returned datasetId.

**Cost:** ~$0.005 per video (~200 videos for $1, regardless of length)

---

### Best Practices

**Token management:**
- Full transcripts can be 10-30K tokens for long videos
- Always use `include_transcript_text: true` to get plain text (not timestamped array)
- When fetching output, use `fields` parameter to get only what you need:
  ```
  fields: "title,channel_name,transcript_text"
  ```
- Don't dump raw transcripts into research files — synthesize first

**Efficient workflow:**
1. Call actor → get datasetId
2. Fetch with specific fields (title, transcript_text, view_count)
3. Synthesize immediately — extract frameworks, quotes, patterns
4. Save synthesis, not raw transcript

**If MCP fails:**
1. Check Apify account has credits
2. Verify video has captions (some don't)
3. Try different language code
4. Check if video is age-restricted or private
5. **Never** fall back to Chrome — fix the root cause

---

### Use Cases

**Best for:**
- Mining competitor messaging from their videos
- Extracting frameworks from educational content
- Researching what experts say about a topic
- Getting exact quotes for proof/angles

**After transcription:**
1. Synthesize key findings (don't dump raw transcript)
2. Extract quotable moments
3. Note messaging patterns
4. Save to `research/YYYY-MM-DD-[topic]-mining.md`

**Example workflow:**
> User: "Research what Alex Hormozi says about pricing"
> 1. Search YouTube for relevant Hormozi videos
> 2. Transcribe 2-3 key videos via Apify
> 3. Extract pricing principles and frameworks
> 4. Synthesize into actionable findings

---

## X/Twitter Social Research

When user wants to know what people are saying about a topic in real-time.

**Trigger phrases:**
- "what are people saying about..."
- "sentiment on X"
- "what's trending in..."
- "social proof research"

**How to use:** Grok X Insights MCP provides `grok_search_posts`, `grok_analyze_topic`, `grok_get_trends`.

**Setup:** See [grok-setup.md](grok-setup.md)
**Full workflow:** See [grok-social.md](grok-social.md)

**Quick example:**
```
User: "What are people saying about Skool communities?"

1. Check if Grok MCP available
2. grok_search_posts with query "Skool communities" timeWindow "7d"
3. Synthesize findings
4. Save to research/YYYY-MM-DD-skool-sentiment-x-social.md
```

**Fallback:** If no Grok MCP, use web search or ask user to share X screenshots manually.

---

## Local Video/Audio Transcription

When user wants to mine their OWN recordings (not YouTube), use local transcription.

**Trigger phrases:**
- "transcribe this video"
- "I have a recording to mine"
- "transcribe my Loom"
- "process this voice memo"
- User shares a local `.mp4`, `.mov`, `.m4a`, `.wav` file path

**How to use:**

See [local-transcription.md](local-transcription.md) for full workflow.

**Quick version (CLI):**
```bash
# Convert to 16kHz WAV
ffmpeg -i "video.mp4" -ar 16000 -ac 1 /tmp/audio.wav -y

# Transcribe
whisper-cli --model ~/.whisper/ggml-base.en.bin --file /tmp/audio.wav --output-txt
```

**With whisper-mcp:** Use `transcribe_audio` tool directly.

**After transcription:**
1. Synthesize key findings (don't dump raw transcript)
2. Extract quotable moments
3. Note messaging patterns
4. Save to `research/YYYY-MM-DD-[topic]-mining.md`

---

## Writing Good Synthesis

Every research output MUST have a synthesis section. This forces distillation.

**The rule:** If you can't synthesize it, you don't understand it.

---

## Content Mining: Framework Extraction (Human Work)

When mining competitor content, AI collects data. YOU extract the frameworks.

> "AI can show WHAT worked. Human must judge WHY." — Koston Williams

**Three dimensions to extract:**

| Dimension | What AI Observes | What YOU Determine |
|-----------|------------------|-------------------|
| **Visual** | Format, production style, patterns | Does this fit MY setup/skills? |
| **Audible** | Energy, pacing, delivery | Can I match this energy authentically? |
| **Emotional** | Primary emotion triggered | Does this align with MY audience's identity? |

**The skill is framework transfer.** A competitor's video worked for THEM — their audience, their personality, their offer. Your job is to see the framework beneath the content, judge whether it transfers to your context, and adapt it to your voice.

**Don't skip to content.** Mining → Framework Extraction (human) → Reference Update → THEN Generate.

This methodology comes from Koston Williams, who used it to create a 6M view video. The insight: copying content doesn't work. Extracting and transferring frameworks does.

---

### One-Sentence Summary

The hardest part. Forces clarity.

**Constraints:**
- **20 words maximum** — Not 21. Not "about 20."
- **One sentence** — Period at the end. No semicolons connecting two thoughts.
- **Actionable insight** — Not a description of what you researched.

**Bad:**
> "We researched competitor pricing strategies and found various approaches."

Problems: Describes research, not finding. Says nothing actionable.

**Good:**
> "Three-tier pricing with free/paid/premium maximizes reach while creating natural upgrade paths."

Why it works: Specific structure, specific benefit, 14 words.

### Key Findings

**Constraints:**
- **5-10 bullets** — Not 4. Not 11.
- **15 words each maximum** — Forces precision.
- **Facts, not opinions** — "Competitors charge $47-147" not "Competitors are reasonable."

Each finding should stand alone. Someone reading just the bullets should understand the research.

**Include:** Data points with numbers, patterns across sources, surprises, direct quotes.
**Exclude:** Background information, methodology details, tangential findings, speculation.

### Implications for Reference Files

Makes research actionable. Without it, research becomes orphaned knowledge.

For each finding, ask: "Does this change anything in my reference files?"

| File | Potential Update |
|------|------------------|
| `reference/core/offer.md` | Add tier structure, update pricing |
| `reference/core/audience.md` | Segment by tier |

**Bad:** "Update offer.md"
**Good:** "Update offer.md — Add three-tier pricing with benefits per tier"

### Open Questions

Research rarely answers everything. Document what you still don't know.

**Good:** "What should the free tier include to create desire for paid?"
**Bad:** "How do we make more money?" (too vague)

Each open question is a potential next research session.

---

## Synthesis Checklist

Before marking research as complete:

- [ ] One-sentence summary is under 20 words
- [ ] Summary states an insight, not a description
- [ ] 5-10 key findings, each under 15 words
- [ ] Findings are facts, not opinions
- [ ] Each finding could stand alone
- [ ] Implications section maps to specific reference files
- [ ] Open questions identify follow-up research needs
- [ ] Someone could read just the synthesis and understand the research

---

## Exit Criteria

Research is complete when:

- [ ] Research question answered
- [ ] Synthesis section completed
- [ ] Key findings extracted (5-10 bullets)
- [ ] Open questions documented
- [ ] File saved to `research/`

---

## Template

See [templates/research-template.md](templates/research-template.md) for full file structure.
