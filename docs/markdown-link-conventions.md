# Markdown and Link Conventions

Main Branch business repos should be readable in GitHub, local editors, and
Obsidian without becoming dependent on any markdown app.

The repo is the durable source of truth. Markdown tools are views over that
truth.

## Goals

- GitHub links work in pull requests, issues, and the browser.
- Obsidian can browse the same repo as a vault.
- `mb graph` can build useful file and entity relationships.
- `mb validate --cross-refs` can catch broken important links.
- Agents can follow links without guessing.

## Filenames

Use stable, lowercase, hyphenated filenames:

```text
decisions/2026-05-04-pricing-model.md
research/2026-05-04-audience-notes.md
bets/2026-05-04-trial-offer.md
pushes/2026-05-04-spring-launch/push.md
core/offers/main-branch/offer.md
```

These examples use the current v0.x canonical folders. If future user research
shows that folder names should change, that change should land through
path-config and migration work, not ad hoc docs or skill examples that teach a
different repo shape.

Avoid spaces, case-only distinctions, punctuation-heavy names, and repeated
stems in different folders when you expect to use wikilinks. Obsidian can
resolve `[[pricing-model]]` by filename stem only when the stem is unique.

## Frontmatter Links

Frontmatter links are machine-readable. Use repo-relative paths with `.md`
extensions:

```yaml
linked_decisions:
  - decisions/2026-05-04-pricing-model.md
linked_research:
  - research/2026-05-04-audience-notes.md
linked_pushes:
  - pushes/2026-05-04-spring-launch/push.md
```

Do not use Obsidian wikilink syntax in frontmatter. Do not omit the extension.
Do not use absolute local paths.

Legacy `linked_campaigns` frontmatter remains readable for migrated repos, but
new records should use `linked_pushes`.

Allowed external references:

```yaml
linked_issues:
  - https://github.com/noontide-co/mainbranch/issues/274
```

Use external URLs for public issue, PR, release, or source links. Use local
paths for files inside the same repo.

## Body Links

Use standard Markdown links when GitHub clickability matters:

```markdown
See [the pricing decision](../decisions/2026-05-04-pricing-model.md).
```

Use Obsidian wikilinks when graph browsing is the main reason and the target is
unambiguous:

```markdown
See [[decisions/2026-05-04-pricing-model|pricing decision]].
See [[pricing-model]] only when that filename stem is unique.
```

For durable docs, prefer the path form over bare stems. It is clearer to
GitHub readers, agents, and future validation.

Heading anchors are less stable than file links because GitHub and Obsidian do
not generate anchors the same way in every case. Prefer linking to the file and
using a clear heading near the target.

## Entity Tags

`mb graph` recognizes typed entity tags in markdown bodies:

```markdown
#company/example-co
#person/jane-doe
#offer/main-branch
#channel/github
#competitor/status-quo
#metric/activation-rate
```

Use these for durable entities that should appear in graph output. Keep values
lowercase and hyphenated. Do not use entity tags for secrets, private customer
names, account numbers, or legal/finance identifiers that should not be visible
to the repo audience.

## Cross-Repo Links

A business repo may link to another repo, but a cross-repo link is not the same
as access.

Use public URLs when the target is public:

```markdown
See [Main Branch issue #274](https://github.com/noontide-co/mainbranch/issues/274).
```

Use a plain-text repo/path reference when the target may be private and the
link should not imply broad access:

```markdown
Private finance source: finance-repo/core/finance/ledger/
```

Do not commit private local machine paths. If a local-only path is needed for
an operator, keep it in local config, a private repo, or `.context/` rather
than public docs.

## Obsidian Setup

Opening a business repo as an Obsidian vault should be optional:

1. Open the repo root as the vault.
2. Keep attachments and exports in existing repo folders only when they are
   safe for the repo audience.
3. Do not rely on an Obsidian plugin for Main Branch correctness.
4. Keep `.obsidian/` local unless a team intentionally agrees to commit shared
   vault settings.

Main Branch should not require Obsidian, replace Obsidian, or add Obsidian as a
runtime dependency.

## Validation

Run:

```bash
mb validate --cross-refs
```

This checks known frontmatter link fields and warns when important links are
missing. It also warns when wikilinks point to missing markdown files or match
multiple files by stem.

Use strict mode in CI or branch cleanup when warnings should fail:

```bash
mb validate --cross-refs --strict
```

Validation does not prove a user can access a private cross-repo target. It only
checks the current repo and safe external references.
