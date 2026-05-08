# Work Continuity

Main Branch does not ask operators to pick a separate task tracker. The normal
loop is work continuity: start from current facts, choose the next business
move, ship or clarify it, and save enough durable memory for the next session
to recover.

If you feel the urge to "save the conversation," extract what mattered into the
right Main Branch primitive instead:

| What mattered | Durable home |
| --- | --- |
| A wager, success metric, deadline, or lesson | `bets/` |
| A coordinated launch, drop, challenge, promo, or operating push | `pushes/` |
| A choice and its rationale | `decisions/` |
| Evidence, synthesis, or open questions | `research/` |
| A repeatable procedure | playbook |
| A daily record, handoff, or event memory | `log/` |
| Saved work at a meaningful boundary | `mb checkpoint` / git commit |
| A durable work thread that needs visibility across sessions or people | GitHub issue |

The conversation is scaffolding. The value should land in files, issues when
needed, proposals, or saved checkpoints.

---

## How `/mb-start` Recovers Context

`/mb-start` regenerates the current view from facts. It should read
`mb status --json --peek`, then use repo health, graph links, update state,
provider readiness, recent saved work, GitHub activity, checkpoint state, and
ranked actions to propose the next one to three meaningful moves.

It is not reading a backlog. It is answering:

1. What changed since last time?
2. What business move looks important now?
3. What needs repair, approval, or a saved checkpoint before we continue?

Those moves should be at push or scope altitude, not atomic chore altitude.

---

## Decisions Are Rationale, Not Progress Boards

Use decision files for choices where the "why" matters.

Decision status describes rationale maturity:

| Status | Meaning |
| --- | --- |
| `proposed` | A direction is drafted and still being evaluated. |
| `accepted` | The operator chose the direction. |
| `codified` | The rationale has been integrated into durable business or engine truth. |

This does not mean downstream work is done. A codified decision can still have
follow-up work. An accepted decision might already have shipped. If follow-up
work needs durability, route it into a push, playbook, checkpoint, log entry, or
GitHub issue instead of turning the decision into a generic work board.

---

## When Work Becomes a GitHub Issue

Create or suggest a GitHub issue when work needs a durable thread:

- it crosses sessions and would otherwise be forgotten;
- it has an owner, blocker, dependency, deadline, or discussion;
- it is public Main Branch engine work, support friction, or a reproducible bug;
- it should connect to a branch, pull request, release, or review loop;
- it needs team visibility;
- it does not naturally belong in one bet, push, playbook, decision, or log.

Do not create issues for raw thought dumps, quick one-session work, ordinary
decision rationale, sensitive private context, or checklist steps inside an
active push/playbook.

Skills should usually draft or suggest an issue before creating one. Public
issue creation is a shared-memory action that needs operator approval.

---

## What To Put In `CLAUDE.md`

Do not record a task-tracking preference. Record the business primitives and
continuity rules that help `/mb-start` route work:

```markdown
## Work Continuity

- Active bets: `bets/`
- Active pushes: `pushes/`
- Decisions that explain direction: `decisions/`
- Team handoffs and daily records: `log/`
- Use GitHub issues only when work needs a durable thread across sessions,
  proposals, releases, or team visibility.
```

Keep this section short. The repo facts and `mb status` should do the heavy
lifting.

---

## Quick Routing Guide

**"I have a strategic choice to make"** -> decision file or `/mb-think`.

**"I need to coordinate a launch/drop/challenge/promo"** -> push.

**"I need to remember what happened today"** -> log entry or checkpoint.

**"This work crosses sessions, has blockers, or needs team visibility"** ->
GitHub issue draft.

**"I just have a quick small thing"** -> do it, then checkpoint if the result
matters.
