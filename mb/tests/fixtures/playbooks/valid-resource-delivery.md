---
type: playbook
status: draft
push: ../push.md
platform: instagram
provider: manual
provider_boundary: plan-only
trigger:
  kind: comment_keyword
  keyword: TEMPLATE
resource:
  kind: url
  value: https://example.com/resource
copy:
  public_cta: Comment TEMPLATE for the resource.
  reply: Thanks. The resource is linked in the post.
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
  notes: Fixture is a plan only and performs no provider mutation.
linked_outcomes: []
---
# Resource Delivery Playbook

This sanitized fixture demonstrates the v1 push playbook frontmatter shape.
