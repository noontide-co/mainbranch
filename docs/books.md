# Books

This page describes how Main Branch treats bookkeeping today. It is the
operator-facing companion to
[the mb books foundation decision](../decisions/2026-05-11-mb-books-foundation.md).

## The Short Version

- Main Branch will eventually have an `mb books` command group. The first
  surface (`mb books check`) is planned, not shipped.
- **Main Branch uses hledger as the bookkeeping engine for `mb books`.**
  The hledger journal is the only authoritative ledger.
- hledger is **optional** for base `mb` installs, but it is the chosen
  bookkeeping engine when using `mb books`. `mb` does not require hledger
  to install, onboard, or run.
- CSV and SQLite are import staging, source snapshots, caches, or report
  outputs. They are not the books.
- Real ledgers, statements, payroll, tax data, and account identifiers are
  **Class B data** and never belong in a team-visible business repo by
  default.
- The team-visible business repo holds only safe bookkeeping metadata: a
  policy file, a chart-of-accounts description, and links to wherever the
  real ledger actually lives.

## What Lives Where

### In the business repo (safe to commit)

```text
core/finance/books.md             # bookkeeping policy + pointer to the real ledger
core/finance/chart-of-accounts.md # account-naming convention
```

Both files are optional. A business repo with neither is still valid. When
present, they describe how the operator runs the books — not what the
numbers are.

`core/finance/books.md` is a small policy file. A starting shape
(advisory, not yet enforced):

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

# Books

This business uses an hledger journal kept in a private finance repo.
This file is the public-safe pointer. The journal itself is not committed.
```

`core/finance/chart-of-accounts.md` describes the account roots the
operator uses (`assets`, `liabilities`, `equity`, `income`, `expenses`)
and the naming convention beneath them. It does not list real account
numbers, balances, or specific institution names tied to live accounts.

### Outside the business repo (Class B; never committed here)

The real ledger and its source material live in one of three places, by
operator choice:

1. **A private `finance` child repo** — separate GitHub private repo or
   self-hosted git. This is the topology role already described in
   [system-architecture.md](system-architecture.md).
2. **A local-only path outside any tracked repo**, with disk encryption
   where appropriate.
3. **A private business repo** — only when a solo operator has explicitly
   decided that team visibility never expands.

Inside whichever location the operator chose, the durable shape is:

```text
ledger/main.journal           # the actual hledger journal
ledger/                        # additional account/period files
imports/                       # raw bank/credit-card/payment-processor exports + .rules
statements/                    # downloaded PDFs/CSVs from institutions
reconciliations/               # working notes per reconcile pass
tax/                           # tax-year working files
```

None of these paths are tracked by the team-visible business repo. They
are written to whichever repo or local path actually owns the data.

## Class B Examples For Bookkeeping

The following are Class B and must not be committed to a team-visible
business repo:

- raw ledger transaction rows in any format
  (`*.journal`, `*.hledger`, `*.ledger`, `*.beancount`);
- bank, credit-card, payment-processor, merchant-account exports
  (`*.csv`, `*.ofx`, `*.qfx`, `*.qbo`, `*.qif`, statement-shaped PDFs);
- account numbers, routing numbers, card numbers, provider account
  identifiers tied to real customers/members/vendors;
- payroll runs, employee compensation rows, contractor 1099 detail;
- tax-return data, tax-withholding ledgers, sales-tax filings;
- vendor/customer payment history at row granularity;
- owner draws, distributions, equity events tied to real individuals;
- invoices, contracts, dispute records, legal-finance correspondence;
- anything that would re-identify a real customer or vendor when
  combined with other fields in the repo.

These prohibitions inherit from the accepted
[workspace and sensitive-data boundary](../decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md);
`mb books` sharpens them.

## Fixtures Vs Real Ledgers

A **fake fixture** is a small, obviously-fake `.journal` file used to
exercise the `mb books` contract and to give operators a starting shape.
This engine repo ships one under
[`docs/examples/books/`](examples/books/).

A **real ledger** is the operator's actual bookkeeping. It never lives in
this engine repo and does not live in the team-visible business repo by
default.

Telling them apart should be easy:

- the company name is obviously fake (`Acme`, `Test Co`, `Fixture Inc`);
- the file is small (a chart-of-accounts, opening balances, a handful of
  transactions, maybe one balance assertion);
- a header comment names the file as a sample.

When `mb books check` ships, it will treat anything that looks like a
real ledger committed under `core/finance/` as a defect, not a feature.

## Optional Local Viewer

`hledger-web` is an optional local web viewer that ships with hledger
itself. Install and run it yourself if you want a UI over your journal;
Main Branch does not start, supervise, proxy, or detect `hledger-web`.
There is no `mb` command for it.

## What `mb books` Does Today

`mb books` is not a shipped command group yet. When the first surface
lands, it will be `mb books check`, and it will:

- detect whether `core/finance/books.md` exists and parses;
- detect whether `core/finance/chart-of-accounts.md` exists and follows
  the documented convention;
- warn when files that look like real ledgers or statement exports are
  committed under `core/finance/` (likely Class B leak);
- when an operator opts in and hledger is installed, validate a fake
  `.journal` fixture by shelling out to `hledger ... -O json` and
  reading the structured output;
- print exact repair commands when something is off;
- emit a JSON envelope with `--json` for scripts and skills.

It will **not**:

- run real imports, reconciliation, month-close, P&L, balance sheet,
  cash-flow, or tax claims;
- import the hledger library directly into `mb`;
- scrape human terminal output when structured output exists;
- read files outside `core/finance/` (other than the gitignore for
  detection);
- mutate any file.

The full first-surface spec lives in
[the mb books foundation decision](../decisions/2026-05-11-mb-books-foundation.md).

## What `mb books` Will Not Do (Until Separate Decisions Land)

- replace QuickBooks, Xero, Wave, or a human bookkeeper;
- give tax advice;
- run payroll;
- import from real banks, credit cards, or payment processors;
- reconcile statements automatically;
- close months automatically;
- generate financial reports from real data;
- sync with provider APIs;
- run scheduled imports.

Each of those is a separate scope conversation. The current foundation
makes those conversations possible without committing anything sensitive
in the meantime.

## When You Are Ready To Keep A Real Ledger

The setup path, when the time comes:

1. Decide where the real ledger lives. A private `finance` child repo is
   the cleanest default for most operators; a local-only path is fine
   for small solo setups.
2. Install hledger yourself (download the pre-built binary or the
   install path your environment prefers). Main Branch does not install
   it for you.
3. Optionally install / run `hledger-web` for a local UI.
4. In your business repo, add `core/finance/books.md` with the pointer
   shape shown above. Do not paste the journal contents in.
5. Optionally add `core/finance/chart-of-accounts.md` describing your
   account-naming convention.
6. When `mb books check` ships, run it to make sure the metadata is
   well-formed and nothing Class B has leaked into the business repo.

## Related

- [mb books foundation decision](../decisions/2026-05-11-mb-books-foundation.md)
- [hledger vs Beancount fit report](reports/2026-05-11-hledger-vs-beancount-fit.md)
- [Workspace and sensitive-data boundary](../decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md)
- [Sidecar enrichment CLI contract](../decisions/2026-05-04-sidecar-enrichment-cli-contract.md)
- [System architecture: topology and `core/finance/`](system-architecture.md)
- [Dependency choices](dependency-choices.md)
