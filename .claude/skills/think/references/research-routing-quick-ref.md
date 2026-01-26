# Research Routing Quick Reference

Fast lookup table for routing research requests in /think skill.

---

## Intent Detection Cheat Sheet

| User Says | Route To | Requires | Fallback |
|-----------|----------|----------|----------|
| YouTube URL, "transcribe video" | Apify YouTube | `mcp__apify__*` | Ask for manual transcript |
| "what are people saying", "X sentiment" | Grok X search | `XAI_API_KEY` OR `mcp__xai__*` | WebSearch site:x.com |
| Quick research, fact-checking | Gemini Flash (Tier 1) | `GOOGLE_API_KEY` | WebSearch + synthesis |
| "deep dive", "comprehensive research" | Gemini Deep (Tier 2) | `GOOGLE_API_KEY` | Tier 1 or WebSearch |
| Local file path, "transcribe recording" | whisper-mcp | `mcp__whisper__*` | CLI fallback |
| Instagram handle, "mine competitors" | Apify Instagram | `mcp__apify__*` | Manual guidance |
| "what do we know", "check existing" | Codebase grep | Always available | N/A |
| General question | WebSearch | Always available | N/A |

**Gemini Tier Status:**
- Tier 1 (Flash): **TESTED** - works via REST API
- Tier 2 (Deep Research): **NOT TESTED** - documented but needs verification

---

## Tool Availability Check

**Run once per session, cache results:**

```bash
# Check for Apify (YouTube, Instagram)
if mcp__apify__* exists: APIFY=true

# Check for Grok (X/Twitter)
if $XAI_API_KEY set OR mcp__xai__* exists: GROK=true

# Check for Gemini (deep research)
if $GOOGLE_API_KEY set: GEMINI=true

# Check for whisper (local transcription)
if mcp__whisper__* exists: WHISPER=true
```

---

## File Naming by Source

| Suffix | Tool | Example |
|--------|------|---------|
| `-yt-mining.md` | Apify YouTube | `2026-01-26-hormozi-pricing-yt-mining.md` |
| `-x-social.md` | Grok X/Twitter | `2026-01-26-skool-sentiment-x-social.md` |
| `-flash.md` | Gemini Flash (Tier 1) | `2026-01-26-quick-research-flash.md` |
| `-gemini-deep.md` | Gemini Deep (Tier 2) | `2026-01-26-guarantee-psychology-gemini-deep.md` |
| `-ig-mining.md` | Apify Instagram | `2026-01-26-competitor-content-ig-mining.md` |
| `-local-mining.md` | whisper-mcp | `2026-01-26-sales-call-local-mining.md` |
| `-claude-code.md` | This session | `2026-01-26-pricing-strategy-claude-code.md` |
| `-web.md` | WebSearch fallback | `2026-01-26-industry-trends-web.md` |
| (no suffix) | Mixed/manual | `2026-01-26-customer-feedback.md` |

---

## Token Estimates

| Source | Data Volume | Approx Tokens | Cost |
|--------|-------------|---------------|------|
| YouTube (short) | 10-min video | ~2-3k | $0.005 |
| YouTube (long) | 60-min video | ~10-15k | $0.005 |
| Grok X search | 20 posts | ~5-7k | $0.002 |
| Grok X search | 50 posts | ~10-15k | $0.005 |
| Instagram quick | 5 posts | ~3-5k | $0.01 |
| Instagram deep | 20 posts | ~10-15k | $0.04 |
| Gemini Flash (Tier 1) | Quick query | ~5-10k | ~$0.01-0.05 |
| Gemini Deep (Tier 2) | Complex research | ~60-80k output | ~$2-5/task |

**Note:** Tier 1 is for 80% of research. Reserve Tier 2 for complex multi-source synthesis.

**Rule:** Warn if single operation >15k tokens

---

## Setup Guide Paths

| Tool | Guide |
|------|-------|
| Apify | `.claude/skills/organic/references/apify-setup.md` |
| Grok | `.claude/skills/think/references/grok-setup.md` |
| Gemini | `.claude/skills/think/references/gemini-setup.md` |
| whisper | `.claude/skills/think/references/local-transcription.md` |

---

## Routing Decision Flow

```
1. Check for explicit URL/file
   ├─> YouTube URL → route_youtube()
   ├─> Instagram URL → route_instagram()
   └─> Local file → route_local_transcription()

2. Check for social triggers
   ├─> X/Twitter mention → route_x_social()
   └─> Instagram handle → route_instagram()

3. Check complexity
   ├─> Simple question → route_gemini_tier1()
   └─> Complex multi-step → route_gemini_tier2()

4. Default
   └─> route_general_research()

**Gemini Tier Decision:**
- Tier 1: Quick questions, fact-checking (30-60s, ~$0.01-0.05)
- Tier 2: Competitive analysis, industry research, multi-source synthesis (5-20min, ~$2-5)
```

---

## Error Handling Quick Rules

| Situation | Action |
|-----------|--------|
| Tool missing | Offer setup once, then fallback |
| Tool fails | Explain error, offer fallback |
| No results | Ask for refined query or alternative |
| Partial results | Synthesize what we got, note limitation |
| Token limit hit | Synthesize in chunks, or reduce scope |

---

## Quality Checklist

Before saving research file:

- [ ] One-sentence summary (20 words max)
- [ ] 5-10 key findings (15 words each)
- [ ] Implications for reference files
- [ ] Open questions documented
- [ ] Source suffix correct
- [ ] Token usage reasonable (< 25k)

---

## Multi-Source Pattern

For questions needing multiple research types:

```
1. Identify all needed sources
2. Spawn parallel subagents (if >1 source)
3. Each source → separate research file
4. Create synthesis file combining all
5. Synthesis file references individual sources
```

**Example:**
```
research/
├── 2026-01-26-guarantee-x-social.md       (social sentiment)
├── 2026-01-26-guarantee-competitors.md    (what they do)
├── 2026-01-26-guarantee-psychology-gemini.md  (deep research)
└── 2026-01-26-guarantee-synthesis.md      (combines all three)
```

---

## See Also

- `research-architecture.md` — Full architecture document
- `research-phase.md` — Detailed workflow
- `research-template.md` — File template
- `gemini-setup.md` — Gemini setup guide
- `gemini-deep-research.md` — Deep research with Gemini
- `grok-setup.md` — Grok MCP setup guide
- `grok-social.md` — X/Twitter research details
