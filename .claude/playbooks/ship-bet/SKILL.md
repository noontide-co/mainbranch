---
name: ship-bet
tier: playbook
calls: [start, think, skill-brief-draft, skill-concept, skill-review, site, ads, end]
status: skeleton
description: "Reusable skeleton playbook. Walks the operator from a proposed bet or offer to a launch push, landing page, first ad creative, review evidence, and checkpoint. Not yet a single executable orchestrator."
---

# ship-bet (skeleton)

This is a reusable operating recipe, not a one-off run file. Use it when the
operator wants to turn one proposed bet or offer into a launch push with a
landing page, first ad creative, review evidence, and a saved checkpoint.

**Current status: skeleton.** This file documents the intended chain and
artifact routing. It is not yet executable as one coherent workflow with a
single progress surface, retry-on-failure, or cross-skill data passing. Run each
step through the named skills and `mb` commands today.

## Playbook Versus Run

This file is the reusable engine recipe under `.claude/playbooks/ship-bet/`.
The concrete run belongs in the business repo:

```text
pushes/<YYYY-MM-DD-slug>/push.md
pushes/<YYYY-MM-DD-slug>/playbooks/ship-bet.md
```

Create or select the push first. Use a push playbook run record when the run
needs approval state, provider readiness, forks from the recipe, manual steps,
review evidence, or outcome links. Do not write new work under `campaigns/`;
that folder is legacy compatibility read only.

## Intended Flow

```
1. /mb-start          — read repo health, active bets, pushes, provider state
2. /mb-think codify   — confirm bet, offer, audience, proof, and success bar
3. pushes/            — create or select the launch push record
4. skill-brief-draft  — draft minisite brief from offer + audience + voice
5. skill-review       — Seven Sweeps + Expert Panel against the brief
6. /mb-site build     — generate or update the landing page/site record
7. skill-concept      — N variations on localhost, operator picks one
8. /mb-site publish   — publish only after operator approval and readiness
9. /mb-ads generate   — first ad creative from the brief
10. /mb-ads review    — compliance + lens check
11. push playbook     — record forks, approvals, review evidence, outcomes
12. /mb-end           — checkpoint accepted artifacts
```

## Inputs

- A bet or proposed offer to ship.
- `core/offers/<slug>/offer.md` or the operator's approval to create/update it.
- Audience, proof, voice, and conversion-path context.
- A launch push, or permission to create one.
- A `dial` pick when the creative path needs one: `convert`, `story`, or
  `brand`.
- Provider and site readiness facts from `mb status --json --peek`,
  `mb connect plan`, and `mb site check` when a site repo exists.

## Outputs

- A launch push at `pushes/<YYYY-MM-DD-slug>/push.md`.
- Optional run record at `pushes/<YYYY-MM-DD-slug>/playbooks/ship-bet.md`.
- A site record under the push or a linked child site repo update.
- First ad creative under `pushes/<YYYY-MM-DD-slug>/ads/`.
- Review notes, outcome links, or a weekly/session log entry when the operator
  approves them.
- A checkpoint plan and operator-approved checkpoint for accepted artifacts.

## Skeleton Caveats

- Each step runs as its own command today.
- No retry-on-failure exists; the operator restarts the failed step.
- Data passing between steps is via files in the business repo.
- Provider mutation remains manual or provider-native unless a future accepted
  adapter ships with approval gates and smoke evidence.

## Cross-references

- [start/SKILL.md](../../skills/mb-start/SKILL.md)
- [think/SKILL.md](../../skills/mb-think/SKILL.md)
- [skill-brief-draft/SKILL.md](../../skills/mb-skill-brief-draft/SKILL.md)
- [skill-concept/SKILL.md](../../skills/mb-skill-concept/SKILL.md)
- [skill-review/SKILL.md](../../skills/mb-skill-review/SKILL.md)
- [site/SKILL.md](../../skills/mb-site/SKILL.md)
- [ads/SKILL.md](../../skills/mb-ads/SKILL.md)
- [end/SKILL.md](../../skills/mb-end/SKILL.md)
