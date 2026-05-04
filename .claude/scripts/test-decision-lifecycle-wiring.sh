#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
START_FILE="$ROOT_DIR/.claude/skills/mb-start/references/readiness-assessment.md"
END_FILE="$ROOT_DIR/.claude/skills/mb-end/SKILL.md"

fail=0

assert_contains() {
  local file="$1"
  local pattern="$2"
  local label="$3"

  if grep -q "$pattern" "$file"; then
    printf 'PASS: %s\n' "$label"
  else
    printf 'FAIL: %s\n' "$label"
    fail=1
  fi
}

assert_contains "$START_FILE" ".claude/scripts/decision_lifecycle_audit.sh" "/mb-start references shared lifecycle script path"
assert_contains "$END_FILE" ".claude/scripts/decision_lifecycle_audit.sh" "/mb-end references shared lifecycle script path"
assert_contains "$START_FILE" "bash \"\\\$AUDIT_SCRIPT\" --repo" "/mb-start executes shared lifecycle script"
assert_contains "$END_FILE" "bash \"\\\$AUDIT_SCRIPT\" --repo" "/mb-end executes shared lifecycle script"

if [ "$fail" -ne 0 ]; then
  exit 1
fi

printf 'PASS: shared lifecycle script wiring is present in /mb-start and /mb-end\n'
