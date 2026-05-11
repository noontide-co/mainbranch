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
create or select the site repo, and record push/site state.

The business repo keeps durable truth: offer, audience, voice, research,
briefs, push records, measurement state, launch status, and manual approval
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

The site repo should include the role-neutral `.mainbranch/repo.json` child
descriptor:

```json
{
  "schema": "mb.child_repo.v0",
  "role": "site",
  "display_name": "Flagship site",
  "github_owner": "example-co",
  "repo_name": "flagship-site",
  "safe_purpose": "Public site for the flagship offer.",
  "parent": {
    "display_name": "Example Business",
    "github_owner": "example-co",
    "repo_name": "example",
    "remote": "github:example-co/example",
    "local_checkout": "../example"
  },
  "linked": {
    "offers": ["core/offers/flagship/offer.md"],
    "pushes": ["pushes/2026-05-06-paid-minisite/push.md"]
  },
  "return_to_hub_command": "cd ../example && claude",
  "safe_to_share": true
}
```

Do not commit absolute local paths in the descriptor. `parent.local_checkout`
is optional and must be a relative checkout hint. If the descriptor only has
GitHub owner/repo handles, run `mb site check . --business-repo <hub-checkout>
--json` when local offer metadata is needed.

Existing site repos may still have `.mainbranch/source.json`:

```json
{
  "business_repo": "/absolute/path/to/my-business",
  "offer_path": "core/offers/flagship/offer.md",
  "campaign_path": "pushes/2026-05-06-paid-minisite/push.md",
  "safe_to_share": true
}
```

Treat `source.json` as a compatibility file. The `campaign_path` key may point
at a current `pushes/<slug>/push.md` record.

The site repo also stores `.mainbranch/conversion.json` for the conversion
endpoint and local measurement plan. `mb site check` reads these files and can
infer the business repo from `repo.json` or legacy `source.json` when a local
checkout hint exists and `--business-repo` is omitted.

## Reverse Link

The business repo should keep a reverse site record in `pushes/<YYYY-MM-DD-slug>/`
(current) or the relevant offer note. Legacy repos may still have the
record under `campaigns/<slug>/`; `mb` reads both. The reverse record can
include:

- site repo path or GitHub URL;
- deployed URL and domain;
- Cloudflare project and environment;
- offer path and push path (the JSON key may still be `campaign_path` for
  compatibility);
- measurement state from `mb site check`;
- launch status and next manual approval step.

Keep secrets, tokens, raw provider exports, customer rows, and private browser
traces out of both repos.
