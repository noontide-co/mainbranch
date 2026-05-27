---
name: google-ads-search-launch
title: Google Ads Search Launch
source_type: reusable_playbook
status: draft_manual
calls:
  - mb-start
  - mb-think
  - mb-site
  - mb-ads
  - mb-end
runtime_support:
  claude_code: manual_recipe
  codex_cli: blocked_by_provider_gates
provider_mutation: false
publishing_or_spend: false
approval_gates:
  - file_writes
  - checkpoint
  - provider_mutation
  - publishing_or_spend
  - customer_contact
  - private_data
  - account_change
  - upload_assets
  - budget_change
  - campaign_publish
  - conversion_upload
  - gtm_publish
---

# Google Ads Search Launch

This is the reusable draft source for validating whether paid search can turn
one concrete offer into leads, calls, bookings, deposits, trials, or another
business outcome. It is a manual recipe and run-record template, not an
executable orchestrator.

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

This source is the reusable recipe. The business run belongs in:

```text
pushes/<push>/playbooks/google-ads-launch-plan.md
```

Create or update that run file from
[`templates/push-playbook.md`](templates/push-playbook.md). The run file is the
approval record, provider-boundary record, launch checklist, review-window
record, and outcome hook for a specific offer or push.

Runtime shells may point at this source, but they must not turn it into hidden
authority. Official Google Ads docs are the source of truth for platform facts;
Main Branch owns the provider boundary and run-record shape; this playbook owns
the defaults for small controlled offer-validation runs.

## Defaults And Fork Points

Use [`references/noontide-approach.md`](references/noontide-approach.md) as the
style and decision rubric. For B2B local-services lead-form campaigns, also use
[`references/b2b-local-services-field-notes.md`](references/b2b-local-services-field-notes.md).

Defaults:

- one offer, one primary conversion, one review window;
- one conversion path chosen up front: call/booking, Stripe/deposit, lead form,
  trial, or another concrete action;
- Maximize Conversions only when the selected primary conversion is verified;
  use Maximize Clicks or manual CPC only as a written fork when conversion
  tracking is absent or intentionally delayed;
- exact and phrase match first; broad match only with a written reason;
- explicit geography: local radius, multi-city service area, statewide,
  national, or multi-location;
- campaign settings, negatives, sitelinks, callouts, structured snippets, and
  skipped assets are part of the plan;
- market-intent research precedes asset writing when the offer is new, the
  audience/search language is thin, or the geography is unfamiliar;
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
- provider readiness from `mb status --json --peek`, `mb connect plan`, and
  `mb connect doctor --json`;
- measurement readiness from `mb site check` when a site repo exists;
- sanitized account history or read-only provider facts only when already
  approved and available.

If no Google Ads account history exists for this offer, say so and continue.
Do not invent prior winners or require pre-offer account scraping.

## Flow

1. **Start and scope.** Use `mb-start` facts. Identify the offer, push, bet,
   current repo health, provider readiness, and whether this is a new offer or
   a rescue of an existing campaign.
2. **Bet and KPI.** Use `mb-think` when the success criterion is vague. Press
   for what would make the spend a win, a useful loss, or an inconclusive test.
3. **Lander and conversion.** Use `mb-site` and `mb site check` before calling
   the campaign locally ready for operator review. Missing measurement can
   still allow copy drafting, but not spend approval.
4. **Market-intent pass.** If the offer is new, thin, or entering a new
   geography, use `mb-think` to research buyer/search intent, competitor
   offers, customer language, objections, proof, and bad-fit exclusions before
   writing assets. Persist findings to `research/` when they become reusable.
5. **Campaign plan.** Use `mb-ads launch-plan` and the Google Ads campaign-plan
   reference. Generate the full reviewable spec: settings, bidding, geography,
   ad groups, keywords, negatives, RSA assets, sitelinks, callouts, structured
   snippets, skipped assets, budget, manual provider steps, and approval gates.
6. **B2B local-services pass.** When applicable, check the field notes for
   GA4/GTM/Ads import order, Search-only defaults, geo presence, Search
   Partners, Final URL Expansion, AI Max, negative categories, UI gotchas, and
   volume calibration.
7. **Run record.** Write or update the push playbook run from the template only
   after approval. Record defaults used, forks taken, asset rationale, skipped
   asset rationale, research files, and any core updates made or proposed.
8. **Manual launch.** The operator performs Google Ads/GTM/billing/spend steps
   manually unless a future adapter is accepted.
9. **Review.** Use `mb-ads check` after the review window. Write the result to
   the run record and link an outcome/log file after approval.
10. **Checkpoint.** Use `mb-end` or `mb checkpoint` to save accepted artifacts.

## Current Checks

Run these when applicable:

```bash
mb status --json --peek
mb connect plan
mb connect doctor --json
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
mb validate --cross-refs --json
```

These checks help the agent stay grounded. They do not prove terminal Google
Ads campaign creation is supported.

## Manual Gates

Keep these human-approved:

- Google Ads account selection, billing, and customer/account changes;
- GA4 to Google Ads link;
- conversion import and primary conversion selection in Ads;
- GTM workspace publish;
- asset uploads;
- campaign publish or unpause;
- budget changes after launch;
- audience, geography, network, AI Max, URL-expansion, or bidding changes;
- customer contact.

## Future Surface

The playbook should eventually enable deeper checks when those surfaces exist:

- Google Ads read adapter or sidecar for campaigns, search terms, spend, and
  conversions;
- daily paid-search metrics cache tied to bets/pushes;
- deterministic playbook checks for Search Partners, Final URL Expansion,
  AI Max, primary conversion presence, and provider review gates;
- playbook health in `mb status`;
- provider-specific repair commands;
- dashboard view that hides technical plumbing by default but can expose
  issues, branches, PRs, provider refs, and evidence for technical operators.

Until then, keep the run useful: clear inputs, clear approvals, clean manual
steps, and a concrete review decision.
