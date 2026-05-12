---
type: educational
topic: hledger
status: draft
last-updated: 2026-05-12
---

# hledger: bookkeeping without leaking raw finance data

hledger is the bookkeeping engine Main Branch chose for `mb books`.
It uses plain-text journals that can be inspected, versioned, reviewed,
and checked by a local command-line tool.

That does not mean raw finance data belongs in every shared business repo.

## When you need this

Use the hledger rail when the business needs durable financial memory:

- revenue and expense summaries;
- offer-level profitability;
- payout and provider reconciliation;
- monthly operating review;
- bookkeeping handoff notes;
- finance decisions that should feed future planning.

## The safe boundary

Recommended pattern:

1. Keep real journals, statements, receipts, and account exports in a private
   books vault, restricted books repo, or accounting system with explicit
   access rules.
2. Keep business-readable summaries in the main business repo.
3. Link decisions, offers, pushes, and outcomes to the relevant safe summary.
4. Never commit bank credentials, account numbers, tax IDs, payroll rows,
   customer-private rows, or secrets.

For solo local use, the default private books vault path is:

```text
.mb/private/books/
```

The business repo should ignore `.mb/private/`, `*.journal`, `*.hledger`, and
`*.ledger` so real books do not enter shared history by accident.

## What `mb books` checks

Run this from a business repo:

```bash
mb books check
```

The current check validates Main Branch's safe bookkeeping metadata and private
books vault guardrails. It does not require hledger to be installed unless you
opt into validating the bundled fake fixture:

```bash
mb books check --fixture
```

## Why not a normal accounting SaaS only?

Accounting SaaS can be useful and may still be required for bookkeeping, tax,
payroll, or accountant collaboration. The Main Branch concern is operating
memory: can the business inspect the financial lesson later, connect it to the
offer or push, and preserve the decision in a repo-backed way?

Plain-text summaries and hledger journals make that possible without forcing
every operator into a vendor-specific dashboard.

## What Main Branch does not claim

Main Branch does not provide accounting, tax, legal, or financial advice.
hledger is optional for base Main Branch installs, and `mb books` does not
automate bookkeeping end to end today.

When in doubt, store less raw finance data in the shared repo and more safe
summary context for business decisions.
