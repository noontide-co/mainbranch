# Connection Model

Main Branch uses `mb connect` as the durable, secret-safe account handle for
business tools. The model is deliberately smaller than a native integration:
record enough setup truth for agents to reason from facts, keep credentials
outside git, and require separate approval for anything that can change a
provider account.

Field lesson: using a custom Mercury provider for a bookkeeping migration
proved the shape. The same pattern should work for Printful, A2X, Xero, bank
APIs, and niche SaaS tools before Main Branch has native wrappers.

## What worked

- Provider metadata lives in `.mb/connect.yaml`, so setup state is durable and
  inspectable.
- Secret values live outside git through `SecretStore` backends such as macOS
  Keychain, Python keyring, or local file storage.
- `mb connect token <provider>` gives scripts one narrow credential read path
  that prints only the token to stdout.
- `status`, `doctor`, `list`, `identity`, `hygiene`, and `test` give agents
  facts without copying credentials into chat or workpapers.
- User scope lets worktrees and scheduled jobs resolve the same credential
  setup without asking the operator to re-auth every day.

## What failed

- Custom providers were stored correctly but broad list/status/doctor surfaces
  initially enumerated only the built-in provider registry.
- Provider-specific status was parsed by the CLI but not handled as a distinct
  status path.
- Repair commands for missing custom secrets did not include `--custom`, which
  made the correct repair easy to miss.
- Custom providers had no identity schema, so agents could see "connected" but
  not the safe role of the account, such as `operating_cash_source`.
- Docs did not show the full finance-token lifecycle or safe script pattern.

## Lifecycle

1. **Declare.** Choose a provider id and record safe intent metadata.
   Built-ins use the registry; custom providers use `--custom`.
2. **Store secret.** Store token material through `--token-stdin`,
   provider-native auth, Keychain, keyring, local secret store, 1Password, or a
   current-process environment command. Never commit `.env` files or paste raw
   tokens into docs, issues, logs, or workpapers.
3. **Smoke test.** Run `mb connect test <provider>` when a safe read-only probe
   exists. For custom providers without a probe, credential presence can mark
   local readiness, but it does not prove provider API behavior.
4. **Record identity metadata.** Record non-secret facts that prevent agents
   from guessing: role, access level, data domain, auth state, account label,
   workspace, environment, or provider-specific ids when safe for the repo.
5. **Use token in scripts.** Scripts call `mb connect token <provider>` and
   keep stdout in memory or a pipe. They do not echo tokens, enable shell trace,
   write env files, or commit raw exports.
6. **Rotate or repair.** Missing or stale secrets report a reconnect command.
   For custom providers, repair output includes `--custom --token-stdin`.
7. **Audit and hygiene.** `mb connect doctor`, `mb connect status --all`,
   `mb connect identity`, and `mb connect hygiene` are the read-only audit
   surfaces before agents use provider facts.

## Public vs Private

Safe to commit:

- provider id and category;
- account label when it does not expose a private account number;
- secret backend name and secret ref;
- role, access level, data domain, auth state, environment, and source system;
- validation state, timestamps, and repair commands.

Keep private:

- API keys, access tokens, refresh tokens, passwords, service-account JSON;
- raw bank, payment, order, customer, member, payroll, tax, or legal exports;
- full account numbers, routing numbers, card numbers, and private debt terms;
- provider payloads, workpapers, logs, or scripts that print secret values.

## Finance Providers

Finance and bookkeeping providers are more sensitive than marketing/site
providers because read access can expose bank balances, customer payments,
vendor names, debt terms, tax records, and payroll context. Treat finance
connections as read-only by default and keep raw source data in a restricted
finance repo, local books vault, or provider export location.

Recommended custom metadata:

```text
role=operating_cash_source
access_level=read_only
data_domain=banking
auth_state=api_token
source_system=mercury
account_ref=operating-cash
```

Avoid raw bank account numbers in repo metadata. Use a business-readable handle
such as `operating-cash` and put the exact mapping in the private finance
workspace if needed.

## Agent Boundary

Agents can do without seeing secrets:

- inspect provider readiness;
- check whether a secret is present;
- read safe identity metadata;
- tell the operator which repair command to run;
- run approved scripts that consume `mb connect token` without printing it;
- summarize sanitized import counts and freshness.

Approval-gated every time:

- provider mutation;
- spend, budget, campaign, or checkout changes;
- money movement, transfers, bill pay, refunds, or payout changes;
- emailing, publishing, posting, customer/member contact, or fulfillment writes;
- exporting raw private records into a shared repo, public issue, PR, log, or
  model context.

## Implemented Follow-Ups

- Custom providers are included in broad status/list/doctor surfaces.
- Custom provider tests cover status, list, doctor, token, missing secrets, and
  user scope.
- Custom provider identity metadata is surfaced by `mb connect identity`.
- `docs/connect.md` includes Mercury-style Keychain setup and safe token use.

## Issue-Ready Follow-Ups

- Add explicit secret-backend diagnostics: selected backend, backend
  availability, Keychain/keyring read failure state, and repair commands.
- Add `mb connect rotate <provider>` as a clearer alias over reconnecting with
  `--token-stdin`, including sibling-ref rotation evidence.
- Add finance-provider metadata validation warnings for raw-looking account
  numbers, missing `access_level`, and missing `data_domain`.
- Add optional 1Password command integration for token reads without teaching
  committed `.env` files.
- Add native read-only wrappers only after one provider has public-safe smoke
  evidence and a privacy-bounded output contract.
