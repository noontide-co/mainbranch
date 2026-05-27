---
type: playbook
status: draft
push: ../push.md
platform: google-ads
provider: google-ads
provider_boundary: plan-only
playbook:
  recipe: google-ads-search-launch
  source: playbooks/google-ads-search-launch/playbook.md
trigger:
  kind: operator_launch_request
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

- Reusable playbook: `playbooks/google-ads-search-launch/playbook.md`
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

## Readiness

- Lander:
- Conversion endpoint:
- Measurement readiness:
- Provider readiness:

## Budget And Review Window

- Budget cap:
- Review window:
- Expected click range:
- Continue/change/stop threshold:

## Campaign Structure

- Goal:
- Type:
- Ad groups:
- Keywords:
- Negatives:
- RSA assets:
- Sitelinks:
- Callouts:
- Structured snippets:
- Skipped assets and rationale:

## Manual Provider Steps

- GA4/GTM checks:
- Google Ads conversion action:
- Billing and account owner:
- Campaign publish:
- Budget/spend approval:
- Post-launch review date:

## Review Outcome

- Decision: continue / change / stop / inconclusive
- Evidence:
- Outcome/log link:
- Follow-up:
