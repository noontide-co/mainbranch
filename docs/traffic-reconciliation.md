# Traffic reconciliation: counting humans, not crawlers

Every paid-traffic business hits the inflated-visitor trap in its first
week of ads: the analytics dashboard says hundreds visited, the ad manager
says a handful clicked, and both are telling the truth about different
things. Proven on a real business we built — raw "visitors" overstated
real humans by an order of magnitude on day one of a fresh campaign.

This page is the recipe for an honest visitor number. Briefings, pulse
reports, and agents reporting traffic follow it; "visitors" without a
layer label is a bug in the report.

## The three layers

| Layer | What it counts | Honest use |
| --- | --- | --- |
| Edge / zone requests | Every HTTP request — bots, crawlers, scanners, humans | Infrastructure load. Never report as visitors. |
| Real-browser analytics (RUM) | Clients that executed JavaScript | Closer — but ad-platform review crawlers run real browsers too. |
| Ad-platform link clicks | A human clicked your ad | The anchor. The most honest human-intent count you have for paid traffic. |

## The crawler tell

When ads are fresh, in review, or recently edited, the ad platform hammers
the landing page with its **own** review and link-preview crawlers — and
those run real browsers, so they land in RUM too. The tell, on
Meta-family traffic specifically:

- referrer host is the platform itself (`m.facebook.com`,
  `www.facebook.com`),
- geography is a platform data-center region (Sweden/Luleå and
  Ireland/Clonee for Meta), not your market,
- volume spikes exactly when a campaign enters or re-enters review.

Other platforms have equivalent fingerprints; the shape — platform
referrer + data-center geography + review-window timing — generalizes.

## The recipe

1. **Anchor on ad-platform link clicks.** That number is a human with
   intent. Start every traffic statement from it.
2. **Pull RUM grouped by referrer host and country.** Platform-referred,
   DC-geography page loads are crawler load.
3. **Reconcile:** if platform-referred RUM loads greatly exceed the
   platform's own reported link clicks, the excess is crawlers — say so
   explicitly in the report, with both numbers.
4. **Never present edge/zone totals as visitors.** Use them only for
   infrastructure questions (cache hit rate, attack detection).
5. **Recheck after every campaign edit** — review crawlers return each
   time the platform re-reviews.

## Report language

- Right: "9 real ad clicks (platform-reported); RUM shows 240
  platform-referred loads, ~230 of which are review crawlers (DC
  geography). Honest human traffic: ~9."
- Wrong: "240 visitors today."
- A zero-leads day on tiny real-click volume is "too early," not
  "broken" — only flag a break when a mechanism fails, not when honest
  small numbers look small.

Related: [delivery-truth.md](delivery-truth.md) (the same
never-trust-the-aggregate discipline, applied to sends) and
[operating-principles.md](operating-principles.md) §11 (validate against
live state).
