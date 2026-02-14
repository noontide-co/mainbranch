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
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
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

## What AI Can and Cannot Do

> "AI can show WHAT worked. Human must judge WHY." — Koston Williams

Understanding this distinction prevents frustration and sets realistic expectations.

### AI CAN:
- **Collect** — Scrape posts, pull metrics, gather content
- **Transcribe** — Convert video/audio to text
- **Identify** — Surface patterns, hooks, formats, engagement rates
- **Generate** — Write scripts from concepts in YOUR voice

### AI CANNOT:
- **Explain** — Tell you WHY something actually worked
- **Judge** — Know if a framework transfers to YOUR niche
- **Feel** — Sense the emotional resonance that makes content connect
- **Decide** — Choose which frameworks fit YOUR energy and personality

### YOUR JOB (Framework Transfer):

When reviewing mined content, extract three dimensions:

| Dimension | What to Notice | Your Question |
|-----------|----------------|---------------|
| **Visual** | Format, production style, visual patterns | Does this fit my setup/skills? |
| **Audible** | Energy level, pacing, vocal delivery | Can I match this energy authentically? |
| **Emotional** | Primary emotion triggered, identity play | Does this align with my audience's identity? |

**The skill is framework transfer** — taking what worked elsewhere and applying it to your niche with your voice.

This methodology comes from Koston Williams, who used it to create a 6M view video. The insight: a competitor's content worked for THEM. Your job is to see the framework beneath the content, judge whether it transfers to YOUR context, and adapt it to YOUR voice and audience.

### Mining Flows INTO Reference

Mining is INPUT. Reference is OUTPUT.

```
Mining → Human Synthesis → Reference Update → THEN Content Generation
```

**Do not skip straight from mining to scripts.** The temptation is real — you see a great concept and want to generate immediately. Resist it.

The path:
1. Mine competitor content (data collection)
2. **Extract frameworks** — You judge Visual/Audible/Emotional dimensions
3. **Update reference files** — Codify what you learned into angles, voice, audience insights
4. Generate content from enriched reference

Why this matters: Scripts generated from enriched reference files are better than scripts generated from raw concepts. Your reference files ARE your competitive advantage. They compound.

This is why mining lives in `/think` — it's research that feeds your evergreen context, not a shortcut to content.

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. Check `.vip/local.yaml` for `current_offer`
2. If set: load `reference/offers/[current_offer]/offer.md` as the active offer
3. If not set AND `reference/offers/` exists: ask which offer
4. If no `offers/` folder: use `reference/core/offer.md` (single-offer, backward compatible)

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

**Offer argument:** `/organic video [offer] "concept"` — e.g., `/organic video community "morning routine"`
If offer specified, overrides session `current_offer` for this run.

---

## First-Time Setup

Requires `reference/core/voice.md` (always core), plus resolved `offer.md` and `audience.md` (offer-aware — checks `offers/[active]/` first, falls back to `core/`).

**Optional but recommended:** `reference/domain/content-strategy.md` — If present, /organic reads content pillars to align generated content and platform strategy for format selection. Note that `content-strategy.md` is brand-level, but content can be offer-specific. Works perfectly without it.

**Congruence check:** If `reference/domain/funnel/skool-surfaces.md` exists, read it. Organic content should echo the same positioning and claims visible on the Skool about page and pricing cards. No contradictions between organic and the landing experience.

**CWD-first:** If `reference/core/` exists in CWD, you're already in the business repo. Otherwise, resolve via `~/.config/vip/local.yaml` (`default_repo`). If missing, ask the user or run `/setup`.

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
Check research/ -> Check content-strategy.md (if exists, suggest pillar-aligned topic) -> Select concept -> Generate -> Output
```

If content-strategy.md exists and has pillars defined, suggest topics aligned to those pillars when the user has no specific concept in mind.

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

**Output path (all script modes):** `outputs/YYYY-MM-DD-organic-[offer]-{campaign}/organic-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)

Campaign name is REQUIRED. Ask user if not provided. Examples: `january-hooks`, `transformation-series`, `pain-point-reels`.

---

## Context Awareness (Check Before Recommending)

**At session start, scan what's been done:**

1. Check `research/*-competitor-mine.md` — Who was mined? When?
2. Check `outputs/*-organic-*/` — What scripts exist?
3. Don't suggest re-mining same handles from today
4. Recommend generating from existing mining if concepts unused
5. Check `reference/domain/content-strategy.md` — What pillars are defined? What platform is the target?

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

## Content Strategy Integration

If `reference/domain/content-strategy.md` exists, /organic uses it to improve output:

- **Pillar alignment:** Suggest topics from defined pillars when user has no specific concept
- **Platform format:** Default to the format matching the target platform from platform strategy
- **Content mix:** Track which pillar types have been generated recently to maintain ratio balance
- **Hooks library:** Pull proven hooks from the hooks library section if populated
- **Enemy-pillar mapping:** Each pillar fights a named enemy. Content should position against the enemy. Check voice.md for declared enemies.
- **Saves-first metrics:** Weight save-ability highest when evaluating content concepts. Saveable = educational, actionable, reference-worthy.

If content-strategy.md does not exist, /organic works exactly as before -- from mined concepts or user-provided topics. No warnings, no degradation.

---

## Quality Checklist

**Content:** Hook stops scroll. One idea. Value before ask. Soft CTA.

**Saves optimization:** Is this content saveable? Educational, actionable, reference-worthy content drives saves. Saves are the #1 purchase intent signal — weight them above shares and likes.

**Enemy clarity:** Does this content fight a named enemy? Check voice.md for Named Enemies section. Enemy-driven content creates identity contrast.

**Voice:** Sounds like creator. Matches energy. Uses vocabulary. No AI tells.

**Platform:** Appropriate length. Correct structure. Optimized for retention/saves.

**Skool congruence:** If `skool-surfaces.md` exists, claims and positioning match live about page + pricing cards.

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

