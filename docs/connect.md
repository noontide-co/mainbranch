# Connect Providers

`mb connect` records safe provider metadata in the business repo and stores
credential material outside git.

Use it when a business workflow needs a durable handle to an external account:
site deploys, ads, email, payment, research, bookkeeping, or a private finance
source. `mb connect` answers whether the credential is present, whether a safe
readiness check has passed where supported, and which command repairs the first
broken step.

## Secret Boundary

Tracked repo metadata may include:

- provider id;
- account label;
- non-secret metadata such as account role or token type;
- secret-store backend name;
- secret refs.

Tracked repo metadata must not include:

- API tokens, keys, refresh tokens, passwords, or service-account JSON;
- raw provider exports;
- account-private finance, customer, member, payroll, legal, or tax data.

By default, Main Branch selects the safest available local secret backend. On
macOS that is usually Keychain. You can force a backend for setup or testing:

```bash
MB_CONNECT_SECRET_BACKEND=macos-keychain mb connect cloudflare --token-stdin
```

`mb connect token <provider>` is the scripted read path. It prints the raw token
to stdout and nothing else. Use it only in pipes or local scripts that need the
credential; do not paste its output into chat, docs, issues, PRs, or tracked
files.

The product model behind this surface lives in
[connection-model.md](connection-model.md).

## Custom Providers

Use `--custom` when the provider is not in the built-in registry yet. Custom
provider ids use lowercase letters, digits, and hyphens. They get one
`api_key` secret slot and the same status, doctor, list, token, repo-scope, and
user-scope behavior as built-in providers.

Example: a read-only finance provider token.

```bash
MB_CONNECT_SECRET_BACKEND=macos-keychain \
  mb connect mercury \
    --custom \
    --token-stdin \
    --account "Mercury Operating Account" \
    --metadata role=operating_cash_source \
    --metadata auth_state=api_token
```

This writes safe metadata and a secret ref under `.mb/connect.yaml`; the token
goes to the selected local secret backend.

Check it without printing the token:

```bash
mb connect status mercury --json
mb connect status --all --json
mb connect doctor --json
mb connect list --json
mb connect identity --json
```

Read the token for a local importer or scheduled collector:

```bash
mb connect token mercury
```

In a shell script, capture the token without echoing it. Keep shell tracing off
around secret reads.

```bash
#!/usr/bin/env bash
set -euo pipefail
set +x

token="$(mb connect token mercury)"
curl --fail --silent --show-error \
  --header "Authorization: Bearer ${token}" \
  "https://api.example.invalid/accounts" \
  > /tmp/mercury-accounts.json

unset token
```

Do not use `set -x`, `echo "$token"`, committed `.env` files, or logs that
print request headers. Raw exports should go to a private finance workspace or
an ignored local staging path, not to a public repo.

If metadata exists but the secret is missing, Main Branch reports
`missing_secret` and gives a reconnect command that includes `--custom`, for
example:

```bash
mb connect mercury --custom --token-stdin
```

## When the credential backend itself is unhealthy

A missing provider secret and an unusable secret backend are different
problems, and only the first is fixed by reconnecting. When the backend cannot
answer — most often a locked macOS login Keychain, or one whose password is out
of sync with the account password — Main Branch reports the provider state as
`backend_unavailable` rather than `missing_secret`, and `mb connect doctor`
reports a failed `credential-backend` check with a `keychain_locked` or
`keychain_auth_failed` state before it suggests reconnecting anything.

Repair the backend first:

```bash
mb connect doctor --json
security unlock-keychain ~/Library/Keychains/login.keychain-db
```

If the login keychain rejects the passphrase, unlock it in Keychain Access with
the older password and resync it with Edit > Change Password for Keychain
"login". Do not reset or delete the login keychain — that destroys every
credential already stored in it, for Main Branch and for every other app.

A connect attempt that fails on the backend stores nothing and leaves repo
metadata unchanged, so it cannot leave a provider reading `connected: true`
next to a secret that was never written. Main Branch classifies the failure
from the `security` exit code and a small set of known phrases; raw `security`
output is never printed, because it can echo the command's own arguments.

Reconnecting an already configured custom provider also works without
`--custom`, but keeping the flag in repair output makes the command safe to
reuse from a fresh or partially repaired repo.

For rotation, run the same command with the new token:

```bash
MB_CONNECT_SECRET_BACKEND=macos-keychain \
  mb connect mercury --custom --token-stdin
```

Then verify readiness without printing the token:

```bash
mb connect status mercury --json
mb connect doctor --json
mb connect identity --json
```

Recommended custom metadata for finance providers:

```text
role=operating_cash_source
access_level=read_only
data_domain=banking
auth_state=api_token
source_system=mercury
account_ref=operating-cash
```

Use `account_ref` as a business-readable handle. Do not commit raw account
numbers, routing numbers, statements, transaction rows, tax records, or provider
payloads.

## User Scope

Use user scope when several worktrees for the same business repo should read
the same credential metadata from local Main Branch state:

```bash
mb connect mercury --custom --scope user --token-stdin
```

A fresh worktree can see that user-scoped metadata exists and can hydrate the
repo-local `.mb/connect.yaml` copy:

```bash
mb connect hydrate --repo .
```

Secret material remains outside git in both repo and user scope.
