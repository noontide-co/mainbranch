# Google Ads Campaign Plan Workflow

Load this when the operator asks for a Google Ads campaign plan, campaign
rescue, search launch, paid-traffic launch, or launch check. This workflow
turns business context and account facts into a reviewable plan. It does not
publish campaigns, change budgets, upload conversions, publish GTM, or mutate
provider accounts.

## Route

Use this route:

1. `/mb-think` when the offer, audience, policy fit, keywords, competitor terms,
   or lander argument needs research before campaign work.
2. `/mb-site` when the landing page, conversion endpoint, GTM/dataLayer events,
   consent posture, sitelinks, or measurement readiness is missing.
3. `/mb-ads launch-plan` when the operator needs campaign structure, keywords,
   negatives, ad assets, budget, manual provider steps, and approvals.
4. `/mb-ads check` when the operator asks whether to continue, change, or stop
   after a review window.

If the work is repeatable or has approval state, write a plan-only playbook at
`pushes/<push>/playbooks/google-ads-launch-plan.md` with `type: playbook`.
When the operator wants the reusable Noontide paid-search recipe, use the
`google-ads-search-launch` playbook under `.claude/playbooks/`; that playbook
instantiates the push playbook run record and calls this skill for campaign
planning.
For B2B local-services lead-form launches, load that playbook's field notes for
GA4/GTM/Ads import order, Search-only defaults, UI gotchas, negative categories,
and volume calibration.

## Required Inputs

Read or ask for:

- active offer, audience, promise, proof, and current lander;
- launch push at `pushes/<push>/push.md`;
- provider readiness from `mb status --json --peek` and `mb connect doctor --json`;
- site readiness from `mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json`
  when a site repo exists;
- Google Ads account state if the operator provides a sanitized export or an
  explicitly approved read-only provider tool is already available;
- historical winners: search terms, keywords, CPC/CPA, conversions, landing
  pages, and disapproval or policy history;
- existing negative keyword lists and campaign-level exclusions;
- budget cap, review window, geographic scope, and launch objective;
- regulated-category risks such as healthcare, finance, credit, employment,
  housing, legal, politics/social issues, alcohol, supplements, or claims that
  need proof.

Do not ask the operator to paste OAuth tokens, API keys, customer records,
raw account exports with PII, conversion uploads, or screenshots that expose
private account details. Ask for sanitized exports or manual answers instead.

## Prerequisite Setup And CLI Boundary

Before planning from live account facts, identify which access path actually
exists:

1. Run `mb status --json --peek` and `mb connect plan` from the business repo.
2. If a site repo exists, run `mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json`.
3. Treat `mb connect` as the Main Branch readiness and repair surface, not as
   proof that Google Ads campaign creation is supported from the terminal.
4. Treat the current Google/Workspace connection as a docs/sheets/drive bridge
   unless this release's `mb connect list` or `mb connect doctor --json`
   explicitly reports a Google Ads provider adapter.
5. Use live Google Ads reads only when an approved runtime tool, MCP server,
   sidecar, or future `mb` adapter is already configured and the operator
   approves read-only account inspection for this business.
6. Use Google Ads UI/manual provider steps for account creation, billing,
   OAuth consent, customer selection, campaign creation, launch/unpause, and
   budget changes unless a shipped adapter with smoke evidence says otherwise.

For a first-time or new-offer setup, prerequisite facts are:

- Google account or manager account that owns the business relationship;
- Google Ads customer selected for this business/offer boundary;
- billing and spend owner confirmed in Google Ads;
- Google Ads conversion action or GA4-imported conversion chosen for the
  launch goal;
- GTM or gtag instrumentation plan verified through `/mb-site`;
- consent/privacy posture and policy pages reviewed;
- account history either unavailable, intentionally ignored, or read through
  a sanctioned source.

If `mb connect` reports Google Ads as missing, planned, unsupported, or absent
from the provider list, do not block copy/plan work. Continue in plan-only mode
using repo facts, `mb site check`, sanitized exports, and manual Google Ads UI
steps.

## Decision Sequence

### 1. Offer And Policy Fit

Confirm the offer can be advertised as stated. For regulated categories, read
provider policy before writing copy. If the offer or lander triggers a
restricted classification, stop and present options:

- rewrite the offer/lander/copy into a policy-safe form;
- build a separate product or front door only if the operator accepts the
  business, legal, and brand boundary;
- pursue required certification or verification;
- pause paid traffic and route to organic, SEO, referrals, or another channel.

Do not frame policy work as "bypassing" a provider. Frame it as accurate
classification, clean claims, and operator-approved compliance.

### 2. Existing Campaign Versus New Campaign

Prefer an existing campaign when all are true:

- same offer or service line;
- same conversion event;
- same goal and budget structure;
- useful historical search/query/negative-list data exists;
- the problem is copy, lander, policy, or stale settings rather than a broken
  campaign structure.

Start a new campaign only when goal, product/service line, conversion event,
budget model, geography, or structural settings materially change.

When rescuing a campaign, pause bad or disapproved ads instead of immediately
deleting them. Add new clean assets inside the existing campaign or a new ad
group, keep the campaign paused until at least one new asset is approved, and
record the old asset status as audit context. After a clean review window, the
operator can delete stale assets manually.

### 3. Campaign Structure

Draft only the structure that fits the evidence. Common search structures:

- brand defense: brand, founder, product, and close variants;
- geo/local intent: service plus city/region terms;
- high-intent service: ready-to-buy terms and "near me" variants;
- competitor/alternative: only when policy-safe and not misleading;
- proof or education: only when the lander and measurement path support it.

Each ad group should have:

- exact/phrase keyword targets where intent matters;
- broad match only with a clear reason and tight negatives;
- one lander or sitelink set;
- policy-safe headlines/descriptions;
- explicit manual review notes.

### 4. Keywords And Negative Strategy

Use account history first when available. Keep:

- historical converters;
- search terms with acceptable economics;
- brand and geo-intent winners;
- exact/phrase terms aligned with the lander promise.

Exclude:

- DIY, free, job, school, research, entertainment, definition, unrelated
  locations, competitor terms that create policy risk, and impossible-fit
  searches;
- regulated terms that imply unsupported claims, prescription/order behavior,
  guarantees, discriminatory targeting, or sensitive personal attributes;
- any term the operator marks as a bad-fit lead.

If a shared negative list exists, tell the operator to attach it to the campaign
manually. Do not paste a large account-specific negative export into public
docs or committed examples.

### 5. Lander And Conversion Prerequisites

Before recommending launch:

- run `mb site check` when a site repo exists;
- verify GTM/dataLayer event names match
  `docs/google-ads-gtm-conversion-rubric.md`;
- confirm the primary conversion action matches the launch goal;
- audit every sitelink destination, not only the final URL;
- confirm consent/privacy posture and policy pages are acceptable;
- if conversion tracking has been dark or stale, require a manual test before
  trusting performance data.

Use the `mb site check` readiness state. Never invent `ready_for_launch`, and
never treat `ready` as permission to spend.

### 6. Budget And Review Window

Capture:

- daily/monthly budget cap;
- bid strategy for the first review window;
- launch geography and schedule;
- review date or spend threshold;
- continue/change/stop criteria;
- who approves spend.

If the account has stale conversion history, recommend conservative bidding
until recent conversion data exists. Do not switch to automated bidding because
it sounds sophisticated; tie it to evidence and volume.

### 7. Approval Gates

The plan must show separate approvals for:

- campaign structure and keywords;
- negative list;
- ad copy and assets;
- lander/sitelinks;
- conversion action and GTM/Tag Assistant evidence;
- consent/privacy posture;
- budget and billing;
- launch/unpause.

Main Branch may write the plan and checklist. The operator performs provider
actions unless a future adapter ships with approval gates and smoke evidence.

## Output Shape

For `pushes/<push>/ads.md` or the campaign-plan playbook body, include:

- `## Source Facts`
- `## Offer And Policy Fit`
- `## Existing Account/Campaign Decision`
- `## Readiness`
- `## Budget And Review Window`
- `## Campaign Structure`
- `## Keyword Targets`
- `## Negative Strategy`
- `## Ads And Assets`
- `## Lander And Sitelinks`
- `## Measurement Checklist`
- `## Manual Provider Steps`
- `## Approval Gates`
- `## Review Loop`

Keep real account IDs, screenshots, raw exports, customer data, and private
spend details out of public-safe committed examples.
