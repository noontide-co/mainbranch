# Generated Claude Shell: Think Research Decision Codify

Source workflow: `workflows/mb-think/workflow.md`
Runtime support: `claude_code: supported_shell`

Use from `/mb-think` when the operator asks to research, decide, figure out,
compare, codify, sharpen an offer, or turn learning into durable business
truth. Preserve slash-command-native language for Claude Code only.

This snapshot does not replace shipped `.claude/skills/mb-think/SKILL.md`.

## Required mb Commands

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`
- `mb connect doctor --json`
- `mb checkpoint --plan --json`

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
- `books`
- `runtime.codex`
- `runtime.claude_code`

## Routing

1. Run hard gates first: required updates, broken repo wiring, repair blockers,
   validation blockers, unsafe provider operations, private-data boundaries,
   and destructive-operation requests.
2. Read deterministic `mb` facts before raw markdown. Then read only relevant
   `core/`, `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and `docs/`
   files.
3. Give a Research Depth Recommendation from 0-5 before outside research:
   memory, repo context, lightweight public/manual research, multi-source
   synthesis, structured approved-source collection, or high-resolution market
   analysis.
4. Use parallel research files for multiple sources, then synthesize in the
   main thread. Each source file records source quality, access/permission,
   caveats, promotion limits, and public/private handling.
5. Write a decision when durable business truth changes. Codify only after the
   operator accepts the direction.
6. Ask for approval before creating or editing business files, promoting
   research into core truth, using structured collection, or saving a
   checkpoint.

## Handoff Shape

```text
Thinking task: <research, decision, codify, or full flow>.
Repo facts read: <status/start/connect/repair/checkpoint facts used>.
Current bottleneck: <MoneyPath, content strategy, readiness, drift, or user question>.
Research depth recommendation: <0-5>, because <reason>.
Useful sources: <repo files, public/manual sources, approved providers, or operator input>.
Stop condition: <what is enough signal>.
Durable targets: <research/, decisions/, core/, bets/, pushes/, log/, or documents/>.
Approval needed before writes: yes.
```

Use business language. Do not say an offer is bad, will convert, or will not
convert. Do not tell Codex users to run Claude slash commands.
