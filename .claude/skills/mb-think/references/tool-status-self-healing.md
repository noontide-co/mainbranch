# Tool Status Self-Healing

Operational contract for runtime-local tool notes. Provider readiness and
repair belong to `mb status --json --peek`, `mb connect plan`, and
`mb connect doctor --json`.

---

## Staleness Definition

A tool entry is **stale false** when all are true:

- `status: false`
- `last_checked` is missing, invalid, or older than 30 days

Do not routinely re-probe provider entries here. Runtime-local entries can be
rechecked when a selected workflow needs that exact tool.

---

## Detection Contract (/mb-think)

On first `/mb-think` invocation each session:

1. Read `mb status --json --peek`.
2. Run `mb connect doctor --json` if the selected provider is missing or
   degraded.
3. Build a runtime detection list only for the selected workflow.
4. Run the relevant runtime probe methods from `SKILL.md`.
5. Cache session knowledge and optionally update local runtime notes for tools
   actually touched.

Every touched entry must include:
- `status`
- `notes`
- `last_checked`

---

## Status-Change Messaging

Do not hide state flips:

- `false → true`:
  - "Found [tool] installed and working. `mb connect doctor --json` has the current provider repair path if account readiness is still missing."
- `true → false`:
  - "Warning: [tool] was previously available but is not detected now. Treat old `.vip/config.yaml` tool status as stale and use current `mb connect`/runtime checks."

If status does not change, use normal experience-level reporting.

---

## Degradation Rule for `status: true`

If a runtime-local tool marked `status: true` fails at use time (missing command
or missing MCP tool):

1. Re-probe that tool immediately
2. Warn the user in the same turn
3. If the failure is provider auth/readiness, report the `mb connect doctor --json` repair command

Never let a previously-true runtime-local tool fail silently. If the failure is
provider auth/readiness, report the `mb connect doctor --json` repair command
instead of inventing one.

---

## Example Normalized Shape

```yaml
tools:
  gemini:
    status: true
    notes: "GOOGLE_API_KEY verified"
    last_checked: 2026-03-02
  whisper:
    status: false
    notes: "No CLI or MCP tool detected"
    last_checked: 2026-03-02
  document_tools:
    status: true
    notes: "markitdown verified"
    last_checked: 2026-03-02
```

---

## See Also

- [SKILL.md](../SKILL.md)
- [tool-surfacing.md](tool-surfacing.md)
- [local-transcription.md](local-transcription.md)
