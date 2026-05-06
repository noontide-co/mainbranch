#!/usr/bin/env bash
# setup_creds.sh — write Cloudflare credentials into ~/.config/vip/env.sh.
#
# Prompts for an API token (hidden input) + account ID (visible), then writes
# CLOUDFLARE_API_TOKEN, CLOUDFLARE_API_TOKEN_REGISTRAR, and CF_ACCOUNT_ID to
# ~/.config/vip/env.sh with chmod 600. Idempotent — re-running replaces
# existing values for these three vars without duplicating lines.
#
# This is the legacy env bridge for /mb-site atoms. From the business repo,
# also run `mb connect cloudflare --token-stdin --metadata token_type=account
# --metadata account_id=<account-id>` so Main Branch stores provider readiness
# metadata in .mb/connect.yaml and keeps the secret outside git.
#
# Token must have these scopes on the account that owns the /mb-site assets
# (registrar domains + Pages projects + DNS zones):
#   Cloudflare Registrar:Edit
#   Zone:Read, Zone:Edit
#   DNS:Read, DNS:Edit
#   Cloudflare Pages:Edit
# Pin Account Resources to the single account (not "All accounts") so the
# token can't drift to the wrong place.
#
# Create at: https://dash.cloudflare.com/profile/api-tokens

set -euo pipefail

ENV_FILE="$HOME/.config/vip/env.sh"

mkdir -p "$(dirname "$ENV_FILE")"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

cat <<'EOF'

=== Cloudflare credentials setup for /mb-site atoms ===

Writes to: ~/.config/vip/env.sh (chmod 600, owner-only)
Vars set:  CLOUDFLARE_API_TOKEN, CLOUDFLARE_API_TOKEN_REGISTRAR, CF_ACCOUNT_ID

Existing values for these three vars will be replaced (idempotent).
Token input is hidden; nothing is echoed back to the terminal.

This script writes the legacy atom env bridge. It does not replace the
repo-scoped Main Branch connection stored by `mb connect`.

EOF

# --- Token (hidden) ---
printf 'Paste CF API token (input hidden, hit Enter when done): '
IFS= read -rs CF_TOKEN
echo
CF_TOKEN="$(printf '%s' "$CF_TOKEN" | tr -d '[:space:]')"

if [[ ${#CF_TOKEN} -lt 20 ]]; then
  echo "ERROR: token looks too short (got ${#CF_TOKEN} chars). Aborting; nothing written." >&2
  exit 1
fi

# --- Account ID (visible — not secret) ---
printf 'Paste CF_ACCOUNT_ID (visible, 32 hex chars): '
IFS= read -r CF_ACCT
CF_ACCT="$(printf '%s' "$CF_ACCT" | tr -d '[:space:]')"

if [[ ! "$CF_ACCT" =~ ^[a-f0-9]{32}$ ]]; then
  echo "ERROR: account ID should be 32 lowercase hex chars; got '${CF_ACCT}'." >&2
  echo "       Find it in dash.cloudflare.com → click any zone → right sidebar." >&2
  exit 1
fi

# --- Idempotent var update (replace existing line; otherwise append) ---
update_var() {
  local var="$1"
  local val="$2"
  if grep -q "^export ${var}=" "$ENV_FILE"; then
    awk -v var="$var" -v val="$val" '
      $0 ~ "^export " var "=" { printf "export %s=\"%s\"\n", var, val; next }
      { print }
    ' "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
  else
    printf 'export %s="%s"\n' "$var" "$val" >> "$ENV_FILE"
  fi
}

update_var CLOUDFLARE_API_TOKEN           "$CF_TOKEN"
update_var CLOUDFLARE_API_TOKEN_REGISTRAR "$CF_TOKEN"
update_var CF_ACCOUNT_ID                  "$CF_ACCT"

chmod 600 "$ENV_FILE"

# --- Verify, redacted ---
echo
echo "=== ~/.config/vip/env.sh (relevant lines, redacted) ==="
if grep -qE "^export (CLOUDFLARE_API_TOKEN|CLOUDFLARE_API_TOKEN_REGISTRAR|CF_ACCOUNT_ID)=" "$ENV_FILE"; then
  grep -E "^export (CLOUDFLARE_API_TOKEN|CLOUDFLARE_API_TOKEN_REGISTRAR|CF_ACCOUNT_ID)=" "$ENV_FILE" \
    | sed -E 's/=("[^"]+"|[^[:space:]]+)/=<set>/'
else
  echo "WARNING: nothing matched after write — file may have unexpected format." >&2
fi

cat <<EOF

Next:
  source ~/.config/vip/env.sh
  printf '%s' "\$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=${CF_ACCT}
  mb connect test cloudflare
  python3 .claude/skills/mb-site/scripts/verify_live.py

`cfat_` account tokens route automatically when account_id metadata is present;
`token_type=account` stays in the command because it is explicit and works on
older mb versions. Expected: CF auth + zone lookup should flip green
immediately. The token is never printed; safe to scroll back.
EOF
