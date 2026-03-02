# Tool Status Self-Healing

Operational contract for tool status in `.vip/config.yaml`.

---

## Staleness Definition

A tool entry is **stale false** when all are true:

- `status: false`
- `last_checked` is missing, invalid, or older than 30 days

Only stale false entries are re-probed during routine audits.

---

## Detection Contract (/think)

On first `/think` invocation each session:

1. Read `.vip/config.yaml` `tools` section
2. Build detection list:
   - `status: null` or missing → detect
   - `status: false` + stale false → re-detect
   - `status: true` or recent false → skip
3. Normalize metadata:
   - Add `last_checked: [today]` to any existing tool entry missing it
4. Run probe methods from `SKILL.md`
5. Write updates immediately

Every touched entry must include:
- `status`
- `notes`
- `last_checked`

---

## Status-Change Messaging

Do not hide state flips:

- `false → true`:
  - "Found [tool] installed and working — updated `.vip/config.yaml`."
- `true → false`:
  - "Warning: [tool] was previously available but is not detected now. I updated `.vip/config.yaml` so this doesn't fail silently."

If status does not change, use normal experience-level reporting.

---

## Degradation Rule for `status: true`

If a tool marked `status: true` fails at use time (missing command, missing MCP tool, auth failure):

1. Re-probe that tool immediately
2. Update config to `status: false`, set `last_checked: [today]`, add explanatory notes
3. Warn the user in the same turn

Never let a previously-true tool fail silently.

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
  pipeboard:
    status: null
    method: mcp
    tier: null
    notes: "unknown"
    last_checked: null
    weekly_calls_used: 0
```

---

## See Also

- [SKILL.md](../SKILL.md)
- [tool-surfacing.md](tool-surfacing.md)
- [local-transcription.md](local-transcription.md)
