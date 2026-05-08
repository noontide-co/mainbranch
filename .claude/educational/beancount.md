---
type: educational
topic: beancount
status: draft
last-updated: 2026-05-08
---

# Beancount: plain-text finance without leaking raw finance data

Beancount is a plain-text accounting format. It fits Main Branch's philosophy
because ledgers can be inspected, versioned, reviewed, and backed up like code
or markdown.

That does not mean raw finance data belongs in every shared business repo.

## When you need this

Use Beancount-style thinking when the business needs durable financial memory:

- revenue and expense summaries;
- offer-level profitability;
- payout and provider reconciliation;
- monthly operating review;
- bookkeeping handoff notes;
- finance decisions that should feed future planning.

## The safe boundary

Recommended pattern:

1. Keep raw ledgers, statements, receipts, and account exports in a private
   finance repo or accounting system with explicit access rules.
2. Keep business-readable summaries in the main business repo.
3. Link decisions, offers, pushes, and outcomes to the relevant safe summary.
4. Never commit bank credentials, account numbers, tax IDs, payroll rows,
   customer-private rows, or secrets.

## Why not a normal accounting SaaS only?

Accounting SaaS can be useful and may still be required for bookkeeping, tax,
payroll, or accountant collaboration. The Main Branch concern is operating
memory: can the business inspect the financial lesson later, connect it to the
offer or push, and preserve the decision in a repo-backed way?

Plain-text summaries and ledgers make that possible without forcing every
operator into a vendor-specific dashboard.

## What Main Branch does not claim

Main Branch does not provide accounting, tax, legal, or financial advice.
Beancount is a planned/optional finance rail, not a guarantee that `mb` can
automate your books end to end.

When in doubt, store less raw finance data in the shared repo and more safe
summary context for business decisions.
