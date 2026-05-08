# Launch Plan And Check Modes

Use this when the operator asks to launch/check paid traffic, especially Google
Ads traffic for a lander or minisite.

This mode prepares a reviewable plan and checks recorded readiness. It does not
mutate Google Ads, GTM, Meta Ads, Stripe, or analytics providers unless a future
adapter ships with approval gates and smoke evidence.

## Launch-Plan Inputs

From the business repo:

- active offer and audience;
- the launch push at `pushes/<push>/push.md`;
- keyword-gate research, especially ready-to-buy terms and negative seeds;
- site record or linked site repo;
- `docs/google-ads-gtm-conversion-rubric.md`;
- `mb status --json --peek`;
- `mb connect plan` or `mb connect doctor --json`;
- when a site repo exists:

```bash
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
```

## Readiness States

Use the returned `mb site check` state:

- `missing`: measurement setup has not been declared; draft strategy only and
  route setup through `/mb-site` or the measurement rubric before traffic.
- `blocked`: stop launch planning after listing blockers and next commands.
- `ready_for_preview`: draft ads only; operator still needs GTM Preview/Tag
  Assistant and provider metadata.
- `ready_for_operator_review`: prepare campaign materials and approval list.
- `ready`: local checks passed; still require explicit operator approval before
  provider mutation or spend.

Never say `ready_for_launch`.

## Output

Write a provider-safe plan under the launch push, for example:

```text
pushes/<YYYY-MM-DD-slug>/ads.md
```

Sections:

- `## Readiness`
- `## Budget And Review Window`
- `## Campaign Structure`
- `## Keyword Targets`
- `## Negative Seeds`
- `## Headlines`
- `## Descriptions`
- `## Sitelinks`
- `## Policy Preflight`
- `## Measurement Checklist`
- `## Manual Provider Steps`
- `## Approval`

If the work includes repeatable provider setup, resource delivery, or approval
state, draft a `type: playbook` file under `pushes/<push>/playbooks/` instead
of hiding the plan in prose.

## Policy Preflight

Before preparing launch copy:

- run the normal ad compliance review flow;
- check for regulated verticals: medical, finance, credit, employment,
  housing, legal, social issues/politics;
- compare claims against offer proof and Skool/site surfaces when present;
- stop on unsupported guarantees, "cures/treats/heals" claims, impossible
  outcomes, or provider-specific disallowed phrases.

## Check Mode

Use check mode when the operator asks "how are the ads doing" or "should we
continue/kill this launch."

Because live provider metrics are not yet a supported mutation/read adapter by
default, use one of these sources:

1. `mb status --json --peek` and relationship/outcome health.
2. Existing push outcome/review files.
3. Operator-provided Ads/GTM/Stripe screenshots or CSV exports.
4. Read-only provider context only when `mb connect` and the current runtime
   prove it is ready.

Output a concise continue/change/stop recommendation and write findings to the
push review or outcome file when the operator approves.

## Approval Boundary

Do not:

- upload campaigns;
- publish GTM containers;
- change budgets;
- start spend;
- upload conversions;
- ask for OAuth secrets, API keys, customer records, or raw account exports in
  chat.

Do:

- prepare the plan;
- cite exact manual steps;
- record approval requirements;
- checkpoint approved artifacts.
