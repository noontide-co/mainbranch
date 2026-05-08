---
name: google-ads-search-launch
tier: playbook
calls: [start, think, site, ads, end]
status: draft
description: "Reusable Noontide draft playbook for validating an offer with a tightly scoped Google Ads Search launch, a paid-traffic lander, explicit approval gates, and a capped review window."
---

# google-ads-search-launch

This is a reusable draft operating playbook, not a one-off ad checklist. Use it
with manual operator judgment when the operator wants to test whether a real
offer can turn paid search intent into leads, calls, bookings, deposits, trials,
or another concrete business outcome.

It is usable today as a manual recipe and run-record template. It is not a
single executable orchestrator, does not automate Google Ads/GTM, and is still
collecting evidence from operator runs.

The playbook's job is to turn one offer into one paid-search proof run:

1. define the bet and success criteria;
2. prepare or verify the lander and conversion path;
3. build a tightly scoped Google Ads Search plan;
4. preserve manual approval gates before spend or provider mutation;
5. record the run as a push playbook with review evidence and an outcome hook.

It does not publish campaigns, change budgets, upload conversions, publish GTM,
or mutate provider accounts. Those steps stay manual or provider-native until a
future accepted adapter ships with approval gates and smoke evidence.

## Playbook Versus Run

This file is the reusable Noontide recipe: an opinionated paid-search
offer-validation sprint. The run belongs in the business repo:

```text
pushes/<push>/playbooks/google-ads-launch-plan.md
```

Create or update that run file from
[`templates/push-playbook.md`](templates/push-playbook.md). The run file is the
approval record, provider-boundary record, launch checklist, review-window
record, and outcome hook for a specific offer/push.

This playbook follows the authority model in [`docs/playbooks.md`](../../../docs/playbooks.md):
official Google Ads docs are the source of truth for platform facts, Main
Branch owns the provider boundary and run-record shape, and this file owns the
Noontide defaults for testing many offers quickly with tight control. If the
operator forks a default, record the fork and reason in the run file.

## Playbook Defaults And Fork Points

Use [`references/noontide-approach.md`](references/noontide-approach.md) as the
style and decision rubric.
For B2B local-services lead-form campaigns, also use
[`references/b2b-local-services-field-notes.md`](references/b2b-local-services-field-notes.md).

Defaults:

- one offer, one primary conversion, one review window;
- one conversion path chosen up front: call/booking, Stripe/deposit, lead form,
  trial, or another concrete action;
- Maximize Conversions for the first launch window when the selected primary
  conversion is verified; use Maximize Clicks or manual CPC only as a written
  fork when conversion tracking is absent or intentionally delayed;
- exact and phrase match first; broad match only with a written reason;
- geography is explicit: local radius, multi-city service area, statewide,
  national, or multi-location; do not reuse local defaults for national tests;
- campaign settings, negatives, sitelinks, callouts, structured snippets, and
  skipped assets are part of the plan, not afterthoughts;
- market-intent research precedes asset writing when the offer is new, the
  audience/search language is thin, or the geography is unfamiliar;
- a small proof budget is only useful when CPC, conversion rate, and business
  value make the result interpretable;
- account history is useful when it exists, but a new offer can start from
  offer/customer/keyword reasoning and lander readiness;
- Search Partners, Display Network, AI Max, Final URL Expansion, broad match,
  price assets, lead forms, call assets, and automated URL options default to
  off or skipped for first proof runs unless the operator records why this run
  should fork;
- no spend before the operator approves the lander, conversion action, consent
  posture, billing, budget, campaign structure, copy/assets, asset
  destinations, and review criteria;
- post-launch judgment is `continue`, `change`, or `stop`, written as an
  outcome or push review.

## Required Inputs

- active offer and audience;
- explicit bet or success criterion for the proof run;
- launch push, or permission to create one;
- lander or site repo, if one exists;
- budget cap, review window, geography shape, and business value of the
  conversion;
- conversion path: call/booking, Stripe/deposit, lead form, trial, or other;
- market-intent research, competitor/offer positioning, customer language,
  objections, proof, and exclusion notes when available;
- provider readiness from `mb status --json --peek` and `mb connect plan`;
- measurement readiness from `mb site check` when a site repo exists;
- sanitized account history or read-only provider facts only when already
  approved and available.

If no Google Ads account history exists for this offer, say so and continue.
Do not invent prior winners or require pre-offer account scraping.

## Flow

1. **Start and scope.** Use `/mb-start` facts. Identify the offer, push, bet,
   current repo health, provider readiness, and whether this is a new offer or
   a rescue of an existing campaign.
2. **Bet and KPI.** Use `/mb-think` when the success criterion is vague. Press
   for what would make the spend a win, a useful loss, or an inconclusive test.
3. **Lander and conversion.** Use `/mb-site` and `mb site check` before calling
   the campaign launchable. Missing measurement can still allow copy drafting,
   but not spend approval.
4. **Market-intent pass.** If the offer is new, thin, or entering a new
   geography, use `/mb-think` to research buyer/search intent, competitor
   offers, customer language, objections, proof, and bad-fit exclusions before
   writing assets. When 2+ lanes are needed, run them as parallel foreground
   research agents and persist findings to `research/`. If the findings change
   durable offer, audience, market, proof, or positioning truth, update the
   relevant `core/` files after operator approval or record proposed core
   updates in the run file.
5. **Campaign plan.** Use `/mb-ads launch-plan` and load the Google Ads campaign
   plan reference. Generate the full reviewable spec: campaign settings,
   bidding, geography mode, ad groups, keywords, negatives, RSA headlines and
   descriptions, display paths, sitelinks, callouts, structured snippets,
   skipped assets, budget, manual provider steps, and approval gates.
6. **B2B local-services pass.** When the offer is B2B local services, check the
   field notes for GA4/GTM/Ads import order, Search-only defaults, geo
   presence, Search Partners, Final URL Expansion, AI Max, negative categories,
   UI gotchas, and volume calibration.
7. **Run record.** Write or update the push playbook run from the template.
   Record defaults used, forks taken, asset rationale, and skipped asset
   rationale. Record research files and any core updates made or proposed. Keep
   provider refs safe and do not store raw account exports.
8. **Manual launch.** The operator performs Google Ads/GTM/billing/spend steps
   manually unless a future adapter is accepted.
9. **Review.** Use `/mb-ads check` after the review window. Write the result to
   the run record and link an outcome/log file.
10. **Checkpoint.** Use `/mb-end` or `mb checkpoint` to save accepted artifacts.

## Current Checks

Run these when applicable:

```bash
mb status --json --peek
mb connect plan
mb connect doctor --json
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
mb validate
```

These checks help the agent stay grounded. They do not prove terminal Google Ads
campaign creation is supported.

## Future Surface

The playbook should eventually enable deeper checks when those surfaces exist:

- Google Ads read adapter or sidecar for campaigns, search terms, spend, and
  conversions;
- daily paid-search metrics cache tied to bets/pushes;
- deterministic playbook checks for Search Partners, Final URL Expansion,
  AI Max, primary conversion presence, and provider review gates;
- playbook health in `mb status`;
- provider-specific repair commands;
- dashboard view that hides technical plumbing by default but can expose issues,
  branches, PRs, provider refs, and evidence for technical operators.

Until then, keep the run useful: clear inputs, clear approvals, clean manual
steps, and a concrete review decision.
