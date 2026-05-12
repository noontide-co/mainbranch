# Sales Video Repurposing

Use this when the operator asks to make short clips from a sales video, turn a
VSL into reels, cut an about-page video into creator-style posts, extract short
hooks, or repurpose a pitch script for organic distribution.

## Route

`/mb-organic` owns excerpts, short-form scripts, carousel adaptations, and
creator-style cuts from an existing sales video, transcript, or pitch script.
It does not own the long-form sales-video framework by default.

Hand off instead when:

- the operator wants to write the page/about/lander video from scratch:
  `/mb-site`;
- the operator wants paid video creative or variants: `/mb-ads`;
- the operator wants teardown, objection mining, or pitch codification:
  `/mb-think`.

## Shared References

Load `.claude/reference/conversion/vsl-routing.md` when routing is unclear.
Load the long-form frameworks only when clip selection depends on the original
sales-video structure:

- Skool / membership: `.claude/reference/conversion/vsl/skool-18-section.md`
- B2B high-ticket: `.claude/reference/conversion/vsl/b2b-haynes.md`

## Repurposing Rules

- Start from the source script/transcript, not from memory.
- Preserve claim accuracy and typicality context when shortening.
- Prefer one idea per clip: hook, objection, proof moment, mechanism, CTA, or
  identity shift.
- Save outputs through the normal organic output path and checkpoint-first
  behavior after approved durable writes.
