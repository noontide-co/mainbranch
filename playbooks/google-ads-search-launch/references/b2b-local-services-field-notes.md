# B2B Local Services Field Notes

Use this reference when the Google Ads Search launch is for a B2B
local-services offer with a lead-form conversion and tight geography. These are
public-safe field notes; keep raw ad copy, keyword lists, negative lists,
screenshots, and account identifiers out of public examples.

## Measurement Chain

Recommended setup order:

1. GA4: confirm or add the lander as a data stream.
2. GTM: use a container for the lander surface.
3. Install the GTM snippet on the lander and ship the lander.
4. GTM: add GA4 configuration plus conversion-relevant events.
5. GA4: mark conversion-relevant events as key events.
6. Link GA4 to Google Ads with admin access in both products.
7. Google Ads: import the GA4 key event as a conversion and mark one primary.

The primary conversion should exist before campaign publish. Otherwise
Maximize Conversions launches without a primary conversion to optimize against.

## Campaign Defaults

- Goal: Leads.
- Campaign type: Search.
- Bidding: Maximize Conversions only after the primary conversion is verified.
- Networks: Google Search only. Search Partners off. Display Network off.
- Geography: primary city plus practical radius; use presence-only targeting.
- AI Max: off for tightly scoped B2B proof.
- Final URL Expansion: off.
- Keywords: phrase and exact mirrors at launch. Broad requires a written reason.
- RSAs: at least one per ad group.
- Headline pinning: pin only the claim that must always show.
- Logo and display path: set explicitly so unrelated account-level assets do
  not bleed into the proof run.

Re-check Search Partners, Final URL Expansion, and AI Max at review/publish.
They can silently return in some UI flows.

## Negative Categories

For B2B local-services campaigns, block consumer and bad-fit intent before
launch. Start with categories, then adapt to the niche:

- consumer service intent: repair, service, install, replacement, fix,
  "near me", broken, leaking, noisy;
- component or equipment terms that draw DIY or consumer searches;
- hiring and career intent: salary, jobs, hiring, careers, apprentice,
  training, school, license, certification;
- warranty, rebate, tax credit, and regulatory-shopping terms;
- DIY or education terms: diy, how to, free, cheap, manual;
- trust-research terms that indicate non-lead intent: reviews, complaints,
  lawsuit.

## Manual Gates

Keep these human-approved:

- GTM workspace publish;
- GA4 to Google Ads link;
- conversion import and primary conversion selection in Ads;
- campaign publish;
- budget changes after launch;
- audience, geography, network, AI Max, or URL-expansion changes after launch.
