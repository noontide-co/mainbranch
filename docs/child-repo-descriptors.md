# Child Repo Descriptors

Child repos use a repo-local descriptor to explain where they fit without
becoming the hub's source of truth.

Use:

```text
.mainbranch/repo.json
```

for role-neutral child repo metadata. Existing site repos may still have:

```text
.mainbranch/source.json
```

`source.json` remains a site compatibility file. New non-site child repos
should use `repo.json`.

## Shape

```json
{
  "schema": "mb.child_repo.v0",
  "role": "site",
  "display_name": "Workshop site",
  "github_owner": "example-co",
  "repo_name": "workshop-site",
  "safe_purpose": "Public paid-traffic site for the workshop offer.",
  "parent": {
    "display_name": "Example Business",
    "github_owner": "example-co",
    "repo_name": "example",
    "remote": "github:example-co/example",
    "local_checkout": "../example"
  },
  "linked": {
    "offers": ["core/offers/workshop/offer.md"],
    "pushes": ["pushes/2026-05-20-workshop-launch/push.md"],
    "bets": ["bets/2026-05-01-workshop-test.md"],
    "decisions": ["decisions/2026-05-08-site-boundary.md"]
  },
  "return_to_hub_command": "cd ../example && claude",
  "safe_to_share": true
}
```

Fields:

| Field | Meaning |
| --- | --- |
| `schema` | Descriptor schema. Use `mb.child_repo.v0`. |
| `role` | One of the repo roles from the topology decision: `site`, `offer`, `product`, `client`, `finance`, `legal`, `ops`, `integration_sidecar`, `experiment`, or `archive`. |
| `display_name` | Human-readable child repo name. This is not the GitHub repo name. |
| `github_owner` / `repo_name` | Durable technical handle for this child repo. |
| `safe_purpose` | Public-safe reason the child repo exists. |
| `parent` | Safe hub reference. Include GitHub owner/repo distinctly from display name. |
| `parent.local_checkout` | Optional relative checkout hint from the child repo to the hub. Do not commit absolute local paths. |
| `linked` | Safe handles to hub business primitives. Use repo-relative hub paths. |
| `return_to_hub_command` | Optional exact command when a sibling checkout makes it safe and useful. Prefer relative paths. |
| `safe_to_share` | Whether this descriptor is intended to be safe for the child repo's normal audience. This does not grant access. |

## Relation To Hub Topology

The hub registry lives at:

```text
core/operations/repo-topology.md
```

The hub registry is the durable business map: child repo list, lifecycle,
visibility, relationships, and approved business meaning. A child descriptor is
only the child repo's local signpost back to that map. If the two disagree, the
operator should treat that as topology drift and repair it deliberately.

Use the child descriptor to answer:

- "What kind of repo am I in?"
- "Which hub does this child report to?"
- "Which offer, push, bet, or decision explains this work?"
- "How do I return to the hub when I need strategy, routing, or checkpoint
  context?"

Use the hub topology registry to answer:

- "Which child repos exist for this business?"
- "Which repos are active, paused, restricted, archived, or superseded?"
- "Which repo should an agent work in next?"
- "Which finance, legal, client, or sidecar boundaries are intentionally
  private?"

## Site Compatibility

Existing site repos may keep `.mainbranch/source.json`:

```json
{
  "business_repo": "/absolute/path/to/my-business",
  "offer_path": "core/offers/workshop/offer.md",
  "campaign_path": "pushes/2026-05-20-workshop-launch/push.md",
  "safe_to_share": true
}
```

`business_repo`, `offer_path`, and `campaign_path` are compatibility fields.
The `campaign_path` key may point at a current `pushes/<slug>/push.md` record.

For new site repos, write `.mainbranch/repo.json` first. Add
`.mainbranch/source.json` only when a legacy workflow still needs it.
`mb site check` can read the role-neutral descriptor. If the descriptor only
contains GitHub owner/repo handles, pass the local hub checkout explicitly:

```bash
mb site check . --business-repo ../example --json
```

## Sensitive Repos

Finance, legal, client, and integration sidecar descriptors must use safe
handles only.

Allowed:

- role and display name;
- GitHub owner/repo when that handle is safe for the repo audience;
- safe purpose statement;
- parent hub GitHub owner/repo;
- linked approved summaries, decisions, pushes, or policies;
- high-level provider names or non-secret project handles when safe.

Not allowed:

- secrets, tokens, credentials, OAuth refresh tokens, service-account JSON,
  webhook secrets, bearer tokens, or MCP tokens;
- raw ledger paths, bank exports, payroll files, contracts, legal advice,
  disputes, customer/member rows, private browser traces, provider caches,
  metrics databases, connector secrets, or large raw exports;
- absolute local paths;
- claims that a user has permission to read or mutate finance, legal, provider,
  customer, or teammate data. Permission comes from GitHub, local OS access,
  provider systems, or future accepted auth surfaces, not from a descriptor.

Integration sidecars may declare what they safely produce:

```json
{
  "schema": "mb.child_repo.v0",
  "role": "integration_sidecar",
  "display_name": "Example analytics sidecar",
  "github_owner": "example-co",
  "repo_name": "example-analytics",
  "safe_purpose": "Produces approved analytics summaries for pushes.",
  "parent": {
    "display_name": "Example Business",
    "github_owner": "example-co",
    "repo_name": "example",
    "remote": "github:example-co/example"
  },
  "linked": {
    "pushes": ["pushes/2026-05-20-workshop-launch/push.md"],
    "decisions": ["decisions/2026-05-08-analytics-boundary.md"]
  },
  "safe_to_share": true
}
```

Raw provider caches, metrics databases, connector glue, and exports stay in the
sidecar repo, provider system, or local state under the appropriate access
boundary. The hub receives approved summaries and links only.

## Agent Routing

Agents should start in the hub for strategy, bets, decisions, offers, routing,
and checkpoint context. Agents should switch to the child repo when editing
that child repo's code, site, product, client deliverable, sidecar, or ops
files.

Before deleting, renaming, merging, or moving an offer folder, child repo, or
topology entry, ask the operator for an explicit decision or migration plan.
