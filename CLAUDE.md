# Claude Code Instructions

Read `AGENTS.md` first. It is the shared operating contract for all agents
working in this repository.

This file only adds Claude Code-specific guidance for the Main Branch engine
repo.

## Repository Role

This is the public `noontide-co/mainbranch` engine repository. It contains the
`mb` CLI, bundled agent-runtime skills, docs, fixtures, tests, and release
metadata.

It is not a user's business repo. Business data belongs in the repo created by
`mb onboard` or `mb init`, not in this engine checkout.

## How to Work Here

- Follow `AGENTS.md` for product shape, scope, public/private boundaries, branch
  discipline, validation, and PR expectations.
- Use `README.md`, `docs/`, `decisions/`, tests, and GitHub issues as durable
  context.
- Keep `.context/` as local scratch only.
- Run `scripts/check.sh` from the repo root before pushing code or docs that
  could affect packaged behavior.
- If you change first-run, skill discovery, `mb init`, `mb onboard`,
  `mb start`, `mb status`, `mb update`, or bundled skills, add the relevant
  fixture/package/runtime smoke evidence described in `AGENTS.md`.

## Engine vs Business Repo

When a user is operating Main Branch, they should be in their business repo:

```bash
cd path/to/my-business
mb status
mb start --launch
```

When contributing to the engine, work in this repository and keep changes
scoped to the assigned issue or PR.

## Skills

Bundled Claude Code skills live in `.claude/skills/`. If you edit a skill:

- read the skill's `SKILL.md` before changing it;
- keep `SKILL.md` under the repo's line-count gate;
- update tests, fixtures, or docs when behavior changes;
- do not write outputs into this engine repo unless the test/fixture explicitly
  requires it;
- avoid private member data, private launch strategy, or machine-specific paths
  in examples.

Claude Code is first-class today. Other runtimes are roadmap targets until an
adapter and smoke evidence exist, so do not overclaim compatibility in docs.
