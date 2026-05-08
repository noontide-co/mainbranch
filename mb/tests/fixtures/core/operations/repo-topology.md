---
type: repo_topology
status: active
schema: mb.repo_topology.v0
home: github:example-co/example
business_display_name: "Example Business"
repos:
  - slug: example
    display_name: "Example Business"
    role: business
    lifecycle: active
    github_owner: example-co
    repo_name: example
    remote: github:example-co/example
    visibility: team_private
    relationship: hub_for
    purpose: Company-level strategy, decisions, bets, pushes, and logs.
  - slug: workshop-site
    display_name: "Workshop site"
    role: site
    lifecycle: active
    relationship: execution_vehicle_for
    parent: example
    github_owner: example-co
    repo_name: workshop-site
    remote: github:example-co/workshop-site
    visibility: public
    domain: workshop.example.com
    linked_offers:
      - core/offers/workshop/offer.md
    linked_pushes:
      - pushes/2026-05-06-resource-delivery/push.md
    linked_playbook_runs:
      - pushes/2026-05-06-resource-delivery/playbooks/valid-resource-delivery.md
  - slug: finance
    display_name: "Finance source"
    role: finance
    lifecycle: active
    visibility: restricted
    relationship: reports_to
    parent: example
    purpose: Private bookkeeping source; hub stores approved summaries only.
---
# Repo Topology

Sanitized topology fixture for validating hub, site, finance, and push
playbook run-record boundaries.
