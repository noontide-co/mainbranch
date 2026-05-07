---
name: mb-organic
description: "CREATE organic content scripts (Reels, TikTok, carousels, static posts). Use when user wants to GENERATE new scripts from concepts. NOT for research/mining competitor content - that's /mb-think. NOT for paid ads - use /mb-ads instead. Modes: video, carousel, static. If user says \"mine\", \"scrape\", \"research competitors\" → route to /mb-think."
loops: [ship]
---

# Organic

Create organic content scripts in your voice — Reels, TikToks, carousels, static posts.

**Need help?** Type `/mb-help` + your question anytime. If conversation compacts, `/mb-help` reloads fresh context.

## Output destinations and operator vocabulary

When this skill produces a coordinated push (a content sequence with a goal,
audience, and review date), write the wrapping record to
`pushes/<YYYY-MM-DD-slug>/push.md` (`type: push`, `linked_pushes` for inbound
links). One-off scripts and source captures route to `documents/transcripts/`
or `documents/prototypes/` per the artifact-routing rules in the system
architecture doc; they don't need a push wrapper.

If `core/vocabulary.md` defines display words (e.g. `terms.push.singular: drop`),
speak the operator's word in conversation while still writing canonical files.
If the repo still has legacy `campaigns/` records, recommend `mb doctor` and
`mb migrate campaigns --plan` before creating new push work.

When creating `push.md`, include the validator-required frontmatter and fill
the values from repo truth or operator answers:

```yaml
---
type: push
slug: YYYY-MM-DD-slug
kind: nurture
status: planned
health: unknown
goal: { metric: "", target: "", by: YYYY-MM-DD }
owner: ""
audience: ""
offer: core/offers/<offer>/offer.md
promise: ""
---
```

---

## Triage

Detect if user is in the right place:

| User Says | They Want | Route To |
|-----------|-----------|----------|
| "mine", "scrape", "research competitors", "what are they saying" | Research/Mining | `/mb-think` (research mode) |
| "transcribe", "extract from video" | Mining | `/mb-think` (research mode) |
| "create", "generate", "write scripts", "make content" | Create | Continue in `/mb-organic` |

**If mining intent detected:**
> "Sounds like you want to research/mine competitor content. That's `/mb-think` territory — it saves to `research/` and feeds your reference files. Should I switch you to `/mb-think`?"

**If unclear:**
> "Are you trying to mine competitor content (research) or create new scripts (generate)?"

---

## Pull Latest Updates

For the canonical engine resolution + pull bash block (and the failure warning), see [`references/pull-engine-updates.md`](references/pull-engine-updates.md). Run it at the start of every invocation.

Then run `mb status --json --peek` from the business repo and use its
`readiness`, `drift.items`, and `ranked_actions` facts before asking setup or
reference-health questions. Direct file checks below are content-specific, not
repo-health probes.

---

## About Mining (Lives in /mb-think Now)

Mining competitor content is research work. It belongs in `/mb-think` because:
- Mining output goes to `research/` folder
- Extracted insights feed into reference files
- It's the "Research" phase of the think cycle

**If user wants to mine:** Route them to `/mb-think`. Say:
> "Mining is research work — `/mb-think` handles that and saves to your `research/` folder. Should I switch you over?"

**This skill assumes mining already happened.** Users arrive here with:
- Concepts from `research/*-competitor-mine.md`
- A topic they want to turn into content
- Inspiration from their own research

For the full mining methodology (Visual/Audible/Emotional framework, AI capabilities and limits, why mining flows into reference) see [references/mining-methodology.md](references/mining-methodology.md).

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. Check `.vip/local.yaml` for `current_offer`
2. If set: load `core/offers/[current_offer]/offer.md` as the active offer
3. If not set AND `core/offers/` exists: ask which offer
4. If no `core/offers/` folder: use `core/offer.md` (single-offer mode)
5. Legacy fallback: if the repo does not have `core/`, read the old
   `reference/core/` and `reference/offers/` paths.

In current repos, `reference/core` and `reference/offers` are compatibility
bridges to `core/` and `core/offers/`. Treat them as aliases, not duplicate
files. Read through them only as fallback, and write once to the canonical
`core/` path when reference updates are needed.

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

**Offer argument:** `/mb-organic video [offer] "concept"` — e.g., `/mb-organic video community "morning routine"`
If offer specified, overrides session `current_offer` for this run.

---

## First-Time Setup

Requires `core/voice.md` (always core), plus resolved `offer.md` and `audience.md` (offer-aware — checks `core/offers/[active]/` first, falls back to `core/`).

**Optional but recommended:** `core/content-strategy.md` — If present, /mb-organic reads content pillars to align generated content and platform strategy for format selection. Note that `content-strategy.md` is brand-level, but content can be offer-specific. Works perfectly without it.

**Congruence check:** If `core/operations/funnel/skool-surfaces.md` exists, read it. Organic content should echo the same positioning and claims visible on the Skool about page and pricing cards. No contradictions between organic and the landing experience.

**CWD-first:** If `core/` or legacy `reference/core/` exists in CWD, you're already in the business repo. Otherwise, run `mb status --json --peek` and use its repo/readiness facts if available. If status cannot identify a repo, ask the user or run `/mb-setup`.

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

1. Mine competitors first → `/mb-think` (saves to research/, come back here after)
2. Skip mining, give me a topic → I'll generate directly

Which works better for you?
```

---

## Modes

### `/mb-organic` (Default)

Check for existing mined concepts, pick one, generate scripts.

```
Check research/ -> Check content-strategy.md (if exists, suggest pillar-aligned topic) -> Select concept -> Generate -> Output
```

If content-strategy.md exists and has pillars defined, suggest topics aligned to those pillars when the user has no specific concept in mind.

If no mining exists, prompt: "No mined concepts found. Want to mine competitors first? That's `/mb-think` — should I switch you over?"

### `/mb-organic mine` (Routes to /mb-think)

If user types `/mb-organic mine`, redirect:
> "Mining is research work now. Routing you to `/mb-think` for mining — it'll save to `research/` and you can come back here to generate scripts from those concepts."

Then invoke `/mb-think`.

### `/mb-organic video "concept"`

Generate Reels/TikTok script from a concept.

### `/mb-organic carousel "concept"`

Generate multi-slide carousel copy from a concept.

### `/mb-organic static "concept"`

Generate single-post caption from a concept.

**Output path (all script modes):** `pushes/YYYY-MM-DD-organic-[offer]-{slug}/organic-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode). On legacy repos that still have `campaigns/`, run `mb migrate campaigns --plan` first; do not write new content under `campaigns/`.

**Output frontmatter:**
```yaml
---
type: output
format: video | carousel | static
date: YYYY-MM-DD
status: draft
platform: instagram | tiktok
---
```

Campaign name is REQUIRED. Ask user if not provided. Examples: `january-hooks`, `transformation-series`, `pain-point-reels`.

---

## Context Awareness (Check Before Recommending)

**At session start, scan what's been done:**

1. Check `research/*-competitor-mine.md` — Who was mined? When?
2. Check `pushes/*-organic-*/` — What scripts exist? Treat `campaigns/` as a legacy fallback only.
3. Don't suggest re-mining same handles from today
4. Recommend generating from existing mining if concepts unused
5. Check `core/content-strategy.md` — What pillars are defined? What platform is the target?

**Example context-aware response:**
```
Found today's mining (research/2026-01-20-competitor-mine.md):
- @cassie.schoonover, @likfoon already mined
- 10 concepts extracted, 2 scripts generated

Options:
1. Generate from remaining 8 concepts
2. Mine new competitors → `/mb-think`
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
2. **If no concepts** — Ask if they want to mine first (route to `/mb-think`) or provide a topic directly
3. **Select concept** — User picks from mined concepts or provides their own
4. **Adapt to brand** — Map concept to user's offer, audience, voice
5. **Generate scripts** — Use appropriate framework (video/carousel/static)
6. **Save output** — Scripts to `pushes/YYYY-MM-DD-organic-{slug}/` (canonical). Never `campaigns/`; that folder is legacy compatibility only.
7. **Checkpoint prompt** — run `mb checkpoint --plan --json`, show the proposed checkpoint and blockers, validate the chosen message with `mb checkpoint --validate "..." --json`, then after operator approval save with `mb checkpoint --message "..." --yes`.

**Mining lives in `/mb-think` now.** If user needs to mine competitors, route them there first.

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

Read `core/voice.md` (or legacy `reference/core/voice.md` only when `core/` is absent). Match tone, use their vocabulary, avoid their "never say" list.

**Authenticity:** Sounds like creator (not copywriter). Uses contractions. Matches energy. No AI tells ("dive into", "unlock", "game-changer").

See [references/organic-frameworks.md](references/organic-frameworks.md) for soft CTA examples.

---

## Integration with /mb-think

To save winning angles: route to `/mb-think codify` → `core/proof/angles/`.

---

## Content Strategy Integration

If `core/content-strategy.md` exists, /mb-organic uses it to improve output:

- **Pillar alignment:** Suggest topics from defined pillars when user has no specific concept
- **Platform format:** Default to the format matching the target platform from platform strategy
- **Content mix:** Track which pillar types have been generated recently to maintain ratio balance
- **Hooks library:** Pull proven hooks from the hooks library section if populated
- **Enemy-pillar mapping:** Each pillar fights a named enemy. Content should position against the enemy. Check voice.md for declared enemies.
- **Saves-first metrics:** Weight save-ability highest when evaluating content concepts. Saveable = educational, actionable, reference-worthy.

If content-strategy.md does not exist, /mb-organic works exactly as before -- from mined concepts or user-provided topics. No warnings, no degradation.

---

## Quality Checklist

**Content:** Hook stops scroll. One idea. Value before ask. Soft CTA.

**Saves optimization:** Is this content saveable? Educational, actionable, reference-worthy content drives saves. Saves are the #1 purchase intent signal — weight them above shares and likes.

**Enemy clarity:** Does this content fight a named enemy? Check voice.md for Named Enemies section. Enemy-driven content creates identity contrast.

**Voice:** Sounds like creator. Matches energy. Uses vocabulary. No AI tells.

**Platform:** Appropriate length. Correct structure. Optimized for retention/saves.

**Skool congruence:** If `skool-surfaces.md` exists, claims and positioning match live about page + pricing cards.

---

## Examples & Compaction Recovery

For walkthrough examples (context-aware start, video-only, mining redirect) and the recovering-from-compaction protocol, see [references/examples.md](references/examples.md).

---

## References

**Setup:** [first-time-setup.md](references/first-time-setup.md), [minimal-voice-template.md](references/minimal-voice-template.md), [apify-setup.md](references/apify-setup.md)

**Frameworks:** [organic-frameworks.md](references/organic-frameworks.md)

**Templates:** [mining-template.md](references/mining-template.md), [video-script-template.md](references/video-script-template.md), [carousel-template.md](references/carousel-template.md), [static-template.md](references/static-template.md)

**Methodology & Examples:** [mining-methodology.md](references/mining-methodology.md), [examples.md](references/examples.md)
