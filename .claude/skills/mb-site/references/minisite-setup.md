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

Confirm credentials are in place:

```bash
source ~/.config/vip/env.sh
python3 .claude/skills/mb-site/scripts/verify_live.py
```

Expect Cloudflare scopes, zone lookup, and domain-check CLI to pass. If anything is red, route to:

```bash
bash .claude/skills/mb-site/scripts/setup_creds.sh
```

Then re-run `verify_live.py`.

## 5c. Domain: Existing Or New

Ask:

- Already own the domain? Skip to DNS ensure with the domain name.
- Need to buy? Run an availability check first:

```bash
python3 .claude/skills/mb-site/scripts/domain.py check <name> --tlds .com,.co,.io
```

For API-supported TLDs and after explicit operator approval on price, proceed:

```bash
python3 .claude/skills/mb-site/scripts/domain.py buy <name>
```

For dashboard-only TLDs, fall back to https://dash.cloudflare.com/registrar.

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
  "campaign_path": "campaigns/2026-05-paid-minisite.md",
  "safe_to_share": true
}
```

The business repo should keep the reverse site record in `campaigns/` or the relevant offer/campaign note: site repo path or URL, domain, Cloudflare project, environment, measurement state, launch status, and the next manual approval step.

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
