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

1. Click **Settings** (gear icon, bottom left)
2. Click **API & Integrations** tab
3. Under "Personal API tokens" you'll see a default token already created
4. Click the **copy icon** (looks like two squares) next to the asterisks

That's your token. Don't create a new one - the default works fine.

### 3. Add MCP to Claude Code (1 min)

Open a **new terminal window** and run this command:

```
claude mcp add apify -e APIFY_TOKEN=YOUR_TOKEN --scope user -- npx -y @apify/mcp-server-rag-web-browser
```

Replace `YOUR_TOKEN` with your actual token (no spaces around it).

---

**Why `--scope user`?** This saves Apify to your global settings so it works from any directory. Without it, the MCP only works in the folder where you ran the command.

**Why a separate terminal?** Keeps your API token local instead of passing through chat servers.

---

**Tip:** Build the command in pieces:
1. Type: `claude mcp add apify -e APIFY_TOKEN=`
2. Paste your token
3. Type: ` --scope user -- npx -y @apify/mcp-server-rag-web-browser`
4. Press Enter

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
