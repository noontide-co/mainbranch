# JSON Output Contract

Main Branch CLI JSON is for skills, runtime harnesses, dashboards, and scripts
that need deterministic facts without parsing human terminal output.

The v1 result envelope is additive. Commands keep their existing domain payload
keys at the top level, and high-value `--json` surfaces also expose shared
metadata:

```json
{
  "schema_version": "1.0",
  "schema": {"name": "mainbranch.status", "version": "1.0"},
  "mb_command": "mb status",
  "ok": true,
  "status": "ok",
  "errors": [],
  "warnings": [],
  "actions": []
}
```

## Shared Fields

- `schema_version`: shared result-envelope version. Existing command-specific
  schema versions are preserved where they already existed.
- `schema`: command-specific schema identifier. Older command payloads that
  already used a string schema keep that value for compatibility.
- `mb_command`: the `mb` command surface that emitted the JSON. The field is
  prefixed so commands can keep existing domain keys such as `command`.
- `ok`: boolean success flag suitable for automation.
- `status`: concise machine-readable state. When a command already had a
  domain `status` such as `ready`, `valid`, or `committed`, that value is
  preserved.
- `errors`: top-level list of failure messages or objects. Empty when there are
  no shared top-level errors.
- `warnings`: top-level list of warnings. Empty when there are no shared
  top-level warnings.
- `actions`: top-level list of recommended or repair actions when the command
  already exposes them. Empty for commands whose actions live in
  command-specific sections such as `ranked_actions` or `next_actions`.

## First Migrated Surfaces

The v1 envelope is present on:

- `mb status --json`
- `mb start --json`
- `mb checkpoint --json`
- `mb issue draft --json`
- `mb issue open --json`
- `mb doctor --json`
- `mb doctor repair --json`
- `mb onboard --json`
- `mb onboard status --json`
- `mb onboard plan --json`

Future commands should use the same shared metadata when they add or revise
`--json` output. Avoid moving existing payloads under a new `data` key unless a
future schema version explicitly deprecates the top-level domain keys.
