# Sales Video And VSL Routing

VSL is conversion knowledge, not a durable Main Branch primitive. Route the
operator by the surface they are trying to improve.

## Natural Prompt Routing

| Prompt shape | Route |
|---|---|
| "Analyze this VSL", "extract the pitch", "mine objections", "codify the mechanism" | `/mb-think` |
| "Write a VSL for this offer", "sales video for my page", "about page video", "lander video", "embedded pitch script" | `/mb-site` |
| "Turn this offer into a video ad script", "paid sales video", "long-form video ad", "hook variants" | `/mb-ads` |
| "Make short clips from this sales video", "repurpose this VSL", "creator-style cuts" | `/mb-organic` |

Default ambiguous "write a VSL" requests to `/mb-site` because they usually
mean an owned conversion surface. If the operator says paid traffic, route to
`/mb-ads`. If they provide an existing script to inspect, route to `/mb-think`.
If they want excerpts or short-form distribution, route to `/mb-organic`.

## Framework References

Load these only when the task needs long-form sales video structure:

- Skool / membership: `.claude/reference/conversion/vsl/skool-18-section.md`
- B2B high-ticket: `.claude/reference/conversion/vsl/b2b-haynes.md`
- B2B example: `.claude/reference/conversion/vsl/examples/b2b-ijanitorial.md`

## Context Rules

- Resolve offer context through current `core/` and `core/offers/` paths.
- Treat `.vip/local.yaml` as legacy audit input only; never use it as the
  active-offer source of truth.
- Verify every claim against offer, audience, proof, typicality, and live
  surface references. Do not invent stats, testimonials, pricing, guarantees,
  client counts, or outcome claims.
- If the output becomes durable work, run `mb checkpoint --plan --json`,
  validate the proposed message with `mb checkpoint --validate "..." --json`,
  and save only after operator approval with
  `mb checkpoint --message "..." --yes`.
