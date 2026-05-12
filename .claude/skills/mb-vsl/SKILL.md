---
name: mb-vsl
description: "Compatibility router for existing /mb-vsl users. VSL is reusable conversion knowledge, not a standalone durable primitive. Use only when the operator explicitly invokes /mb-vsl or asks which workflow handles a VSL. Route sales/about/landing-page videos to /mb-site, paid long-form video ads to /mb-ads, teardown/pitch extraction/objection mining to /mb-think, and clips or excerpts to /mb-organic. Never invents facts."
loops: [decide, ship]
---

# VSL Compatibility Router

`/mb-vsl` exists for compatibility. Do not treat VSL as its own Main Branch
primitive. Treat it as conversion knowledge that belongs inside the workflow
the operator is actually trying to run.

## Start Every Run

1. Load `.claude/reference/conversion/vsl-routing.md`.
2. Run `mb status --json --peek` from the business repo and use its readiness,
   drift, and ranked-action facts before asking for missing context.
3. Resolve offer context through current `core/` and `core/offers/` paths. Do
   not treat `.vip/local.yaml` as active-offer truth; it is legacy audit input
   only.

## Route By Intent

Ask one question if the surface is unclear:

> "Where will this sales video live: a page, a paid ad, a teardown/research
> note, or short-form clips?"

Then route:

| Operator asks for | Route |
|---|---|
| "write a VSL for this offer", "sales video for my about page", "landing page video", "embedded pitch script" | `/mb-site` |
| "turn this offer into a video ad script", "paid sales video", "long-form video ad", "hook variants" | `/mb-ads` |
| "analyze this VSL", "extract the pitch", "mine objections", "codify the mechanism" | `/mb-think` |
| "make short clips from this sales video", "repurpose this VSL", "creator-style cuts" | `/mb-organic` |

Default ambiguous "write a VSL" requests to `/mb-site` because operators
usually mean an owned conversion surface. If paid traffic is explicit, use
`/mb-ads`. If an existing script or transcript is being inspected, use
`/mb-think`. If the output is excerpts, use `/mb-organic`.

## Framework References

Do not load long-form framework files unless the routed workflow needs them.
When it does, use the shared conversion references:

- Skool / membership:
  `.claude/reference/conversion/vsl/skool-18-section.md`
- B2B high-ticket:
  `.claude/reference/conversion/vsl/b2b-haynes.md`
- B2B example:
  `.claude/reference/conversion/vsl/examples/b2b-ijanitorial.md`

## Fact And Save Rules

- Verify every claim against offer, audience, proof, typicality, and live
  surface references.
- Do not invent statistics, credentials, testimonials, prices, guarantees,
  client counts, or outcome claims.
- If durable files are written, use checkpoint-first behavior:
  `mb checkpoint --plan --json`, then
  `mb checkpoint --validate "..." --json`, then after operator approval
  `mb checkpoint --message "..." --yes`.
- Use beginner-safe language: "saved checkpoint," not raw git ceremony.

## Recovery From Compaction

If the operator returns with the `/mb-vsl` compatibility router, rebuild state
from `mb status --json --peek`, recent `pushes/`, `research/`, and explicit
operator context. Ask the surface question again if the previous route is
unclear.
