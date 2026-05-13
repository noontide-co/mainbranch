# Generated Claude Shell: Start To MoneyPath Think Handoff

Source workflow: `workflows/mb-start-money-path/workflow.md`
Runtime support: `claude_code: supported_shell`

Use from `/mb-start` when the operator asks about revenue, offer readiness, the
next dollar, or the path to money. Preserve slash-command-native language and
handoff to `/mb-think` only when the next useful move is to clarify, decide,
research, or codify durable business truth.

This snapshot does not replace shipped `.claude/skills` prose.

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

## Routing

1. Run hard gates first: required updates, broken repo wiring, repair blockers,
   validation blockers, relationship-health blockers, unsafe provider
   operations, private-data boundaries, and destructive-operation requests.
2. Start MoneyPath interpretation from `money_path.overall_level`,
   `money_path.overall_label`, the required `money_path.objects.*` paths, and
   `money_path.ranked_actions`.
3. Compare top-level `ranked_actions` with the MoneyPath bottleneck. If they
   disagree, name the gate or route taking priority.
4. Read supporting markdown only after deterministic facts identify the
   bottleneck.
5. Hand off to `/mb-think` with the MoneyPath snapshot when the next move is a
   decision, research pass, or codify write.

## Handoff Shape

```text
MoneyPath snapshot: overall <level> / <label>.
Bottleneck: <object or gate>.
Proof: <generic/specific/offer-linked/typicality/outcome-feedback facts>.
Offer and ladder: <structured facts and missing fields>.
CTA/channel/push: <connection facts>.
Outcome feedback: <instrumentation facts>.
Ranked actions: <agreement or disagreement with MoneyPath bottleneck>.
Recommended route: use /mb-think to <decision or write target>.
Approval needed before writes: yes.
```

Avoid subjective conversion judgment. Do not say an offer is bad, will convert,
or will not convert.
