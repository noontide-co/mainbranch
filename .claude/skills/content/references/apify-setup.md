# Apify Setup Guide

One-time 5-minute setup. After this, Apify works automatically every time you use Main Branch.

---

## Why Apify?

Instagram blocks browser automation aggressively. Without Apify:
- Slow screenshot-by-screenshot browsing
- 60-70% success rate
- Burns through your Claude usage

With Apify:
- Clean data in seconds
- 95%+ success rate
- Handles rate limits automatically

---

## Setup Steps

### 1. Create Apify Account (2 min)

Go to [apify.com](https://apify.com) → Sign up (free tier works)

### 2. Get Your API Token (1 min)

Settings → Integrations → API tokens → Copy your token

### 3. Add MCP to Claude Code (2 min)

Run this command in terminal:

```bash
claude mcp add apify -e APIFY_TOKEN=your_token_here -- npx -y @anthropic-ai/apify-mcp-server
```

Replace `your_token_here` with your actual token.

---

## That's It

Apify is now saved to your global Claude Code settings (`~/.claude/settings.json`).

Every time you run `/content mine` on Instagram, it will use Apify automatically. No re-setup needed.

---

## Verify It's Working

In Claude Code, type:

```
/mcp
```

You should see `apify` in the list of configured servers.

---

## Troubleshooting

**"apify not found"** — Run the `claude mcp add` command again, make sure you replaced the token.

**"Invalid token"** — Double-check your API token on apify.com → Settings → Integrations.

**"Rate limited"** — Free tier covers ~2000 posts/month. If you hit limits, upgrade to ~$5/mo.
