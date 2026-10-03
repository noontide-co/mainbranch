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

- `command` is what you passed with `--command`, or `null`.
- `repo_kind` is `hub` when the line was written from a business repo, else
  `unknown`.
- `text`, `command` and a refusal's `rule` are scrubbed before they are
  written. Secret-shaped values become `<redacted>`: key=value and JSON
  `"key": "value"` pairs whose key names a token, secret, password, key,
  credential or signature (including environment names such as
  `GITHUB_TOKEN`), Bearer and Basic credentials, URL passwords
  (`scheme://user:<redacted>@host`), and provider token families such as
  GitHub's `ghp_`/`ghs_`, Slack, OpenAI and AWS key ids. Home directory paths
  become `~`. Any other absolute path (Unix, Windows drive with either
  slash, or UNC share) becomes `<local-path>`; URLs and slash commands such as
  `/mb-start` are left alone.

Write a credential-free summary in your own words and pass only the command
name to `--command`. The scrubber is a backstop, not permission to paste a
command line with its arguments.

The file is created with owner-only permissions. Add `--json` for the shared
[result envelope](json-output-contract.md) (`mainbranch.feedback.v1`).

## Refusals log themselves

When `mb` refuses at a credential or safety boundary, it appends a
`kind: refusal` line with the rule that fired and the command. It never logs
the refused value or the refusal message.

```json
{"command": "mb connect list", "kind": "refusal", "mb_version": "0.5.3", "repo_kind": "hub", "rule": "connect.config_boundary", "schema": 1, "time": "2026-10-03T12:00:00Z"}
```

| Rule | Fires when |
| --- | --- |
| `connect.config_boundary` | `mb connect` refuses `.mb/connect.yaml` because it is a symlink, invalid, or outside the repo. |

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
