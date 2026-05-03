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
"$PYTHON" -m mypy mb
"$PYTHON" -m pytest tests/ -v --cov=mb --cov-report=term-missing --cov-fail-under=70
"$PYTHON" -m mb skill validate --all --json
