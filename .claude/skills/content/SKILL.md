---
name: content
description: |
  Mine competitor content and generate organic scripts. ALWAYS offer Apify MCP first for data extraction (manual fallback if unavailable). Use when user says "mine", "competitors", "organic", "reels", "tiktok", or needs scripts for talking-head videos, carousels, static posts. Modes: mine, video, carousel, static.
---

# Content

Mine competitor content, extract winning concepts, generate scripts in your voice.

**Need help?** Type `/help` + your question anytime.

---

## Data Extraction (ALWAYS MENTION FIRST)

**For Instagram mining, Apify is essential** — not nice-to-have:
- 95%+ reliable vs 60-70% for browser automation
- 100x faster (pulls data directly vs slow screenshot-by-screenshot browsing)
- Handles Instagram's rate limits automatically
- Free tier covers ~2000 posts/month (~$5/mo after)
- **One-time 5-minute setup**, then remembered forever in your Claude settings

Offer in order:
1. **Apify MCP** (strongly recommended for Instagram) — Pull posts with engagement metrics
2. **Browser MCP** (fallback) — Works but slow and unreliable
3. **Manual** (last resort) — User shares screenshots

Ask: "Do you have Apify set up? It's a one-time 5-minute setup, then it just works every time."

For setup walkthrough, see [references/apify-setup.md](references/apify-setup.md).

---

## First-Time Setup

Requires `reference/core/voice.md`, `audience.md`, `offer.md`.

Search all working directories for `reference/core/`. If not found, ask user or run `/setup`.

Missing files? See [references/first-time-setup.md](references/first-time-setup.md).

---

## Presenting Options (Keep It Tight)

Don't list all modes in chunky blocks. Instead:

1. **Recommend ONE path** based on their context
2. **Mention alternatives briefly** in one line
3. **State data extraction method** (Apify or manual)

**Example output:**
```
Recommended: `/content mine` — research competitors first since your voice file is still draft.

Other modes: `video "topic"`, `carousel "topic"`, `static "topic"`

Data: I'll ask you to share competitor screenshots (or use Apify MCP if you have it set up).

Platform?
1. Instagram
2. TikTok
3. Both
4. Other (Skool, YouTube, etc.)

(hit a number)
```

---

## How It Differs from Ad Skills

| Aspect | /ad-video-scripts | /content |
|--------|-------------------|----------|
| **Purpose** | Paid traffic conversion | Organic reach and engagement |
| **Tone** | Direct response, urgency | Authentic, value-first |
| **CTA** | Hard (link in bio, buy now) | Soft (follow, save, comment) |
| **Framework** | AIDA, PAS | Hook-Retain-Reward |
| **Goal** | Clicks and conversions | Views, saves, follows |

---

## Modes

### `/content` (Full Flow - Default)

Mine competitors -> pick concepts -> generate scripts.

```
Mine -> Select -> Generate -> Output
```

### `/content mine`

Research competitor content only. Saves to `research/`.

### `/content video "concept"`

Generate Reels/TikTok script from a concept.

### `/content carousel "concept"`

Generate multi-slide carousel copy from a concept.

### `/content static "concept"`

Generate single-post caption from a concept.

---

## Finding the Business Repo

1. Search all working directories for `reference/core/`
2. If multiple found, ask which one to use
3. If none found, ask user for the path or suggest `/start`

## Reference Required

Business repo must have these files:

| File | What It Contains |
|------|------------------|
| `reference/core/offer.md` | What you sell (for CTA context) |
| `reference/core/audience.md` | Who watches your content |
| `reference/core/voice.md` | How you sound on camera |

**Optional but recommended:**

| File | Purpose |
|------|---------|
| `reference/competitors/handles.md` | List of competitor handles to mine |
| `reference/proof/angles/*.md` | Proven angles to adapt |

If core files are missing, prompt user to create them first or run `/setup`.

---

## Full Flow Walkthrough

### Step 1: Identify Competitors

Check `reference/competitors/handles.md`. If missing, ask:

> "Who are 3-5 creators making content for your audience?"

### Step 2: Mine Content

**Apify:** Instagram Profile Scraper → structured JSON with metrics

**Manual:** Ask for screenshots of top 10-15 posts with engagement counts

Sort by engagement. Extract concepts from top 20%.

### Step 3: Extract Concepts

For each winning post, extract:

| Element | What to Capture |
|---------|-----------------|
| **Hook** | First line/first 3 seconds |
| **Topic** | Core subject matter |
| **Structure** | How content is organized |
| **Angle** | Emotional entry point |
| **Format** | Talking head, carousel, text, etc. |

### Step 4: Adapt to User's Brand

Map concepts to user's offer, audience, and voice.

### Step 5: Generate Scripts

- Talking head → video framework
- Carousel → carousel framework
- Single post → static framework

### Step 6: Save Output

- Mining: `research/YYYY-MM-DD-competitor-mine.md`
- Scripts: `outputs/content-scripts/YYYY-MM-DD-[concept-slug].md`

---

## Mine Mode

Research only (no scripts). See [references/mining-template.md](references/mining-template.md).

Output: `research/YYYY-MM-DD-competitor-mine.md`

---

## Video Mode

Input: concept from mining, user topic, or research file.

| Framework | Structure | When to Use |
|-----------|-----------|-------------|
| **Educational** | Hook -> Tips -> Takeaway | How-to, lists |
| **Story-based** | Hook -> Trigger -> Outcome | Personal narrative |
| **Transformation** | Before -> Turning Point -> After | Journey, case study |
| **Problem-Solution** | Hook -> Problem -> Solution | PAS for organic |

Structure: Hook (0-3s) → Retain (3-45s) → Reward (final 5-15s)

See [references/organic-frameworks.md](references/organic-frameworks.md) and [references/video-script-template.md](references/video-script-template.md).

---

## Carousel Mode

7-10 slides: Hook → Value (one idea/slide) → Summary → CTA

See [references/carousel-template.md](references/carousel-template.md).

---

## Static Mode

Hook (first line) → Body → Soft CTA → Hashtags (optional)

See [references/static-template.md](references/static-template.md).

---

## Voice Adaptation

Read `reference/core/voice.md`. Match tone, use their vocabulary, avoid their "never say" list.

**Authenticity:** Sounds like creator (not copywriter). Uses contractions. Matches energy. No AI tells ("dive into", "unlock", "game-changer").

---

## CTA Softness

| Hard (Avoid) | Soft (Use) |
|--------------|-----------|
| "Link in bio to buy" | "Save this for later" |
| "Sign up now" | "Follow for more" |
| "Limited time" | "Comment [word] for more" |
| "Don't miss out" | "Share with someone who needs this" |

Exception: Match user's style if their voice file shows harder CTAs work.

---

## Integration with /think

To save winning angles: route to `/think codify` → `reference/proof/angles/`.

---

## Quality Checklist

**Content:** Hook stops scroll. One idea. Value before ask. Soft CTA.

**Voice:** Sounds like creator. Matches energy. Uses vocabulary. No AI tells.

**Platform:** Appropriate length. Correct structure. Optimized for retention/saves.

---

## Examples

### Example 1: Full Flow

```
User: /content

Claude: Let me check for your competitor list...
[Reads reference/competitors/handles.md]

Found 5 competitors. Want me to mine their top-performing content?

User: Yes

Claude: [Uses Apify or asks for data]
[Extracts top 10 concepts]

Here are the winning concepts:
1. "The one thing successful [audience] do differently" (Story)
2. "Stop doing [common mistake]" (Problem-Solution)
3. "3 tools I use every day for [outcome]" (Educational)
...

Which concepts resonate? I'll generate scripts in your voice.

User: 1 and 4

Claude: [Reads voice.md, generates scripts]
[Saves to outputs/content-scripts/]
```

### Example 2: Video Only

```
User: /content video "how I structure my morning routine"

Claude: What framework fits this best?
- Educational (tips and steps)
- Story-based (your journey)
- Transformation (before/after)

User: Story-based

Claude: [Generates script using story framework]
[Saves to outputs/content-scripts/]
```

### Example 3: Mine Only

```
User: /content mine

Claude: [Gathers competitor data]
[Extracts concepts]
[Saves to research/2026-01-19-competitor-mine.md]

Mining complete. 12 winning concepts extracted.
Run `/content video` or `/content carousel` to generate from these.
```

---

## References

**Setup:** [first-time-setup.md](references/first-time-setup.md), [minimal-voice-template.md](references/minimal-voice-template.md), [apify-setup.md](references/apify-setup.md)

**Frameworks:** [organic-frameworks.md](references/organic-frameworks.md)

**Templates:** [mining-template.md](references/mining-template.md), [video-script-template.md](references/video-script-template.md), [carousel-template.md](references/carousel-template.md), [static-template.md](references/static-template.md)

---

## Pre-Response Checklist

Before responding to user, verify:
- [ ] Explained Apify's value for Instagram (essential, not nice-to-have)
- [ ] Used numbered options for multi-choice
- [ ] Asked which platform (Instagram/TikTok/Both/Other)
- [ ] Kept response tight (recommend ONE path, not all modes)
