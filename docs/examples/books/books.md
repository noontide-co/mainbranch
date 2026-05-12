---
type: books
ledger: hledger
operating_currency: USD
fiscal_year_start: "01-01"
reporting_cadence: monthly
storage_mode: solo-local
vault_location: ".mb/private/books/"
github_backup: false
encrypted_backup: false
class_b_data: true
---

# Bookkeeping — Sample

> Sample file. Not a real bookkeeping policy. See
> [docs/books.md](../../books.md) for the operator-facing description and
> [decisions/2026-05-11-mb-books-foundation.md](../../../decisions/2026-05-11-mb-books-foundation.md)
> for the contract.

This is what a real `core/finance/books.md` could look like in a
business repo for a fictional company using the solo-local storage
mode. The real bookkeeping records live in a private bookkeeping vault inside the
business repo's local working tree, ignored from the business repo's
tracked content and never pushed to its remote.

## Storage

- Engine: hledger
- Storage mode: solo-local
- Vault location: `.mb/private/books/`
- Authoritative file: `.mb/private/books/main.journal`
- Operating currency: USD
- Fiscal year: calendar year
- Reporting cadence: monthly close, quarterly review
- GitHub backup: not enabled
- Encrypted backup: not configured

## Workflow

1. Statements and exports land in `.mb/private/books/imports/`.
2. `hledger import` rules categorise rows into
   `.mb/private/books/main.journal`.
3. Monthly close runs `hledger -f .mb/private/books/main.journal
   balance --tree` and `hledger incomestatement` locally; findings
   are notes in `.mb/private/books/reports/`.
4. Approved monthly summaries (no row-level data) may be written
   back to this business repo as research, log entries, or files
   under `docs/reports/finance/` when the audience is right.

## Class B Reminder

This repo is team-visible. It does not contain:

- raw ledger rows;
- bank/credit-card/processor exports;
- account numbers or routing numbers;
- payroll detail;
- tax-return data;
- customer/vendor payment history at row granularity.

If any of those appear here, treat it as a leak and rotate the
affected material per the operator's incident process.
