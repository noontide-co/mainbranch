"""``mb doctor`` — check the health of a Main Branch repo.

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
from pathlib import Path
from typing import Any

from mb.engine import install_mode, link_status
from mb.freshness import format_update_alert, package_update_status, version_key
from mb.migrate import LATEST_SCHEMA_VERSION, pending_migrations, read_schema_version
from mb.skill_validate import run_all as validate_all_skills

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


def _mainbranch_version_check(update: dict[str, Any]) -> dict[str, Any]:
    mode = install_mode()
    severity = str(update["severity"])
    latest = str(update["latest"])
    installed = str(update["installed"])

    if mode in {"clone", "source"} and severity not in {"required", "recommended"}:
        return {
            "name": "mainbranch-version",
            "ok": True,
            "detail": f"{update['installed']} ({mode} mode)",
            "severity": "info",
        }

    if severity == "unknown":
        return {
            "name": "mainbranch-version",
            "ok": True,
            "detail": f"{installed}; could not check PyPI for latest",
            "severity": "info",
        }

    if severity == "required":
        return {
            "name": "mainbranch-version",
            "ok": False,
            "detail": (
                f"installed {installed}; minimum supported is {update['minimum_supported']}. "
                f"Run `{update['command']}`."
            ),
            "severity": "error",
        }

    if severity == "recommended" or (latest and version_key(latest) > version_key(installed)):
        return {
            "name": "mainbranch-version",
            "ok": False,
            "detail": (
                f"installed {installed}, latest is {latest}. "
                f"Run `{update['command']}` when you can."
            ),
            "severity": "warn",
        }
    return {
        "name": "mainbranch-version",
        "ok": True,
        "detail": f"{installed} is current" if latest else installed,
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


def _repo_layout_check(repo: Path) -> dict[str, Any]:
    has_core = (repo / "core").is_dir()
    has_reference_core = (repo / "reference" / "core").exists()
    has_reference = (repo / "reference").is_dir()

    if has_core:
        return {
            "name": "repo-layout",
            "ok": True,
            "detail": "current core/ layout present",
        }

    if has_reference_core:
        return {
            "name": "repo-layout",
            "ok": False,
            "detail": (
                "legacy reference/core layout detected. This still works, but "
                "run `mb skill link --repo .` after upgrading and read "
                "`docs/MIGRATING.md` before moving files."
            ),
            "severity": "warn",
        }

    if has_reference:
        return {
            "name": "repo-layout",
            "ok": False,
            "detail": (
                "legacy reference/ layout detected without core/. Main Branch can "
                "brief this repo, but current six-folder features may be limited. "
                "Read `docs/MIGRATING.md` before moving files."
            ),
            "severity": "warn",
        }

    return {
        "name": "repo-layout",
        "ok": False,
        "detail": "no core/ or reference/ layout found",
        "severity": "warn",
    }


def _schema_version_check(repo: Path) -> dict[str, Any]:
    current = read_schema_version(repo)
    pending = pending_migrations(repo)
    if pending:
        names = ", ".join(info.name for info, _module in pending)
        return {
            "name": "schema-version",
            "ok": False,
            "detail": (
                f"schema {current}; pending migration(s): {names}. "
                "Run `mb migrate --check` before `mb migrate --apply`."
            ),
            "severity": "warn",
        }
    if current == "unknown":
        return {
            "name": "schema-version",
            "ok": False,
            "detail": "schema version unknown; run `mb migrate status` from the repo root.",
            "severity": "warn",
        }
    return {
        "name": "schema-version",
        "ok": True,
        "detail": f"schema {current} (latest {LATEST_SCHEMA_VERSION})",
    }


def run(path: str) -> dict[str, Any]:
    """Run all checks, return a structured report dict."""
    repo = Path(path).resolve()
    checks: list[dict[str, Any]] = []
    update = package_update_status(repo)

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

    checks.append(_mainbranch_version_check(update))
    skill_validation = validate_all_skills()
    skill_summary = skill_validation["summary"]
    checks.append(
        {
            "name": "bundled-skills",
            "ok": bool(skill_validation["ok"]),
            "detail": (
                f"{skill_summary['passed']}/{skill_summary['skills']} bundled skill(s) validate"
                if skill_validation["ok"]
                else (
                    f"{skill_summary['failed']} bundled skill(s) failed validation; "
                    "run `mb skill validate --all`."
                )
            ),
            "severity": "ok" if skill_validation["ok"] else "error",
        }
    )
    checks.append(_repo_layout_check(repo))
    checks.append(_schema_version_check(repo))

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
        "update": update,
        "python": sys.version.split()[0],
    }


def render_human(report: dict[str, Any]) -> None:
    """Print a friendly summary to stdout."""
    from rich.console import Console

    console = Console()
    console.print(f"\n[bold]mb doctor[/bold]  {report['repo']}\n")
    alert = format_update_alert(report.get("update", {}))
    if alert:
        console.print(alert)
        console.print()
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
        console.print("[green]all good — you're set to run `claude`.[/green]")
    else:
        console.print("[red]a few things to fix above — most are quick.[/red]")
