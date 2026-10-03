# Friction Feedback (mb feedback)

Agents and operators hit friction in `mb`: a refused command, a confusing
message, a missing probe. Log it when it happens with `mb feedback` so the
workaround is not lost. The log is a local file. Nothing is sent anywhere.

## Log friction

```bash
mb feedback "status said ready but connect test failed" --command "mb connect test"
```

Each call appends one JSON line to
`$XDG_STATE_HOME/mainbranch/feedback.jsonl`, which defaults to
`~/.local/state/mainbranch/feedback.jsonl`:

```json
{"command": "mb connect test", "kind": "feedback", "mb_version": "0.5.3", "repo_kind": "hub", "schema": 1, "text": "status said ready but connect test failed", "time": "2026-10-03T12:00:00Z"}
```

- `command` is the `mb` command path only: `mb` plus up to three lowercase
  command words from `--command`, for example `mb connect test`. It stops at
  the first token that is not a plain command word (a flag, a value, a path,
  a quote) and drops everything after it, so `mb connect meta --token ...`
  is stored as `mb connect meta`. `null` when no command word remains.
- `repo_kind` is `hub`, `child`, `engine` or `none`, from the same repo
  classifier the launch screen, `mb doctor` and `mb checkpoint` use. It is
  `unknown` only if classification itself fails.
- `text` is capped at 4,000 characters (then marked ` [truncated]`) and
  scrubbed before it is written. The cap comes first, so a huge paste is never
  scanned in full. The scrubber is defence in depth, so the default is to
  redact:
  - A `key=value`, `key: value`, JSON `"key": "value"` or `--key value` pair is
    redacted when any segment of the key (split on `_`, `-`, `.` and case
    changes) is a secret word: token, secret, password, passwd, pwd,
    passphrase, apikey, credential, auth, authorization, signature, sig,
    session, cookie or bearer, or the pairs api+key, private+key and
    access+key. So `access_token_v2`, `client_secret_new` and
    `password_confirmation` are redacted. A short allowlist of harmless
    metadata keys keeps its values: `token_count`, `tokens_used`,
    `max_tokens`, `max_output_tokens`, `input_tokens`, `output_tokens`,
    `total_tokens`, `token_type`, `token_limit` and `tokenizer`.
  - Quoted values are read by matching the opening quote to its closing twin,
    across lines and honouring backslash escapes; adjacent quoted and bare
    fragments (`"a"'b'c`) are one value; an unterminated quote is redacted to
    the end of the field.
  - A sensitive HTTP header (`Authorization`, `Proxy-Authorization`,
    `Cookie`, `Set-Cookie`, or a hyphenated header with a secret segment such
    as `X-Api-Key`) loses its whole value to the end of the line, or to the
    closing quote inside `curl -H '...'`: every cookie pair and Digest field.
  - Under a secret YAML key, a `|` or `>` block, or a value on the indented
    lines below, is redacted as a whole block: every following line more
    indented than the key, with blank and comment lines inside it. The key may
    carry a tag (`!!str`, `!<...>`), an anchor (`&name`), chomping and indent
    digits (`|-`, `>+2`) and a trailing `# comment`. A tag or anchor before an
    inline value does not hide the value.
  - Escaped characters (`\ `, `\;`) are part of a bare value. A secret flag
    (`--password`, `--api-key`, any flag with a secret segment) loses its next
    argument even when it starts with `-` or sits on the next line.
  - Bearer and Basic credentials, URL passwords
    (`scheme://user:<redacted>@host`) and provider token families such as
    GitHub's `ghp_`/`ghs_`, Slack, OpenAI and AWS key ids are redacted
    anywhere.
  - Home directory paths become `~`. Every other absolute path becomes
    `<local-path>`: Unix paths (also right after a colon, as in
    `failed:/srv/...`, and with escaped spaces), `file:///` URLs, Windows
    drive paths with either slash, UNC shares with either slash, and quoted
    paths, read with the same quote matching and allowed to hold spaces and
    the other quote, even in the first segment. URLs, relative paths and slash
    commands such as `/mb-start` are left alone.
  - Known limit: a share written as `scheme://server/share` cannot be told
    apart from a URL, so it is left as written. Do not paste one.

Write a credential-free summary in your own words and pass only the command
name to `--command`. The scrubber is a backstop, not permission to paste a
command line with its arguments.

The file is created with owner-only permissions. Add `--json` for the shared
[result envelope](json-output-contract.md) (`mainbranch.feedback.v1`).

## Refusals log themselves

When `mb` refuses at a credential or safety boundary, it appends a
`kind: refusal` line with the rule that fired and the command path (the same
`mb` plus command words as above). It never logs the refused value or the
refusal message. `rule` is a slug matching `[a-z0-9][a-z0-9_.:-]{0,63}`;
anything else is stored as `other`.

```json
{"command": "mb connect list", "kind": "refusal", "mb_version": "0.5.3", "repo_kind": "hub", "rule": "connect.config_boundary", "schema": 1, "time": "2026-10-03T12:00:00Z"}
```

Every `mb connect` refusal that ends the command is logged once, as
`connect.<rule>`, where `<rule>` is the name the refusal itself carries. The
log holds the rule name only: never the refusal message, the value, a path or a
token. Code that calls `mb.connect` as a library and handles a refusal itself
logs nothing.

| Rule | Fires when |
| --- | --- |
| `connect.config_boundary` | `mb connect` refuses `.mb/connect.yaml` because it is a symlink, invalid, or outside the repo. |
| `connect.token_print` | `mb connect token` refuses to print to a terminal or a pipe. |
| `connect.metadata_secret_value`, `connect.metadata_format` | `--metadata` holds a secret-shaped value or is not `key=value`. |
| `connect.source_secret_value` | `--source` holds a secret value instead of a reference. |
| `connect.key_shape`, `connect.stripe_mode_mismatch` | A credential does not match the provider's key shape or mode. |
| `connect.exec_no_command`, `connect.exec_env_name` | `mb connect exec` has no command, or `--env` is not a usable variable name. |
| `connect.rotate_*` | `mb connect rotate` has nothing to rotate, no usable recorded source, or cannot read the source. |

Set `MB_FEEDBACK_LOG=0` to turn refusal logging off. Logging is best effort: if
the file cannot be written, the refusal still happens exactly as before.

Code that adds a refusal calls `mb.feedback.record_refusal(rule, command)` with
a stable dotted rule id. Never pass the refused value.

## Read and prune

```bash
mb feedback rollup                 # last 7 days, Markdown draft
mb feedback rollup --since 30d     # or 12h, 2w, 2026-09-01
mb feedback rollup --json          # groups plus the Markdown in `markdown`
mb feedback list                   # newest 50 lines
mb feedback list --kind refusal --since 7d --limit 0
mb feedback clear --before 2026-09-01
```

`rollup` groups entries by kind, command and rule with a count, the oldest and
newest time, repo kinds and mb versions. Refusals come first as a table;
feedback follows with each note under its command. The draft is meant for a
maintainer to turn into issues with [`mb issue draft`](issue-drafting.md) after
a review. Sending, telemetry, and filing issues automatically are out of scope.

`clear --before <date>` removes entries older than the date, plus any
unreadable lines.

## Exit codes

`0` on success. `2` for a usage error: empty text, an unknown subcommand
argument, `--kind` other than `feedback` or `refusal`, an unreadable `--since`
or one longer than 100 years (`invalid_since`), or a missing or unreadable
`--before` (`missing_before`, `invalid_date`). `1` when the file cannot be
read or written (`feedback_read_failed`, `feedback_write_failed`,
`feedback_clear_failed`). With `--json`, every failure returns the result
envelope with `ok: false` and a scrubbed message. Unreadable lines in the file
are skipped and counted as `skipped_lines`; they never fail a command.
