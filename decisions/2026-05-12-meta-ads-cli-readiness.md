---
date: 2026-05-12
status: accepted
tags: [providers, meta-ads, paid, connect, readiness]
---

# Meta Ads CLI Readiness

## Decision

Treat Meta Ads as a `readiness` provider in Main Branch.

The official path is Meta's `meta-ads` Python package and `meta` CLI. Main
Branch can describe the setup requirements and the read-only command surface,
but it should not claim `read_only`, `reporting`, or mutation support until
`mb` owns detection, auth-state reporting, and a sanitized read-only smoke.

## Evidence

Primary sources and local CLI inspection on 2026-05-12 show:

- PyPI package `meta-ads` 1.0.1 exists, requires Python 3.12+, is classified
  Alpha, and describes itself as a CLI for the Meta Marketing API.
- The installed binary is `meta`; `meta --version` returned `meta, version
  1.0.1`.
- `meta ads --help` exposes `adaccount`, `campaign`, `adset`, `ad`,
  `creative`, `dataset`, `insights`, `page`, catalog, and product commands.
- With no credentials, `meta auth status` exits 3 and reports that
  `ACCESS_TOKEN` is missing without printing a token.
- Meta setup docs describe `ACCESS_TOKEN`, `AD_ACCOUNT_ID`, optional
  `BUSINESS_ID`, a Meta developer app, system user token, and scopes including
  `business_management`, `ads_management`, `pages_show_list`,
  `pages_read_engagement`, `pages_manage_ads`, `catalog_management`, and
  `read_insights`.
- Meta command docs expose read paths for accounts, campaigns, ad sets, ads,
  creatives, insights, and datasets/pixels, alongside write-capable create,
  update, connect, assign, and delete commands.

Source links:

- https://pypi.org/project/meta-ads/
- https://developers.facebook.com/blog/post/2026/04/29/introducing-ads-cli/
- https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/get-started
- https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/command-reference

Private maintainer smoke from 2026-04-30 also proved the read path against a
real ad account and found the main write-path caveat: campaign and ad set
creation default to paused, but fresh creative creation can require a Live-mode
Meta app. That private smoke is useful product evidence, but it does not by
itself promote public Main Branch support because `mb` still lacks its own
detection and sanitized read-only smoke.

## Support Level

`readiness` means:

- `mb connect plan`, `mb connect status`, `mb connect doctor`, and
  `mb status --json --peek` can explain that the official path is known.
- Skills can tell users which CLI and credentials are required.
- Skills continue from reference files or manual Ads Manager notes when the
  provider is not ready.
- `mb connect meta` must not store token-like metadata or mark Meta connected.

Do not claim:

- `read_only` until `mb` verifies `meta`, `meta auth status`, account listing,
  campaign listing, and one insights query without writing private data.
- `reporting` until safe summarized performance import exists.
- `mutation_gated` until preview, approval, paused-by-default behavior, account
  authority, and safe-account mutation smoke are all documented.

## User Setup Shape

The easy path Main Branch should eventually offer:

```bash
pipx install meta-ads
meta --version
meta auth status
meta -o json ads campaign list
meta -o json ads insights get --fields spend,impressions,clicks,ctr,cpc
```

`mb` should wrap that into business-language readiness:

1. Is the official CLI installed?
2. Is auth configured without exposing token material?
3. Can the user choose or confirm an ad account?
4. Can a read-only campaign list and insights query run?
5. What exact next step fixes the first missing requirement?

Secrets stay outside repo files. Safe repo metadata may record provider ids,
setup state, and non-sensitive labels only after `mb` owns the path.

## Out Of Scope

- Third-party Meta connector fallbacks.
- Raw account exports in tracked repos.
- Tokens, account-private IDs, or customer data in markdown, GitHub issues, or
  committed config.
- Campaign, ad set, ad, creative, budget, pixel, catalog, or page mutation from
  Main Branch.
