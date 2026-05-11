---
type: books
ledger: hledger
operating_currency: USD
fiscal_year_start: "01-01"
reporting_cadence: monthly
ledger_location: private-finance-repo
ledger_pointer: "private (not committed)"
class_b_data: true
---

# Books — Sample

> Sample file. Not a real bookkeeping policy. See
> [docs/books.md](../../books.md) for the operator-facing description and
> [decisions/2026-05-11-mb-books-foundation.md](../../../decisions/2026-05-11-mb-books-foundation.md)
> for the contract.

This is what a real `core/finance/books.md` would look like in a business
repo for a fictional company that keeps its ledger in a private finance
child repo.

## Ledger Location

The real hledger journal lives in a private finance child repo. This file
points at that repo without copying its contents.

- Engine: hledger
- Authoritative file: `ledger/main.journal` in a private finance repo
- Operating currency: USD
- Fiscal year: calendar year
- Reporting cadence: monthly close, quarterly review

## Workflow

1. Statements and exports land in the private finance repo's `imports/`.
2. `hledger import` rules categorise rows into `ledger/main.journal`.
3. Monthly close runs `hledger -f ledger/main.journal balance --tree`
   and `hledger incomestatement` locally; findings are notes in the
   private repo's `reconciliations/`.
4. Approved monthly summaries (no row-level data) can be written back
   to this business repo as research or log entries when the audience
   is right.

## Class B Reminder

This repo is team-visible. It does not contain:

- raw ledger rows;
- bank/credit-card/processor exports;
- account numbers or routing numbers;
- payroll detail;
- tax-return data;
- customer/vendor payment history at row granularity.

If any of those appear here, treat it as a leak and rotate the affected
material per the operator's incident process.
