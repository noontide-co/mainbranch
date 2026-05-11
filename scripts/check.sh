#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/mb"

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
  else
    PYTHON=python
  fi
fi

"$PYTHON" -m ruff format --check .
"$PYTHON" -m ruff check .
"$PYTHON" -m mypy mb tests
"$PYTHON" -m pytest tests/ -v --cov=mb --cov-report=term-missing --cov-fail-under=79
"$PYTHON" -m mb skill validate --all --json
fail=0
while IFS= read -r f; do
  n=$(wc -l < "../$f")
  if [ "$n" -gt 500 ]; then
    echo "SKILL.md too long: $f ($n lines > 500). Split references out." >&2
    fail=1
  fi
done < <(cd .. && find .claude/playbooks -name SKILL.md 2>/dev/null)

# Docs naming convention.
# Under docs/, Markdown filenames are lowercase kebab-case.
# Allowed exceptions:
#   - docs/README.md (the docs index).
#   - docs/reports/YYYY-MM-DD-<kebab>.md (dated evidence reports).
while IFS= read -r rel; do
  base="$(basename "$rel")"
  if [ "$rel" = "docs/README.md" ]; then
    continue
  fi
  case "$rel" in
    docs/reports/*)
      if [[ "$base" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]]; then
        rest="${base#????-??-??-}"
        if [[ ! "$rest" =~ ^[a-z0-9]+(-[a-z0-9]+)*\.md$ ]]; then
          echo "Docs naming: $rel — after YYYY-MM-DD- prefix, use lowercase kebab-case." >&2
          fail=1
        fi
        continue
      fi
      ;;
  esac
  if [[ ! "$base" =~ ^[a-z0-9]+(-[a-z0-9]+)*\.md$ ]]; then
    echo "Docs naming: $rel — use lowercase kebab-case (only docs/README.md may be all-caps)." >&2
    fail=1
  fi
done < <(cd .. && find docs -type f -name '*.md' 2>/dev/null | sort)

exit $fail
