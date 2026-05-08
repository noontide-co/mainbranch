# Noontide Google Ads Search Launch Approach

This playbook validates whether paid search can turn a concrete offer into a
business outcome. It is not a generic "set up Google Ads" tutorial.

The method is built for fast offer-validation sprints: quick brand, quick
offer, small proof budget, and a concrete conversion signal such as a call,
booking, Stripe/deposit payment, trial, or qualified lead. The goal is to learn
whether market intent will convert before the operator overbuilds the offer.

## What Makes The Playbook Noontide

- **Bet first.** Paid search is a proof run. The operator should know what would
  make the spend a win, useful loss, or inconclusive test.
- **Offer before account.** Account history helps, but the offer, audience,
  promise, proof, and lander decide what the campaign should try.
- **Conversion path before spend.** Traffic without measurement is just a bill.
- **Research feeds core.** Paid-search discovery should not die in the campaign
  plan. If research clarifies demand, buyer language, proof, objections,
  pricing, conversion path, or service boundaries, update `core/` after
  operator approval or record proposed core updates in the run file.
- **Market intent before assets.** Headlines, descriptions, sitelinks, callouts,
  structured snippets, and negatives come from researched demand, competitor
  gaps, customer language, objections, and proof.
- **Search intent over volume.** Start with high-intent terms the lander can
  honestly satisfy.
- **Negatives protect the bet.** Bad-fit queries are a strategy problem, not
  cleanup trivia.
- **Control before automation.** For the first proof run, prefer tight
  geography, exact/phrase targeting, explicit URLs, and manually reviewed copy
  over automated expansion. Fork only when the operator accepts the tradeoff.
- **One clean review window.** The first launch should answer a bounded
  question, not become a forever campaign by accident.
- **Manual provider authority.** Main Branch can prepare, check, and record the
  plan. The operator approves and performs provider mutation until an accepted
  adapter exists.

## Source And Forks

Official Google Ads documentation remains the source of truth for platform
limits, policy, feature behavior, and UI mechanics. This playbook owns the
Noontide defaults for one use case: validating many offers quickly with tight
control and a small budget.

Forks are expected. Record the default, the fork, and the reason in the push
playbook when changing geography scope, conversion path, bidding, broad match,
AI Max, Final URL Expansion, Search Partners, asset types, or review windows.

## New Offer Default

When the business has never advertised this offer:

- skip claims about historical winners;
- research customer intent and keyword families through `/mb-think`;
- research the geography: local radius, multi-city, statewide, national, or
  multi-location;
- pick the conversion path before asset writing: call/booking,
  Stripe/deposit, lead form, trial, or another concrete action;
- keep the first campaign small enough to learn from;
- document assumptions in the run record;
- expect the first review to refine keywords, negatives, lander copy, and
  conversion assumptions.

## Existing Account Default

When the account has useful history:

- inspect prior campaigns, search terms, negatives, conversion actions,
  disapprovals, and economics if approved read-only access or sanitized exports
  exist;
- rescue an existing campaign when the offer, conversion, goal, budget model,
  and geography still match;
- create a new campaign when the offer, conversion, goal, budget model,
  geography, or structure materially changes;
- pause bad assets before deleting them, so the audit trail survives the first
  review window.

## Proof Budget

A small proof budget is acceptable only when it can produce an interpretable
answer. The operator should set:

- budget cap;
- expected CPC range;
- minimum clicks or spend before review;
- primary conversion target;
- business value of the conversion;
- stop/change/continue threshold.

Do not present a fixed spend amount as universal. Some niches need more data;
some can learn from a smaller test.

## Review Decision

At the end of the review window:

- **Continue** when the economics and lead quality are promising enough to let
  the campaign gather more data.
- **Change** when intent exists but the campaign, negatives, lander, conversion
  path, or offer needs repair.
- **Stop** when the bet is disproven, blocked by policy, or too expensive to
  learn from responsibly.
