# First-Time Setup

Before `/content`, create these core files.

---

## Required

| File | Purpose | Min |
|------|---------|-----|
| `reference/core/voice.md` | How you sound | 1 para |
| `reference/core/audience.md` | Who watches | 2-3 sentences |
| `reference/core/offer.md` | What you sell | 1 sentence |

**Missing?** Run `/setup` or create manually below.

---

## Minimal voice.md

```markdown
# Voice

**Tone:** [casual, professional, energetic, calm, funny, serious, inspirational]

**You sound like:** [1 sentence]

**Words you use:** [3-5 words]

**Never say:** "unlock", "leverage", "game-changer", "dive into"

**Energy:** High / Medium / Low
```

See [minimal-voice-template.md](minimal-voice-template.md) for full template.

---

## Minimal audience.md

```markdown
# Audience

[Age range] [life stage] who struggle with [main problem].
They want [outcome] but [obstacle].
They hang out on [platforms].
```

---

## Minimal offer.md

```markdown
# Offer

I help [audience] [achieve outcome] through [method].
```

---

## Platform Timing

| Platform | Optimal | Notes |
|----------|---------|-------|
| Instagram Reels | 15-30s | First frame = grid |
| TikTok | 30-90s | Longer OK with retention |
| Both | 15-45s | Sweet spot for cross-post |

---

## Data Extraction

**Apify** (automated): Free tier ~2000 posts/month. Requires MCP config.

**Manual** (no setup):
1. Screenshot competitor's top 10-15 posts
2. Note: likes, comments, first line of caption
3. Share with Claude

---

## First Run Options

```
/content mine      # Research competitors first (recommended)
/content video "topic"  # Generate immediately
```
