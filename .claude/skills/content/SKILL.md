---
name: content
description: |
  Mine competitor content and generate organic scripts for Reels, TikTok, and carousels. Use when:
  (1) User wants to research competitor Instagram/TikTok content
  (2) User says "mine", "competitors", "organic", "reels", "tiktok"
  (3) User needs scripts for talking-head videos (not ads)
  (4) User wants carousel copy for Instagram
  (5) User needs captions for static posts

  Supports modes: full flow (mine -> script), mine-only, video, carousel, static.
---

# Content

Mine competitor content, extract winning concepts, generate scripts in your voice.

**Need help?** Type `/help` + your question anytime.

---

## First-Time Setup

Requires `reference/core/voice.md`, `audience.md`, and `offer.md`.

**Two-repo model:** vip is the engine (skills). The user's business repo has their data. Search all working directories for `reference/core/`. If not found, ask user which business repo to use.

**Missing these files?** See [references/first-time-setup.md](references/first-time-setup.md) for quick templates, or run `/setup`.

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

Which platform? Instagram Reels, TikTok, or both?
```

---

## Data Extraction

**Always mention upfront** how data will be gathered:

- **If Apify MCP available:** "I'll use Apify to pull competitor data automatically."
- **If no Apify:** "I'll need you to share screenshots of competitor posts (manual mode)."

Check for Apify by looking for MCP tools. If unclear, assume manual mode.

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

Check for `reference/competitors/handles.md`:

```markdown
# Competitor Handles

## Primary Competitors (same niche)
- @competitor1
- @competitor2

## Adjacent Creators (similar audience)
- @adjacent1
- @adjacent2

## Aspirational (bigger accounts to study)
- @aspirational1
```

If file missing, ask:

> "Who are 3-5 creators making content for your audience? These can be:
> - Direct competitors
> - Adjacent creators (similar audience, different offer)
> - Bigger accounts you admire"

### Step 2: Mine Content

**Option A: Apify MCP (if available)**

Use Instagram Profile Scraper actor. Returns structured JSON with engagement metrics. Sort server-side by engagement rate.

**Option B: Manual (no setup required)**

Ask user to share:
- Screenshots of competitor's top 10-15 posts
- Like/comment counts for each
- Caption text (at least first line)

Either method works. Apify is faster; manual requires no setup.

**Filter for winners:**

Sort by engagement (likes + comments). Extract concepts from top 20%.

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

Map competitor concepts to user's:
- Offer (what relates to their product)
- Audience (what resonates with their people)
- Voice (how they would say it)

### Step 5: Generate Scripts

Based on content type:
- **Talking head** -> Use video framework
- **Carousel** -> Use carousel framework
- **Single post** -> Use static framework

### Step 6: Save Output

Save mining results to:
```
research/YYYY-MM-DD-competitor-mine.md
```

Save generated scripts to:
```
outputs/content-scripts/YYYY-MM-DD-[concept-slug].md
```

---

## Mine Mode

Research competitor content without generating scripts.

### Workflow

1. Identify competitors (file or ask)
2. Gather content data (Apify or manual)
3. Sort by engagement (server-side)
4. Extract top concepts
5. Save to research file

### Output Location

```
research/YYYY-MM-DD-competitor-mine.md
```

### Template

See [references/mining-template.md](references/mining-template.md)

### Exit Criteria

Mining is complete when:
- [ ] Competitors identified
- [ ] Content data gathered
- [ ] Sorted by performance
- [ ] Top 10-20 concepts extracted
- [ ] Saved to research/

---

## Video Mode

Generate Reels/TikTok scripts from concepts.

### Input

Either:
- A concept from mining session
- User-provided topic
- Reference to research file

### Framework Selection

Detect or ask for framework:

| Framework | Structure | When to Use |
|-----------|-----------|-------------|
| **Educational** | Hook -> Tips -> Takeaway | How-to, lists, advice |
| **Story-based** | Hook -> Trigger -> Outcome -> Result | Personal narrative |
| **Transformation** | Before -> Turning Point -> After | Journey, case study |
| **Problem-Solution** | Hook -> Problem -> Solution -> CTA | PAS for organic |

User can specify: `/content video "topic" --framework story`

### Hook-Retain-Reward Structure

Every video script follows:

1. **Hook** (0-3 seconds): Stop the scroll
2. **Retain** (3-45 seconds): Deliver value, maintain attention
3. **Reward** (last 5-15 seconds): Payoff + soft CTA

See [references/organic-frameworks.md](references/organic-frameworks.md) for detailed breakdown.

### Output

See [references/video-script-template.md](references/video-script-template.md)

---

## Carousel Mode

Generate multi-slide Instagram carousels.

### Input

Either:
- A concept from mining session
- User-provided topic
- Number of slides (default: 7-10)

### Structure

| Slide | Purpose |
|-------|---------|
| 1 | Hook slide (stops scroll) |
| 2-8 | Value slides (one idea per slide) |
| 9 | Summary or recap |
| 10 | CTA slide |

### Output

See [references/carousel-template.md](references/carousel-template.md)

---

## Static Mode

Generate single-post captions.

### Input

- Topic or angle
- Image context (what the image shows)
- Desired length (short/medium/long)

### Structure

1. **Hook** (first line visible before "more")
2. **Body** (value or story)
3. **CTA** (soft: save, comment, follow)
4. **Hashtags** (optional, user preference)

### Output

See [references/static-template.md](references/static-template.md)

---

## Voice Adaptation

When generating, always:

1. Read `reference/core/voice.md`
2. Match tone markers (casual, professional, energetic, etc.)
3. Use vocabulary from voice file
4. Avoid phrases marked as "never say"

### Authenticity Checklist

- [ ] Sounds like the creator, not a copywriter
- [ ] Uses contractions naturally
- [ ] Matches their energy level
- [ ] Includes their verbal quirks
- [ ] Avoids AI tells ("dive into", "unlock", "game-changer")

---

## CTA Softness

Organic content uses soft CTAs:

| Hard (Avoid) | Soft (Use) |
|--------------|-----------|
| "Link in bio to buy" | "Save this for later" |
| "Sign up now" | "Follow for more like this" |
| "Limited time offer" | "Comment [word] if you want the full breakdown" |
| "Don't miss out" | "Share with someone who needs this" |

**Exception:** If user's voice file shows they use harder CTAs successfully, match their style.

---

## Integration with /think

When user wants to save winning angles to reference:

> "Want to save these winning concepts to your angles folder? I can route to `/think codify` to add them to `reference/proof/angles/`."

This keeps codification logic in one place.

---

## Quality Checklist

Before outputting any script:

**Content:**
- [ ] Hook stops scroll (first 3 seconds/first line)
- [ ] One clear idea per piece
- [ ] Value delivered before any ask
- [ ] Soft CTA appropriate to platform

**Voice:**
- [ ] Sounds like the creator
- [ ] Matches their energy
- [ ] Uses their vocabulary
- [ ] No AI tells

**Platform:**
- [ ] Appropriate length for format
- [ ] Structure matches content type
- [ ] Optimized for the algorithm (retention, saves)

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

**Setup (read for new users):**
- [references/first-time-setup.md](references/first-time-setup.md) - Prerequisites and quick start
- [references/minimal-voice-template.md](references/minimal-voice-template.md) - Voice file template

**Frameworks (read when generating):**
- [references/organic-frameworks.md](references/organic-frameworks.md) - Content structure frameworks

**Templates (read when outputting):**
- [references/mining-template.md](references/mining-template.md) - Mining output format
- [references/video-script-template.md](references/video-script-template.md) - Reels/TikTok template
- [references/carousel-template.md](references/carousel-template.md) - Carousel slide template
- [references/static-template.md](references/static-template.md) - Single post template
