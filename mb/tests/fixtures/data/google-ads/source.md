---
type: data_source
provider: google-ads
owner: growth
privacy: team_private
cadence: daily
freshness: 2026-05-10
storage:
  primary: data/google-ads/daily.sqlite
  snapshots:
    - data/google-ads/snapshots/2026-05-10.csv
reports:
  - reports/2026-05-10-google-ads-weekly.md
useful_queries:
  - name: weekly_spend_by_campaign
    query: >-
      SELECT campaign, SUM(cost_micros) / 1e6 AS spend
      FROM ads_daily
      WHERE date >= date('now', '-7 day')
      GROUP BY campaign
      ORDER BY spend DESC;
    notes: Top spenders for the past 7 days; pair with weekly report.
tags:
  - channel/google-ads
  - metric/spend
---

# Google Ads — data source

This record describes the local Google Ads data Main Branch trusts when
markdown decisions, pushes, playbooks, or outcomes reference Google Ads
numbers. The numbers themselves live in the structured files under
`storage.primary` and `storage.snapshots`. The weekly report explains what
the numbers mean.

## What is here

- `daily.sqlite` is the ongoing local table for spend, impressions, clicks,
  and conversions.
- Daily CSV snapshots are kept under `snapshots/` for quick inspection.
- The latest weekly report is linked under `reports:`.

## What is not here

- Raw account IDs, refresh tokens, or login credentials. Those live in the
  OS keychain or environment, never in this file.
- Customer-identifying information.

## How agents should use this record

- Treat this file (not the raw SQLite) as the readable handle.
- Prefer linking from decisions, pushes, and outcomes via
  `linked_data_sources` or to the weekly report directly.
- Re-run the documented `useful_queries` instead of inventing new SQL when a
  comparable answer already exists.
