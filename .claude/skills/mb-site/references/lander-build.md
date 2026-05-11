# Lander Build Flow

The lander shape is one static page for one offer and one launch push. It is
for focused paid-traffic, retargeting, or direct-response tests where extra
navigation would weaken the decision.

Use the minisite shape when the offer needs multiple proof/process/FAQ pages.

## Start

1. Resolve the business repo and active offer using the normal `/mb-site`
   rules.
2. Run `mb status --json --peek` and use readiness, relationship health,
   legacy `campaigns/` drift, provider facts, and ranked actions before
   continuing.
3. Create or select the launch push:

```yaml
---
type: push
slug: YYYY-MM-DD-slug
kind: launch
status: planned
health: unknown
goal: { metric: "", target: "", by: YYYY-MM-DD }
owner: ""
audience: ""
offer: core/offers/<offer>/offer.md
promise: ""
channels: [site]
---
```

4. If keyword-gate research exists, load it. If paid traffic is intended and no
   keyword gate exists, route back to `/mb-think` keyword-gate mode before
   building.

## Setup

Use [site-repo-workflow.md](site-repo-workflow.md) for business-repo vs site-repo
mode. The business repo stores the push and site records; the site repo stores
the HTML/CSS/SVG files.

Before domain, DNS, Pages, or deploy work:

```bash
mb connect doctor --json
```

If Cloudflare is not ready, offer connect-now, read-only planning, or stop and
record the blocker.

## Build

Load [lander-generation-system.md](lander-generation-system.md). Generate in
Claude Code or a foreground subagent; do not call a model from a Python atom.

Inputs:

- active offer and audience;
- keyword-gate file, if present;
- voice, proof, testimonials, visual style, and named enemies;
- selected push path;
- conversion endpoint or hosted form/checkout/booking link;
- optional reference URLs for taste only.

Output in the site repo:

```text
index.html
_headers
og.svg
favicon.svg
README.md
```

Render `og.png` from `og.svg` when the render tool is available. Keep both files
in the site repo when rendered.

## Paid-Traffic Check

When paid traffic, Google Ads, GTM, conversion tracking, or "ready to launch" is
in scope, load [site-measurement.md](site-measurement.md) and run:

```bash
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
```

Report the exact readiness state. `ready` still means local checks passed, not
permission to mutate ad accounts or spend money.

## Publish

Publishing is an explicit operator action. Before push/deploy:

- show the changed files;
- run any available static/site checks;
- list provider or measurement blockers;
- ask for approval;
- after approval, checkpoint the business repo and commit/push the site repo
  through the existing site workflow.

## Graduation

If the lander gets traffic but needs more proof, process detail, or SEO surface,
recommend graduating to minisite. See [graduation.md](graduation.md).
