---
name: skill-brief-draft
tier: skill
calls: []
description: "Compose a site brief from offer.md + audience.md + voice.md + research files + the operator's dial / archetype picks. Used by /site as the brief-drafting step. Loadable independently for /vsl, /ads, /organic if they want to share the same brief shape."
---

# skill-brief-draft

A composable skill for drafting a site / campaign brief. /site calls this in Step 2 of the minisite flow. /vsl, /ads, /organic *may* call it in v0.2 — for now it's /site-only.

## Inputs

- `offer.md`, `audience.md`, `voice.md` (resolved via `mb resolve`)
- `research/*.md` produced earlier in the flow
- Operator picks: `dial`, `archetype` (optional), `audience_current_archetype` (optional)
- Picked headline formulas (2-3 from `references/headline-formulas.md`)

## Outputs

A single markdown artifact: `decisions/YYYY-MM-DD-minisite-brief-<slug>.md` with the v0.1 schema:

```yaml
---
type: brief
date: YYYY-MM-DD
slug: <offer-slug>
status: proposed
dial: convert | story | brand
archetype: ...
audience_current_archetype: ...
copy_framework_tag: ...
headline_formulas_picked: [...]
do_not_state: [...]
four_forces: {push, pull, habit, anxiety}
voice_anchor_lines: {use: [...], avoid: [...]}
---
```

Plus the body sections: headline + subhead, value prop, mechanism summary, picked supporting pages, conversion endpoint, adjacency map.

## Flow

1. **Read inputs.** Resolve offer/audience/voice; load picked archetype detail file.
2. **Compose schema header.** Fill in fields from operator picks.
3. **Draft headline + subhead.** Apply one of the picked formulas. Aim for ≤ 2 lines.
4. **Draft value prop.** 3 short reasons OR one extended argument. Match the dial.
5. **Draft mechanism summary.** For the how-it-works page.
6. **Pick supporting pages.** 2-4 from proof / pricing / faq / about.
7. **Build adjacency map.** Per Hughes paired-imagery rule, name two images per section.
8. **Hand off to skill-review** with the dial.

## Cross-references

- [references/archetypes.md](references/archetypes.md)
- [references/headline-formulas.md](references/headline-formulas.md)
- `skill-review` composable skill
