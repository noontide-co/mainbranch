# Gemini Setup

3-minute setup. Free tier available for quick research.

---

## Verification Status

| Tier | Status | Notes |
|------|--------|-------|
| **Tier 1** | **TESTED** | Flash API works via REST endpoint |
| **Tier 2** | **NOT TESTED** | Interactions API documented but needs verification |

---

## What You Get

Two tiers of Gemini research:

**Tier 1: Quick Research (Free tier)** - CONFIRMED WORKING
- Standard API calls via `generate_content`
- 30-60 second response times
- Good for most questions
- Tested model: `gemini-2.0-flash`

**Tier 2: Deep Research (Pay-as-you-go)** - NOT YET VERIFIED
- Agentic multi-step research via Interactions API
- 5-20 minute autonomous investigation
- Searches 80-160+ sources, produces comprehensive reports
- Requires additional testing before production use

Best for:
- Competitor analysis
- Industry research
- Complex questions requiring multiple sources
- Academic-style investigation
- Best practices research

---

## Cost Upfront

**Free tier available for Tier 1 research.** Google AI Studio has a generous free tier.

| Tier | Cost | What You Get |
|------|------|--------------|
| Free | $0 | 15 RPM, 1M tokens/day — quick research |
| Pay-as-you-go (quick) | ~$0.01-0.05/query | Higher limits, Flash/Pro models |
| Pay-as-you-go (deep) | ~$2-5/task | Full Deep Research Agent |

**What does that mean practically?**
- Quick research (Tier 1): ~5-10K tokens, ~100-200 queries/day free
- Deep research (Tier 2): ~250K-900K tokens, $2-5 per research task

**Bottom line:** Start free with Tier 1. Use Tier 2 Deep Research when you need comprehensive multi-source synthesis.

---

## Setup Steps

### 1. Get API Key (2 min)

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key

### 2. Add to Environment (1 min)

Create or edit your vip env file:

```bash
mkdir -p ~/.config/vip
nano ~/.config/vip/env.sh
```

Add your key:

```bash
export GOOGLE_API_KEY="your_key_here"
```

Save (Ctrl+X, Y, Enter) and reload:

```bash
source ~/.config/vip/env.sh
```

**Optional:** Add to your shell profile for persistence:

```bash
echo 'source ~/.config/vip/env.sh' >> ~/.zshrc
```

---

## Verify It's Working

```bash
echo $GOOGLE_API_KEY
```

Should show your key (not empty).

**In Claude Code:**

```
/think deep research on a simple topic
```

If Gemini is detected, Claude will use it for complex research.

---

## That's It

Gemini Deep Research is now available in /think.

---

## Troubleshooting

**"Key not found"**
- Did you `source ~/.config/vip/env.sh`?
- Or restart your terminal?
- Check: `echo $GOOGLE_API_KEY`

**"Invalid API key"**
- Verify key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Make sure you copied the full key (no trailing spaces)

**"Quota exceeded"**
- Free tier has limits (15 requests/minute, 1M tokens/day)
- Wait a minute and retry, or upgrade at Google AI Studio

**"Model not available"**
- Gemini models may vary by region
- Check [ai.google.dev/models](https://ai.google.dev/models) for availability

---

## Why Google AI Studio (Not Google Cloud)?

| Option | Complexity | Cost |
|--------|------------|------|
| **Google AI Studio** | 3 min setup, one API key | Free tier, simple billing |
| Google Cloud + Vertex AI | 30+ min setup, project config, IAM | Enterprise pricing |

**We use Google AI Studio.** It's the same Gemini models with simpler setup.

---

## See Also

- [gemini-deep-research.md](gemini-deep-research.md) — How to use Gemini for research
- [research-architecture.md](research-architecture.md) — Full routing logic
