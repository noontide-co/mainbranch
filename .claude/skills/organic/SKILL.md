---
name: organic
description: CREATE organic content scripts (Reels, TikTok, carousels, static posts). Use when user wants to GENERATE new scripts from concepts. NOT for research/mining competitor content - that's /think. NOT for paid ads - use /ads instead. Modes: video, carousel, static. If user says "mine", "scrape", "research competitors" → route to /think.
---

# Organic

Create organic content scripts in your voice — Reels, TikToks, carousels, static posts.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

---

## Triage

Detect if user is in the right place:

| User Says | They Want | Route To |
|-----------|-----------|----------|
| "mine", "scrape", "research competitors", "what are they saying" | Research/Mining | `/think` (research mode) |
| "transcribe", "extract from video" | Mining | `/think` (research mode) |
| "create", "generate", "write scripts", "make content" | Create | Continue in `/organic` |

**If mining intent detected:**
> "Sounds like you want to research/mine competitor content. That's `/think` territory — it saves to `research/` and feeds your reference files. Should I switch you to `/think`?"

**If unclear:**
> "Are you trying to mine competitor content (research) or create new scripts (generate)?"

---

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## About Mining (Lives in /think Now)

Mining competitor content is research work. It belongs in `/think` because:
- Mining output goes to `research/` folder
- Extracted insights feed into reference files
- It's the "Research" phase of the think cycle

**If user wants to mine:** Route them to `/think`. Say:
> "Mining is research work — `/think` handles that and saves to your `research/` folder. Should I switch you over?"

**This skill assumes mining already happened.** Users arrive here with:
- Concepts from `research/*-competitor-mine.md`
- A topic they want to turn into content
- Inspiration from their own research

---

## First-Time Setup

Requires `reference/core/voice.md`, `audience.md`, `offer.md`.

Search all working directories for `reference/core/`. If not found, ask user or run `/setup`.

Missing files? See [references/first-time-setup.md](references/first-time-setup.md).

---

## Presenting Options (Keep It Tight)

Don't list all modes in chunky blocks. Instead:

1. **Check for existing concepts** — Is there recent mining in `research/`?
2. **Recommend ONE path** based on their context
3. **Mention alternatives briefly** in one line

**Example output (concepts exist):**
```
Found recent mining (research/2026-01-20-competitor-mine.md) with 10 concepts.

Recommended: Pick a concept and generate a video script.

Other modes: `carousel "concept"`, `static "concept"`

Which concept interests you? Or provide your own topic.
```

**Example output (no concepts):**
```
No recent mining found. Two options:

1. Mine competitors first → `/think` (saves to research/, come back here after)
2. Skip mining, give me a topic → I'll generate directly

Which works better for you?
```

---

## Modes

### `/organic` (Default)

Check for existing mined concepts, pick one, generate scripts.

```
Check research/ -> Select concept -> Generate -> Output
```

If no mining exists, prompt: "No mined concepts found. Want to mine competitors first? That's `/think` — should I switch you over?"

### `/organic mine` (Routes to /think)

If user types `/organic mine`, redirect:
> "Mining is research work now. Routing you to `/think` for mining — it'll save to `research/` and you can come back here to generate scripts from those concepts."

Then invoke `/think`.

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
2. Mine new competitors → `/think`
3. Start fresh with your own topic

What should we call this batch? (e.g., "january-hooks", "transformation-reels")
```

---

## Transparency

Before generating: show which reference files you're using.
Before saving: show file paths.

---

## Full Flow Walkthrough

1. **Check for concepts** — Look in `research/*-competitor-mine.md` or `research/*-mining.md`
2. **If no concepts** — Ask if they want to mine first (route to `/think`) or provide a topic directly
3. **Select concept** — User picks from mined concepts or provides their own
4. **Adapt to brand** — Map concept to user's offer, audience, voice
5. **Generate scripts** — Use appropriate framework (video/carousel/static)
6. **Save output** — Scripts to `outputs/YYYY-MM-DD-organic-{campaign}/`
7. **Commit prompt** — "Saved to [path]. Want me to commit this to git?"

**Mining lives in `/think` now.** If user needs to mine competitors, route them there first.

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
2. Mine new competitors → `/think`
3. Give me a fresh topic

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

### Example 3: Mining Redirect

```
User: /organic mine

Claude: Mining is research work now — it lives in `/think` so your mined
concepts go to `research/` and can feed your reference files.

Switching you to `/think` for mining. Once you've got concepts, come back
to `/organic` to generate scripts from them.

[Routes to /think]
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

