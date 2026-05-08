---
type: educational
topic: provider-readiness
status: draft
last-updated: 2026-05-04
---

# Provider readiness: connect tools when the business job needs them

Main Branch does not ask you to connect every account on day one. Setup should
answer a business question:

1. What are you trying to do next?
2. Which outside account is needed for that job?
3. Does `mb` say that account is ready, missing, or optional?
4. What exact command fixes the next missing step?

Run this from your business repo:

```bash
mb connect plan
```

For machine-readable status, use:

```bash
mb status --json --peek
mb connect doctor --json
```

## The default order

1. **GitHub** - durable work threads, proposals, reviews, and shipped history.
   - Check: `mb connect doctor --json`
   - Common fix: `gh auth login`
   - You can start local setup without it, but shared work-thread and proposal loops are limited.

2. **Cloudflare** - sites, DNS, Pages, and future Workers.
   - Check: `mb connect doctor --json`
   - Preferred setup for multi-business operators: `printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=...`
   - User API tokens remain supported as a fallback: omit `token_type=account` to use Cloudflare's user-token verify path.
   - Connect it when you are ready to publish or attach a domain.

3. **Google / Workspace** - Drive, Docs, Sheets, Slides, and workspace source material.
   - Check: `mb connect doctor --json`
   - Common setup: `mb connect google --from-env`
   - Connect it when a workflow needs existing Google files. Do not connect it just because you have a Google account.

4. **Meta Ads** - ad accounts, campaigns, pixels, and future performance context through the official Meta Ads CLI once Main Branch wiring is verified.
   - Check: `mb connect doctor --json`
   - Common setup: planned for `meta-ads` / `meta`; do not run `mb connect meta` until this provider is wired.
   - Connect it when paid-ad work needs account facts and `mb` reports the CLI path ready.

5. **Apify** - research sidecar for scraping, YouTube, Instagram, and web mining.
   - Check: `mb connect doctor --json`
   - Common setup: `printf '%s' "$APIFY_TOKEN" | mb connect apify --token-stdin`
   - Connect it when research or organic workflows need structured external data.

## Readiness states

- `not_connected` means no repo-safe provider metadata exists yet.
- `planned` means the provider is a supported direction, but this `mb` release
  does not yet wire a safe setup, detection, or validation path.
- `missing_secret` means metadata exists but the local secret is missing.
- `unvalidated` means a credential is stored, but it has not been tested.
- `invalid` means validation failed and the credential should be replaced.
- `ready` means the safest available check passed.

Secrets stay outside the business repo. `.mb/connect.yaml` stores only safe
metadata, labels, secret references, and last-check facts, and is gitignored by
default. Do not paste tokens into markdown files, GitHub issues, screenshots,
or committed config.

## Why this is business onboarding

Providers are not developer config. They are permissions for business actions:
publishing a site, reading source documents, learning from ads, or collecting
research. Connect the rail when the next business action needs it, then let
`mb status` and `mb connect` explain what is ready.
