# Minisite Setup

Load this for step 5 of the minisite flow: infrastructure provisioning.

This step does not change the brief. It creates or repairs the empty deploy target and links the site repo back to the business repo.

## 5a. Name And Project Repo

Ask the operator:

- Site name, such as `thelastbill`. This becomes the Cloudflare Pages project name.
- Project repo location. Default to a sibling repo the operator can inspect, such as `~/Documents/GitHub/<name>`.
- Apex domain. If they do not have one, route to [`naming-heuristic.md`](naming-heuristic.md).

Use an empty repo. Do not merge a template into the minisite shape.

## 5b. Prerequisites

Hard-gate Cloudflare-dependent setup before tool dispatch:

```bash
mb connect doctor --json
```

If `provider:cloudflare` is not `ready`, stop and offer three choices:

- **connect now:** `printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=... && mb connect test cloudflare`
- **continue read-only:** domain availability, naming, brief, and research only; no buy, DNS, Pages, custom-domain, or deploy calls.
- **skip for now:** record the Cloudflare blocker in the push/site notes and stage a follow-up.

Prefer Cloudflare account-scoped tokens for multi-business operators. User API
tokens remain supported as a fallback by omitting `token_type=account`.

After `mb connect` reports Cloudflare ready, `verify_live.py` can be used as a
deeper manual smoke for Cloudflare scopes, zone lookup, and domain-check CLI.

## 5c. Domain: Existing Or New

Ask:

- Already own the domain? Skip to DNS ensure with the domain name.
- Need to buy? Run an availability check first:

```bash
python3 .claude/skills/mb-site/scripts/domain.py check <name> --tlds .com,.co,.io
```

Main Branch cannot buy domains through `domain.py` yet. If the operator needs a
new domain, route them to https://dash.cloudflare.com/registrar after the
availability check, then resume once they confirm they own the full domain.

## 5d. DNS Ensure

Once the domain is owned:

```bash
python3 .claude/skills/mb-site/scripts/dns.py ensure <domain> --registrar cloudflare --skip-propagation-poll
```

## 5e. GitHub Repo And Placeholder Push

```bash
gh repo create <owner>/<name> --public --add-readme
git clone https://github.com/<owner>/<name>.git ~/Documents/GitHub/<name>
cd ~/Documents/GitHub/<name>
```

Create the placeholder with normal file-edit tooling, then:

```bash
git add -A
git commit -m "[add] placeholder"
git push
```

## 5f. Cloudflare Pages Project

```bash
python3 .claude/skills/mb-site/scripts/pages.py create-project <name> --repo-owner <owner> --repo-name <repo> --branch main
```

If you hit `github_app_not_installed`, the envelope's `suggestion` field walks through the dashboard handshake step. See [`cloudflare-pages-link.md`](cloudflare-pages-link.md).

## 5g. Custom Domain Attach

```bash
python3 .claude/skills/mb-site/scripts/pages.py set-domain <name> <domain> --timeout-seconds 300
```

Expect roughly 3-4 minutes. This path was live-tested end-to-end in PR #97.

## 5h. Link Records

Prefer repo-local links over global config.

Write `<site_repo>/.mainbranch/source.json`:

```json
{
  "business_repo": "/absolute/path/to/my-business",
  "offer_path": "core/offers/flagship/offer.md",
  "campaign_path": "pushes/2026-05-06-paid-minisite/push.md",
  "safe_to_share": true
}
```

The business repo should keep the reverse site record in the relevant `pushes/` record or offer note: site repo path or URL, domain, Cloudflare project, environment, measurement state, launch status, and the next manual approval step. The `campaign_path` key is a historical compatibility name; point it at the current push record.

Treat `~/.mainbranch/sites.json` as legacy fallback only when no repo-local link exists. If needed, write or extend:

```json
{
  "name": "<name>",
  "site_repo": "/absolute/path/to/repo",
  "business_repo": "/absolute/path/to/business-repo",
  "shape": "minisite",
  "hosting": "cloudflare",
  "domain": "<full apex>"
}
```

After setup, move to [`minisite-conversion.md`](minisite-conversion.md).
