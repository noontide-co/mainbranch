# Tool Status Audit

Lightweight provider/readiness pass run during `/mb-start` before routing.

---

## Goal

Use deterministic `mb` facts for provider readiness, setup repair, and stale
status before any skill-specific runtime checks. `/mb-start` should not
reimplement provider probes or mutate provider state from prose.

---

## Audit Flow

1. Read `mb status --json --peek`.
2. If a provider, GitHub, runtime-wiring, or drift section is degraded, missing,
   or selected by the operator, run:

   ```bash
   mb connect doctor --json
   ```

3. Use the CLI's `summary`, `next_command`, and `repair_command` in the
   operator-facing answer.
4. Run `mb connect plan` when the operator asks what to connect first.
5. Stay silent when status reports the selected path as healthy.

---

## Scope Boundary

- This is not full `/mb-think` runtime detection.
- Provider readiness belongs to `mb status`, `mb connect plan`, and
  `mb connect doctor --json`.
- Local runtime tool presence is checked only when a selected workflow needs it
  and `mb` cannot inspect it directly.
- Full research tool surfacing remains in `/mb-think`.

Use probe methods defined in `/mb-think` only for runtime-local tools after the
provider facts have been read.

---

## See Also

- [SKILL.md](../SKILL.md)
- [mcp-preflight.md](mcp-preflight.md)
- `/mb-think` tool-status-self-healing reference
