---
type: data_source
provider: example-provider
owner: growth
privacy: team_private
cadence: daily
freshness: YYYY-MM-DD
storage:
  primary: data/example-provider/daily.sqlite
  snapshots:
    - data/example-provider/snapshots/YYYY-MM-DD.csv
reports:
  - reports/YYYY-MM-DD-example-provider-weekly.md
useful_queries:
  - name: example_query
    query: SELECT 1;
    notes: Replace with a real query that an agent can re-run.
tags:
  - channel/example-provider
---

# Example provider — data source

This is the starter shape for a `data/<provider>/source.md` record. Copy it
into a real provider folder (`data/google-ads/source.md`,
`data/stripe/source.md`, `data/crm/source.md`) and edit the frontmatter.

## What this record is

- The readable handle for one provider's local data.
- A pointer to the structured files Main Branch trusts for repeatable
  numbers (SQLite for ongoing local data, CSV for snapshots).
- A pointer to the report(s) that explain what the numbers mean.

## What this record is not

- A place to store secrets, API tokens, refresh tokens, or raw account IDs.
- A place to copy customer-identifying rows.
- A replacement for the structured file. The numbers live in
  `storage.primary` and `storage.snapshots`; markdown stays the meaning.

## How agents should use this record

- Reference it from decisions, pushes, playbooks, and outcomes via
  `linked_data_sources` when the relationship is durable, or link the
  weekly report inline when the sentence is about meaning.
- Re-run the documented `useful_queries` instead of inventing new SQL when
  a comparable answer already exists.
