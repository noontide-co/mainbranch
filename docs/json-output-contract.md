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

### MoneyPath Proof Quality

`money_path.objects.proof` has two layers:

- Component-level `level`, `status`, `summary`, `paths`, and `missing` describe
  the proof component in the same gated MoneyPath scale as other components.
- Nested `quality` describes factual proof signals that skills, dashboards, and
  scripts can cite without inventing a persuasion score.

`proof.status: structured` means standard proof files, parseable entries, or
frontmatter exist. It does not mean each testimonial has outcome structure.
Nested `proof.quality.structured_entries` means status found structured
testimonial entries or frontmatter inside `testimonials.md`.

When no proof files exist, `quality` contains the baseline empty shape:

```json
{
  "testimonials": {
    "total": 0,
    "generic": 0,
    "specific": 0,
    "permissioned_public": 0,
    "linked_to_offer": 0,
    "with_before_state": 0,
    "with_outcome": 0,
    "with_timeframe": 0,
    "with_metric": 0,
    "with_mechanism": 0,
    "with_objection": 0
  },
  "typicality": {
    "exists": false,
    "has_average_case": false,
    "has_caveats": false,
    "has_common_failure_context": false,
    "has_time_to_outcome": false
  },
  "claim_links": {
    "linked_offers": [],
    "unsupported_offer_claims": []
  }
}
```

When proof files exist and status can inspect them, `quality` also includes:

```json
{
  "structured_entries": false,
  "source_backed": false,
  "instrumentation": {
    "active_push": false,
    "playbook": false,
    "page_readiness": false,
    "outcome_feedback": false
  }
}
```

Generic testimonials are real proof material, but they are not treated as
specific, offer-linked, typicality-aware, or outcome-backed unless the relevant
fields say so. Skills and dashboards should cite facts such as
`permissioned_public`, `linked_to_offer`, `with_outcome`, `with_timeframe`,
`with_metric`, `typicality.exists`, and, when present,
`instrumentation.outcome_feedback`; those are factual signals, not persuasion
scores.

Dashboard-safe proof categories can be derived from these facts:

- Missing proof: component `status` is `missing`.
- Generic proof: testimonials exist, but `specific` is `0`.
- Specific proof: `testimonials.specific` is greater than `0`.
- Offer-linked proof: `testimonials.linked_to_offer` is greater than `0`.
- Typicality-aware proof: `typicality.exists` is `true`.
- Outcome-backed proof: `instrumentation.outcome_feedback` is present and
  `true`.

Use factual copy such as "Proof exists, but it is generic", "Proof includes
specific outcomes", "Proof is linked to an offer", "Proof has typicality
context", or "Proof is connected to outcome feedback." Avoid claims such as
"good proof", "bad proof", "high-converting proof", "ready to win", or
"persuasive proof."

`mb status --json` also includes a `content_strategy` section for layered
content-strategy health. It reports whether the simple
`core/content-strategy.md` entry point exists, which optional distribution,
channel, account, and person layers exist, whether layers are indexed from the
business strategy, whether account layers resolve their channel and voice
source, and whether fast-changing channel/account layers are stale. Dashboard
and runtime callers should read these normalized facts instead of parsing raw
markdown. Use `overall_state` as summary health and `findings[].code` for
repair cards, such as `content_strategy_unindexed_layer` when a layer exists
but is not indexed from `core/content-strategy.md`.

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
