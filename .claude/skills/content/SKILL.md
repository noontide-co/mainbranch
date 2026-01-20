---
name: content
description: |
  Mine competitor content, generate organic scripts. ALWAYS offer Apify MCP first (manual fallback if unavailable). Use for "mine", "competitors", "organic", "reels", "tiktok", carousels, talking-head videos. Modes: mine, video, carousel, static.
---

# Content

Mine competitors → extract concepts → generate scripts in your voice.

**Need help?** `/help` + your question.

---

## Data Extraction (ALWAYS MENTION FIRST)

Offer these in order:

1. **Apify MCP** (best) — "I can use Apify to pull their posts automatically"
2. **Browser MCP** (okay) — "I can open Instagram in Chrome"
3. **Manual** (fallback) — "Share screenshots of their top 10-15 posts"

Ask: "Do you have Apify set up? If not, browser mode or screenshots."

---

## Setup Required

Requires `reference/core/voice.md`, `audience.md`, `offer.md`.

**Two-repo model:** vip = engine (skills). User's business repo = data. Search all working directories for `reference/core/`. If not found, ask which repo or suggest `/start`.

**Missing files?** See [references/first-time-setup.md](references/first-time-setup.md) or run `/setup`.

---

## Presenting Options

1. **Recommend ONE path** based on context
2. **Mention alternatives** in one line
3. **State data method** (Apify or manual)

```
Recommended: /content mine — research competitors first.

Other: video "topic", carousel "topic", static "topic"

Data: Screenshots (or Apify MCP if set up).

Platform?
1. Instagram Reels
2. TikTok
3. Both

(hit a number)
```

---

## /content vs /ad-video-scripts

| Aspect | /ad-video-scripts | /content |
|--------|-------------------|----------|
| Purpose | Paid traffic | Organic reach |
| Tone | Direct response | Authentic, value-first |
| CTA | Hard (link, buy) | Soft (save, follow) |
| Framework | AIDA, PAS | Hook-Retain-Reward |

---

## Modes

| Mode | What |
|------|------|
| `/content` | Full flow: mine → select → generate |
| `/content mine` | Research only, save to research/ |
| `/content video "topic"` | Reels/TikTok script |
| `/content carousel "topic"` | Multi-slide carousel |
| `/content static "topic"` | Single-post caption |

---

## Full Flow

### Step 1: Identify Competitors

Check `reference/competitors/handles.md` or ask:

> "Who are 3-5 creators making content for your audience?"
> - Direct competitors
> - Adjacent creators (similar audience, different offer)
> - Aspirational accounts

### Step 2: Mine Content

**Apify MCP:** Instagram Profile Scraper → structured JSON with engagement.

**Manual:** Screenshots of top 10-15 posts + like/comment counts.

**Filter:** Sort by engagement. Extract top 20%.

### Step 3: Extract Concepts

| Element | Capture |
|---------|---------|
| Hook | First line / 3 seconds |
| Topic | Core subject |
| Structure | How organized |
| Angle | Emotional entry |
| Format | Talking head, carousel, etc. |

### Step 4: Adapt to Brand

Map concepts to user's offer, audience, voice.

### Step 5: Generate Scripts

- Talking head → video framework
- Carousel → carousel framework
- Single post → static framework

### Step 6: Save Output

```
research/YYYY-MM-DD-competitor-mine.md
outputs/content-scripts/YYYY-MM-DD-[concept-slug].md
```

---

## Video Framework

Hook-Retain-Reward:

1. **Hook** (0-3s): Stop scroll
2. **Retain** (3-45s): Deliver value
3. **Reward** (last 5-15s): Payoff + soft CTA

Frameworks:
| Type | Structure |
|------|-----------|
| Educational | Hook → Tips → Takeaway |
| Story-based | Hook → Trigger → Outcome |
| Transformation | Before → Turning Point → After |
| Problem-Solution | Hook → Problem → Solution → CTA |

User can specify: `/content video "topic" --framework story`

See [references/organic-frameworks.md](references/organic-frameworks.md)

---

## Carousel Structure

| Slide | Purpose |
|-------|---------|
| 1 | Hook (stops scroll) |
| 2-8 | Value (one idea per slide) |
| 9 | Summary |
| 10 | CTA |

See [references/carousel-template.md](references/carousel-template.md)

---

## Static Structure

1. **Hook** (first line before "more")
2. **Body** (value or story)
3. **CTA** (soft: save, comment, follow)
4. **Hashtags** (optional)

See [references/static-template.md](references/static-template.md)

---

## Voice Adaptation

Always:
1. Read `reference/core/voice.md`
2. Match tone markers
3. Use their vocabulary
4. Avoid "never say" phrases

**Authenticity checklist:**
- [ ] Sounds like creator, not copywriter
- [ ] Uses contractions naturally
- [ ] Matches energy level
- [ ] No AI tells ("dive into", "unlock", "game-changer")

---

## CTA Softness

| Hard (Avoid) | Soft (Use) |
|--------------|------------|
| Link in bio to buy | Save this for later |
| Sign up now | Follow for more |
| Limited time | Comment [word] for breakdown |

Exception: Match user's voice if they use harder CTAs.

---

## Pre-Response Checklist

Before responding:
- [ ] Mentioned data method (Apify > Browser > Manual)
- [ ] Used numbered options for multi-choice
- [ ] Asked platform (Instagram/TikTok/Both)
- [ ] Kept it tight (recommend ONE path)

---

## References

**Setup:** [references/first-time-setup.md](references/first-time-setup.md)

**Frameworks:** [references/organic-frameworks.md](references/organic-frameworks.md)

**Templates:**
- [references/mining-template.md](references/mining-template.md)
- [references/video-script-template.md](references/video-script-template.md)
- [references/carousel-template.md](references/carousel-template.md)
- [references/static-template.md](references/static-template.md)
