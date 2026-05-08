---
type: educational
topic: forgejo
status: draft
last-updated: 2026-05-08
---

# Forgejo: owning the git server when GitHub is not the right boundary

GitHub is the default Main Branch public and team rail today because it gives
issues, pull requests, releases, and broad tool support. Forgejo matters because
some teams eventually need a self-hosted git forge.

## When you need this

Consider Forgejo when:

- the business needs stronger custody over a private repo;
- a finance, legal, client, or operations repo should not sit in a broad SaaS
  account;
- the team already runs self-hosted infrastructure;
- GitHub is unavailable, inappropriate, or intentionally not the source of
  truth for that repo boundary.

For most beginners, GitHub is still the right starting point.

## Why Forgejo fits the Main Branch philosophy

**It keeps git as the substrate.** Main Branch wants durable files, git history,
and inspectable changes. Forgejo preserves that model.

**It is self-hostable.** A team can run the forge on infrastructure it controls
when the access boundary matters.

**It can keep sensitive repos separate.** A business repo can link to a
separate finance, legal, site, client, or ops repo without copying raw private
data into shared memory.

## What changes if you use Forgejo

You still need the same operating concepts:

- issues or equivalent work threads;
- proposals or review conversations;
- readable commits;
- backups and restore drills;
- explicit access rules;
- no secrets in committed files.

The difference is who operates the forge and how much responsibility the team
takes on for uptime, security updates, backups, and account recovery.

## What Main Branch does not claim

Main Branch does not claim Forgejo is a fully supported first-run provider
today. GitHub remains the concrete public rail for issues, proposals, releases,
and most current workflows.

Forgejo is a compatible direction for teams that need self-hosted git, not a
beginner requirement.
