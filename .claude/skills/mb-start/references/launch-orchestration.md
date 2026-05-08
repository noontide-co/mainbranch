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

## Sequence

1. **Resolve the offer.** Use the normal active-offer rules. If no offer exists,
   route to `/mb-think` to codify the offer and audience before launch work.
2. **Create or select a push.** Use `pushes/<YYYY-MM-DD-slug>/push.md` with
   `type: push`, `kind: launch`, structured `goal`, `owner`, `audience`,
   `offer`, and a short `promise`. If a matching active/planned launch push
   exists, ask whether to continue it instead of creating a duplicate.
3. **Keyword gate.** Route to `/mb-think` keyword-gate mode. A "kill" verdict
   stops the default path unless the operator explicitly overrides.
4. **Lander plan/build.** Route to `/mb-site` lander mode. If paid traffic is in
   scope, require the site measurement checks from `/mb-site` before ads work.
5. **Ad launch plan/check.** Route to `/mb-ads` launch-plan or check mode. This
   prepares copy, keyword targets, negatives, policy findings, budget notes, and
   manual provider steps. It does not mutate Google Ads/GTM/Meta accounts.
6. **Checkpoint.** After each accepted artifact or approval record, run
   `mb checkpoint --plan --json`, validate the message, and save only after
   operator approval.

## Beginner Output Pattern

Show exactly one current step plus the next two steps:

```text
Current step: keyword gate the offer.
Next: create/update the launch push.
After that: build the lander and prepare ads for review.
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
