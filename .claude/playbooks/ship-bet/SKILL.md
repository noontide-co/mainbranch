---
name: ship-bet
tier: playbook
calls: [skill-brief-draft, skill-concept, skill-review, site, ads]
status: skeleton
description: "Skeleton playbook (v0.1). Walks the operator from a half-formed bet to a shipped landing page + first ad creative. v0.2 implementation lands real orchestration."
---

# ship-bet (skeleton)

A playbook that takes one bet from `core/offers/<slug>/offer.md` (status: `proposed`) to a published landing page + first ad creative inside one flow.

**v0.1 status: skeleton.** This file documents the intended depth-3 chain. Real orchestration (single progress surface, retry on stage failure, cross-skill data passing) lands in v0.2.

## Intended flow (v0.2 implementation)

```
1. /think codify    — confirm offer is named in core/offers/<slug>/
2. skill-brief-draft  — draft minisite brief from offer + audience + voice
3. skill-review     — Seven Sweeps + Expert Panel against the brief
4. /site build      — generate, deploy to Cloudflare Pages
5. skill-concept    — N variations on localhost, operator picks one
6. /site publish    — push picked concept; auto-deploy
7. /ads generate    — first ad creative from the brief
8. /ads review      — compliance + lens check
9. log/             — write playbook-run summary
```

## Inputs

- An offer slug with `status: proposed` in `core/offers/<slug>/`
- A `dial` pick (convert | story | brand)

## Outputs

- A published Cloudflare Pages site
- A first ad creative draft in `campaigns/<slug>/`
- A playbook-run entry in `log/YYYY-MM-DD-shipbet-<slug>.md`

## v0.1 caveats

- Each step runs as its own /command today; no single progress surface
- No retry-on-failure; operator restarts the failed step
- Data passing between steps is via files in the consumer repo

## Cross-references

- [skill-brief-draft/SKILL.md](../../skills/skill-brief-draft/SKILL.md)
- [skill-concept/SKILL.md](../../skills/skill-concept/SKILL.md)
- [skill-review/SKILL.md](../../skills/skill-review/SKILL.md)
- [site/SKILL.md](../../skills/site/SKILL.md)
- [ads/SKILL.md](../../skills/ads/SKILL.md)
