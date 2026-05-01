# Decision Lifecycle Reconciliation (Step 2b)

Run the shared lifecycle audit script so `/end` uses the same decision buckets as `/start`.

```bash
# Resolve vip script path (settings.local.json first, then ~/.config/vip/local.yaml)
AUDIT_SCRIPT=$(python3 -c "
import json, os
path = '.claude/settings.local.json'
target = ''
try:
    with open(path) as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        candidate = os.path.join(d, '.claude/scripts/decision_lifecycle_audit.sh')
        if os.path.isfile(candidate):
            target = candidate
            break
except Exception:
    pass
print(target)
" 2>/dev/null)

if [ -z "$AUDIT_SCRIPT" ] && [ -f "$HOME/.config/vip/local.yaml" ]; then
  vip_path=$(awk -F': *' '/^vip_path:/ {print $2; exit}' "$HOME/.config/vip/local.yaml" | tr -d '"')
  [ -n "$vip_path" ] && AUDIT_SCRIPT="$vip_path/.claude/scripts/decision_lifecycle_audit.sh"
fi

if [ -n "$AUDIT_SCRIPT" ] && [ -f "$AUDIT_SCRIPT" ]; then
  bash "$AUDIT_SCRIPT" --repo "[repo-path]" --format text
else
  echo "Decision lifecycle audit script not found; fallback to strict status counts."
  codified=0
  accepted=0
  invalid_or_missing=0

  for f in [repo-path]/decisions/*.md; do
    [ -f "$f" ] || continue
    status=$(awk 'NR==1&&$0=="---"{fm=1;next} fm&&$0=="---"{exit} fm&&/^status:[[:space:]]*/{val=$0; sub(/^status:[[:space:]]*/, "", val); gsub(/[[:space:]]+$/, "", val); print val; exit}' "$f")
    case "$status" in
      codified) codified=$((codified + 1)) ;;
      accepted) accepted=$((accepted + 1)) ;;
      proposed) ;;
      *) invalid_or_missing=$((invalid_or_missing + 1)) ;;
    esac
  done

  printf "Decisions: %s codified, %s accepted\n" "$codified" "$accepted"
  [ "$invalid_or_missing" -gt 0 ] && printf "Decisions with invalid/missing status: %s\n" "$invalid_or_missing"
fi
```

## Expected Buckets

From the shared script:

- `needs_review` — accepted decisions with implementation evidence
- `action_needed` — accepted decisions with no evidence and not stale
- `stale_orphaned` — accepted decisions past stale threshold with weak/no evidence
- `invalid_or_missing` — missing/invalid lifecycle frontmatter (never guess)

## Manual Confirmation Rule (Non-Negotiable)

- Never auto-flip to `codified` from evidence alone.
- If `needs_review > 0`, offer: "I found [N] accepted decisions with implementation evidence. Want to review and mark any as codified now?"
- For each file, require explicit user confirmation before editing `status: accepted` -> `status: codified`.
- After each edit, read the file back and confirm there is exactly one `status:` field and it is `codified`.

If the user declines, leave statuses unchanged and continue to Step 3.
