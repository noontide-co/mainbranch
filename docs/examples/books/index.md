# Bookkeeping Examples

Fake bookkeeping fixtures used to exercise the shipped `mb books check`
contract. Everything in this folder is intentionally fake.

These files exist in this engine repo only. They are not copied into a
business repo by `mb init` or `mb onboard`. A real business ledger never
lives here.

| File | Purpose |
| --- | --- |
| [`acme-fixture.journal`](acme-fixture.journal) | Minimal hledger journal fixture for a fictional company |
| [`books.md`](books.md) | Sample `core/finance/books.md` policy file |
| [`chart-of-accounts.md`](chart-of-accounts.md) | Sample `core/finance/chart-of-accounts.md` description |

Rules these fixtures follow:

- the company name is obviously fake (`Acme Fixture Inc`);
- accounts use only the conventional plain-text-accounting roots:
  `assets`, `liabilities`, `equity`, `income`, `expenses`, each pinned
  to the right hledger account type;
- no real vendors, customers, banks, account numbers, routing numbers,
  payroll detail, or tax numbers;
- one placeholder operating currency (`USD`);
- transactions are illustrative, not derived from any real ledger;
- a header comment names each file as a sample.

See:

- [docs/books.md](../../books.md) for what `mb books` does.
- [decisions/2026-05-11-mb-books-foundation.md](../../../decisions/2026-05-11-mb-books-foundation.md)
  for the safe path contract.
- [docs/reports/2026-05-11-hledger-vs-beancount-fit.md](../../reports/2026-05-11-hledger-vs-beancount-fit.md)
  for the hledger vs Beancount evaluation.
