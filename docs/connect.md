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

## Using a Credential: `exec`

`mb connect exec <provider> [--env NAME] -- <command> [args...]` runs one
command with the stored credential in that command's environment and nowhere
else:

```bash
mb connect exec stripe -- stripe products list --limit 3
mb connect exec cloudflare -- npx wrangler pages deployment list
mb connect exec mercury --env MERCURY_TOKEN -- python3 scripts/import.py
```

- No shell is involved: the words after `--` are the program and its
  arguments, exactly as given.
- The secret is never printed, logged, or returned in JSON. stdin, stdout and
  stderr belong to the command.
- The exit code is the command's own; a command killed by a signal exits
  `128 + signal`, as in a shell. `mb connect exec` itself exits 1 when the
  credential cannot be read, 2 for a refused request, and 127 when the
  command is not found.
- Default variable: the provider's own, which is its first registered
  environment variable (`CLOUDFLARE_API_TOKEN`, `GITHUB_TOKEN`,
  `RESEND_API_KEY`, `APIFY_TOKEN`, Meta's `ACCESS_TOKEN`, and so on). Stripe
  uses `STRIPE_API_KEY`, which the Stripe CLI reads, and Google uses
  `GOOGLE_OAUTH_TOKEN`. Custom ids and providers with no registered variable,
  such as GA4, get `MB_SECRET`. `--env` overrides it.
- `--repo` selects the business repo, and a user-scoped connection resolves
  from a worktree as it does for `status`.

This is the path agents and scripts should use. What the command prints is
still the command's business: avoid commands that echo their environment.

## Raw Read: `token`

`mb connect token <provider>` prints the raw credential with no added newline.
It refuses, with exit 2, when stdout is a terminal or a pipe, because both put
the secret into some other process's text: a transcript, a log, a variable
an agent later prints. The refusal points at `exec`. A script that must write
the raw value to a file can still do so explicitly:

```bash
mb connect token stripe --print > "$private_tmp/stripe-key"
```

`--print` also lifts the refusal for a terminal or a pipe. Use it only when
nothing reading that output is an agent or a log.

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
Meta, Stripe, GitHub and GA4 have real probes (see [Probes](#probes)). Every
other built-in provider, and every custom provider, reports
`stored, unverified`: the credential is present and readable,
and nothing has checked that it works. `mb connect doctor` and `mb status` grade
that as a warning, not a pass.

The scoping matters. A provider with no `required_secrets` sends nothing to a
provider, so there is no credential to confirm and `provider_verified` stays
false. Such a provider is not covered by the invariant and keeps reporting
`ready` from its repo-local metadata — see below. Claiming `provider_verified`
for it would be the same overclaim this behavior exists to remove.

There is no repair command for `stored, unverified` on a provider with no
probe. Rerunning `mb connect test` records the same answer, so confirm the
credential in the provider's own dashboard, or let the first real workflow run
be the check.

### What the exit code means

An exit code from `mb connect test`, `mb connect status`, and `mb connect
doctor` answers one question: **is there something you can act on?** All three
surfaces answer it the same way, so there is no lenient command to run instead.

| Situation | Exit |
| --- | --- |
| `unvalidated`, `invalid`, `missing_secret`, credential-backend failure | 1 |
| `stored, unverified` on a provider **with** a probe | 1 — run `mb connect test` |
| `stored, unverified` on a provider **with no** probe | 0 — nothing to run |
| `ready` | 0 |

The table covers provider readiness. `mb connect doctor` also checks GitHub
context and credential-backend health, and either can still exit 1 on its own —
both name a command to run.

The probe-less case exits 0 on purpose. A red that nobody can clear gets
ignored, and these providers can never turn green until a probe exists
upstream. Only the process exit softens: the provider still reports
`ok: false`, doctor still grades it `warn`, and the verification fields stay
truthful. Each provider carries `has_probe` in `mb connect status --json`, and
`mb connect doctor` names the connected providers that lack one so the gap is
visible and fixable upstream.

A provider that needs no credential at all, such as `hledger`, still reports
`ready` from repo-local metadata, with `stored: false` and
`provider_verified: false`. Its readiness is a statement about repo-local
metadata, never about a provider call. Read `provider_verified` as "a provider
call confirmed a stored credential", not as "this provider is unhealthy".

Metadata written before this behavior existed recorded `ready` without
recording whether a provider was called, so it reads as `stored, unverified`
until `mb connect test` runs once more. Nothing is rewritten, and a provider
with a real probe returns to `ready` after one re-test.

## Probes

Every probe is a read-only GET. Response bodies are never returned or stored;
only the outcome, the HTTP status, and the facts listed here.

| Provider | Probe | Extra facts recorded |
| --- | --- | --- |
| Cloudflare | token verify (user or account token) | none |
| Apify | current user | none |
| Meta | Meta's Ads CLI read smoke | per-command results |
| Stripe | list products, prices, customers and charges (`limit=1`) and read the balance | `scopes`: `allowed`, `refused` or `unknown` per resource |
| GitHub | authenticated user | `token_kind`; `token_scopes` for classic tokens |
| GA4 | the configured property, from the Admin API | none |

Stripe: a 2xx means the key may read that resource, a 403 means the key is
valid but restricted from it, and a 401 on any probe means Stripe rejected the
key itself. A restricted key that reads products and prices but not customers
is `ready`, with the refusals named in the summary and in `scopes`.

GitHub: classic tokens report their scopes through the `X-OAuth-Scopes`
header. GitHub does not list a fine-grained or app token's permissions through
the API, so the probe says so instead of guessing. The GitHub entry stores its
token in an `api_key` slot, which keeps a GitHub token connected earlier with
`--custom` readable.

GA4: the probe needs the numeric property id as metadata. Without it the test
reports `unvalidated` and names the command:

```bash
mb connect ga4 --token-stdin --metadata property_id=<property-id>
mb connect test ga4
```

The GA4 credential is an OAuth access token with Analytics read scope.

## Metadata Is Judged by Value

`--metadata key=value` is for labels and ids. A value that looks like a secret
is refused, and nothing is stored. The value is judged whole and word by
word, so a short label in front of a key (`note: <key>`) does not hide it. The
rules:

- `credential_prefix:<prefix>`: a public credential grammar matched in full,
  prefix and generated part together (for example `sk_live_`/`sk_test_`,
  `rk_`, `pk_live_`, `whsec_`, Resend `re_<8>_<16+>`, `ghp_` and the other
  GitHub token prefixes, `github_pat_`, `glpat-`, `xox?-`, `AKIA`, `AIza`).
  A word that only shares a prefix, such as `re_engagement` or
  `pk_test_publishable`, passes;
- `jwt_shape`: three dot-separated base64url segments starting `eyJ`;
- `bearer_credential`: a value starting `Bearer `, or `Bearer <long token>`
  after a label;
- `high_entropy`: 24 or more token characters, mixed case, enough entropy, and
  at least 30% of its CamelCase/digit segments look generated (a single
  letter, a letter run with no vowel, or a lone digit). Labels are made of
  words, so `UsEuUkCaAuNzApiKeyName2026` and `HTTPSRedirectCheckerProdV2`
  pass. A short letter-digit code between words counts as a word when the
  rest of the value reads as words (a final version digit is allowed), so
  `CloudflareR2StorageBucket`, `B2BMarketingCampaignOctober2026` and
  `S3ProductionBucketUsWest2` pass too, and a code next to a generated tail
  is judged letter by letter.

A value is judged whole and word by word. URLs, emails and env references
stay whole. Each part of a URL (user name, password, host labels, path
segments, query keys and values, fragment pieces) is percent-decoded until
stable (at most three passes) before it is split, then split on `:` and
`=` and judged like a bare value; a URL nested in a part is judged the same
way, up to three levels deep. So `?campaign=CloudflareR2StorageBucket`,
`/docs/getting-started`, IP addresses and `xn--` host labels pass, and a
token in `?token=`, `/token=`, `#token:`, a path segment, a user name, a
host label or behind an encoded `%2F` is refused. A URL that does not
parse, such as one with a bad port, is judged from its decoded raw pieces.

Measured limits of `high_entropy`, 10,000 random values each from
`random.Random(987)` (the test `test_metadata_high_entropy_miss_rates_match_docs`
keeps these numbers current): it misses 33 of 10,000 (0.33%) 24-character
alphanumeric values, 37 of 10,000 (0.37%) 24-character base64-alphabet values
and 168 of 10,000 (1.68%) 40-character mixed-case values with no digits.
Values shorter than 24 characters, and all-lowercase or all-uppercase random
strings, are not judged by entropy at all: hex ids and UUIDs look the same.
Metadata detection is a heuristic, not complete token detection: a value
built only from invented pronounceable words around a short code, for
example `AmoriavenaR2UlenavopiraPavirelona`, reads as a label and passes,
because it looks like `CloudflareR2StorageBucket`. Metadata is a label
field, not a secret scanner; pass credentials with `--token-stdin`.

Hex ids, UUIDs, numeric ids, URLs, emails, paths, `op://` references,
`${VAR}` references and CamelCase labels pass. The key name alone never
refuses, so labels such as `key_name=Main restricted key` or
`onepassword_item=Stripe restricted` are fine. The refusal names the rule and
the key, never the value.

## Refusals Are Logged Locally

Each refusal above that ends an `mb connect` command appends one line to the
local feedback log (see [feedback.md](feedback.md)): the rule name as
`connect.<rule>`, the command path, the repo kind, the time and the mb
version. It never holds the refusal message, the value, a path or a token, and
nothing is sent anywhere. `mb feedback rollup` counts them by rule. Set
`MB_FEEDBACK_LOG=0` to turn this off; a log that cannot be written never
changes the refusal or its exit code.

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

Run a local importer or scheduled collector with the token in its
environment:

```bash
mb connect exec mercury --env MERCURY_TOKEN -- python3 scripts/import_mercury.py
```

The script reads the variable and keeps the token in memory and out of
child-process arguments:

```python
import os
import urllib.request

request = urllib.request.Request(
    "https://api.example.invalid/accounts",
    headers={"Authorization": f"Bearer {os.environ['MERCURY_TOKEN']}"},
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
trusts the installed Python application identity that created it, so after the
Python under `mb` changes (a uv Python upgrade or reinstall), macOS wants to
ask once more before that item can be read. Main Branch never waits on that
dialog: every command reads with keychain interaction turned off, so a pending
prompt fails at once with the `keychain_prompt_pending` state instead of
running into the safety deadline. A locked keychain fails at once with
`keychain_locked`, since unlocking would also need a dialog.

To answer the prompts, run this once from a terminal in the hub, at the screen,
and choose **Always Allow** (Allow lets only that one read through):

```bash
mb connect repair --keychain
```

It is the only command that lets macOS show the keychain dialog. It refuses to
run without a terminal, waits up to 60 seconds per credential, and never prints
a value. It reports a credential as repaired only after a fresh unattended read
succeeds; otherwise it says the prompt is still pending. Never reset or delete the login keychain to repair one item.

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

### Rotate from a recorded source

Record where the credential lives once, as a non-secret reference:

```bash
op read "op://Business/Stripe restricted/credential" \
  | mb connect stripe --token-stdin --source "op://Business/Stripe restricted/credential"
```

`--source` stores the reference as `metadata.source`. Given on its own, with
no `--metadata`, it keeps the existing metadata and adds the source. A source
that looks like a secret itself is refused.

After the key is rolled in the provider and updated in 1Password:

```bash
mb connect rotate stripe
```

`rotate` re-reads the credential with `op read <ref>` (no shell; the value is
never printed), stores it through the same path as a connect, keeps the
account label, metadata, scope and backend, and runs the provider probe. The
exit code follows `mb connect test`. It refuses, with exit 2 and the next
step, when no source is recorded, when the source is not an `op://`
reference, when the 1Password CLI is missing, and when it is not signed in.

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
value in memory and off argv. Recording the reference with `--source` lets
`mb connect rotate` repeat that read later. Vault choice, service-account creation, token
storage, desktop integration approval, and reapproval remain operator-owned
bootstrap. An unlocked desktop integration is not evidence that unattended
access will remain available.
