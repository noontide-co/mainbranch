---
name: think
description: "Combined research, decision, and codification workflow. Use when: (1) Exploring a question before committing (2) Making a decision that needs documentation (3) User says research, decide, figure out, explore, codify, enrich, add context (4) Updating reference files based on decisions (5) User wants to add new testimonials, angles, or proof to existing files. Supports modes: full flow, research-only, decide-only, codify."
---

# Think

Research, decide, and codify knowledge into reference files.

---

## Don't Overthink Think

This skill is for: **"I don't know what happens next. I just need to start."**

Something came your way — a video, a voice memo, a vague feeling, a problem to solve. You don't need a plan. Just start. The skill finds the overlap between your interest and your offer.

**Re-invoke often.** Saying `/think` again is normal. It reloads context. Do it after:
- Reading a large transcript (burns tokens)
- Compaction (context window reset)
- Switching focus
- Anytime you feel lost

---

## Two Modes of Work

Before diving in, know which mode you're in:

| Mode | You're doing | Examples |
|------|--------------|----------|
| **Enriching the core** | Pulling insights → reference files | Mining videos, making decisions, updating offer.md, **building content-strategy.md** |
| **Creating for the world** | Reference files → output | Ads, scripts, courses, code, posts |

`/think` is for **enriching the core**. When you're ready to create, use `/ads`, `/organic`, `/vsl`, or just ask.

Both are work. Enriching the core levels up everything downstream.

---

## Pull Latest Updates

```bash
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

---

## Tool Detection (Config-First)

Tool status persists in `.vip/config.yaml` under `tools:`. Read config first, only probe unknowns, always write results back.

### Status Values

| Value | Meaning | Action |
|-------|---------|--------|
| `true` | Verified working | Use tool, skip detection |
| `false` | Known unavailable | Skip detection (unless stale) |
| `null` | Unknown | Run detection |
| (missing) | Never checked | Run detection |

### Staleness Check

If `status: false` and `last_checked` is >30 days ago, re-probe. User may have installed it since then.

### Detection Flow

On first /think invocation each session:

```
1. Read .vip/config.yaml → tools section
2. Build list of tools needing detection:
   - status: null or missing → detect
   - status: false AND last_checked >= 30 days → re-detect
   - status: true OR (false AND recent) → skip
3. Run detection for unknowns (see methods below)
4. WRITE config updates immediately (use Edit tool)
5. Report once (experience-appropriate)
```

### Detection Methods

**Apify:** Check if `mcp__apify__search-actors` tool exists in session.

**Gemini:**
```bash
[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"
[ -n "$GOOGLE_API_KEY" ] && echo "GEMINI=true"
```

**Grok:** Requires BOTH env var AND Python SDK:
```bash
[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"
[ -n "$XAI_API_KEY" ] && python3 -c "import xai_sdk" 2>/dev/null && echo "GROK=true"
```

**whisper:** Check MCP tools (`mcp__whisper__*`) OR CLI (multiple implementations exist):
```bash
which mlx_whisper >/dev/null 2>&1 && echo "WHISPER=mlx_whisper"
which whisper-cli >/dev/null 2>&1 && echo "WHISPER=whisper-cli"
pip3 list 2>/dev/null | grep -i "mlx-whisper" && echo "WHISPER=mlx_whisper"
```

**Save which binary was found** in config `tools.whisper.notes` (e.g., `"mlx_whisper verified"`). Different variants use different command syntax — the notes field tells future sessions which command to use. See [local-transcription.md](references/local-transcription.md) for variant-specific commands.

**Nano Banana** (image generation): Available when Gemini is configured (uses GOOGLE_API_KEY). Detect alongside Gemini.

**Pipeboard** (Meta ad account access): Check for MCP tools, then probe:
```bash
# Detection: check if mcp__pipeboard__* tools exist in session
# If found, probe with get_ad_accounts (lightweight call)
# If probe succeeds, cache status: true
```
Pipeboard is a remote MCP at `mcp.pipeboard.co/meta-ads-mcp` (OAuth, no local install). Free tier: 30 calls/week. Pro: $29.90/mo, 100 calls/week. **Lazy detection only** -- triggered when topic is ads-related, not on every /think invocation. See `/ads` SKILL.md for full Pipeboard integration details.

**Document tools:**
```bash
which markitdown >/dev/null 2>&1 && echo "MARKITDOWN=true"
which pandoc >/dev/null 2>&1 && echo "PANDOC=true"
which marker_single >/dev/null 2>&1 && echo "MARKER=true"
```

**Manual probe script:** `scripts/detect-tools.sh` provides a standalone CLI check for all tools. Useful for debugging outside a Claude session.

### Config Update (REQUIRED)

After detection, **immediately update config** using Edit tool:

```yaml
tools:
  gemini:
    status: true              # ← detection result
    notes: "GOOGLE_API_KEY verified"
    last_checked: 2026-02-03  # ← today's date
  pipeboard:
    status: true              # true | false | null
    method: mcp               # always mcp for Pipeboard
    tier: free                # free | pro (self-reported)
    notes: "meta-ads MCP configured via remote URL"
    last_checked: 2026-02-10
    weekly_calls_used: 0      # lightweight tracking (Phase 1.5)
```

**Do not skip this step.** Config updates prevent re-probing next session.

### Reporting by Experience

| Experience | Format |
|------------|--------|
| `beginner` | "Research ready. I'll help with tool setup when you need it." |
| `intermediate` | "Tools: Apify ✓, Gemini ✓, Grok ✗, whisper ✗" |
| `advanced` | Silent unless changes from last session |

### Intent-Based Tool Surfacing

When user's intent matches an unavailable tool, **surface the option once per session**:

| User Intent | If Tool Missing | Message |
|-------------|-----------------|---------|
| YouTube URL | Apify | "YouTube transcripts need Apify MCP (5 min setup). Set up? Paste transcript? Skip?" |
| "X sentiment" | Grok | "X sentiment is best with Grok (real-time). Use web search? Set up Grok (5 min, $5 credit)?" |
| "deep research" | Gemini | "Deep synthesis works best with Gemini (free tier). Web search fallback? Set up (3 min)?" |
| Local file | whisper | "Local transcription needs whisper (10 min). Set up? External service? Skip?" |
| "ad performance", "what's working", "check my CPA" | Pipeboard | "Pulling ad account data needs a Meta Ads connection (5 min setup, uses Pipeboard). Set up? Research from reference only? Skip?" |

**Rules:**
- Surface once per session per tool (track in session state)
- Always offer working fallback
- Never block research

See [tool-surfacing.md](references/tool-surfacing.md) for full details on progressive disclosure.

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. Check `.vip/local.yaml` for `current_offer`
2. If set: load `reference/offers/[current_offer]/offer.md` as the active offer
3. If not set AND `reference/offers/` exists: ask which offer
4. If no `offers/` folder: use `reference/core/offer.md` (single-offer, backward compatible)

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

---

## Where Files Go

All files save to YOUR business repo, not the engine (vip).

```
your-business-repo/          <- Files saved here
├── research/                 <- Research output
├── decisions/                <- Decision output
└── reference/                <- Codify updates this
    ├── core/                 <- Brand-level
    ├── offers/               <- Per-offer (if multi-offer)
    └── domain/

vip/ (engine)                 <- Never modified
```

---

## Route by Intent

Detect mode from user's natural language:

| User Says | Mode | Reference |
|-----------|------|-----------|
| "figure out", "explore", "I'm trying to..." | Full Flow | - |
| "research", "investigate", "what do we know about" | Research | [research-phase.md](references/research-phase.md) |
| "what are people saying", "sentiment", "X/Twitter", "trending" | Research (Grok) | [grok-social.md](references/grok-social.md) |
| "decide", "we chose", "document decision" | Decide | [decide-phase.md](references/decide-phase.md) |
| "codify", "apply", "update reference files" | Codify | [codify-phase.md](references/codify-phase.md) |
| "add context", "enrich", "I have new info" | Codify | [codify-phase.md](references/codify-phase.md) |
| "content strategy", "pillars", "what platforms", "content plan", "cadence" | Full Flow (codify to content-strategy.md) | [codify-phase.md](references/codify-phase.md) |
| "where was I", "continue", "pick up" | Recovery | [recovery.md](references/recovery.md) |
| "here's a PDF", "ingest this", "convert this document", file path (.pdf/.docx/.pptx) | Document Ingestion | [document-ingestion.md](references/document-ingestion.md) |

If unclear, ask: "Are you exploring a question, documenting a decision, or updating reference files?"

---

## Research Routing by Intent

When routing to research mode, detect research TYPE from user intent:

| User Intent | Trigger Phrases | Primary Tool | Fallback |
|-------------|-----------------|--------------|----------|
| YouTube research | YouTube URL, "transcribe video", "what does [creator] say" | Apify | Ask for manual transcript |
| X/Twitter sentiment | "what are people saying", "sentiment on X", "Twitter discourse" | Grok | WebSearch site:x.com |
| Deep web research | "deep research", "comprehensive analysis", "research everything" | Gemini | Multi-source WebSearch |
| Local transcription | Local file path (.mp4, .m4a), "transcribe my recording" | whisper | CLI mlx_whisper or whisper-cli |
| Instagram mining | Instagram handle, "mine [handle]", "competitor posts" | Apify | Manual screenshots |
| Ad account research | "ad performance", "what's working", "check CPA", "audit my ads" | Pipeboard | Manual Ads Manager check |
| General research | Default, "research [topic]", "what do we know" | WebSearch + codebase | Always available |

**Multiple types needed at once?** Spawn them as parallel Task agents in a single message. Example: user says "research what [creator] says on YouTube and what people think on X" — spawn one agent for YouTube transcript mining and another for X/Twitter sentiment simultaneously. Each saves its own research file; main conversation synthesizes when both return.

### Routing Logic

```
1. Parse user message for intent triggers
2. Check if preferred tool is available (from session cache)
3. If multiple sources needed → spawn parallel Task agents (one per source)
4. If single source → use preferred tool directly
5. If not available → offer setup ONCE, then use fallback
6. Never block on missing optional tools
```

### Fallback Examples

**YouTube without Apify:**
> "YouTube transcript mining needs Apify MCP. Options:
> 1. Set up Apify now (5 min)
> 2. Paste transcript manually
> 3. Skip this video"

**X/Twitter without Grok:**
> "X sentiment research is best with Grok, but I can use web search instead. Results will be less real-time. Proceed with web search?"

**Deep research without Gemini:**
> "Running comprehensive research using Claude Code web search. This may take longer than Gemini deep research."

**Local file without whisper:**
> "Local transcription needs a whisper variant. Check: `which mlx_whisper` or `which whisper-cli`. Or upload to a transcription service and paste the result."

**Ad account data without connection:**
> "Ad account research works best with a direct Meta Ads connection (OAuth, no developer account needed, uses Pipeboard). Options:
> 1. Set up now (5 min, free tier: 30 calls/week)
> 2. Check Ads Manager manually and paste what you find
> 3. Skip account data, research from reference files only"

### Key Principle

**Never block on missing tools.** WebSearch + codebase search are ALWAYS available. External tools enhance but don't gate research.

---

## Active Guidance (Your Job)

**Don't just provide templates. Actively move people through the cycle.**

On every `/think` invocation, detect state and guide the next step:

```bash
# Check for work in progress
ls -lt research/*.md 2>/dev/null | head -3
grep -l "status: proposed\|status: accepted" decisions/*.md 2>/dev/null
# Also check content strategy state
ls reference/domain/content-strategy.md 2>/dev/null
```

| If you find... | Then... |
|----------------|---------|
| Recent research, no decision | "You have research on [topic]. Ready to make a decision?" |
| Proposed decision | "Decision [topic] is proposed. Ready to accept it?" |
| Accepted decision (not yet codified) | "Decision [topic] is accepted. Ready to codify the changes into reference files?" |
| content-strategy.md exists but empty/thin | "Your content strategy file is a skeleton. Want to fill it in? We can derive pillars from your soul.md + offer.md + audience.md." |
| content-strategy.md missing (community biz) | "You don't have a content strategy yet. Want to build one? It'll define your pillars, platforms, and cadence." |
| skool-surfaces.md missing (community biz with live Skool) | "Your Skool about page and pricing card copy aren't in reference yet. Want to add them? Skills check this for congruence." |
| `reference/offers/` exists | Multi-offer repo. Check `.vip/local.yaml` for `current_offer`. If not set, ask which offer this research/decision is about. |
| Nothing in progress | "What are you trying to figure out?" |

**The goal is reference files.** Research and decisions are waypoints. Keep asking: "What needs to happen to get this into reference?"

---

## Full Flow (Default)

```
Research -> Checkpoint -> Decide -> Checkpoint -> Codify
```

### 1. Define Question

> "What specifically are you trying to figure out?"

### 2. Research

Gather from codebase, web, user input, local recordings.

**When research involves 2+ sources** (e.g., YouTube + web, X/Twitter + codebase, competitor mining + deep research), spawn parallel Task agents in a single message — one agent per source. Use `subagent_type: "general-purpose"` (has Write, Edit, Bash, MCP access). Each agent:
- Gets a focused prompt: one source, one research question
- Writes its own dated file (e.g., `research/YYYY-MM-DD-topic-yt-mining.md`)
- **Verifies the write:** checks the file exists after writing (use Read or ls)
- Returns: file path + write status + 5-bullet summary
- If write failed: returns the **full research content** so main conversation can write it
- Does NOT need the full business context — just the research question and source instructions

**After all agents return:** Check that files landed on disk. If any agent reported a write failure or the file doesn't exist, write it from the returned content. Then synthesize across summaries. This keeps heavy content out of your main context window while recovering gracefully from the known Claude Code subagent write persistence bug.

**Do NOT run research agents in background** (`run_in_background: true`) — background agents cannot access MCP tools (Apify, etc.) and cannot prompt for permissions.

**Mining sources:**

| Source | How | Output suffix |
|--------|-----|---------------|
| YouTube videos | Apify transcript MCP | `-yt-mining.md` |
| X/Twitter sentiment | Grok X Insights MCP ([grok-social.md](references/grok-social.md)) | `-x-social.md` |
| Local video/audio | whisper-cpp ([local-transcription.md](references/local-transcription.md)) | `-local-mining.md` |
| Voice memos | whisper-cpp | `-voice-mining.md` |
| Instagram mining | Apify or manual | `-ig-mining.md` |
| Ad account data | Pipeboard MCP (Meta Ads) | `-ad-account.md` |
| Competitor sites | Browser MCP or web fetch | `-competitor-mining.md` |
| Your own emails/DMs | Paste into conversation | `-internal-mining.md` |
| Deep research | Build prompt → Gemini/GPT | `-gemini.md` or `-gpt.md` |
| Codebase exploration | Grep, read, subagents | `-claude-code.md` |
| Documents (PDF, DOCX, PPTX) | markitdown / pandoc / marker ([document-ingestion.md](references/document-ingestion.md)) | `-doc-extraction.md` |

### 3. Synthesize (Required)

Every research output needs:
- One-sentence summary (20 words max)
- Key findings (5-10 bullets)
- Implications for reference files
- Open questions

Synthesis works best when the main conversation is clean — which is exactly what subagents provide. Heavy raw content (transcripts, mined posts) lives in the subagent context windows, and only distilled summaries return to main.

**For content mining specifically:** AI shows WHAT worked. You must judge WHY.

Extract three dimensions from mined content:
- **Visual** — Format, production style, patterns
- **Audible** — Energy, pacing, delivery
- **Emotional** — Primary emotion, identity play

**Framework extraction is human judgment work.** AI surfaces the data; you interpret the frameworks. This methodology comes from Koston Williams (6M view video) — the skill isn't copying, it's framework transfer. A competitor's content worked for THEM. Your job is to:

1. See the framework beneath the content
2. Judge whether it transfers to YOUR context
3. Adapt it to YOUR voice and audience
4. Codify what you learned into reference files

Don't skip to content generation. Mining → Human Synthesis → Reference Update → THEN Create.

### 4. Checkpoint

> "Ready to make a decision, or need more research?"

### 5. Decide

Present options with pros/cons. Document choice and rationale.

### 6. What Changes

Describe what reference files are affected in the decision file:

```markdown
## What Changes

offer.md gets a guarantee section after pricing. A new angle file (risk-reversal.md) captures the guarantee messaging.
```

See [decide-phase.md](references/decide-phase.md) for format details.

### 7. Checkpoint

> "Ready to update reference files now, or save for later?"

### 8. Codify

Apply changes described in `## What Changes` to reference files. Mark decision as codified.

**Codify targets include:** `reference/core/*.md`, `reference/offers/[active]/offer.md`, `reference/offers/[active]/audience.md` (when multi-offer), `reference/proof/angles/*.md`, `reference/proof/testimonials.md`, **`reference/domain/content-strategy.md`** (pillars, hooks library, framework library, metrics), `reference/domain/funnel/skool-surfaces.md` (live Skool copy — update when about page or pricing changes), `reference/domain/product-ladder.md` (when multi-offer, cross-offer decisions).

---

## Research Mode

```
/think research "topic"
```

Output: `research/YYYY-MM-DD-topic-claude-code.md`

See [references/research-phase.md](references/research-phase.md) for full workflow.

---

## Decide Mode

```
/think decide "topic"
```

Output: `decisions/YYYY-MM-DD-topic.md`

See [references/decide-phase.md](references/decide-phase.md) for full workflow.

---

## Codify Mode

```
/think codify decisions/YYYY-MM-DD-topic.md
```

Or: "/think add new testimonials to my files"

See [references/codify-phase.md](references/codify-phase.md) for full workflow.

---

## Task Tracking Layers

| Layer | Scope | Use For |
|-------|-------|---------|
| **Claude tasks** | Session | Execution tracking, spinners |
| **Decision files** | Forever | Rationale, anchor for work |
| **GitHub issues** | Forever | Cross-session, team visibility |

Decision files are the anchor — create early with `status: proposed`, update to `accepted`, then `codified`.

See [decide-phase.md](references/decide-phase.md) for task creation patterns.
See [recovery.md](references/recovery.md) for resuming sessions.

---

## Recovery

If conversation compacted, check multiple sources:

**1. Claude tasks (current session):**
```
TaskList
```

**2. Recent files:**
```bash
ls -lt research/*.md 2>/dev/null | head -5
grep -l "status: proposed\|status: accepted" decisions/*.md 2>/dev/null
```

**3. GitHub issues (if using):**
```bash
gh issue list --assignee @me --state open
```

Then confirm: "I see you were working on [topic]. Continue from here?"

See [references/recovery.md](references/recovery.md) for details.

---

## Templates

- [references/templates/research-template.md](references/templates/research-template.md)
- [references/templates/decision-template.md](references/templates/decision-template.md)

---

## When NOT to Use

- Quick factual questions (just ask)
- Simple file edits (just edit)
- Generating content (use `/ads`, `/vsl`, `/organic`)

Use `/think` when the answer requires investigation and the choice needs documentation.

---

## Why This Matters

The repo is a precision instrument. The think cycle exists to filter — not to cram everything in. Research gets synthesized, decisions get distilled, and only the sharpest insights survive into reference. Curation over collection.

Reference files aren't just documentation. They're how you stay connected to why you do this.

The act of researching, deciding, and codifying forces you to articulate:
- **Why you do this** — Not the marketing reason. The real reason.
- **Who actually benefits** — Not demographics. Real people whose lives change.
- **What transformation you enable** — Not features. The before/after.

Research and decisions go stale. Reference files compound. Every update makes all downstream content better.

If the overlaps between your interests and your offer don't make sense, maybe you have the wrong offer. The think cycle should feel like pull, not push.
