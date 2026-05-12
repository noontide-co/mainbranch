# Offer Launch Orchestration

Use this when the operator says "launch this offer," "keyword gate this offer
then build the lander," "get a paid-traffic plan ready," or invokes
`/mb-start launch <offer>`.

This is skill orchestration, not a new `mb` CLI workflow runner. `/mb-start`
keeps the main context lean, reads deterministic `mb` facts, and routes the
operator through existing skills.

## Required Starting Facts

From the business repo:

```bash
mb status --json --peek
mb connect plan
```

If status reports relationship-health gaps, legacy `campaigns/` drift, missing
provider readiness, or update/repair blockers, surface those first and use the
cited repair command.

Also read `status.money_path` before launch routing. If MoneyPath reports
missing customer progress, offer, proof, CTA path, channel strategy, active
push, playbook, page readiness, or outcome feedback, use those facts as launch
prerequisites. The CLI names legibility and connection gaps; offer judgment
still belongs in offer sharpening and the downstream skills.

## Sequence

1. **Resolve the offer.** Use the normal active-offer rules. If no offer exists,
   route to `/mb-think` to codify the offer and audience before launch work.
2. **Sharpen the offer.** Load
   `.claude/reference/conversion/offer-sharpening.md`. If audience, outcome,
   mechanism, proof, risk reversal, objections, reason to act, or next step is
   thin, route to `/mb-think` before keyword gate, lander, or ads work.
3. **Create or select a push.** Use `pushes/<YYYY-MM-DD-slug>/push.md` with
   `type: push`, `kind: launch`, structured `goal`, `owner`, `audience`,
   `offer`, and a short `promise`. If a matching active/planned launch push
   exists, ask whether to continue it instead of creating a duplicate.
4. **Keyword gate.** Route to `/mb-think` keyword-gate mode. A "kill" verdict
   stops the default path unless the operator explicitly overrides.
5. **Lander plan/build.** Route to `/mb-site` lander mode. If paid traffic is in
   scope, require the site measurement checks from `/mb-site` before ads work.
6. **Ad launch plan/check.** Route to `/mb-ads` launch-plan or check mode. For
   Google Ads, the skill should load the Google Ads campaign-plan reference,
   decide whether `/mb-think` policy/keyword research is needed, reuse useful
   account history when the operator provides it or an approved read-only
   provider tool exists, check whether an existing campaign should be rescued
   instead of rebuilt, and prepare copy, keyword targets, negatives, policy
   findings, budget notes, manual provider steps, approval gates, and
   review-window criteria. Use `mb connect` and `mb site check` for readiness
   facts, but do not treat them as proof that Google Ads campaign creation is
   supported from the terminal. It does not mutate Google Ads/GTM/Meta
   accounts.
7. **Checkpoint.** After each accepted artifact or approval record, run
   `mb checkpoint --plan --json`, validate the message, and save only after
   operator approval.

## Beginner Output Pattern

Show exactly one current step plus the next two steps:

```text
Current step: sharpen the offer.
Next: create/update the launch push.
After that: keyword gate the demand before lander and ads work.
```

Use numbered choices when blocked:

1. Fix the blocker now with the exact `mb` command.
2. Continue in read-only planning mode.
3. Stop and save a checkpoint.

## Approval Boundaries

Always require explicit operator approval before:

- buying domains;
- attaching custom domains;
- publishing/deploying site changes;
- creating payment links or modifying Stripe;
- publishing GTM containers;
- mutating Google Ads or Meta Ads;
- spending money;
- uploading customer, conversion, or account data.

If an adapter is not shipped with smoke evidence, describe the step as manual
or plan-only and record it in the push or a push playbook.
