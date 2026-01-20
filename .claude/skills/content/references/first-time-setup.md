# First-Time Setup

Before running `/content`, you need three core reference files. This guide helps you create minimal versions to get started.

---

## Required Files

| File | Purpose | Minimum |
|------|---------|---------|
| `reference/core/voice.md` | How you sound on camera | 1 paragraph |
| `reference/core/audience.md` | Who watches your content | 2-3 sentences |
| `reference/core/offer.md` | What you do/sell | 1 sentence |

**Don't have these?** Run `/setup` first, or create them manually below.

---

## Minimal voice.md

```markdown
# Voice

**Tone:** [Pick 2-3: casual, professional, energetic, calm, funny, serious, inspirational]

**You sound like:** [One sentence - e.g., "your friend giving advice over coffee"]

**Words you use a lot:**
- [word 1]
- [word 2]
- [word 3]

**Never say:** "unlock", "leverage", "game-changer", "dive into", "journey"

**Energy:** [High / Medium / Low]
```

See [minimal-voice-template.md](minimal-voice-template.md) for a complete template with examples.

---

## Minimal audience.md

```markdown
# Audience

[Age range] [life stage] who struggle with [main problem].

They want [desired outcome] but [obstacle in their way].

They hang out on [platforms: Instagram, TikTok, YouTube, etc.].
```

**Example:**
```markdown
# Audience

Creative business owners aged 25-40 who struggle with content consistency.

They want to grow their audience organically but don't know what to post.

They hang out on Instagram and TikTok.
```

---

## Minimal offer.md

```markdown
# Offer

I help [audience] [achieve outcome] through [method/product].
```

**Example:**
```markdown
# Offer

I help creative entrepreneurs build content systems that grow their audience without burning out.
```

---

## Platform Selection

Before generating scripts, know your target platform:

| Platform | Optimal Length | Key Difference |
|----------|---------------|----------------|
| **Instagram Reels** | 15-30 seconds | First frame appears in grid |
| **TikTok** | 30-90 seconds | Can go longer with good retention |
| **Both** | 15-45 seconds | Sweet spot for cross-posting |

Tell Claude which platform you're creating for - it affects timing and structure.

---

## Recommended First Run

### Option A: Research competitors first (recommended)

```
/content mine
```

This extracts winning concepts from competitors, saves to `research/`. Then generate from those concepts.

### Option B: Generate immediately

```
/content video "your topic here"
```

Skips research, generates a script directly. Good if you already know what you want to say.

---

## Data Extraction Options

### Option 1: Apify (automated)

Apify is a data extraction service that automatically pulls Instagram post data.

- **What it does:** Extracts posts, engagement metrics, captions from any public profile
- **Cost:** Free tier covers ~2000 posts/month
- **Setup:** Requires Apify account and MCP configuration

**Don't have Apify?** That's fine - use the manual method.

### Option 2: Manual method (no setup required)

Share screenshots or data directly:

1. Go to competitor's Instagram profile
2. Screenshot their top 10-15 posts (sort by engagement if you can)
3. For each post, note: likes, comments, first line of caption
4. Share with Claude

The skill will extract concepts from whatever you provide.

---

## Next Steps

Once you have the three core files:

1. Run `/content` to start the full flow
2. Or run `/content mine` to just research competitors
3. Or run `/content video "topic"` to generate immediately

The skill will guide you from there.
