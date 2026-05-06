# System Architecture

> **Status:** Current architecture reference.
>
> Main Branch is a CLI plus agent-runtime skill system for running a business
> from markdown files in git. This document describes the current public repo
> model after the `core/` folder decision and the campaign primitive decision.

## Architecture In One Sentence

Main Branch keeps canonical business memory in the business repo, uses `mb` as
the deterministic control plane over that repo, and lets runtime skills perform
judgment-heavy work while leaving provider data, secrets, caches, and dashboard
state outside canonical memory.

```text
Main Branch engine     +     business repo            +     optional systems
mb CLI                       core/                          provider APIs
bundled skills               research/                      sidecar databases
validators                   decisions/                     local caches
templates                    bets/                          dashboard views
docs                         campaigns/
                             log/
                             documents/
```

The engine is business-agnostic. The business repo is engine-readable but not
engine-owned. Provider systems and dashboards are inputs or views; they do not
replace the repo.

## Operating Loops

Main Branch architecture follows the four operator loops in
[OPERATOR-LOOPS.md](OPERATOR-LOOPS.md):

- **Sense:** read current state from files, git, GitHub, provider metadata, and
  deterministic `mb` reports.
- **Decide:** choose a bet, priority, offer direction, or repair path.
- **Ship:** produce and release work into the world or into the operating
  system.
- **Reflect:** extract lessons, close bets, update decisions, and improve the
  next Sense pass.

Files are not categories for their own sake. They are durable stations in those
loops.

## Business Repo Shape

A current Main Branch business repo uses this shape:

```text
my-business/
├── CLAUDE.md
├── .gitignore
├── .mb/                         # explicit Main Branch state
├── .claude/                     # local runtime wiring; only worktrees/ ignored
├── core/
│   ├── soul.md
│   ├── offer.md
│   ├── audience.md
│   ├── voice.md
│   ├── content-strategy.md
│   ├── product-ladder.md
│   ├── offers/
│   ├── proof/
│   ├── brand/
│   ├── strategy/
│   ├── operations/
│   └── finance/
├── research/
├── decisions/
├── bets/
├── campaigns/
├── log/
└── documents/
```

The canonical business brain is `core/`. The old committed business-repo
`reference/` folder is compatibility-only for old repos, as defined in
[decisions/2026-05-06-business-repo-folder-model-reference-deprecation.md](../decisions/2026-05-06-business-repo-folder-model-reference-deprecation.md).

## Primitive Contracts

### `core/`

`core/` contains evergreen business truth that skills can read repeatedly:
offer, audience, soul, voice, proof, brand systems, strategy, operations, and
finance boundaries.

Evergreen files do not usually carry dates in the filename. They represent the
current best version of the business, not a point-in-time snapshot.

### `research/`

`research/` contains point-in-time findings from when the operator went
looking. Research can cite source material, but it should synthesize what
matters rather than becoming an indiscriminate capture folder.

Typical files:

```text
research/2026-05-06-competitor-offer-analysis.md
research/2026-05-06-customer-language-review.md
```

### `decisions/`

`decisions/` contains choices with rationale. A decision explains the situation,
options, accepted direction, rejected alternatives, and what files or workflows
change because of it.

Decisions can be proposed before acceptance. Accepted decisions become durable
product or business truth until superseded.

### `bets/`

`bets/` contains time-boxed operating hypotheses: what the operator will try,
why it might work, by when, and how success or failure will be judged.

A bet is usually Decide -> Ship -> Reflect. It may lead to a campaign, an offer
change, a workflow, a content pillar, a provider setup, or a decision.

### `campaigns/`

`campaigns/` contains coordinated pushes that ship work into the world or into
an adoption surface. A campaign is not a generic generated-artifact bucket.

A campaign has:

- a named goal or outcome;
- a recipient or audience, including internal stakeholders for Ops adoption
  campaigns;
- one or more distribution or adoption channels;
- a bounded time window or review moment;
- artifacts and actions that belong to the same push;
- links to the bets, offers, strategy, decisions, research, logs, and provider
  data that explain or measure it.

Examples that qualify:

- paid ad push;
- organic content sequence;
- email or newsletter launch sequence;
- site or landing-page launch;
- community activation push;
- partner or outreach push;
- product, offer, waitlist, beta, or event announcement;
- internal adoption or migration push with a clear goal, owner, timeline, and
  outcome.

Examples that do not qualify by themselves:

- raw transcripts;
- one-off code experiments;
- provider exports;
- raw analytics tables;
- loose session recovery notes;
- PR review notes for the engine;
- archived repo dumps;
- generated artifacts with no named push or outcome.

#### Campaign Folder Shape

The conventional campaign shape is:

```text
campaigns/
  2026-05-workshop-waitlist/
    campaign.md
    ads.md
    emails.md
    posts.md
    site.md
    review-log.md
    assets/
    source/
```

The folder name gives humans chronological scanability. `campaign.md` is the
record. Other files are campaign artifacts, source notes used by the campaign,
operator review notes, or asset references for that same push.

For larger campaigns, typed subfolders are acceptable:

```text
campaigns/2026-05-workshop-waitlist/
  campaign.md
  ads/
  emails/
  posts/
  site/
  reviews/
  assets/
  source/
```

Do not create a campaign folder just because a file was generated. If the work
does not have a campaign goal, put it in the primitive that owns it.

#### Campaign Record

Recommended `campaign.md` frontmatter:

```yaml
---
type: campaign
slug: workshop-waitlist
status: active
goal: "40 qualified waitlist signups"
channels: [paid, email, pages]
started: 2026-05-06
review_on: 2026-05-20
linked_strategy:
  - core/content-strategy.md
linked_offers:
  - core/offers/workshop/offer.md
linked_bets:
  - bets/2026-05-06-workshop-waitlist.md
linked_decisions:
  - decisions/2026-05-06-workshop-price.md
linked_research: []
provider_refs:
  meta_ads:
    campaign_id: "example-placeholder"
metrics_sources:
  - ".mb/sidecars/meta-ads/workshop-waitlist.sqlite"
---
```

The current validator only enforces a smaller subset. The frontmatter above is
the architecture target for follow-up CLI, graph, status, skill, and migration
work.

Campaign status should map to operator loops:

| Status | Loop meaning |
| --- | --- |
| `draft` | Decide is still forming the push. |
| `planned` | Decide is complete; Ship has not started. |
| `active` | Ship is underway. |
| `paused` | Sense or Decide must resolve a blocker. |
| `completed` | Ship is done; Reflect should evaluate it. |
| `canceled` | The push was intentionally stopped. |
| `archived` | Historical record only. |

`channels` should start as a loose, validation-hinted list rather than a hard
enum. Main Branch can recognize common slugs such as `paid`, `organic`,
`email`, `pages`, `community`, `partner`, `outreach`, and `ops`, while warning
instead of failing when a business needs a more specific channel.

### `log/`

`log/` contains what happened: daily records, session summaries, recovery notes,
operator handoffs, and non-decision work records.

Use `log/` when the durable value is chronology and recovery rather than a
research finding, accepted decision, bet, or campaign artifact.

### `documents/`

`documents/` contains supporting material that is durable enough to keep but
not itself core truth, research synthesis, a decision, a bet, a campaign, or a
log entry.

Blessed conventional subfolders:

```text
documents/transcripts/   # raw or lightly cleaned source transcripts
documents/prototypes/    # throwaway code, HTML, images, scripts, or demos
documents/archive/       # inert legacy imports or reference dumps
```

Use separate repos when a prototype, site, app, offer, finance surface, or
archive graduates into its own operating boundary.

## Artifact Routing

Use this routing rule when deciding where generated work belongs:

| Artifact | Canonical home |
| --- | --- |
| Paid ad batch tied to a named push | `campaigns/<campaign>/ads/...` |
| Organic sequence tied to a named push | `campaigns/<campaign>/posts/...` |
| Email or newsletter launch sequence | `campaigns/<campaign>/emails/...` |
| Landing-page launch record | `campaigns/<campaign>/site.md` or child site repo |
| Campaign review notes | `campaigns/<campaign>/review-log.md` or `reviews/` |
| Raw transcript or source capture | `documents/transcripts/...` |
| Synthesized findings from source material | `research/YYYY-MM-DD-slug.md` |
| Throwaway code, HTML, script, or image experiment | `documents/prototypes/...` |
| Operational site, app, or offer repo | separate child repo with links back |
| Session recovery or daily work record | `log/YYYY-MM-DD.md` |
| Accepted architecture or product choice | `decisions/YYYY-MM-DD-slug.md` |
| Engine coordination or review | GitHub issue or pull request |
| Inert legacy import | `documents/archive/...` or separate archive repo |
| Local cruft | ignored or deleted, not migrated |

Legacy `outputs/` content should not be bulk-moved into `campaigns/`.
Ambiguous items need an operator review path through migration or doctor repair.

## Relationship Model

The core relationship model is:

```text
strategy decides where we should push
bet defines what we are trying to learn
offer defines what we are selling
campaign coordinates the push
provider data records what happened
research / decision / log captures what we learned or changed
```

In practice:

- Strategy lives in `core/content-strategy.md` or additional `core/strategy/...`
  files.
- Offers live in `core/offer.md` and `core/offers/...`.
- Bets live in `bets/...` and can link to one or more campaigns.
- Campaigns link back to bets, offers, decisions, research, and strategy.
- Provider refs identify external campaign/account objects without copying raw
  provider data into the business repo.
- Metrics sources point to provider APIs, local sidecars, `.mb/` caches,
  private analytics stores, or exported files under a boundary the operator has
  intentionally chosen.
- Reflection usually lands in a bet verdict, research note, decision update,
  campaign review log, or `log/` entry.

## State Boundaries

Canonical business state:

- `core/`
- `research/`
- `decisions/`
- `bets/`
- `campaigns/`
- `log/`
- `documents/`
- git history
- GitHub issues and pull requests

Local operational state:

- `.mb/` caches, indexes, schema markers, repair backups, and local connection
  metadata;
- `.claude/settings.local.json` and runtime wiring;
- runtime-specific local files;
- OS keychain, environment variables, 1Password, or other secret stores.

External or optional state:

- provider APIs;
- local SQLite sidecars;
- private analytics or finance repos;
- exported CSVs in private storage;
- future dashboard indexes.

Secrets, bearer tokens, OAuth refresh tokens, service-account JSON, customer
exports, raw member data, and sensitive finance/legal data do not belong in
public examples or committed business repo files.

## `mb` Responsibilities

`mb` is the deterministic control plane. It owns:

- repo scaffolding through `mb onboard` and `mb init`;
- repo health through `mb doctor`;
- safe reconciliation through `mb doctor repair`;
- frontmatter and cross-reference checks through `mb validate`;
- graph output through `mb graph`;
- daily facts and next-action substrate through `mb status` and `mb start`;
- provider metadata through `mb connect`;
- update and migration paths through `mb update` and `mb migrate`;
- skill discovery and repair through `mb skill`;
- git checkpoint plans and guarded commits through `mb checkpoint`.

`mb` should stay inspectable, scriptable, and exit-coded. It should expose JSON
where skills, dashboards, or future adapters need stable facts.

## Skill Responsibilities

Runtime skills own judgment-heavy work:

- asking the operator the right question;
- interpreting business context;
- drafting research, decisions, bets, campaign artifacts, and review notes;
- routing generated work to the right primitive;
- calling deterministic `mb` commands for facts instead of reimplementing repo
  health probes in prose;
- keeping runtime claims honest.

Claude Code is the supported runtime today. Other runtimes are compatibility
targets until adapter code and smoke evidence exist.

## Provider, Sidecar, And Dashboard Boundaries

Provider systems record live operational facts. Sidecars can enrich Main Branch
with structured data. Dashboards can make repo and provider truth easier to
see.

They remain optional and non-canonical unless a future accepted decision says
otherwise.

Correct pattern:

```text
campaigns/2026-05-workshop-waitlist/campaign.md
  provider_refs.meta_ads.campaign_id -> provider object
  metrics_sources[] -> sidecar/cache/private analytics source

mb status / dashboard
  reads campaign.md, graph, git, GitHub, and provider-safe summaries
  displays facts and recommendations
```

Incorrect pattern:

```text
campaign.md becomes a raw ads database
dashboard database becomes the only place campaign truth exists
.mb/cache is treated as business memory
```

## Graph And Status

`mb graph` should index durable markdown relationships: linked decisions,
research, bets, campaigns, offers, outcomes, and documents.

`mb status` should read those same durable relationships plus cheap local facts
to answer:

- what is stale;
- what is active;
- what changed since last check;
- which campaigns need Ship or Reflect attention;
- which bets lack linked campaign work;
- which provider or sidecar signals need operator review.

The status and graph surfaces should consume the campaign primitive instead of
inventing a separate campaign model.

## Validation And Migration

The validation ladder is in [AGENTS.md](../AGENTS.md). The short rule is:
prove the surface you changed.

- Docs and decisions need public/private review and link sanity.
- CLI behavior needs focused tests and exit-code/JSON coverage.
- Packaging, templates, bundled data, or skill discovery need install smoke.
- First-run or repo-shape changes need fixture repo smoke.
- Runtime discovery or LLM-facing workflow changes need runtime smoke, or an
  explicit blocker note.

Migration should preserve user-authored content, distinguish compatibility
bridges from split truth, and leave ambiguous legacy `outputs/` artifacts for
operator review rather than silently classifying them.

## Superseded Model

Older architecture notes used `reference/`, `domain/`, `.vip/local.yaml`, and
`outputs/` as central concepts. Those names can still appear in compatibility
code, migration guidance, or historical decisions, but current public
architecture is:

- `core/` for evergreen business truth;
- `campaigns/` for coordinated pushes;
- `documents/` for supporting/raw/prototype/archive material;
- `.mb/` for explicit local Main Branch state;
- provider/sidecar/dashboard state outside canonical memory unless explicitly
  linked and bounded.
