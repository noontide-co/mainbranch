---
type: playbook
status: draft
push: ../push.md
platform: google-ads
provider: google-ads
provider_boundary: plan-only
trigger:
  kind: operator_launch_request
resource:
  kind: document
  value: docs/google-ads-gtm-conversion-rubric.md
copy:
  public_cta:
  reply:
approval:
  required: true
  status: needed
  approved_by:
  approved_at:
state:
  provider_refs: []
  activated_at:
  retired_at:
validation:
  dry_run: not-run
  smoke_evidence: []
  notes: Plan only; no Google Ads or GTM mutation has been performed.
linked_outcomes: []
---
# Google Ads Search Launch

## Bet And Success Criteria

-

## Source Facts

- `mb status --json --peek`:
- `mb connect plan` / `mb connect doctor --json`:
- `mb site check`:
- Account history source:

## Offer And Policy Fit

-

## Lander And Conversion Readiness

-

## Measurement Chain

- GA4 data stream:
- GTM container:
- GTM snippet installed:
- GTM Preview verified:
- Lander success event:
- GA4 key event:
- Ads imported primary conversion:

## Campaign Structure

- Goal:
- Type:
- Bidding:
- Networks:
- Geo:
- AI Max:
- Final URL Expansion:
- Ad groups:

## Keyword Targets

-

## Negative Strategy

- Consumer service intent:
- Component/equipment terms:
- Hiring/career:
- Warranty/regulatory:
- DIY/education:
- Trust-research terms:

## Ads And Assets

- RSA:
- Pinned headline:
- Descriptions under 90 chars:
- Logo:
- Display path:

## UI Review Gotchas

- [ ] Form-submit tracking uses an explicit success event when auto-detection is unreliable
- [ ] GTM Preview shows the conversion tag firing on the expected event
- [ ] GA4 Realtime or key-event registration confirms the event name
- [ ] Ads imported conversion is selected as primary, even if inactive before traffic
- [ ] Headlines entered one per row or via bulk-add
- [ ] Ad URL options cleared if publish errors appear
- [ ] Search Partners still off
- [ ] Final URL Expansion still off
- [ ] AI Max still off
- [ ] Dependent headline fragments avoided or pinned
- [ ] Surface-specific logo set
- [ ] Ad approval state checked before diagnosing zero impressions

## Manual Provider Steps

-

## Approval Gates

- [ ] Lander and sitelinks reviewed
- [ ] Conversion action reviewed
- [ ] Consent/privacy posture reviewed
- [ ] Campaign structure reviewed
- [ ] Keywords and negatives reviewed
- [ ] Ad copy/assets reviewed
- [ ] Billing and budget reviewed
- [ ] GA4 to Ads link reviewed
- [ ] Primary conversion import reviewed
- [ ] Network, geo, AI Max, and Final URL Expansion reviewed
- [ ] Launch/unpause approved

## Budget And Review Window

- Budget cap:
- Review window:
- Expected click range:
- Extension/widening rule:

## Review Decision

- Continue/change/stop:
- Outcome/log link:
