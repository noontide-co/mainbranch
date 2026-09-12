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

By default, Main Branch selects the native secure store for the current host:
the macOS login Keychain or the Linux Secret Service default collection. It
never falls back automatically to plaintext storage. Unknown selectors and
metadata naming a backend from another operating system fail closed.

Use an explicit backend only for controlled setup or tests:

```bash
MB_CONNECT_SECRET_BACKEND=macos-keychain mb connect cloudflare --token-stdin
MB_CONNECT_SECRET_BACKEND=secret-service mb connect cloudflare --token-stdin
MB_CONNECT_SECRET_BACKEND=local-file mb connect cloudflare --token-stdin
```

`local-file` is a legacy compatibility option and must be selected explicitly.
Existing metadata labeled `keyring` is read through the matching native
adapter; new connections record the native backend name.

The public `--token` option remains as deprecated input compatibility. A value
supplied there is visible in the caller's process arguments. Main Branch never
uses that option in generated commands or internal helper invocation; use
`--token-stdin` for real credentials.

`mb connect token <provider>` is the scripted read path. It prints the raw token
to stdout and nothing else. Use it only in pipes or local scripts that need the
credential; do not paste its output into chat, docs, issues, PRs, or tracked
files.

The product model behind this surface lives in
[connection-model.md](connection-model.md).

## Stored Is Not Verified

`mb connect test` and `mb connect status --json` report three separate facts
per provider:

- `stored`: a credential resolved from the credential backend.
- `provider_verified`: a provider call actually confirmed that credential.
  `false` when Main Branch has no safe read-only probe for the provider.
- `verified_at`: when the credential last worked. `""` if it never has. It
  keeps the earlier timestamp after a later failure, because when a credential
  last worked stays true even once it stops working.

The invariant, stated precisely: **for a provider with `required_secrets`,
`ready` and `ok: true` require `provider_verified: true`.** Cloudflare, Apify,
and Meta have real probes. Every other built-in provider, and every custom
provider, reports `stored, unverified`: the credential is present and readable,
and nothing has checked that it works. `mb connect doctor` and `mb status` grade
that as a warning, not a pass.

The scoping matters. A provider with no `required_secrets` sends nothing to a
provider, so there is no credential to confirm and `provider_verified` stays
false. Such a provider is not covered by the invariant and keeps reporting
`ready` from its repo-local metadata — see below. Claiming `provider_verified`
for it would be the same overclaim this behavior exists to remove.

There is no repair command for `stored, unverified`. Rerunning `mb connect
test` records the same answer, so confirm the credential in the provider's own
dashboard, or let the first real workflow run be the check.

A provider that needs no credential at all, such as `hledger`, still reports
`ready` from repo-local metadata, with `stored: false` and
`provider_verified: false`. Its readiness is a statement about repo-local
metadata, never about a provider call. Read `provider_verified` as "a provider
call confirmed a stored credential", not as "this provider is unhealthy".

Metadata written before this behavior existed recorded `ready` without
recording whether a provider was called, so it reads as `stored, unverified`
until `mb connect test` runs once more. Nothing is rewritten, and a provider
with a real probe returns to `ready` after one re-test.

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

In a local script, keep the token in memory and out of child-process arguments.
The token command writes the exact credential text with no added newline.

```python
import subprocess
import urllib.request

token = subprocess.run(
    ["mb", "connect", "token", "mercury"],
    check=True,
    capture_output=True,
).stdout.decode()
request = urllib.request.Request(
    "https://api.example.invalid/accounts",
    headers={"Authorization": f"Bearer {token}"},
)
with urllib.request.urlopen(request, timeout=10) as response:
    payload = response.read()
```

Do not place a credential in a command argument, use `set -x`, echo it, write a
committed `.env` file, or log request headers. Raw exports should go to a private
workspace or an ignored local staging path, not to a public repo.

If metadata exists but the secret is missing, Main Branch reports
`missing_secret` and gives a reconnect command that includes `--custom`, for
example:

```bash
mb connect mercury --custom --token-stdin
```

## When the credential backend itself is unhealthy

A missing provider secret and an unusable secret backend are different
problems, and only the first is fixed by reconnecting. Main Branch reports
locked, unavailable, incompatible, and timed-out stores as sanitized backend
states. Every native call runs in a helper process, and an aggregate status,
test, or doctor command shares one eight-second credential-store deadline;
unattended reads suppress operating-system unlock UI.

On macOS, unlock the login Keychain interactively inside the reader's owning
user security session, then leave that session running:

```bash
mb connect doctor --json
security unlock-keychain ~/Library/Keychains/login.keychain-db
```

A desktop unlock does not necessarily unlock an already-running remote security
session. Scheduled macOS readers should run as a user `LaunchAgent` in the
logged-in user's GUI launchd domain; Main Branch does not install a daemon,
broker, or launchd job. A new security session or reboot can require another
interactive unlock in that owning session.

Keychain item access control is separate from Keychain lock state. A new item
trusts the installed Python application identity that created it. Reads from a
different or reinstalled interpreter can require a one-time Access Control
addition in Keychain Access or reprovisioning from the intended stable `mb`
install. An item ACL that trusts only `/usr/bin/security` does not authorize the
native reader, which runs inside the Python interpreter named by the installed
`mb` executable's shebang. Provisioning must add that exact interpreter as a
trusted application without granting access to every application. Main Branch
fails closed instead of opening that approval dialog. Never reset or delete the
login keychain to repair one item.

On Linux, Main Branch uses the existing Secret Service default collection. It
checks collection and item lock state and never calls an unlock method. Unlock
the collection in the user's desktop keyring application before starting the
unattended reader.

A connect attempt that fails on the backend stores nothing and leaves repo
metadata unchanged. Replacement updates an existing Keychain item in place,
and Secret Service updates a matched item in place while preserving its
attributes, including legacy Python keyring attributes. New Secret Service
items use its replacement contract. Main Branch never delete-before-adds an
existing credential. Helper stderr and raw exceptions are discarded.

Reconnecting an already configured custom provider also works without
`--custom`, but keeping the flag in repair output makes the command safe to
reuse from a fresh or partially repaired repo.

For rotation, run the same command with the new token:

```bash
MB_CONNECT_SECRET_BACKEND=macos-keychain \
  mb connect mercury --custom --token-stdin
```

Rotation updates only the selected business's `repo_id`-scoped reference. A
same-named provider in another business is not a sibling and is never rewritten.

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

User-scope lookup is indexed by `repo_id`. Worktrees and scheduled jobs for the
same business can reuse the entry; another business with the same provider id
cannot.

## External 1Password option

Main Branch does not yet implement a 1Password credential-store adapter. An
operator may use an existing 1Password CLI or service-account workflow outside
`mb` and pipe a selected field into `mb connect ... --token-stdin`, keeping the
value in memory and off argv. Vault choice, service-account creation, token
storage, desktop integration approval, and reapproval remain operator-owned
bootstrap. An unlocked desktop integration is not evidence that unattended
access will remain available.
