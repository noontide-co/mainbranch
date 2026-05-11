# Data-source registry

Main Branch's first registry shape for structured business data. A
data-source record is a small markdown file with frontmatter that points at
the structured files Main Branch trusts for repeatable numbers and at the
human-readable report(s) that explain what the numbers mean.

This page is the contract for the **first record type** in the registry —
`type: data_source`. The registry as a concept (a small markdown record
with provider/owner/privacy frontmatter, linked from decisions and
outcomes) may grow sibling record types later, such as `provider_config`,
`secret_handle`, or `integration_account`. The `storage`, `useful_queries`,
and SQL-flavored guidance on this page is **specific to data-source
records**, not every future registry record.

[docs/business-connections.md](business-connections.md) is the wider
authoring matrix for choosing typed links, inline links, entity tags,
data/report references, GitHub history, and nearby context.

## Where this fits

A data-source record is portable. The shape is `markdown frontmatter +
structured files in the same folder`, so it travels with the Git history
wherever the repo lives — local-only, personal GitHub, a free GitHub org,
or a self-hosted Git server. The registry does not depend on a hosted
service to be meaningful.

The schema itself is a **mechanical check**: a deterministic rule that can
run in three places without changing shape.

| Surface | Job |
| --- | --- |
| `mb validate` locally | Fast feedback while the operator or agent is editing the record. |
| CI / pre-merge automation | Same `scripts/check.sh` rule can gate merges on a collaborative repo. |
| Agents (Claude Code, Codex) | Read the validation output and explain mechanical fixes vs operator judgment. |

Business-judgment checks like "this data source is stale" or "this
decision changed a key data source without explaining why" are deliberately
not part of this slice. They are warnings or review prompts for a later
follow-up.

## What is a data-source record

A data-source record lives at:

```text
data/<provider>/source.md
```

For example: `data/google-ads/source.md`, `data/stripe/source.md`,
`data/email/source.md`, `data/crm/source.md`.

Each provider gets one folder. The folder is where the structured files for
that provider live (`daily.sqlite`, `snapshots/*.csv`), and `source.md` is
the readable handle that decisions, pushes, playbooks, outcomes, and reports
can point at.

## Why a registry

Markdown decisions, pushes, and outcomes already talk about Google Ads,
Stripe, email, CRM, and analytics. Without a deterministic record, every
mention is a fresh guess about where the numbers live, what they mean, who
owns them, and how fresh they are. `data/<provider>/source.md` is the small
durable record that makes those mentions inspectable.

The registry does not invent a data warehouse. It is the readable index
over portable structured files Main Branch can keep in the business repo:

| Data shape | Use it for |
| --- | --- |
| SQLite (`storage.primary`) | The default for ongoing local queryable data: ads, email, Stripe, CRM, analytics. |
| CSV (`storage.snapshots`) | Simple snapshots, one-time exports, audit-friendly daily cuts. |
| Markdown reports (`reports:`) | What the numbers mean and what to do next. |
| Provider-side dashboards | External; not the source of truth for Main Branch graphs. |

Obsidian or other viewers can browse `source.md` and the reports. They are
not the data store.

## Frontmatter shape

```yaml
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
```

### Required

| Field | Shape | Notes |
| --- | --- | --- |
| `type` | string | Must equal `data_source`. |
| `provider` | string | Lowercase id (`[a-z0-9][a-z0-9_-]*`). Should match the parent folder name. |
| `owner` | string | The function or person accountable for this data (`growth`, `finance`, `ops`). |
| `privacy` | enum | One of `public`, `team_private`, `restricted`, `local_only`. |

### Advisory

| Field | Shape | Notes |
| --- | --- | --- |
| `cadence` | enum | One of `realtime`, `hourly`, `daily`, `weekly`, `monthly`, `quarterly`, `ad_hoc`, `manual`. Warning, not error, if not recognized. |
| `freshness` | date | `YYYY-MM-DD`. Validation will reject other shapes. |
| `storage.primary` | path string | Usually a relative path to a SQLite file. |
| `storage.snapshots` | list of strings | CSV snapshots or other portable cuts. |
| `reports` | list of strings | Human-readable reports that explain the numbers. |
| `useful_queries` | list of mappings | Each entry needs a non-empty `name` and `query`; `notes` is optional. |
| `tags` | list | Entity tags such as `channel/google-ads`, `metric/spend`. |

### Forbidden

- API keys, refresh tokens, bearer tokens, client secrets, passwords,
  session cookies, private keys.
- Raw customer rows, PII, or platform account identifiers that should not
  be visible to the repo audience.
- Local absolute paths and machine-specific scratch directories.

`mb validate` rejects records whose frontmatter contains keys or values
that match common credential patterns.

### Privacy vs mutation/blast-radius

`privacy` describes visibility: who can read the rows or the report. It
does **not** describe what happens when somebody changes a provider
setting. A future `provider_config` record (for example, GitHub org base
permission, repo-creation policy, or team membership) may need separate
fields such as `mutation_risk` and `approval_required` to describe the
blast radius of a change. That work is not part of this slice and is not
modeled by `data_source` records.

### Query typing for the future

`useful_queries[].query` is opaque text today. Data-source records mostly
have SQL queries against a local SQLite, so SQL is the practical default
in examples. Future record types may carry other query kinds (`gh_api`,
`stripe_cli`, `url`, `note`). When that need lands, add an explicit
`useful_queries[].kind` field. Keep the field opaque rather than
hardcoding a SQL-only assumption.

## How records connect to the business

Decisions, pushes, playbooks, outcomes, bets, research, and reports can
point at a data-source record through the typed frontmatter relationship
`linked_data_sources`:

```yaml
---
date: 2026-05-11
status: accepted
linked_data_sources:
  - data/google-ads/source.md
---
```

`mb validate --cross-refs` checks that the target exists. `mb graph` emits
a `linked_data_sources` edge so the relationship shows up in the business
graph and in `mb status` proximity views.

When the relationship is one sentence in a decision or outcome rather than a
durable typed relationship, link the report inline instead:

```markdown
The [Google Ads weekly report](../reports/2026-05-10-google-ads-weekly.md)
showed spend was capped by search volume.
```

`mb suggest links <file>` ranks both options as
`link_report_or_data_metadata`. When the candidate is a registry record, the
suggestion carries `field: linked_data_sources` so agents know the typed
field is available.

If the registry later grows sibling record types, the link fields should
follow the same naming pattern (for example `linked_provider_configs`,
`linked_integration_accounts`, or a more generic `linked_records`). That
naming question is open and intentionally not decided in this slice — pick
it the first time a sibling record type ships.

## What this version does not do

This version is the metadata contract. It deliberately does not:

- Schedule provider data sync (`MAIN-315`).
- Run provider mutations or Google Ads automation (`MAIN-229`).
- Add a `mb doctor` stale-record check. That check needs the contract to
  exist first and will land as a follow-up.
- Scaffold a `data/` directory into new business repos through `mb onboard`.
  A copy-safe stub lives at `mb/mb/_data/stubs/data-source.md`; future
  onboarding can copy it on request.

## Examples

Fixture records used by the test suite:

- `mb/tests/fixtures/data/google-ads/source.md` — daily ads spend.
- `mb/tests/fixtures/data/stripe/source.md` — daily revenue and payouts.

Both records keep raw account IDs, refresh tokens, and PII out of the
repo. They are safe to read as public examples.
