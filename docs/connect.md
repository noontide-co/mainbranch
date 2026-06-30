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
```

Read the token for a local importer or scheduled collector:

```bash
mb connect token mercury
```

If metadata exists but the secret is missing or unreadable, Main Branch reports
`missing_secret` and gives a reconnect command that includes `--custom`, for
example:

```bash
mb connect mercury --custom --token-stdin
```

Reconnecting an already configured custom provider also works without
`--custom`, but keeping the flag in repair output makes the command safe to
reuse from a fresh or partially repaired repo.

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
