---
type: decision
date: 2026-05-11
status: accepted
topic: mb books foundation and safe ledger contract
linked_issues:
  - https://github.com/noontide-co/mainbranch/issues/483
  - https://github.com/noontide-co/mainbranch/issues/128
linked_decisions:
  - decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md
  - decisions/2026-05-04-sidecar-enrichment-cli-contract.md
  - decisions/2026-05-08-business-repo-topology-map.md
linked_docs:
  - docs/books.md
  - docs/dependency-choices.md
  - docs/system-architecture.md
  - docs/reports/2026-05-11-hledger-vs-beancount-fit.md
participants: [Devon, Claude]
tags: [books, finance, hledger, safety, foundation]
---

# mb books foundation and safe ledger contract

## Decision

**Main Branch uses hledger as the bookkeeping engine for `mb books`.**
The hledger journal is the only authoritative ledger. hledger is
optional for base `mb` installs, but it is the chosen bookkeeping
engine when using `mb books`.

CSV and SQLite can be import staging, source snapshots, caches, or
report outputs. They are not the books.

`mb books` is a planned command group whose first responsibility is to
validate that a business repo carries **safe bookkeeping metadata**, not
to read or write real ledgers. Main Branch owns the operator workflow
and wraps hledger in plain-language commands. Real financial ledgers
stay local and gitignored by default. The team-visible business repo
commits only safe metadata, fake fixtures, and documentation.

The product stance:

- bookkeeping is a Ship loop with stricter data boundaries than the rest
  of the business repo;
- real ledgers, statement exports, account identifiers, payroll detail,
  tax records, and customer/member payment data live in a private
  `finance` child repo, a private business repo, a provider account, or
  local encrypted storage;
- `mb books` starts as a check/contract surface and earns deeper
  surfaces (`summarize`, `import`, `reconcile`, `close`, `report`) only
  behind accepted decisions and smoke evidence;
- nothing in this decision promises a QuickBooks, Xero, or bookkeeper
  replacement.

This decision codifies the foundation and names the first `mb books`
surface. It does not ship the command. Implementation lands in a
follow-up issue that references this decision.

## Why hledger

Main Branch evaluated hledger, Beancount v3, Ledger CLI, and the
CSV/SQLite option against current primary sources, weighted for the
10-year regret bar (multi-business durability, maintenance velocity,
installability, built-in CSV import, built-in reports, plain-text
durability, operator practicality). hledger won. The full evaluation
is in
[docs/reports/2026-05-11-hledger-vs-beancount-fit.md](../docs/reports/2026-05-11-hledger-vs-beancount-fit.md).

The reasons that decided it:

- **CSV import is built in.** `hledger import` with `.rules` files is
  in core. Beancount's v3 cutover moved importers to a separate
  project (`beangulp`), so a Beancount operator pays for the
  ecosystem split every time they categorise bank rows.
- **Reports are built in.** `hledger balance`, `balancesheet`,
  `balancesheetequity`, `cashflow`, `incomestatement`, `register`,
  and `aregister` all ship in the same binary. Beancount's
  `bean-report` is deprecated in v3; reporting now needs `beanquery`
  or external tooling.
- **JSON output is first class.** Every major hledger report supports
  `-O json` (documented in `hledger/hledger.m4.md` §690–935), which
  matters for Main Branch's agent-driven workflows. Beancount's
  machine output is ecosystem-dependent.
- **Single-binary install.** hledger ships as a pre-built binary;
  the operator does not pay for Python version drift or a flex/bison
  source build. Plain-text durability for the next 10 years is
  cleaner when the engine is one boring binary.
- **Maintenance velocity.** Releases `1.99.2` and `1.52.1` both
  dated 2026-04-28 (from `doc/CHANGES.md` in the upstream hledger
  repo). Actively maintained on a frequent cadence.
- **Built-in optional viewer.** `hledger-web` ships in the same
  project at the same version. No third-party UI dependency for the
  optional viewer.

The one Beancount-favouring criterion — stricter defaults — is real
but small compared to the four ways the v3 ecosystem split makes
operators pay over time. hledger supports balance assertions and
account-type discipline; Main Branch's own `mb books check` adds
enforcement on top.

## Why hledger Stays Optional

`mb` is a deterministic control plane that has to install and run for
operators who do no bookkeeping. hledger must not be a hard install
dependency:

- **Audience.** Many operators will never run `mb books`. The base
  install must not pay for what they do not use.
- **License.** hledger is `GPL-3.0-or-later`; Main Branch is MIT. The
  shell-out boundary keeps Main Branch's licence clean. `mb` core
  does not depend on the hledger Haskell ecosystem.
- **Toolchain.** Pre-built hledger binaries are easy, but a source
  build needs GHC. Either way the base `mb` install should not pull
  it in.

## How hledger Plugs Into `mb`

Three layers, in this order of preference:

1. **Main Branch metadata wrapper (this slice).** `mb books check`
   validates Main Branch's own bookkeeping contract: the policy file,
   the chart-of-accounts shape, gitignore guardrails, and fake fixture
   conformance. Runs without hledger installed.
2. **Shell-out sidecar (future).** When an operator wants ledger
   validation, an optional sidecar runs `hledger -f <journal>
   check`, `hledger balance -O json`, or similar and returns an
   `mb.sidecar.context.v1`-shaped envelope per the
   [sidecar enrichment CLI contract](2026-05-04-sidecar-enrichment-cli-contract.md).
   Raw ledger output stays outside tracked business files. `mb` reads
   hledger's structured `-O json` / `-O csv` output, never scrapes
   terminal-formatted output.
3. **Library bindings: declined for `mb` core.** No Python or
   Haskell hledger library bindings in `mb` core. Adapter sidecar
   implementations may import upstream libraries internally; `mb`
   core must not. The shell-out boundary is what keeps the licence
   and install profile clean.

## Optional Extras Packaging (Planned, Not Shipped)

When `mb books check` ships, the implementation issue should consider
exposing the deeper-validation paths as a small optional extra:

```bash
pip install "mainbranch[books]"
# or:
uv tool install "mainbranch[books]"
```

The first extra to land should be minimal — just whatever Python-side
helper code `mb` needs to shell out to `hledger` cleanly. The base
`mainbranch` install must continue to work, onboard, validate, and
report without it. Importers, deeper reports, and a viewer are not
add-ons that this decision commits to ship.

## Safe Path Contract

The team-visible business repo commits only safe metadata. Real ledger
files do not live here by default.

Safe (committable, business repo):

```text
core/finance/books.md             # bookkeeping policy and ledger-location pointer
core/finance/chart-of-accounts.md # operator-friendly account-naming description
```

Both files are optional in the v0 contract. A business repo without
them is valid; `mb books check` reports their absence as a
recommendation, not an error.

Real ledger material (private; not in the team-visible business repo):

```text
ledger/main.journal               # operator's actual hledger journal
ledger/                            # account, transaction, balance source files
imports/                           # raw bank/credit-card/payment-processor exports + .rules
statements/                        # PDF/CSV/OFX/QBO downloads
reconciliations/                   # reconciliation working notes
tax/                               # tax-year working files and exports
```

Real ledger material lives in:

1. a **private `finance` child repo** (the topology role already named
   in
   [docs/system-architecture.md](../docs/system-architecture.md));
2. a **local-only path outside any tracked repo**, with disk
   encryption where appropriate;
3. a **private business repo**, only when a solo operator has made an
   explicit decision that team visibility never expands.

`core/finance/books.md` points at whichever location the operator
chose, without copying its contents into the business repo. A sample
frontmatter shape (advisory, not yet enforced):

```yaml
---
type: books
ledger: hledger
operating_currency: USD
fiscal_year_start: "01-01"
reporting_cadence: monthly
ledger_location: private-finance-repo   # or: local-only, private-business-repo
ledger_pointer: "private (not committed)"
class_b_data: true
---
```

`ledger_pointer` is a human description, not a path that resolves on
disk in this repo. `mb books check` should refuse to dereference it.

## Class B Examples For Bookkeeping

The
[workspace, repo, and sensitive-data boundary decision](2026-05-04-workspace-repo-sensitive-data-boundaries.md)
already defines the general Class B rule. `mb books` inherits and
sharpens it. The following are Class B in a bookkeeping context and
must not be committed to a team-visible business repo:

- raw ledger transaction rows in any format
  (`*.journal`, `*.hledger`, `*.ledger`, `*.beancount`, etc.);
- bank, credit-card, payment-processor, and merchant-account exports
  (`*.csv`, `*.ofx`, `*.qfx`, `*.qbo`, `*.qif`, `*.pdf`);
- account numbers, routing numbers, card numbers, and provider
  account identifiers tied to real customers/members/vendors;
- payroll runs, employee compensation rows, contractor 1099 detail;
- tax-return data, tax-withholding ledgers, sales-tax filings;
- vendor/customer payment history at row granularity;
- owner draws, distributions, equity events tied to real individuals;
- invoices, contracts, dispute records, and legal-finance
  correspondence;
- any aggregate that would re-identify a real customer or vendor when
  combined with other fields.

These items belong in a private finance repo, a provider account, or
local encrypted storage. `mb books check` should treat any of these
shapes appearing under `core/finance/` (or anywhere in a team-visible
business repo) as a defect to surface.

## Fixtures Vs Real Ledgers

A **fake fixture** is a small `.journal` file with no real data. It
exists in this engine repo to exercise the validation contract and to
give operators a copy-paste starting point.

A **real ledger** is the operator's actual bookkeeping. It never lives
in this engine repo and does not live in the team-visible business
repo by default.

The fixtures shipped with Main Branch must:

- use an obviously fake business name (`Acme`, `Test Co`,
  `Fixture Inc`, etc.);
- use only the conventional plain-text-accounting roots (`assets`,
  `liabilities`, `equity`, `income`, `expenses`) pinned with hledger
  `account ... ; type:<letter>` directives;
- declare one placeholder operating currency (`USD` is fine);
- include a header comment naming the file as a sample, not a real
  ledger;
- contain no Devon-local, vendor, customer, member, payroll, or tax
  data;
- stay small enough to read at a glance.

The first fixture lives under `docs/examples/books/`. Packaging it
into `mb/mb/_data/` is a follow-up concern when `mb books check`
ships.

## First `mb books` Surface

The first command, deferred to a follow-up implementation issue, is:

```text
mb books check [--json]
```

What it must do:

- detect whether `core/finance/books.md` exists and parses as expected
  frontmatter (when present);
- detect whether `core/finance/chart-of-accounts.md` exists and
  follows the documented account-naming convention (when present);
- warn when files with extensions `.journal`, `.hledger`, `.ledger`,
  `.beancount`, `.csv`, `.ofx`, `.qfx`, `.qbo`, `.qif`, or
  statement-shaped PDFs are committed under `core/finance/` (likely
  real data leak) unless the file is explicitly marked as a fixture
  in frontmatter or a sibling sample manifest;
- when an operator opts in and hledger is installed, validate a fake
  `.journal` fixture by shelling out to
  `hledger -f <fixture> check -O json` and reading the structured
  output;
- print exact repair commands and a link to `docs/books.md` when a
  check fails;
- emit an `mb` JSON envelope when `--json` is passed, matching the
  pattern used by `mb doctor` / `mb validate`.

What it must not do in the first surface:

- run real imports, reconciliation, month-close, P&L, balance sheet,
  cash-flow, or tax claims;
- import any hledger or other ledger library directly into `mb`
  core;
- scrape human-formatted terminal output from any tool when a
  structured (`-O json` / `-O csv`) path exists;
- parse journal syntax beyond what is needed to recognise an obvious
  fixture vs a real ledger;
- read files outside `core/finance/` (other than the gitignore for
  detection);
- mutate any file.

Exit semantics (advisory; follow-up implementation locks them):

- `0` — checks passed, including the "no real ledger committed" guard;
- `1` — checks failed; the envelope lists each failure and a repair
  command;
- `2` — usage/config error (e.g., `--json` passed with unsupported
  flag combination).

## Non-Goals For This Slice

The following are explicitly out of scope until separate accepted
decisions land:

- real bank, credit-card, or payment-processor importers;
- ledger import from QuickBooks, Xero, Wave, or other accounting
  tools;
- month-end close automation;
- P&L, balance sheet, cash-flow, or tax reporting from real data;
- QuickBooks or bookkeeper replacement claims in any user-facing
  copy;
- tax advice or tax-filing automation;
- payroll runs, contractor payment automation, or 1099 generation;
- provider sync (Plaid, bank APIs, processor APIs);
- scheduled or background imports;
- automatic reconciliation against statements;
- public `hledger-web` deployment or hosted ledger viewing;
- writing ledger files from `mb` (the first surface only reads
  presence/shape).

## hledger-web

`hledger-web` is the optional local viewer that ships with hledger
itself. `docs/books.md` may mention it as the optional local UI for
operators who want one. Main Branch will not start, supervise, proxy,
or detect `hledger-web` in this slice. There is no `mb` command for
it and no readiness check.

## Existing Surfaces To Migrate (Follow-Up)

Earlier Main Branch work landed Beancount-flavoured copy and one
provider entry on the assumption Beancount would be the chosen engine.
This decision supersedes those mentions. The actual migration is
out of scope for this foundation PR; a follow-up issue should sweep:

- `mb/mb/connect.py` — replace the `beancount` provider with an
  `hledger` provider id and metadata fields (`journal_path` rather
  than `ledger_path`). This is a CLI/contract change that needs
  focused CLI tests and a migration path for any existing
  `.mb/connect.yaml` records;
- `mb/mb/educational.py` and
  `mb/mb/_data/educational/beancount.md` — rename to `hledger.md`
  and rewrite;
- `mb/mb/init.py` and
  `mb/mb/_data/templates/.gitignore.tmpl` — add `*.journal` and
  `*.hledger` to the default gitignore in newly initialised business
  repos alongside the existing `*.beancount` line (keep the old
  line for defence in depth against legacy files);
- `docs/ethos.md` running-rails sentence, `docs/system-architecture.md`
  topology row, `docs/dependency-choices.md` running-choices log,
  `docs/operator-loops.md`, and `docs/beginner-setup.md` — update
  the descriptive copy from "Beancount" to "hledger" with one short
  superseded note pointing at this decision.

This decision does the foundation-doc rewrite in this PR and
explicitly leaves the engine code migration to a follow-up so a
foundation slice does not also become a CLI refactor.

## Validation Contract

For this decision slice:

- Level 0 (docs/decision) review is required: frontmatter, links, no
  stale product claims, no private data;
- `scripts/check.sh` (Level 1) must pass before pushing;
- no CLI tests (no CLI behaviour changes);
- no package/install smoke (no packaging changes);
- no fixture-repo smoke (no scaffolding changes);
- no runtime smoke (no skill or runtime changes).

The follow-up implementation issue must add focused CLI tests, a
fixture repo smoke when the check reads a real business repo, and a
package smoke if the fixture is later packaged into `mb/mb/_data/`.

## Consequences

- `mb books` ships with one chosen bookkeeping engine; operators get
  one clear recommendation, not a "choose your ledger" UI.
- Built-in CSV import, built-in reports, and first-class JSON output
  mean fewer add-ons over the next 10 years.
- The licence boundary between Main Branch (MIT) and hledger
  (`GPL-3.0-or-later`) stays clean by routing ledger work through a
  shell-out sidecar.
- The team-visible business repo never accidentally becomes a finance
  database.
- A future P&L dashboard view inherits the same private-source rule:
  data may be summarised into the repo only after the operator opts
  in.
- A follow-up issue tracks the existing-surface migration so this
  foundation does not silently leave Beancount copy contradicting
  it.

## Review Trigger

Revisit this decision only if any of these become true:

- hledger changes licence in a way that closes the shell-out
  boundary, drops the journal format, or removes structured output;
- a sidecar implementation needs a contract change beyond
  `mb.sidecar.context.v1`;
- Main Branch wants to write ledger files (not just read);
- a real-data integration (importers, bank APIs, processor APIs) is
  accepted into core or as a first-party sidecar;
- a hosted P&L or finance-dashboard surface is proposed.
