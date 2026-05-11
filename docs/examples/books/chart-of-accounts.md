---
type: chart-of-accounts
ledger: hledger
operating_currency: USD
---

# Chart Of Accounts — Sample

> Sample file. Not a real chart of accounts. See
> [docs/books.md](../../books.md) for the operator-facing description.

This is what a `core/finance/chart-of-accounts.md` could look like for a
fictional company using an hledger journal. It describes the **naming
convention**, not real balances.

## Roots

hledger uses the conventional plain-text accounting roots. The `account`
directive in the journal pins each account to a type so reports such as
`hledger balancesheet` and `hledger incomestatement` work correctly.

| Root | hledger type | Use | Example |
| --- | --- | --- | --- |
| `assets` | `A` | What the business owns | `assets:bank:checking` |
| `liabilities` | `L` | What the business owes | `liabilities:credit-card` |
| `equity` | `E` | Owner equity, opening balances, distributions | `equity:opening-balances` |
| `income` | `R` (revenue) | Revenue streams | `income:sales` |
| `expenses` | `X` (expense) | What the business spends | `expenses:software` |

## Conventions

- One operating currency for the whole ledger (`USD` in this sample).
- Account names use lowercase, colon-separated segments
  (`expenses:office:supplies`).
- Sub-accounts go deeper as needed but no deeper than three levels in
  this sample.
- Generic institution categories instead of named institutions in the
  public chart description (e.g. `bank` rather than the real bank name).
- One income line per durable revenue stream, not per customer.
- One expense line per durable spend category, not per vendor.
- Declare each account once with an `account ... ; type:<letter>`
  directive at the top of the journal.

## Account Inventory (Sample)

The sample fixture
[`acme-fixture.journal`](acme-fixture.journal) declares these accounts:

- `assets:bank:checking`
- `assets:bank:savings`
- `liabilities:credit-card`
- `equity:opening-balances`
- `income:sales`
- `expenses:software`
- `expenses:office:supplies`

A real chart of accounts would grow as the business grows, but the
public-safe description in `core/finance/chart-of-accounts.md` would
still describe the **shape** — not real balances, real institutions,
real customers, or real account numbers.
