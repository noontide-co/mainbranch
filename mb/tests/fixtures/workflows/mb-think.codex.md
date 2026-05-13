# Generated Codex Workflow Guidance: Think Research Decision Codify

Source workflow: `workflows/mb-think/workflow.md`
Runtime support: `codex_cli: experimental_shell`

Codex remains experimental and CLI-first. This guidance tells Codex how to
treat a natural-language request as a Main Branch thinking task through
`AGENTS.md` posture and deterministic `mb` facts. It does not claim Claude
Code slash commands work inside Codex or that all Main Branch workflows are
available in Codex.

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

## Codex Route

1. Use the business repo `AGENTS.md` bootstrap posture: read facts first, keep
   writes approval-gated, and translate git/provider details into business
   language.
2. Run hard gates first: required updates, repair blockers, readiness
   blockers, unsafe provider operations, private-data boundaries, and
   destructive-operation requests.
3. Read deterministic `mb` facts before raw markdown. Then read only relevant
   `core/`, `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and `docs/`
   files.
4. Give a Research Depth Recommendation from 0-5 before outside research:
   memory, repo context, lightweight public/manual research, multi-source
   synthesis, structured approved-source collection, or high-resolution market
   analysis.
5. Use parallel research files for multiple sources, then synthesize in the
   main thread. Each source file records source quality, access/permission,
   caveats, promotion limits, and public/private handling.
6. Write a decision when durable business truth changes. Codify only after the
   operator accepts the direction.
7. Ask for approval before creating or editing business files, promoting
   research into core truth, using structured collection, opening public
   issues, publishing, mutating providers, spending money, contacting
   customers, or saving a checkpoint.

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

Do not tell Codex users to run Claude slash commands. Runtime smoke is required
before docs say this selected workflow is supported or available in Codex.
