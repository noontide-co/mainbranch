# Gemini Setup

3-minute setup. Free tier available.

---

## What You Get

Gemini Deep Research for comprehensive web research with synthesis. Best for:
- Competitor analysis
- Industry research
- Complex questions requiring multiple sources
- Academic-style investigation
- Best practices research

---

## Cost Upfront

**Free tier available.** Unlike Grok (requires $5 minimum), Google AI Studio has a generous free tier.

| Tier | Cost | Limits |
|------|------|--------|
| Free | $0 | 15 RPM, 1M tokens/day |
| Pay-as-you-go | ~$0.01-0.05/query | Higher limits |

**What does that mean practically?**
- A typical deep research query: ~5-10K tokens
- Free tier: ~100-200 deep research queries per day
- Plenty for casual to moderate research use

**Bottom line:** Start free. Upgrade only if you hit limits.

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
