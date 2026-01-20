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

### Token Awareness

Mining uses significant tokens (~3-5k per competitor). Before running:

```
Mining scope: 3 competitors × ~10 posts each
Estimated tokens: ~12-15k

1. Proceed (full scan)
2. Quick scan (top 5 posts each, ~6-8k tokens)
3. Pick specific competitors to mine
```

Let user control scope. Don't auto-run expensive operations.

### Competitor Discovery

If user says "find me competitors" or has thin/empty handles.md:

| Method | When to Use |
|--------|-------------|
| Hashtag search | User knows their niche hashtags |
| Keyword search | User can describe their niche |
| Similar accounts | User knows 1-2 competitors |

See [references/apify-discovery.md](references/apify-discovery.md) for actor details and workflows.

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

---

## Context Awareness (Check Before Recommending)

**At session start, scan what's been done:**

1. Check `research/*-competitor-mine.md` — Who was mined? When?
2. Check `outputs/content-scripts/` — What scripts exist?
3. Don't suggest re-mining same handles from today
4. Recommend generating from existing mining if concepts unused

**Example context-aware response:**
```
Found today's mining (research/2026-01-20-competitor-mine.md):
- @cassie.schoonover, @likfoon already mined
- 10 concepts extracted, 2 scripts generated

Options:
1. Generate from remaining 8 concepts
2. Mine new competitors
3. Start fresh topic
```

---

## Transparency

Before generating: show which reference files you're using.
Before saving: show file paths.

---

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

### Example 1: Context-Aware Start

```
User: /content

Claude: Found ac-repo. Checking existing work...

Today's mining exists (3 competitors, 10 concepts).
Scripts generated: 2 of 10 concepts used.

1. Generate from remaining 8 concepts
2. Mine new competitors
3. Something else

User: 1

Claude: [Shows concepts, user picks, generates with voice.md]
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

- [ ] Checked existing mining/scripts before recommending
- [ ] Didn't suggest re-mining same handles from today
- [ ] Showed token estimate before expensive operations
- [ ] Offered scope control (full vs quick scan)
- [ ] Used numbered options
