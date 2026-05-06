# Minisite Iteration

Load this after the first build is live or when the operator asks for changes to an existing minisite.

## Targeted Edits

For targeted edits, edit files in the site repo directly and push:

```bash
cd <site_repo>
git status
git diff --stat
git add -A
git commit -m "[update] <short description>"
git push
```

Cloudflare auto-deploys.

## Regeneration

For broader regeneration, such as a new brief or a new concept direction, re-run `/mb-site`. It walks the same flow and detects existing state in the project repo.

Before regenerating, check:

- whether the active offer changed;
- whether `core/audience.md` or offer-specific audience context changed;
- whether `core/voice.md`, `core/proof/`, or `core/content-strategy.md` changed;
- whether the existing `.mainbranch/conversion.json` still points to the right endpoint.

## Graduation Signal

When the offer pulls more traffic and the minisite needs more pages or content depth, that is the graduation signal.

Load [`graduation.md`](graduation.md) for paths from minisite to website or website with CMS.

Common signals:

- paid funnel converts and needs deeper proof or content;
- the operator needs more than one conversion endpoint;
- the site is growing beyond 4-6 pages;
- non-developers need to edit content without git.

Do not graduate to fix weak offer/message fit. If the minisite is not converting, first revisit the offer, audience language, proof, or page copy.
