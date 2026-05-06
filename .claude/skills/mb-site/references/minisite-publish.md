# Minisite Publish

Load this for raw publish, pre-publish review, and final push.

## Publish Raw Concept

The picked home page is the rawest working version. Commit and push immediately:

```bash
cd <site_repo>
git add -A
git commit -m "[add] picked home concept - <slug>"
git push
```

Cloudflare auto-deploys when the project is git-connected. The site is now live with one page. The rest follows through [`minisite-buildout.md`](minisite-buildout.md).

## Pre-Publish Review

Run [`review.md`](review.md) gates in parallel against the full site copy:

- in-voice;
- de-AI'd;
- framework-true;
- research-grounded only when core business files changed since brief lock;
- operator-defined gates from `<business_repo>/core/operations/review/*.md`, when present.

Synthesize findings and surface them to the operator. They address or proceed.

## Publish Updates

```bash
cd <site_repo>
git add -A
git commit -m "[add] minisite build-out - <slug>"
git push
```

Cloudflare auto-deploys. Verify `https://<domain>/` returns 200 and shows the new pages.

## Launch Readiness

If the site is for paid traffic, Google Ads, GTM, conversion tracking, retargeting, or launch readiness, load [`site-measurement.md`](site-measurement.md). Do not recommend launch from prose alone.

## Exit

For targeted edits, regeneration, and graduation signals, load [`minisite-iterate.md`](minisite-iterate.md).
