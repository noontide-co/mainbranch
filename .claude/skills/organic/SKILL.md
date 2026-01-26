---
name: organic
description: Mine competitor content and generate organic scripts. ALWAYS offer Apify MCP first for data extraction (manual fallback if unavailable). Use when: (1) User says "mine", "competitors", "organic", "reels", "tiktok", "carousel" (2) User needs scripts for talking-head videos, carousels, static posts (3) User wants to research what content works in their niche (4) User has a topic and wants organic (not paid) content. NOT for paid ads - use /ads instead. Organic = value-first, soft CTAs, engagement focus. Paid = direct response, hard CTAs, conversion focus. Modes: mine, video, carousel, static.
---

# Organic

Mine competitor content, extract winning concepts, generate scripts in your voice.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

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
Recommended: `/organic mine` — research competitors first since your voice file is still draft.

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

## Modes

### `/organic` (Full Flow - Default)

Mine competitors -> pick concepts -> generate scripts.

```
Mine -> Select -> Generate -> Output
```

### `/organic mine`

Research competitor content only. Saves to `research/YYYY-MM-DD-competitor-mine.md`. See [references/mining-template.md](references/mining-template.md).

**Output path (mining):** `research/YYYY-MM-DD-competitor-mine.md`

### `/organic video "concept"`

Generate Reels/TikTok script from a concept.

### `/organic carousel "concept"`

Generate multi-slide carousel copy from a concept.

### `/organic static "concept"`

Generate single-post caption from a concept.

**Output path (all script modes):** `outputs/YYYY-MM-DD-organic-{campaign}/organic-batch-001.md`

Campaign name is REQUIRED. Ask user if not provided. Examples: `january-hooks`, `transformation-series`, `pain-point-reels`.

---

## Context Awareness (Check Before Recommending)

**At session start, scan what's been done:**

1. Check `research/*-competitor-mine.md` — Who was mined? When?
2. Check `outputs/*-organic-*/` — What scripts exist?
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

What should we call this batch? (e.g., "january-hooks", "transformation-reels")
```

---

## Transparency

Before generating: show which reference files you're using.
Before saving: show file paths.

---

## Full Flow Walkthrough

1. **Identify competitors** — Check `reference/competitors/handles.md` or ask user
2. **Mine content** — Apify (preferred) or manual screenshots, sort by engagement
3. **Extract concepts** — Hook, topic, structure, angle, format from top 20%
4. **Adapt to brand** — Map concepts to user's offer, audience, voice
5. **Generate scripts** — Use appropriate framework (video/carousel/static)
6. **Save output** — Mining to `research/`, scripts to `outputs/YYYY-MM-DD-organic-{campaign}/`
7. **Commit prompt** — "Saved to [path]. Want me to commit this to git?"

See [references/mining-template.md](references/mining-template.md) for concept extraction template.

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

See [references/organic-frameworks.md](references/organic-frameworks.md) for soft CTA examples.

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
User: /organic

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
User: /organic video "how I structure my morning routine"

Claude: What framework fits this best?
- Educational (tips and steps)
- Story-based (your journey)
- Transformation (before/after)

User: Story-based

Claude: What should we call this batch? (e.g., "morning-routine", "productivity-series")

User: morning-routine

Claude: [Generates script using story framework]
[Saves to outputs/2026-01-26-organic-morning-routine/organic-batch-001.md]

Saved to outputs/2026-01-26-organic-morning-routine/organic-batch-001.md
Want me to commit this to git?
```

### Example 3: Mine Only

```
User: /organic mine

Claude: [Gathers competitor data]
[Extracts concepts]
[Saves to research/2026-01-19-competitor-mine.md]

Mining complete. 12 winning concepts extracted.
Run `/organic video` or `/organic carousel` to generate from these.
```

---

## Recovering from Compaction

When conversations get long, Claude's memory compresses. If mid-/organic and this happens:

**For the user:** Just type `/organic` again and describe where you were:
- "We were mining @competitor1 and @competitor2"
- "I was picking concepts from today's mining"
- "Generate a video script from the morning routine concept"

**For Claude:** When resuming:
1. Check `research/*-competitor-mine.md` for recent mining
2. Check `outputs/*-organic-*/` for existing scripts
3. Confirm with user: "I see today's mining has X concepts. Want to continue generating from those?"

---

## References

**Setup:** [first-time-setup.md](references/first-time-setup.md), [minimal-voice-template.md](references/minimal-voice-template.md), [apify-setup.md](references/apify-setup.md)

**Frameworks:** [organic-frameworks.md](references/organic-frameworks.md)

**Templates:** [mining-template.md](references/mining-template.md), [video-script-template.md](references/video-script-template.md), [carousel-template.md](references/carousel-template.md), [static-template.md](references/static-template.md)

