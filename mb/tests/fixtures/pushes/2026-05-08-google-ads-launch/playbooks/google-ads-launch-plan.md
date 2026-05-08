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
  public_cta: Prepare Google Ads materials for operator review.
  reply: Plan only; provider changes require explicit operator approval.
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
  notes: Fixture is a plan only and performs no Google Ads or GTM mutation.
linked_outcomes: []
---
# Google Ads Launch Plan Playbook

This sanitized fixture demonstrates a provider-safe Google Ads campaign plan.
It records approval state, readiness evidence, manual provider steps, and review
hooks without storing account IDs, customer data, screenshots, or secrets.

## Source Facts

- `mb status --json --peek` should be read before campaign planning.
- `mb connect plan` or `mb connect doctor --json` should identify provider
  readiness and repair commands.
- `mb site check <site> --business-repo <business> --json` should verify local
  paid-traffic measurement readiness when a site repo exists.
- Live Google Ads account reads require a separately approved runtime tool,
  sidecar, MCP server, or future `mb` adapter. This fixture does not prove
  terminal campaign creation.

## Manual Provider Steps

- Select the Google account or manager account that owns the business.
- Select the Google Ads customer for this offer boundary.
- Confirm billing, conversion actions, consent posture, and launch budget.
- Create, pause, unpause, or edit campaigns in Google Ads only after operator
  approval.
