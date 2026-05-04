# Site Repo Workflow

`/mb-site` has two modes.

## Business Repo Mode

Start here when planning or creating a site:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-site
```

Use this mode to read business context, pick the offer, draft the site brief,
create or select the site repo, and record campaign/site state.

The business repo keeps durable truth: offer, audience, voice, research,
briefs, campaign records, measurement state, launch status, and manual approval
notes.

## Site Repo Mode

Switch here once a site repo exists:

```bash
cd ~/Documents/GitHub/my-offer-site
claude
/mb-site
```

Use this mode to edit site code, review pages, preview, deploy, and run
readiness checks while reading linked business context.

When `/mb-site` creates or selects a site repo, it should also link Main Branch
skills into that repo so Claude can discover `/mb-site` there:

```bash
mb skill link --repo ~/Documents/GitHub/my-offer-site
```

The site repo must include `.mainbranch/source.json`:

```json
{
  "business_repo": "/absolute/path/to/my-business",
  "offer_path": "core/offers/flagship/offer.md",
  "campaign_path": "campaigns/2026-05-paid-minisite.md",
  "safe_to_share": true
}
```

The site repo also stores `.mainbranch/conversion.json` for the conversion
endpoint and local measurement plan. `mb site check` reads these files and can
infer the business repo from `source.json` when `--business-repo` is omitted.

## Reverse Link

The business repo should keep a reverse site record in `campaigns/` or the
relevant offer/campaign note:

- site repo path or GitHub URL;
- deployed URL and domain;
- Cloudflare project and environment;
- offer path and campaign path;
- measurement state from `mb site check`;
- launch status and next manual approval step.

Keep secrets, tokens, raw provider exports, customer rows, and private browser
traces out of both repos.
