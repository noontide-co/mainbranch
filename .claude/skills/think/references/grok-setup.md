# Grok X Insights MCP Setup

One-time 5-minute setup. After this, you can pull real-time X/Twitter data for any research.

---

## Cost Upfront

**This is NOT free.** Unlike Apify (which has a free tier), Grok API requires purchasing credits before use.

| Item | Cost |
|------|------|
| Minimum purchase | $5 |
| New user bonus | $25 free credits |
| Data sharing bonus | +$150/mo free credits |

**Per-query costs (Grok 4.1 Fast):**
- Input: $0.20 per million tokens
- Output: $0.50 per million tokens

**What does that mean practically?**
- A typical X sentiment search: ~5K input + ~2K output tokens
- Cost per search: ~$0.002 (about 500 searches per dollar)
- $5 gets you ~2,500 searches

**Bottom line:** $5 is enough for months of casual research use.

---

## Why Grok MCP?

Web search gives you articles and blogs. Grok gives you what people are actually saying RIGHT NOW on X/Twitter.

**Use cases:**
- "What are people saying about [topic]?"
- "What's the sentiment around [brand/product]?"
- "What's trending in [industry]?"
- Social proof research — find real opinions to inform messaging

**Without Grok:** Manual X searching, can't analyze sentiment, no structured data
**With Grok:** Search, analyze, get trends with citations to actual posts

---

## Setup Steps

### 1. Get Grok API Key (2 min)

1. Go to [console.x.ai](https://console.x.ai)
2. Sign up or log in (requires X account)
3. **Purchase credits first** — Click "Buy some credits" → minimum $5
4. Then go to "API Keys" in sidebar → Create API key
5. Copy the key

### 2. Clone the MCP Server (1 min)

Open a **new terminal window** (not inside Claude Code):

```bash
cd ~/
git clone https://github.com/mzkrasner/grok-x-insights-mcp.git
cd grok-x-insights-mcp
npm install
npm run build
```

### 3. Create Environment File (1 min)

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GROK_API_KEY=your_grok_api_key_here
```

### 4. Add to Claude Code (1 min)

Still in terminal (not Claude Code):

```bash
claude mcp add grok-x-insights --scope user -- node ~/grok-x-insights-mcp/dist/index.js
```

**Why `--scope user`?** Saves to global settings so it works from any directory.

---

## That's It

Grok X Insights is now available in Claude Code.

---

## Verify It's Working

**Restart Claude Code** — MCPs only load at startup:

1. Type `/exit` to quit
2. Run `claude` again
3. Type `/mcp`

You should see `grok-x-insights` in the list of configured servers.

---

## First Time Using Grok

When Claude first uses Grok, you'll see a permission prompt:

```
Do you want to proceed?
1. Yes
2. Yes, and don't ask again for grok-x-insights commands
3. No
```

**Hit 2** to always approve Grok commands.

---

## Available Tools

Once set up, you have access to:

| Tool | Purpose |
|------|---------|
| `grok_search_posts` | Search and analyze X posts on any topic |
| `grok_analyze_topic` | Deep analysis with customizable aspects |
| `grok_get_trends` | Identify trending topics with volume/sentiment |
| `grok_chat` | Chat with Grok, optionally grounded in live X data |

See [grok-social.md](grok-social.md) for detailed usage patterns.

---

## Troubleshooting

**"grok-x-insights not found"** — Make sure you ran `npm run build` and the path in the `claude mcp add` command is correct.

**"Invalid API key"** — Check your key at [console.x.ai](https://console.x.ai).

**"Rate limited"** — Check your credit balance at console.x.ai. You may need to purchase more credits.

**Build errors** — Make sure you have Node.js 18+ installed (`node --version`).
