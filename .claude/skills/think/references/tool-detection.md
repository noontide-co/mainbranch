# Tool Detection (Config-First, Per-Probe Methods)

Tool status persists in `.vip/config.yaml` under `tools:`. Read config first, only probe unknowns, always write results back.

---

## Status Values

| Value | Meaning | Action |
|-------|---------|--------|
| `true` | Verified working | Use tool, skip detection |
| `false` | Known unavailable | Skip detection (unless stale) |
| `null` | Unknown | Run detection |
| (missing) | Never checked | Run detection |

## Staleness Check

Treat `status: false` as stale when `last_checked` is missing, invalid, or older than 30 days. Re-probe stale false entries.

---

## Detection Flow

On first /think invocation each session:

```
1. Read .vip/config.yaml → tools section
2. Detect unknown tools and re-detect stale false entries
3. Normalize metadata (`last_checked`) on existing tool entries missing it
4. WRITE config updates immediately (status + notes + last_checked for touched entries)
5. Report once (experience-appropriate)
```

For full self-healing contract (stale semantics, status-change messaging, and true-tool degradation handling), see [tool-status-self-healing.md](tool-status-self-healing.md).

---

## Detection Methods

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

**Save which binary was found** in config `tools.whisper.notes` (e.g., `"mlx_whisper verified"`). Different variants use different command syntax — the notes field tells future sessions which command to use. See [local-transcription.md](local-transcription.md) for variant-specific commands.

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

---

## Config Update (REQUIRED)

After detection, **immediately update config** using Edit tool:

```yaml
tools:
  gemini:
    status: true              # ← detection result
    notes: "GOOGLE_API_KEY verified"
    last_checked: 2026-03-02  # ← today's date
  whisper:
    status: true
    notes: "mlx_whisper verified"
    last_checked: 2026-03-02
```

**Do not skip this step.** Config updates prevent re-probing next session. Use the self-healing contract in [tool-status-self-healing.md](tool-status-self-healing.md).

---

## Reporting by Experience

| Experience | Format |
|------------|--------|
| `beginner` | "Research ready. I'll help with tool setup when you need it." |
| `intermediate` | "Tools: Apify ✓, Gemini ✓, Grok ✗, whisper ✗" |
| `advanced` | Silent unless changes from last session |

---

## Intent-Based Tool Surfacing

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

See [tool-surfacing.md](tool-surfacing.md) for full details on progressive disclosure.
