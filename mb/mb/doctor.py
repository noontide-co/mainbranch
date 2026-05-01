"""``mb doctor`` — diagnose a Main Branch consumer repo.

Checks Claude Code on PATH, gh auth status, network reachability,
``librsvg`` for ``tool-og-render``, and walks ``core/finance/`` looking
for cloud-backed paths. Cloud-backup detection triggers educational
triage per the master decision: prints a banner and offers
``mb educational anti-cloud-backup`` for the long-form rationale.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mb import __version__
from mb.engine import install_mode, link_status

CLOUD_PREFIXES = (
    "Library/Mobile Documents",  # iCloud Drive
    "Library/CloudStorage",  # macOS unified cloud
    "Google Drive",
    "GoogleDrive",
    "Dropbox",
    "OneDrive",
)


def _which(name: str) -> str:
    """Return path of binary or empty string."""
    return shutil.which(name) or ""


def _gh_status() -> tuple[bool, str]:
    if not _which("gh"):
        return False, "gh not on PATH"
    try:
        out = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return True, "authenticated"
        return False, "not authenticated"
    except subprocess.SubprocessError:
        return False, "gh probe failed"


def _net() -> tuple[bool, str]:
    """Best-effort: open a TCP connection to api.github.com:443."""
    try:
        with socket.create_connection(("api.github.com", 443), timeout=3):
            return True, "reachable"
    except OSError:
        return False, "no route to api.github.com"


def _rsvg() -> tuple[bool, str]:
    """Check rsvg-convert presence (tool-og-render primary path)."""
    if _which("rsvg-convert"):
        return True, "rsvg-convert on PATH"
    return False, "rsvg-convert missing (brew install librsvg)"


def _version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        digits = ""
        for char in piece:
            if not char.isdigit():
                break
            digits += char
        parts.append(int(digits or "0"))
    return tuple(parts)


def _latest_pypi_version(timeout: float = 3.0) -> str:
    with urllib.request.urlopen("https://pypi.org/pypi/mainbranch/json", timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    import json

    parsed = json.loads(data)
    version = parsed.get("info", {}).get("version", "")
    return version if isinstance(version, str) else ""


def _mainbranch_version_check() -> dict[str, Any]:
    mode = install_mode()
    if mode in {"clone", "source"}:
        return {
            "name": "mainbranch-version",
            "ok": True,
            "detail": f"{__version__} ({mode} mode)",
            "severity": "info",
        }

    try:
        latest = _latest_pypi_version()
    except (OSError, TimeoutError, urllib.error.URLError):
        return {
            "name": "mainbranch-version",
            "ok": True,
            "detail": f"{__version__}; could not check PyPI for latest",
            "severity": "info",
        }

    if latest and _version_key(latest) > _version_key(__version__):
        return {
            "name": "mainbranch-version",
            "ok": False,
            "detail": (
                f"installed {__version__}, latest is {latest}. "
                "Run `pipx upgrade mainbranch`; for context run "
                "`mb educational upgrading-mainbranch`."
            ),
            "severity": "warn",
        }
    return {
        "name": "mainbranch-version",
        "ok": True,
        "detail": f"{__version__} is current" if latest else __version__,
    }


def _detect_cloud_paths(repo: Path) -> list[str]:
    """Return list of cloud-prefixed paths inside the repo's finance dir.

    The check matches against the *resolved real path* of ``core/finance/``
    so a symlink into iCloud is caught.
    """
    finance = repo / "core" / "finance"
    if not finance.exists():
        return []
    real = finance.resolve()
    home = str(Path.home())
    rel = str(real)
    if rel.startswith(home):
        rel = rel[len(home) + 1 :]
    hits = [p for p in CLOUD_PREFIXES if p in rel]
    return hits


def run(path: str) -> dict[str, Any]:
    """Run all checks, return a structured report dict."""
    repo = Path(path).resolve()
    checks: list[dict[str, Any]] = []

    cc_path = _which("claude")
    checks.append(
        {
            "name": "claude-code",
            "ok": bool(cc_path),
            "detail": cc_path or "claude not on PATH (https://claude.ai/install)",
        }
    )

    gh_ok, gh_detail = _gh_status()
    checks.append({"name": "gh-auth", "ok": gh_ok, "detail": gh_detail})

    net_ok, net_detail = _net()
    checks.append({"name": "network", "ok": net_ok, "detail": net_detail})

    rsvg_ok, rsvg_detail = _rsvg()
    checks.append(
        {
            "name": "librsvg",
            "ok": rsvg_ok,
            "detail": rsvg_detail,
            "severity": "warn" if not rsvg_ok else "ok",
        }
    )

    repo_ok = repo.exists() and os.access(repo, os.W_OK)
    checks.append(
        {
            "name": "repo-writable",
            "ok": repo_ok,
            "detail": str(repo),
        }
    )

    wiring = link_status(repo)
    wiring_ok = bool(wiring["ok"])
    checks.append(
        {
            "name": "skill-wiring",
            "ok": wiring_ok,
            "detail": (
                f"start skill linked via {wiring['engine_root']}"
                if wiring_ok
                else "Claude Code skill links missing. Run `mb skill link --repo .`."
            ),
            "severity": "ok"
            if wiring_ok
            else ("warn" if not (repo / "CLAUDE.md").exists() else "error"),
        }
    )

    checks.append(_mainbranch_version_check())

    cloud_hits = _detect_cloud_paths(repo)
    cloud_ok = not cloud_hits
    checks.append(
        {
            "name": "anti-cloud-backup",
            "ok": cloud_ok,
            "detail": (
                "core/finance/ looks cloud-backed: "
                + ", ".join(cloud_hits)
                + ". Run `mb educational anti-cloud-backup` for context."
            )
            if cloud_hits
            else "core/finance/ not under iCloud / GDrive / Dropbox / OneDrive",
            "severity": "warn" if cloud_hits else "ok",
        }
    )

    skool_token = bool(os.environ.get("SKOOL_TOKEN"))
    checks.append(
        {
            "name": "skool-token",
            "ok": True,  # informational only
            "detail": "set" if skool_token else "unset (optional)",
            "severity": "info",
        }
    )

    # ``ok`` overall: every check must pass UNLESS its severity is warn/info.
    overall = all(c["ok"] or c.get("severity") in {"warn", "info"} for c in checks)
    hard_fail = any(not c["ok"] and c.get("severity") not in {"warn", "info"} for c in checks)

    return {
        "ok": overall and not hard_fail,
        "checks": checks,
        "repo": str(repo),
        "python": sys.version.split()[0],
    }


def render_human(report: dict[str, Any]) -> None:
    """Print a friendly summary to stdout."""
    from rich.console import Console

    console = Console()
    console.print(f"\n[bold]mb doctor[/bold]  {report['repo']}\n")
    for c in report["checks"]:
        sev = c.get("severity", "ok")
        if c["ok"]:
            mark = "[green]ok[/green]"
        elif sev == "warn":
            mark = "[yellow]warn[/yellow]"
        elif sev == "info":
            mark = "[blue]info[/blue]"
        else:
            mark = "[red]fail[/red]"
        console.print(f"  {mark}  {c['name']:<22} {c['detail']}")
    console.print()
    if report["ok"]:
        console.print("[green]all green[/green]")
    else:
        console.print("[red]issues above; see remediation lines.[/red]")
