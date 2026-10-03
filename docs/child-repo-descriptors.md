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
| `role` | What the repo *is* (see [The repo tree](#the-repo-tree)): `business`, `site`, `offer`, `product`, `client`, `finance`, `legal`, `ops`, `integration_sidecar`, `experiment`, or `archive`. |
| `display_name` | Human-readable child repo name. This is not the GitHub repo name. |
| `github_owner` / `repo_name` | Durable technical handle for this child repo. |
| `safe_purpose` | Public-safe reason the child repo exists. |
| `parent` | Safe hub reference. Include GitHub owner/repo distinctly from display name. |
| `parent.local_checkout` | Optional relative checkout hint from the child repo to the hub. Do not commit absolute local paths. |
| `linked` | Safe handles to hub business primitives. Use repo-relative hub paths. |
| `return_to_hub_command` | Optional exact command when a sibling checkout makes it safe and useful. Prefer relative paths. |
| `safe_to_share` | Whether this descriptor is intended to be safe for the child repo's normal audience. This does not grant access. |

## Sites: several sites in one repo

`role: site` describes one repo. A repo that holds several sites (one shared
engine plus a folder per client, for example) lists them in an optional
`sites` array:

```json
{
  "schema": "mb.child_repo.v0",
  "role": "site",
  "display_name": "Acme client sites",
  "github_owner": "example-co",
  "repo_name": "acme-sites",
  "parent": {"github_owner": "example-co", "repo_name": "example"},
  "sites": [
    {
      "slug": "alpha",
      "display_name": "Alpha",
      "dir": "clients/alpha",
      "domains": ["alpha.example"],
      "deploy": {"provider": "cloudflare-pages", "project": "alpha-site"},
      "lifecycle": "active"
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `slug` | Lowercase id, unique in the repo. `mb site check --site <slug>` uses it. |
| `display_name` | Human-readable site name. |
| `dir` | The site's folder, relative to the repo root (`.` for the root). It must exist and stay inside the repo. |
| `domains` | Domains the site serves. |
| `deploy` | `provider` (today `cloudflare-pages`) and `project`, the provider's project name. |
| `lifecycle` | Same values as the registry: `proposed`, `active`, `paused`, `superseded`, `archived`. |

Rules:

- The list is optional and backward compatible: an older `mb` ignores it, and
  the schema stays `mb.child_repo.v0`.
- Every value is a string (or a list of strings for `domains`). No other keys
  are accepted, and key names must pass the same sensitive-key filter as the
  hub registry: that is why the folder is `dir`, not `data_path`.
- Contacts, prices, contracts and anything else private stay in the hub, never
  in the descriptor.
- A bad entry is dropped and reported as `topology_descriptor_sites_invalid` in
  `mb status` and `mb doctor`; the rest of the descriptor still counts.

Check one site:

```bash
mb site check . --site alpha --json
```

The descriptor and the source link are read from the repo root; the
conversion plan (`.mainbranch/conversion.json`) and the built HTML come from
the site's `dir`. An unknown slug exits `2` and names the slugs the repo lists.

[`mb fleet`](fleet.md) reads `sites` to give each site its own row: framework,
engine pin, CI and what is live.

## The repo tree

One sentence holds the whole model:

> Every repo has a **`role`** (what it is) and a **`parent`** (what it hangs
> under). The hub is the root. Children can have children.

`role` is the single classifier — it answers "what kind of repo is this?" There
is no separate "profile"; `mb` reads `role` to decide what to check.

`parent` is a position, not a kind. "Child repo" is **not** a role — any role
can be a child of any other. Repos form a tree:

```
hub (role: business, no parent)
└── offer repo        (role: offer,  parent: hub)
    └── offer's site  (role: site,   parent: offer repo)
└── finance repo      (role: finance, parent: hub, visibility: restricted)
```

So a graduated offer is a child of the hub, and the website you build for that
offer is a child of the offer repo — arbitrary depth, each node a `role` + a
`parent`.

The roles:

| Role | What it is |
| --- | --- |
| `business` | The hub: strategy, offers, bets, pushes, decisions, the root of the tree. |
| `site` | A deployed website, lander, minisite, or docs/bet feed. |
| `offer` | A durable offer or productized service with its own operating history. |
| `product` | A software product, tool, template, or course with its own build lifecycle. |
| `client` | Fulfillment/deliverables with a separate confidentiality boundary. |
| `finance` | Ledgers, bookkeeping, tax, payroll, P&L sources. Private. |
| `legal` | Contracts, disputes, entity docs, legal review. Private. |
| `ops` | Infrastructure, runbooks, internal routines, provider setup. |
| `integration_sidecar` | A helper repo that emits approved provider/analytics summaries. |
| `experiment` | Exploratory work that may graduate, pause, or die. |
| `archive` | Retired or historical material kept for reference. |

`role`, `lifecycle`, `visibility`, and `relationship` are independent axes — a
`site` can be public or private; a `finance` repo is private regardless of
lifecycle.

### Declaring the role is required

`mb status` / `mb doctor` flag a Main Branch checkout that has **no role**
declared (finding `topology_role_not_identified`) and point here. If on-disk
signals look like a site or a hub, the flag includes that as a *suggestion* — the
CLI never sets the role silently; the operator (with the agent's help) declares
it in `.mainbranch/repo.json` (child) or the hub's
`core/operations/repo-topology.md` entry.

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

`mb site check` also guards against a copied site folder that still names a
different business: it compares the descriptor's `parent` owner/repo with the
business repo's own `.mainbranch/repo.json`, or, when that has no owner/repo,
with the business repo's git `origin` remote. A mismatch blocks the check.

## How mb tells repo kinds apart

Every command that needs to know what kind of repo it is in asks one
classifier. It returns `hub`, `child`, `engine` or `none`, plus the file that
decided it, checking in this order:

1. a valid child descriptor: `.mainbranch/repo.json` with a known `role`
   (`role: business` counts as a hub), or the legacy site `source.json`;
2. the hub registry, `core/operations/repo-topology.md`;
3. the Main Branch engine checkout;
4. the older hub shape: `CLAUDE.md` plus `core/`, `research/` or `decisions/`.

So a product repo that keeps its own `CLAUDE.md` and `research/` is a child,
not a second hub. `mb doctor` and `mb checkpoint` accept a hub or a child.

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

`mb status --json --peek`, `mb start --json`, and onboarding expose a
`repo_boundary` helper that keeps the choice small:

- use the same business repo when brand, team, voice, access, accounts, and
  operating history are shared;
- create a separate business repo when the work has its own entity, team,
  accounts, audience, brand, or operating history;
- create a child repo when the work is an execution surface for the business,
  such as a site, product, client deliverable, finance/legal boundary, ops repo,
  or integration sidecar. A child repo can itself have children (e.g. a site
  under an offer); each declares its own `role` and `parent`.

Before deleting, renaming, merging, or moving an offer folder, child repo, or
topology entry, ask the operator for an explicit decision or migration plan.
