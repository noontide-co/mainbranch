#!/usr/bin/env python3
"""verify_live.py — read-only live smoke test for /site atoms.

Exercises every external dependency the atoms touch, without spending money
or making state changes. Run this after credentials are provisioned in
~/.config/vip/env.sh to confirm all upstreams reach success before merging.

Checks:
  1. domain-check brew CLI: live RDAP query (free).
  2. Cloudflare API auth: lists zones in the account (read-only).
  3. Cloudflare zone lookup: GET /zones?name=<test domain> (read-only).
  4. Porkbun API auth: POST /ping with the keys (read-only; returns yourIp).

Required env (load with `source ~/.config/vip/env.sh` first):
  CLOUDFLARE_API_TOKEN  — Zone:Read + DNS:Read minimum (Edit preferred)
  CF_ACCOUNT_ID         — find in dash.cloudflare.com → right sidebar
  PORKBUN_API_KEY
  PORKBUN_SECRET_KEY

Optional env:
  VERIFY_LIVE_CF_ZONE   — domain to lookup at Cloudflare (default: howdy.md)

Exit code: 0 if all checks pass, 1 if any fail.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _envelope import log  # noqa: E402

# ---------------------------------------------------------------------------

CF_API_BASE = "https://api.cloudflare.com/client/v4"
PORKBUN_API_BASE = "https://api.porkbun.com/api/json/v3"
DEFAULT_CF_ZONE = os.environ.get("VERIFY_LIVE_CF_ZONE", "howdy.md")

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RESET = "\033[0m"


def _ok(msg: str) -> None:
    print(f"{GREEN}✓{RESET} {msg}")


def _fail(msg: str) -> None:
    print(f"{RED}✗{RESET} {msg}")


def _info(msg: str) -> None:
    print(f"{DIM}  {msg}{RESET}")


def check_domain_check_cli() -> bool:
    print(f"\n{YELLOW}[1/4] domain-check brew CLI{RESET}")
    try:
        proc = subprocess.run(
            ["domain-check", "google.com", "--json", "--yes"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        _fail("domain-check not on PATH")
        _info("Fix: brew install domain-check")
        return False
    except subprocess.TimeoutExpired:
        _fail("domain-check timed out (30s)")
        return False

    if proc.returncode != 0:
        _fail(f"domain-check exit {proc.returncode}: {proc.stderr.strip()[:200]}")
        return False

    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        _fail("domain-check returned non-JSON")
        return False

    if not rows or not isinstance(rows, list):
        _fail(f"domain-check unexpected shape: {type(rows).__name__}")
        return False

    google = rows[0]
    if google.get("available") is True:
        _fail("google.com reported as AVAILABLE — RDAP lookup is broken")
        return False

    _ok(f"domain-check works: google.com → TAKEN (method={google.get('method_used')})")
    return True


def check_cf_auth() -> bool:
    print(f"\n{YELLOW}[2/4] Cloudflare API auth (token + account){RESET}")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    account_id = os.environ.get("CF_ACCOUNT_ID")

    if not token:
        _fail("CLOUDFLARE_API_TOKEN not set")
        _info("Fix: create token at https://dash.cloudflare.com/profile/api-tokens")
        _info("     Permissions: Zone:Read (minimum), Zone:Edit + DNS:Edit (preferred)")
        _info("     Add to ~/.config/vip/env.sh: export CLOUDFLARE_API_TOKEN=...")
        return False

    if not account_id:
        _fail("CF_ACCOUNT_ID not set")
        _info("Fix: find it in dash.cloudflare.com → right sidebar of any zone")
        _info("     Add to ~/.config/vip/env.sh: export CF_ACCOUNT_ID=...")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start = time.monotonic()
    try:
        resp = requests.get(
            f"{CF_API_BASE}/user/tokens/verify", headers=headers, timeout=15
        )
    except requests.RequestException as exc:
        _fail(f"network error contacting Cloudflare: {exc}")
        return False

    latency_ms = int((time.monotonic() - start) * 1000)

    if resp.status_code != 200:
        _fail(f"token verify returned HTTP {resp.status_code}")
        try:
            errors = resp.json().get("errors", [])
            for err in errors:
                _info(f"  cf code {err.get('code')}: {err.get('message')}")
        except ValueError:
            pass
        _info("Fix: regenerate token with correct scopes")
        return False

    try:
        body = resp.json()
    except ValueError:
        _fail("CF returned non-JSON for token verify")
        return False

    status = body.get("result", {}).get("status")
    if status != "active":
        _fail(f"token verify status: {status} (expected 'active')")
        return False

    _ok(f"CF token verified ({latency_ms}ms): status=active")
    _ok(f"CF_ACCOUNT_ID set: {account_id[:8]}…")
    return True


def check_cf_zone_lookup() -> bool:
    print(f"\n{YELLOW}[3/4] Cloudflare zone lookup ({DEFAULT_CF_ZONE}){RESET}")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    account_id = os.environ.get("CF_ACCOUNT_ID")

    if not token or not account_id:
        _fail("Skipped — CF auth check failed")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start = time.monotonic()
    try:
        resp = requests.get(
            f"{CF_API_BASE}/zones",
            headers=headers,
            params={"name": DEFAULT_CF_ZONE, "account.id": account_id},
            timeout=15,
        )
    except requests.RequestException as exc:
        _fail(f"network error: {exc}")
        return False

    latency_ms = int((time.monotonic() - start) * 1000)

    if resp.status_code != 200:
        _fail(f"zone lookup returned HTTP {resp.status_code}")
        try:
            for err in resp.json().get("errors", []):
                _info(f"  cf code {err.get('code')}: {err.get('message')}")
        except ValueError:
            pass
        return False

    try:
        body = resp.json()
    except ValueError:
        _fail("non-JSON response")
        return False

    if not body.get("success"):
        _fail("zone lookup unsuccessful")
        return False

    zones = body.get("result") or []
    if not zones:
        _info(f"No zone found for {DEFAULT_CF_ZONE} in account {account_id[:8]}…")
        _info(f"Override with: VERIFY_LIVE_CF_ZONE=<some-domain-you-own> python3 verify_live.py")
        _info("(This is informational, not a failure — the API call succeeded.)")
        _ok(f"CF zone lookup endpoint works ({latency_ms}ms, 0 results)")
        return True

    zone = zones[0]
    ns_pair = zone.get("name_servers") or []
    _ok(f"CF zone lookup works ({latency_ms}ms): id={zone.get('id', '')[:12]}…")
    _ok(f"  zone status: {zone.get('status')}, ns: {ns_pair}")
    return True


def check_porkbun_ping() -> bool:
    print(f"\n{YELLOW}[4/4] Porkbun API auth (POST /ping){RESET}")
    api_key = os.environ.get("PORKBUN_API_KEY")
    secret_key = os.environ.get("PORKBUN_SECRET_KEY")

    if not api_key or not secret_key:
        _fail("PORKBUN_API_KEY and/or PORKBUN_SECRET_KEY not set")
        _info("Fix: create keys at https://porkbun.com/account/api")
        _info("     Add both to ~/.config/vip/env.sh:")
        _info("       export PORKBUN_API_KEY=pk1_...")
        _info("       export PORKBUN_SECRET_KEY=sk1_...")
        return False

    start = time.monotonic()
    try:
        resp = requests.post(
            f"{PORKBUN_API_BASE}/ping",
            json={"apikey": api_key, "secretapikey": secret_key},
            timeout=15,
        )
    except requests.RequestException as exc:
        _fail(f"network error: {exc}")
        _info("If the URL in the error references porkbun.com (not api.porkbun.com), the host fix didn't apply.")
        return False

    latency_ms = int((time.monotonic() - start) * 1000)

    try:
        body = resp.json()
    except ValueError:
        _fail(f"non-JSON response (HTTP {resp.status_code})")
        return False

    if body.get("status") != "SUCCESS":
        _fail(f"Porkbun rejected ping: {body.get('message', 'unknown')}")
        return False

    _ok(f"Porkbun /ping works ({latency_ms}ms): yourIp={body.get('yourIp')}")
    _ok(f"  host pinned correctly to api.porkbun.com")
    return True


def main() -> int:
    print(f"{YELLOW}=== /site atoms — live verification ==={RESET}")
    print(f"{DIM}Read-only smoke test. No state changes, no spending.{RESET}")
    print(f"{DIM}Run after `source ~/.config/vip/env.sh`.{RESET}")

    results = [
        ("domain-check CLI", check_domain_check_cli()),
        ("Cloudflare auth", check_cf_auth()),
        ("Cloudflare zone lookup", check_cf_zone_lookup()),
        ("Porkbun ping", check_porkbun_ping()),
    ]

    print(f"\n{YELLOW}=== Summary ==={RESET}")
    failed = 0
    for name, ok in results:
        marker = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"  {marker} {name}")
        if not ok:
            failed += 1

    print()
    if failed == 0:
        print(f"{GREEN}All 4 checks passed. Atoms are live-ready.{RESET}")
        return 0
    print(f"{RED}{failed}/4 checks failed.{RESET} See messages above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
