# Grok/xAI Setup Guide

Setup guide for real-time X/Twitter data using xAI's Grok API.

---

## CRITICAL: REST API vs Python SDK

**The xAI REST API does NOT support live X search.**

| API | Chat Works | X Search Works |
|-----|------------|----------------|
| REST API (`api.x.ai/v1/chat/completions`) | YES | NO |
| Python SDK (`xai_sdk` via gRPC) | YES | YES |

When you use the REST API with `search: true`, you get `num_sources_used: 0` — no live X data.

**To get live X search, you must use the Python SDK.** The SDK uses gRPC and server-side tool execution, which is how xAI grants access to X data.

---

## Two Setup Options

| Option | Live X Search | Setup Time | Best For |
|--------|---------------|------------|----------|
| **Python SDK** (recommended) | YES | 5 min | Real X sentiment research |
| **MCP wrapper** (community) | MAYBE* | 10 min | If SDK doesn't work |

*MCP wrappers use REST API, which may not return live X data. Test before relying on it.

---

## Cost Upfront

**This is NOT free.** xAI requires credits before API use.

| Item | Cost |
|------|------|
| Minimum purchase | $5 |
| New user bonus | $25 free credits |
| Data sharing bonus | +$150/mo free credits |

**Grok-3 pricing (for X search):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**What does that mean practically?**
- A typical X sentiment search with synthesis: ~5-10K total tokens
- Cost per search: ~$0.02-0.10
- $5 gets you ~50-250 searches depending on complexity

**Bottom line:** $5-10 is enough for weeks of regular research use.

---

## Why X Search via Grok?

Web search gives you articles and blogs. Grok with X search gives you what people are actually saying RIGHT NOW on X/Twitter.

**Use cases:**
- "What are people saying about [topic]?"
- "What's the sentiment around [brand/product]?"
- "What's trending in [industry]?"
- Social proof research — find real opinions to inform messaging

**Without X search:** Manual X browsing, no sentiment analysis, no structured data
**With X search:** Search, analyze, get trends with citations to actual posts

---

## Option 1: Python SDK (Recommended)

The official xAI Python SDK supports live X search via gRPC.

### 1. Get xAI API Key (2 min)

1. Go to [console.x.ai](https://console.x.ai)
2. Sign up or log in (requires X account)
3. **Purchase credits first** — Click "Buy some credits" → minimum $5
4. Then go to "API Keys" in sidebar → Create API key
5. Copy the key

### 2. Install SDK (1 min)

```bash
pip install xai-sdk
```

### 3. Set Environment Variable (1 min)

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export XAI_API_KEY="your-api-key-here"
```

Then reload: `source ~/.zshrc`

### 4. Test X Search

Create a test script `test_grok.py`:

```python
import asyncio
from xai_sdk import Client
from xai_sdk.tools import x_search

async def test():
    client = Client()
    conversation = client.chat.create(
        model="grok-3",
        tools=[x_search()]
    )
    async for token in conversation.add_user_turn(
        "What are people saying about AI coding assistants on X today?"
    ):
        print(token.token, end="", flush=True)
    print()

asyncio.run(test())
```

Run it:

```bash
python test_grok.py
```

If you see actual X posts in the response, X search is working.

### Available X Search Sub-Tools

When you pass `x_search()`, the model gets access to:

| Sub-Tool | Purpose |
|----------|---------|
| `x_user_search` | Find X user accounts |
| `x_keyword_search` | Keyword-based post search |
| `x_semantic_search` | Semantic/contextual search |
| `x_thread_fetch` | Fetch full thread from a post |

The model autonomously decides which to use based on your prompt.

### Search Parameters

The model can use these internally:
- **Date filtering:** `from_date`, `to_date` (ISO8601 format)
- **Handle exclusion:** `excluded_handles` (list of handles to skip)

Influence via prompt: "What have people said about X in the last week, excluding @spamaccount?"

---

## Option 2: MCP Wrapper (Fallback)

A community MCP server that wraps the Grok REST API. **Warning:** May not support live X search since REST API has limitations.

### 1. Get xAI API Key

Same as Option 1 above.

### 2. Clone the MCP Server

Open a **new terminal window** (not inside Claude Code):

```bash
cd ~/
git clone https://github.com/mzkrasner/grok-x-insights-mcp.git
cd grok-x-insights-mcp
npm install
npm run build
```

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GROK_API_KEY=your_grok_api_key_here
```

### 4. Add to Claude Code

```bash
claude mcp add grok-x-insights --scope user -- node ~/grok-x-insights-mcp/dist/index.js
```

### 5. Verify

Restart Claude Code (`/exit` then `claude`), then `/mcp` to see if it loaded.

### MCP Tools Available

| Tool | Purpose |
|------|---------|
| `grok_search_posts` | Search and analyze X posts |
| `grok_analyze_topic` | Deep analysis with aspects |
| `grok_get_trends` | Trending topics |
| `grok_chat` | General chat |

**Test if X search actually works:** Check responses for `num_sources_used > 0`. If it's 0, the MCP is using REST API and X search isn't working.

---

## Fallback: WebSearch

When neither SDK nor MCP work:

```
WebSearch: "[topic] site:x.com"
```

**Limitations:**
- Not real-time (only indexed pages)
- No sentiment analysis
- No structured data

Still useful for finding popular/viral posts that have been indexed.

---

## Troubleshooting

**SDK: "ModuleNotFoundError: xai_sdk"** — Run `pip install xai-sdk`

**SDK: "Invalid API key"** — Check `echo $XAI_API_KEY` and verify at [console.x.ai](https://console.x.ai)

**SDK: "num_sources_used: 0"** — You're using REST API, not SDK. Make sure you're using `x_search()` tool.

**MCP: "grok-x-insights not found"** — Run `npm run build` and check the path.

**MCP: No X data returned** — The MCP may be using REST API. Try the Python SDK instead.

**Rate limited** — Check credit balance at console.x.ai.

---

## Resources

- **xAI Docs:** https://docs.x.ai/docs/guides/tools/search-tools
- **Python SDK:** https://github.com/xai-org/xai-sdk-python
- **Usage patterns:** See [grok-social.md](grok-social.md)
