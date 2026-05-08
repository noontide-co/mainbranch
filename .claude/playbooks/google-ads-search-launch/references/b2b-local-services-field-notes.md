# B2B Local Services Field Notes

Use this reference when the Google Ads Search launch is for a B2B local-services
offer with a lead-form conversion and tight geography. These notes capture
public-safe operator field learnings. Keep raw ad copy, keyword lists, negative
lists, screenshots, and account identifiers out of public examples.

## Measurement Chain

Recommended setup order:

1. GA4: confirm or add the lander as a data stream.
2. GTM: use a container for the lander surface.
3. Install the GTM snippet on the lander and ship the lander.
4. GTM: add GA4 configuration plus the conversion-relevant events, such as
   `form_submit` and optional `booked_call`.
5. GA4: mark conversion-relevant events as key events.
6. Link GA4 to Google Ads with admin access in both products.
7. Google Ads: import the GA4 key event as a conversion and mark one primary.

The primary conversion should exist before campaign publish. Otherwise
Maximize Conversions launches without a primary conversion to optimize against.

## Measurement Gotchas

Validate the measurement chain before treating a campaign as launchable:

- Enhanced measurement may see form starts but miss real form submits when the
  lander prevents the default submit event, sends an async request, or redirects
  after success. Prefer an explicit success event pushed after validation
  passes.
- Separate the lander event name from the GA4 event name when useful. For
  example, the lander can push a success-specific dataLayer event that GTM maps
  into a cleaner GA4 `form_submit` event.
- Use GTM Preview mode before publishing. A one-character mismatch between the
  lander event and the GTM custom-event trigger can leave the tag in "not
  fired" state while the rest of the setup looks correct.
- GA4 Realtime can show an event before the Admin events table is ready. If the
  UI allows it, register the key event by exact name instead of waiting for the
  table to populate.
- Google Ads import paths vary by account UI. If the normal new-conversion flow
  does not show the expected GA4 import tile, check the linked GA4 data source,
  app-and-web metrics import setting, and the conversion data-source editor.

## Campaign Config Defaults

For a first validation run:

- Goal: Leads.
- Campaign type: Search.
- Bidding: Maximize Conversions until enough conversion volume exists for a
  target CPA decision.
- Networks: Google Search only. Search Partners off. Display Network off.
- Geography: primary city plus tight practical radius. Use presence-only
  targeting, not presence-or-interest.
- Languages: English unless the offer has a reason to do otherwise.
- Devices and schedule: all at launch unless the operator has evidence.
- AI Max: off at campaign and ad-group levels for tightly scoped B2B proof.
- Final URL Expansion: off.
- Keywords: phrase and exact mirrors at launch. Broad requires a written reason.
- Structure: one ad group is acceptable for the first signal.
- RSAs: at least one per ad group.
- Headline pinning: pin only the claim that must always show; write all other
  headlines as standalone claims.
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

Phrase match is usually enough for category blocks. Use exact match when a
shorter phrase is ambiguous.

## UI Gotchas

Check these before diagnosing strategy:

- Bulk headline paste can land all headlines in one row and trigger a "headline
  too long" blocker. Add one headline per row or use the UI's bulk-add path.
- "Could not find the entity" at publish can come from stale URL options:
  mobile URL, tracking template, final URL suffix, or custom parameters. Open
  that panel and clear all four.
- A conversion can be imported but still show inactive until real traffic
  produces events. Do not confuse inactive status before traffic with a broken
  campaign when GTM Preview and GA4 Realtime already proved the event chain.
- Search Partners and Final URL Expansion can re-enable after edits. Verify at
  final review.
- Description copy has a 90-character hard cap. Count before paste.
- Dependent headline fragments can render alone if not pinned. Prefer
  standalone headline claims.
- Missing surface-specific logo can cause account-level fallback assets from a
  prior brand.
- Under-review ads can take time. Do not troubleshoot zero impressions until
  the ad itself is approved.

## Volume Calibration

For a tight B2B local-services geography, low absolute volume can be normal.
Set expectations before launch:

- small validation budgets may only produce dozens of clicks in the first
  review window;
- form-fill conversion rates can be low on cold high-ticket traffic;
- zero form fills in the first short window does not automatically disprove the
  offer.

Pre-commit the next move:

- extend the review window at the same daily budget;
- widen geography only if the business can serve that area;
- change keywords, negatives, copy, or lander when click quality is poor;
- stop when the bet is clearly disproven or no longer worth learning from.

## Manual Gates

Keep these human-approved:

- GTM workspace publish;
- GA4 to Google Ads link;
- conversion import and primary conversion selection in Ads;
- campaign publish;
- budget changes after launch;
- audience, geography, network, AI Max, or URL-expansion changes after launch.
