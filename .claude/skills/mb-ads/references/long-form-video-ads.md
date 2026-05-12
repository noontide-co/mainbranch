# Long-Form Video Ads

Use this when the operator asks to turn an offer into a video ad script, paid
sales video, long-form conversion video creative, B2B video ad, VSL-style paid
creative, hook variants, or test angles for paid traffic.

## Route

`/mb-ads` owns paid video scripts, variants, compliance review, launch-plan
readiness, and provider-safe creative notes. If the operator asks for a sales
video that will live on a page, route to `/mb-site`. If they ask to analyze an
existing VSL or extract the pitch, route to `/mb-think`. If they ask for short
clips from a long script, route to `/mb-organic`.

## Shared References

Load `.claude/reference/conversion/vsl-routing.md` first. Load a long-form
framework only when the paid creative needs sales-video structure:

- Skool / membership: `.claude/reference/conversion/vsl/skool-18-section.md`
- B2B high-ticket: `.claude/reference/conversion/vsl/b2b-haynes.md`
- B2B example: `.claude/reference/conversion/vsl/examples/b2b-ijanitorial.md`

## Paid Rules

- Keep provider mutation manual unless shipped `mb` provider rails prove a
  supported path and the operator approves.
- Treat long-form frameworks as source structure, then adapt to paid context:
  hook testing, qualification, proof, objections, CTA, and compliance.
- State or imply only claims supported by offer, proof, typicality, and current
  surface references.
- Run the normal `/mb-ads` review and checkpoint pipeline for saved output.
