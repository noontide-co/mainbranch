# Generated Codex Workflow Guidance: Start To MoneyPath Think Handoff

Source workflow: `workflows/mb-start-money-path/workflow.md`
Runtime support: `codex_cli: experimental_shell`

Codex remains experimental and CLI-first. This guidance is a generated snapshot
for validation; it does not mean `/mb-start` slash commands work inside Codex
and it does not claim selected Codex workflow support.

Start from deterministic `mb` facts before reading business markdown or giving
path-to-money advice.

## Required mb Commands

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`

## Required JSON Fact Paths

- `money_path`
- `money_path.objects.offer`
- `money_path.objects.proof`
- `money_path.objects.proof.quality`
- `money_path.objects.product_ladder`
- `money_path.objects.cta_path`
- `money_path.objects.channel_strategy`
- `money_path.objects.active_push`
- `money_path.objects.outcome_feedback_loop`
- `money_path.ranked_actions`
- `content_strategy`
- `ranked_actions`
- `update`
- `readiness`
- `drift.items`

## Codex Route

1. Use the business repo `AGENTS.md` bootstrap posture: read facts first, keep
   writes approval-gated, and translate git/provider details into business
   language.
2. Run hard gates before MoneyPath interpretation: required updates, repair
   blockers, readiness blockers, unsafe provider operations, private-data
   boundaries, and destructive-operation requests.
3. Use `money_path`, `money_path.objects.proof.quality`, `content_strategy`,
   `ranked_actions`, `update`, `readiness`, and `drift.items` as cited facts.
4. If a thinking/codification step is needed, propose the route in Codex-native
   language instead of pretending Claude slash commands are available.
5. Ask before writing business files, saving checkpoints, opening public
   issues, publishing, mutating providers, spending money, or contacting
   customers.

## Handoff Shape

```text
MoneyPath snapshot: overall <level> / <label>.
Bottleneck: <object or gate>.
Proof: <generic/specific/offer-linked/typicality/outcome-feedback facts>.
Offer and ladder: <structured facts and missing fields>.
CTA/channel/push: <connection facts>.
Outcome feedback: <instrumentation facts>.
Ranked actions: <agreement or disagreement with MoneyPath bottleneck>.
Recommended route: clarify or codify <decision or write target> after approval.
Approval needed before writes: yes.
```

Runtime smoke is required before docs say this selected workflow is supported
or available in Codex.
