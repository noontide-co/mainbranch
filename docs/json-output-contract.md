# JSON Output Contract

Main Branch CLI JSON is for skills, runtime harnesses, dashboards, and scripts
that need deterministic facts without parsing human terminal output.

The v1 result envelope is additive. Commands keep their existing domain payload
keys at the top level, and high-value `--json` surfaces also expose shared
metadata:

```json
{
  "result_envelope_version": "1.0",
  "result_schema": {"name": "mainbranch.status", "version": "1.0"},
  "mb_command": "mb status",
  "ok": true,
  "result_status": "ok",
  "errors": [],
  "warnings": [],
  "actions": []
}
```

## Shared Fields

- `result_envelope_version`: shared result-envelope version. This is separate
  from any command-specific `schema_version` field.
- `result_schema`: shared result-envelope schema identifier for the command
  surface. This is separate from any command-specific `schema` field.
- `mb_command`: the `mb` command surface that emitted the JSON. The field is
  prefixed so commands can keep existing domain keys such as `command`.
- `ok`: boolean success flag suitable for automation.
- `result_status`: concise machine-readable envelope state, currently `ok` or
  `error`. Commands may still expose their own domain `status` field with
  command-specific values such as `ready`, `valid`, `committed`, or structured
  provider state.
- `errors`: top-level list of failure messages or objects. Empty when there are
  no shared top-level errors.
- `warnings`: top-level list of warnings. Empty when there are no shared
  top-level warnings.
- `actions`: top-level list of recommended or repair actions when the command
  already exposes them. Empty for commands whose actions live in
  command-specific sections such as `ranked_actions` or `next_actions`.

## Command-Specific Fields

Existing command payload keys remain top-level and keep their command-specific
meaning. In particular, `schema`, `schema_version`, `status`, and `command`
are not shared envelope fields in v1. For example, `mb status --json` keeps its
status schema object, `mb doctor repair --json` keeps
`schema: "mb.doctor.repair"` and `schema_version: 1`, and `mb checkpoint --json`
can keep a domain `status` such as `ready` while the envelope reports
`result_status: "ok"`.

`mb status --json` includes a `money_path` section for read-only business-path
readiness. It reports gated component objects for customer progress, offer,
audience, proof, product ladder, CTA path, channel strategy, active push,
playbook, page readiness, and outcome feedback. These facts describe whether
the path is legible, supported, connected, and instrumented; they do not infer
conversion quality, market strength, or strategic correctness.

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
