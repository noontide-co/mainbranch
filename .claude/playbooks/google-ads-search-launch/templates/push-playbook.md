---
type: playbook
status: draft
push: ../push.md
platform: google-ads
provider: google-ads
provider_boundary: plan-only
playbook:
  recipe: google-ads-search-launch
  author: Noontide
  source: .claude/playbooks/google-ads-search-launch/SKILL.md
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
- Research files:

## Playbook Defaults And Forks

- Reusable playbook:
  `.claude/playbooks/google-ads-search-launch/SKILL.md`
- Conversion path:
  - [ ] Call/booking
  - [ ] Stripe/deposit
  - [ ] Lead form
  - [ ] Trial/signup
  - [ ] Other:
- Geography shape:
  - [ ] Single city / radius
  - [ ] Multi-city service area
  - [ ] Statewide
  - [ ] National
  - [ ] Multi-location
- Defaults used:
  - [ ] Search only
  - [ ] Exact/phrase first
  - [ ] AI Max off
  - [ ] Final URL Expansion off
  - [ ] Search Partners off
  - [ ] Explicit final URL
  - [ ] Manual provider launch
- Forks from playbook defaults:
  - Default:
  - Fork:
  - Rationale:
  - Approved by:

## Offer And Policy Fit

-

## Existing Account/Campaign Decision

-

## Readiness

- Lander:
- Conversion endpoint:
- Sitelink destinations:
- Measurement readiness:
- Provider readiness:

## Budget And Review Window

- Budget cap:
- Review window:
- Expected click range:
- Extension/widening rule:

## Lander And Sitelinks

-

## Measurement Checklist

- GA4 data stream:
- GTM container:
- GTM snippet installed:
- GTM Preview verified:
- Lander success event:
- GA4 key event:
- Ads imported primary conversion:

## Market Intent Research

- Buyer/search-intent clusters:
- Competitor/alternative offers:
- Customer language:
- Objections:
- Proof claims safe to use:
- Claims to avoid:
- Bad-fit intent to exclude:

## Core Updates From Research

- Research files created or used:
- Core files read:
- Core files updated:
- Proposed core updates not yet applied:
  - Target file:
  - Proposed change:
  - Evidence:
  - Approval status:
- Decisions needed:

## Campaign Structure

- Goal:
- Type:
- Ad groups:
- Structure rationale:

## Campaign Settings And Forks

- Bidding:
- Networks:
- Geography:
- Presence / interest setting:
- Language:
- Devices:
- Schedule:
- AI Max:
- Final URL Expansion:
- Search Partners:
- Display Network:
- URL options:
- Settings rationale:
- Forks from playbook defaults:
  - Default:
  - Fork:
  - Rationale:
  - Approved by:

## Keyword Targets

-

## Negative Strategy

- Consumer service intent:
- Component/equipment terms:
- Hiring/career:
- Warranty/regulatory:
- DIY/education:
- Trust-research terms:

## RSA Assets

- Final URL:
- Display path:
- Headlines:
  - Text:
    Rationale:
    Pin:
- Descriptions:
  - Text:
    Rationale:
- Character-limit check:
- Policy/claim check:

## Sitelinks

- Repeat one block per sitelink.

- Sitelink:
  Text:
  Description 1:
  Description 2:
  Final URL:
  Job:
  Destination audit:

## Callouts

- Repeat one block per callout.

- Callout:
  Text:
  Rationale:
  Claim source:

## Structured Snippets

- Repeat one block per structured snippet header.

- Structured snippet:
  Header:
  Values:
  Rationale:

## Skipped Assets And URL Options

- Logo/business name:
- Image assets:
- Location assets:
- Call assets:
- Lead form assets:
- Price/promotion assets:
- Tracking template:
- Final URL suffix:
- Custom parameters:
- Skipped assets and rationale:

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
- [ ] Sitelink destinations audited
- [ ] Callout claims verified
- [ ] Structured snippet values supported by the offer/lander
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
- [ ] Playbook forks reviewed
- [ ] Skipped assets reviewed
- [ ] Billing and budget reviewed
- [ ] GA4 to Ads link reviewed
- [ ] Primary conversion import reviewed
- [ ] Network, geo, AI Max, and Final URL Expansion reviewed
- [ ] Launch/unpause approved

## Review Loop

- Continue/change/stop:
- Outcome/log link:
