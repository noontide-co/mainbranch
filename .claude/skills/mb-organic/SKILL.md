---
name: mb-organic
description: "CREATE organic content scripts (Reels, TikTok, carousels, static posts) and repurpose sales videos/VSLs into short clips or creator-style excerpts. Use when user wants to GENERATE new scripts from concepts or make short clips from a sales video. NOT for research/mining competitor content - that's /mb-think. NOT for paid ads - use /mb-ads instead. Modes: video, carousel, static, sales-video repurpose. If user says \"mine\", \"scrape\", \"research competitors\" → route to /mb-think."
loops: [ship]
---

# Organic

Create organic content scripts in your voice — Reels, TikToks, carousels, static posts.

**Need help?** Type `/mb-help` + your question anytime. If conversation compacts, `/mb-help` reloads fresh context.

**CLI facts first:** Run `mb status --json --peek` from the business repo before
triage, reference-health checks, or content planning. Use its readiness, drift,
and ranked-action facts instead of hand-rolled repo-health probes.

## Output destinations and operator vocabulary

When this skill produces a coordinated push (a content sequence with a goal,
audience, and review date), write the wrapping record to
`pushes/<YYYY-MM-DD-slug>/push.md` (`type: push`, `linked_pushes` for inbound
links). One-off scripts and source captures route to `documents/transcripts/`
or `documents/prototypes/` per the artifact-routing rules in the system
architecture doc; they don't need a push wrapper.

If a content push uses a comment-keyword, DM-keyword, reply/link, resource
delivery, or external provider setup plan, write the durable plan to
`pushes/<YYYY-MM-DD-slug>/playbooks/<playbook>.md` with `type: playbook`.
The playbook records the plan, approval state, safe provider state, validation
evidence, and outcomes. It does not execute provider mutation.

If `core/vocabulary.md` defines display words (e.g. `terms.push.singular: drop`),
speak the operator's word in conversation while still writing engine files.
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

If the push is tied to a bet, decision, research file, playbook, or outcome,
add the appropriate typed frontmatter link (`linked_bets`,
`linked_decisions`, `linked_research`, `linked_playbooks`,
`linked_outcomes`). Mirror frontmatter links in `## Related links` with
Markdown relative links, or preview `mb doctor repair --plan` and ask before
applying the repair. Use the connection decision matrix in
docs/business-connections.md before adding typed links. Do not infer
frontmatter links from body-only references.

---

## Triage

Detect if user is in the right place:

| User Says | They Want | Route To |
|-----------|-----------|----------|
| "mine", "scrape", "research competitors", "what are they saying" | Research/Mining | `/mb-think` (research mode) |
| "transcribe", "extract from video" | Mining | `/mb-think` (research mode) |
| "short clips from sales video", "repurpose this VSL", "turn this sales video into clips" | Repurpose | Continue with [references/sales-video-repurpose.md](references/sales-video-repurpose.md) |
| "create", "generate", "write scripts", "make content" | Create | Continue in `/mb-organic` |

**If mining intent detected:**
> "Sounds like you want to research/mine competitor content. That's `/mb-think` territory — it saves to `research/` and feeds your reference files. Should I switch you to `/mb-think`?"

**If unclear:**
> "Are you trying to mine competitor content (research) or create new scripts (generate)?"

---

## Pull Latest Updates

For the standard Main Branch update check and failure warning, see [`references/pull-engine-updates.md`](references/pull-engine-updates.md). Run it at the start of every invocation.

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

If a selected research file has `brief_format: grok-8`, use its downstream
handoff before generating: ICP and audience language for hooks, journey stage
for format and CTA, competitive landscape for contrast, brand story for voice,
content/assets for proof, and metrics/constraints for the success bar. If the
brief names a resource-delivery mechanic, write or update a push playbook as a
plan only; do not execute provider mutation.

When organic work is meant to sharpen an offer instead of only create content,
load `.claude/reference/conversion/offer-sharpening.md`. Use the rubric to turn
audience language, objections, proof angles, and soft CTAs into durable offer
updates through `/mb-think`; do not treat comments or saves as buyer proof by
themselves.

For the full mining methodology (Visual/Audible/Emotional framework, AI capabilities and limits, why mining flows into reference) see [references/mining-methodology.md](references/mining-methodology.md).

---

## Offer Context Resolution

Before loading reference files, resolve active offer context with
`.claude/reference/business-primitives/offer-bet-push-proof.md`:

1. If a future `mb` JSON field exposes active offer state, use it.
2. Do not treat `.vip/local.yaml` as the source of truth for active-offer
   state. If legacy state exists, confirm the offer with the user instead of
   silently routing.
3. If an offer is selected and `core/offers/[offer]/offer.md` exists, load it as the active offer.
4. If no offer is selected AND `core/offers/` exists: ask which offer.
5. If no `core/offers/` folder: use `core/offer.md` (single-offer mode)
6. Legacy fallback: if the repo does not have `core/`, read the old
   `reference/core/` and `reference/offers/` paths.

In current repos, `reference/core` and `reference/offers` are compatibility
bridges to `core/` and `core/offers/`. Treat them as aliases, not duplicate
files. Read through them only as fallback, and write once to the current
`core/` path when reference updates are needed.

**Always-core files:** `soul.md`, `voice.md`, `content-strategy.md`
**Content strategy layers:** read `core/marketing/distribution-strategy.md`,
`core/marketing/channels/<channel>.md`,
`core/marketing/accounts/<platform>-<account>.md`, and
`core/people/<person>.md` when the run names a channel, account, founder, or
weekly content plan that depends on them. Do not copy person voice into every
account file; reference it.
**Offer-aware files:** `offer.md`, `audience.md`
**Proof files:** company-wide proof in `core/proof/testimonials.md`,
`core/proof/typicality.md`, and `core/proof/angles/`; offer-specific proof in
matching files under `core/offers/[active]/proof/`. Read older offer
testimonial files as compatibility context only.

**Offer argument:** `/mb-organic video [offer] "concept"` — e.g., `/mb-organic video community "morning routine"`
If offer specified, it selects the offer for this run only.

---

## First-Time Setup

Requires `core/voice.md` (always core), plus resolved `offer.md` and `audience.md` (offer-aware — checks `core/offers/[active]/` first, falls back to `core/`).

**Optional but recommended:** `core/content-strategy.md` — If present,
/mb-organic reads the recognition target, pillars, asset jobs, non-publishing
rules, and strategy links. If the repo has
`core/marketing/distribution-strategy.md`, channel files, account files, or
`core/people/<person>.md`, read the relevant ones before drafting. Works
perfectly without them.

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
Check research/ -> Check content-strategy.md and relevant strategy layers (if present) -> Select concept -> Generate -> Output
```

If content-strategy.md exists and has pillars or asset jobs defined, suggest topics aligned to those pillars when the user has no specific concept in mind.

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
5. Check `core/content-strategy.md` — What recognition target, pillars, asset jobs, and strategy links are defined?
6. If the channel/account/person is named, check the matching `core/marketing/` and `core/people/` files before drafting.

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
6. **Save output** — Scripts to `pushes/YYYY-MM-DD-organic-{slug}/`. Never `campaigns/`; that folder is legacy compatibility only.
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
- **Asset job:** Identify whether the piece should rank, teach, prove, compare, convert, announce, or start a conversation
- **Platform format:** Default to the format matching the target platform from channel or distribution strategy
- **Account fit:** Use account strategy for allowed topics, CTA path, cadence, and content mix when present
- **Person voice:** Use `core/people/<person>.md` for founder/person beliefs, stories, and fabrication boundaries when an account references it
- **Content mix:** Track which pillar types have been generated recently to maintain ratio balance
- **Hooks library:** Pull proven hooks from the hooks library section if populated
- **Enemy-pillar mapping:** Each pillar fights a named enemy. Content should position against the enemy. Check voice.md for declared enemies.
- **Saves-first metrics:** Weight save-ability highest when evaluating content concepts. Saveable = educational, actionable, reference-worthy.

If content strategy files do not exist, /mb-organic works exactly as before --
from mined concepts or user-provided topics. No warnings, no degradation.

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

**Sales video repurposing:** [sales-video-repurpose.md](references/sales-video-repurpose.md)

**Templates:** [mining-template.md](references/mining-template.md), [video-script-template.md](references/video-script-template.md), [carousel-template.md](references/carousel-template.md), [static-template.md](references/static-template.md)

**Methodology & Examples:** [mining-methodology.md](references/mining-methodology.md), [examples.md](references/examples.md)
