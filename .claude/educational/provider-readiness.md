---
type: educational
topic: provider-readiness
status: draft
last-updated: 2026-05-12
---

# Provider readiness: connect outside tools only when the job needs them

Providers are outside accounts Main Branch can use for business work: GitHub,
Cloudflare, Google/Workspace, ads platforms, research sidecars, booking tools,
payments, social scheduling, bookkeeping, and future adapters.

You do not need to connect everything during first setup.

## The beginner version

Ask four questions:

1. What am I trying to do next?
2. Which outside account is needed for that job?
3. Does `mb` say that account is ready, missing, planned, or optional?
4. What exact command fixes the next missing step?

Run this from your business repo:

```bash
mb connect plan
```

For machine-readable status, agents and power users can use:

```bash
mb status --json --peek
mb connect doctor --json
```

## The default order

1. **GitHub** - tasks, blockers, proposals, reviews, and shipped history.
   - Common fix: `gh auth login`
   - You can start locally without it, but shared work threads and proposals
     are limited.

2. **Cloudflare** - sites, DNS, Pages, and future Workers.
   - Connect it when you are ready to publish, deploy, or attach a domain.
   - Learn more: `mb educational cloudflare-pages`

3. **Google / Workspace** - source material in Drive, Docs, Sheets, and Slides.
   - Connect it when a workflow needs existing Google files.
   - Do not connect it just because you have a Google account.

4. **Meta Ads / Google Ads** - account facts, campaign references, pixels, and
   future performance context where official paths are verified.
   - Meta Ads uses Meta's official `meta-ads` package and `meta` CLI. Main
     Branch can explain setup requirements now, but live account checks stay
     unavailable until `mb` owns detection and read-only smoke.
   - Connect only when paid work needs account facts and Main Branch reports the
     path ready.

5. **Apify and similar sidecars** - research, scraping, YouTube, Instagram, and
   web mining.
   - Connect when research or organic workflows need structured external data.

6. **Specialized rails** - Cal.com, Stripe, hledger, Forgejo, Postiz, and
   other tools.
   - These are chosen for a specific business job, not as a day-one checklist.

## Readiness states

- `not_connected` means no repo-safe provider metadata exists yet.
- `planned` means the provider is a supported direction, but this release does
  not yet wire a safe setup, detection, or validation path.
- `readiness` means the official provider path and setup requirements are known,
  but `mb` does not yet validate the account or use live provider data.
- `missing_secret` means metadata exists but the local secret is missing.
- `unvalidated` means a credential is stored, but it has not been tested.
- `invalid` means validation failed and the credential should be replaced.
- `ready` means the safest available check passed.

Secrets stay outside the business repo. `.mb/connect.yaml` stores only safe
metadata, labels, secret references, and last-check facts, and is gitignored by
default. Do not paste tokens into markdown files, GitHub issues, screenshots,
or committed config.

## Why this is business onboarding

Connected accounts are permissions for business actions:

- publish a site;
- read source documents;
- learn from ads;
- collect research;
- take a payment;
- book a call;
- keep operating summaries current.

Main Branch should teach this while setup happens. Numbered choices,
readiness checks, and exact next commands beat a long essay and a pile of
manual account setup.

## Meta Ads readiness

Meta Ads is at `readiness` support. The official path is the Meta Ads CLI:

```bash
pipx install meta-ads
meta --version
meta auth status
```

The CLI binary is `meta`; the package is `meta-ads`. It uses Meta Marketing API
credentials from `ACCESS_TOKEN`, `AD_ACCOUNT_ID`, and optional `BUSINESS_ID`.
Meta's setup docs describe a Meta developer app, Business Manager access, a
system user token, and scopes including `business_management`, `ads_management`,
`pages_show_list`, `pages_read_engagement`, `pages_manage_ads`,
`catalog_management`, and `read_insights`.

Practical read-only commands available through the official CLI include:

```bash
meta ads adaccount list
meta ads campaign list
meta ads adset list
meta ads ad list
meta ads creative list
meta ads insights get --fields spend,impressions,clicks,ctr,cpc
meta ads dataset list
```

Main Branch should make this easy before promoting support:

1. detect `meta` and `meta --version`;
2. run `meta auth status` without printing tokens;
3. verify a read-only account/campaign/insights smoke;
4. report safe readiness facts through `mb connect status`, `mb connect doctor`,
   and `mb status --json --peek`;
5. keep raw exports, tokens, and account-private IDs out of tracked files.

Write-capable CLI commands exist for campaigns, ad sets, ads, creatives,
datasets, and catalogs. They remain out of scope for Main Branch until approval
gates and mutation smoke exist.

## What Main Branch does not claim

Main Branch does not claim all providers are fully automated. Trust the current
CLI status, compatibility docs, and provider-specific smoke evidence. If a
provider is marked planned or readiness, treat it as direction, not shipped live
account support.
