#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: decision_lifecycle_audit.sh [--repo PATH] [--format text|json] [--stale-days N]

Audits decision lifecycle state using frontmatter-only parsing.

Options:
  --repo PATH        Business repo path (default: current directory)
  --format FORMAT    Output format: text|json (default: text)
  --stale-days N     Accepted stale threshold in days (default: 14)
  -h, --help         Show this help
EOF
}

repo="."
format="text"
stale_days=14

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo)
      repo="${2:-}"
      shift 2
      ;;
    --format)
      format="${2:-}"
      shift 2
      ;;
    --stale-days)
      stale_days="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$format" in
  text|json) ;;
  *)
    echo "Invalid format: $format (expected text or json)" >&2
    exit 2
    ;;
esac

case "$stale_days" in
  ''|*[!0-9]*)
    echo "Invalid --stale-days: $stale_days" >&2
    exit 2
    ;;
esac

for cmd in awk git date; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 3
  fi
done

if ! repo_abs=$(cd "$repo" 2>/dev/null && pwd); then
  echo "Repo path not found: $repo" >&2
  exit 3
fi

if ! git -C "$repo_abs" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository: $repo_abs" >&2
  exit 3
fi

decisions_dir="$repo_abs/decisions"
reference_dir="$repo_abs/reference"

iso_to_epoch() {
  local iso="$1"

  if [ -z "$iso" ]; then
    return 1
  fi

  if epoch=$(date -j -f "%Y-%m-%d" "$iso" "+%s" 2>/dev/null); then
    printf "%s" "$epoch"
    return 0
  fi

  if epoch=$(date -d "$iso" "+%s" 2>/dev/null); then
    printf "%s" "$epoch"
    return 0
  fi

  return 1
}

cutoff_date() {
  local days="$1"

  if cutoff=$(date -u -v-"${days}"d "+%Y-%m-%d" 2>/dev/null); then
    printf "%s" "$cutoff"
    return 0
  fi

  if cutoff=$(date -u -d "${days} days ago" "+%Y-%m-%d" 2>/dev/null); then
    printf "%s" "$cutoff"
    return 0
  fi

  return 1
}

is_iso_date() {
  case "$1" in
    ????-??-??) return 0 ;;
    *) return 1 ;;
  esac
}

json_escape() {
  printf "%s" "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

if ! cutoff=$(cutoff_date "$stale_days"); then
  echo "Unable to compute stale cutoff date" >&2
  exit 3
fi

now_iso=$(date -u "+%Y-%m-%d")
if ! now_epoch=$(iso_to_epoch "$now_iso"); then
  now_epoch=""
fi

tmp_records=$(mktemp)
trap 'rm -f "$tmp_records"' EXIT

total=0
codified=0
accepted=0
proposed=0
needs_review=0
action_needed=0
stale_orphaned=0
invalid_or_missing=0
parse_errors=0

if [ -d "$decisions_dir" ]; then
  for decision_file in "$decisions_dir"/*.md; do
    [ -f "$decision_file" ] || continue
    total=$((total + 1))

    if ! parsed=$(awk '
      NR==1 && $0=="---" { fm=1; next }
      fm && $0=="---" { exit }
      fm && /^status:[[:space:]]*/ {
        st=$0
        sub(/^status:[[:space:]]*/, "", st)
        gsub(/[[:space:]]+$/, "", st)
        gsub(/^["'"'"']|["'"'"']$/, "", st)
        status=st
      }
      fm && /^date:[[:space:]]*/ {
        d=$0
        sub(/^date:[[:space:]]*/, "", d)
        gsub(/[[:space:]]+$/, "", d)
        gsub(/^["'"'"']|["'"'"']$/, "", d)
        datev=d
      }
      END { print status "\t" datev }
    ' "$decision_file"); then
      parse_errors=$((parse_errors + 1))
      continue
    fi

    status=${parsed%%$'\t'*}
    date_value=${parsed#*$'\t'}
    file_rel="decisions/$(basename "$decision_file")"

    bucket=""
    confidence="low"
    evidence_commits=0
    age_days=""

    if is_iso_date "$date_value" && [ -n "${now_epoch:-}" ]; then
      if decision_epoch=$(iso_to_epoch "$date_value"); then
        age_days=$(( (now_epoch - decision_epoch) / 86400 ))
      fi
    fi

    case "$status" in
      codified)
        codified=$((codified + 1))
        bucket="codified"
        confidence="high"
        ;;
      proposed)
        proposed=$((proposed + 1))
        bucket="proposed"
        confidence="medium"
        ;;
      accepted)
        accepted=$((accepted + 1))

        if is_iso_date "$date_value" && [ -d "$reference_dir" ]; then
          evidence_commits=$(git -C "$repo_abs" log --since="${date_value} 00:00:00" --pretty=format:%H -- "$reference_dir" 2>/dev/null | awk 'NF { c++ } END { print c + 0 }')
        elif [ -d "$reference_dir" ]; then
          evidence_commits=$(git -C "$repo_abs" log --since="30 days ago" --pretty=format:%H -- "$reference_dir" 2>/dev/null | awk 'NF { c++ } END { print c + 0 }')
        fi

        if [ "$evidence_commits" -gt 0 ]; then
          bucket="needs_review"
          needs_review=$((needs_review + 1))
          # Reference commit evidence is directional, not proof of codification.
          confidence="medium"
        elif is_iso_date "$date_value" && [ "$date_value" \< "$cutoff" ]; then
          bucket="stale_orphaned"
          stale_orphaned=$((stale_orphaned + 1))
          confidence="medium"
        else
          bucket="action_needed"
          action_needed=$((action_needed + 1))
          if is_iso_date "$date_value"; then
            confidence="medium"
          else
            confidence="low"
          fi
        fi
        ;;
      *)
        invalid_or_missing=$((invalid_or_missing + 1))
        bucket="invalid_or_missing"
        confidence="low"
        ;;
    esac

    [ -n "$status" ] || status="(missing)"
    [ -n "$date_value" ] || date_value="(missing)"
    [ -n "$age_days" ] || age_days="(unknown)"

    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$file_rel" "$status" "$date_value" "$bucket" "$confidence" "$evidence_commits" "$age_days" \
      >> "$tmp_records"
  done
fi

if [ "$parse_errors" -gt 0 ]; then
  echo "Frontmatter parsing failed for $parse_errors decision file(s)" >&2
  exit 4
fi

if [ "$format" = "json" ]; then
  printf '{\n'
  printf '  "summary": {\n'
  printf '    "total": %s,\n' "$total"
  printf '    "codified": %s,\n' "$codified"
  printf '    "accepted": %s,\n' "$accepted"
  printf '    "proposed": %s,\n' "$proposed"
  printf '    "needs_review": %s,\n' "$needs_review"
  printf '    "action_needed": %s,\n' "$action_needed"
  printf '    "stale_orphaned": %s,\n' "$stale_orphaned"
  printf '    "invalid_or_missing": %s,\n' "$invalid_or_missing"
  printf '    "stale_days": %s,\n' "$stale_days"
  printf '    "cutoff_date": "%s"\n' "$(json_escape "$cutoff")"
  printf '  },\n'
  printf '  "records": [\n'

  first=1
  while IFS=$'\t' read -r file_rel status date_value bucket confidence evidence_commits age_days; do
    [ -n "$file_rel" ] || continue
    if [ "$first" -eq 0 ]; then
      printf ',\n'
    fi
    first=0

    printf '    {"file":"%s","status":"%s","date":"%s","bucket":"%s","confidence":"%s","evidence_commits":%s,"age_days":"%s"}' \
      "$(json_escape "$file_rel")" \
      "$(json_escape "$status")" \
      "$(json_escape "$date_value")" \
      "$(json_escape "$bucket")" \
      "$(json_escape "$confidence")" \
      "$evidence_commits" \
      "$(json_escape "$age_days")"
  done < "$tmp_records"

  printf '\n  ]\n'
  printf '}\n'
  exit 0
fi

printf 'SUMMARY|total=%s|codified=%s|accepted=%s|proposed=%s|needs_review=%s|action_needed=%s|stale_orphaned=%s|invalid_or_missing=%s|cutoff=%s\n' \
  "$total" "$codified" "$accepted" "$proposed" "$needs_review" "$action_needed" "$stale_orphaned" "$invalid_or_missing" "$cutoff"

while IFS=$'\t' read -r file_rel status date_value bucket confidence evidence_commits age_days; do
  [ -n "$file_rel" ] || continue
  printf 'RECORD|file=%s|status=%s|date=%s|bucket=%s|confidence=%s|evidence_commits=%s|age_days=%s\n' \
    "$file_rel" "$status" "$date_value" "$bucket" "$confidence" "$evidence_commits" "$age_days"
done < "$tmp_records"

printf '\n'
printf '%s decisions need review\n' "$needs_review"
printf '%s look implemented but are not marked codified\n' "$needs_review"
printf '%s still need codification\n' "$action_needed"
printf '%s appear stale\n' "$stale_orphaned"
if [ "$invalid_or_missing" -gt 0 ]; then
  printf '%s have invalid or missing status frontmatter\n' "$invalid_or_missing"
fi

exit 0
