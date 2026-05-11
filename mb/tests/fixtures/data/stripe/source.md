---
type: data_source
provider: stripe
owner: finance
privacy: team_private
cadence: daily
freshness: 2026-05-10
storage:
  primary: data/stripe/payouts.sqlite
  snapshots:
    - data/stripe/snapshots/2026-05-10-payouts.csv
reports:
  - reports/2026-05-10-stripe-weekly.md
useful_queries:
  - name: gross_revenue_last_7_days
    query: >-
      SELECT date, SUM(amount_cents) / 100.0 AS gross
      FROM charges
      WHERE date >= date('now', '-7 day')
      GROUP BY date
      ORDER BY date;
    notes: Daily gross revenue trend; pair with the weekly report.
tags:
  - channel/stripe
  - metric/revenue
---

# Stripe — data source

This record describes the local Stripe payments data Main Branch trusts
when markdown decisions, pushes, or outcomes reference revenue, refunds,
or payouts. The numbers live in `storage.primary`; the weekly report
explains what they mean.

## What is here

- A local SQLite of charges, refunds, and payouts derived from the official
  Stripe export.
- Snapshot CSVs for human inspection.
- A weekly report under `reports:` that summarizes trend and notable moves.

## What is not here

- API keys, webhook secrets, or customer PII. Those stay in environment or
  keychain, never in this file.
- Per-customer rows beyond what the public-safe weekly report needs.

## How agents should use this record

- Reference this file from decisions and outcomes that turn on revenue,
  not the raw SQLite or per-row CSVs.
- Use `linked_data_sources` for typed links, or link the weekly report when
  the sentence is about meaning.
