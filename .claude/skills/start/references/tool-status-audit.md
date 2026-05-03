# Tool Status Audit

Lightweight self-healing pass run during `/start` before readiness scoring.

---

## Goal

Repair stale false negatives in `.vip/config.yaml` without running a full research tool scan.

---

## Audit Flow

1. Read `.vip/config.yaml` `tools` section
2. For each tool entry:
   - If `status: false` and stale (`last_checked` missing, invalid, or older than 30 days), re-probe
   - If entry exists and `last_checked` is missing, add `last_checked: [today]`
3. Write config updates immediately
4. Notify only on state changes:
   - `false → true`: "Found [tool] installed — updated your config."
   - `true → false`: "Warning: [tool] was previously available but is now missing."
5. If no status changes, stay silent

---

## Scope Boundary

- This is not full `/think` tool detection.
- Only stale false entries are probed.
- `status: true` entries are not routinely re-probed here.
- Full detection and tool surfacing remain in `/think`.

Use probe methods defined in `/think` (`Gemini`, `Grok`, `whisper`, document tools, and lazy `Pipeboard` handling).

---

## See Also

- [SKILL.md](../SKILL.md)
- [mcp-preflight.md](mcp-preflight.md)
- `/think` tool-status-self-healing reference
