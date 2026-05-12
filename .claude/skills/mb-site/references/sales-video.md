# Sales Video For Pages

Use this when the operator asks to write a VSL, sales video, about-page video,
landing-page video, lander video, embedded pitch script, or page conversion
video for an owned surface.

## Route

`/mb-site` owns sales video scripts that sit on a site, sales page, about page,
minisite, lander, checkout-adjacent page, or Skool/about surface. Default
ambiguous "write a VSL for this offer" requests here unless the operator says
paid ad, teardown, or repurposing.

Hand off instead when:

- analysis, objection mining, pitch extraction, or codification is the task:
  `/mb-think`;
- paid long-form video ad creative or hook variants are the task: `/mb-ads`;
- clips, excerpts, or creator-style cuts are the task: `/mb-organic`.

## Shared References

Load `.claude/reference/conversion/vsl-routing.md` first. Load the specific
long-form framework only when the task needs structured sales-video sections:

- Skool / membership: `.claude/reference/conversion/vsl/skool-18-section.md`
- B2B high-ticket: `.claude/reference/conversion/vsl/b2b-haynes.md`
- B2B example: `.claude/reference/conversion/vsl/examples/b2b-ijanitorial.md`

## Page Rules

- Resolve offer context through `references/site-context.md`.
- Read live page, Skool, pricing, or funnel surface copy when present.
- Keep claims congruent with the visible page and next step.
- If the page promises less than the video script, fix the script or ask before
  updating the page.
- Save durable business-side notes under the current push/site record or offer
  context; site code and page assets stay in the linked site repo.
- Use checkpoint-first behavior after approved durable writes.
