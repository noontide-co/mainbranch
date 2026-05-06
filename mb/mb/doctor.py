"""``mb doctor`` — check the health of a Main Branch repo.

Checks Claude Code on PATH, gh auth status, network reachability,
``librsvg`` for ``tool-og-render``, and walks ``core/finance/`` looking
for cloud-backed paths. Cloud-backup detection triggers educational
triage per the master decision: prints a banner and offers
``mb educational anti-cloud-backup`` for the long-form rationale.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mb import connect as connect_mod
from mb import engine as engine_mod
from mb import graph as graph_mod
from mb import migrate as migrate_mod
from mb import onboard as onboard_mod
from mb import validate as validate_mod
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
REPAIR_SCHEMA = "mb.doctor.repair"
REPAIR_SCHEMA_VERSION = 1
LOCAL_GITIGNORE_ENTRIES = (
    ".claude/settings.local.json",
    ".claude/worktrees/",
    ".mb/backups/",
    ".mb/onboarding.json",
    ".mb/last-status-seen.json",
    ".mb/issue-drafts/",
)
LOCAL_STATE_PATHS = (
    ".mb/backups",
    ".mb/onboarding.json",
    ".mb/last-status-seen.json",
    ".mb/issue-drafts",
)
DURABLE_MB_PATHS = (".mb/schema_version", ".mb/connect.yaml")
LEGACY_CLAUDE_LINK_DIRS = (".claude/lenses", ".claude/reference")
REFERENCE_COMPAT_LINKS = {
    "reference/core": "../core",
    "reference/offers": "../core/offers",
}
STATE_ORDER = {"ok": 0, "info": 1, "warn": 2, "error": 3}


def _which(name: str) -> str:
    """Return path of binary or empty string."""
    return shutil.which(name) or ""


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _rel(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def _state_from_check(check: dict[str, Any]) -> str:
    if check.get("ok"):
        severity = str(check.get("severity") or "ok")
        return severity if severity in {"info"} else "ok"
    severity = str(check.get("severity") or "error")
    return severity if severity in {"info", "warn", "error"} else "error"


def _max_state(states: list[str]) -> str:
    if not states:
        return "ok"
    return max(states, key=lambda state: STATE_ORDER.get(state, 3))


def _read_gitignore_entries(repo: Path) -> set[str]:
    gitignore = repo / ".gitignore"
    if not gitignore.exists():
        return set()
    try:
        return {line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()}
    except OSError:
        return set()


def _append_unique_lines(path: Path, entries: list[str]) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    existing_lines = set(existing.splitlines())
    missing = [entry for entry in entries if entry not in existing_lines]
    if not missing:
        return False
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    path.write_text(existing + prefix + "\n".join(missing) + "\n", encoding="utf-8")
    return True


def _run_git(repo: Path, args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return {"ok": False, "stdout": "", "stderr": "git unavailable"}
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "returncode": proc.returncode,
    }


def _git_summary(repo: Path) -> dict[str, Any]:
    inside = _run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if not inside["ok"] or inside["stdout"] != "true":
        return {
            "inside_work_tree": False,
            "branch": "",
            "dirty": False,
            "changed_files": [],
            "state": "warn",
            "summary": "not a git work tree; initialize git before reviewable repairs",
        }
    branch = _run_git(repo, ["branch", "--show-current"])
    porcelain = _run_git(repo, ["status", "--short"])
    changed = [line for line in porcelain["stdout"].splitlines() if line]
    state = "warn" if changed else "ok"
    return {
        "inside_work_tree": True,
        "branch": branch["stdout"],
        "dirty": bool(changed),
        "changed_files": changed,
        "state": state,
        "summary": (
            f"{len(changed)} changed file(s); review before committing repair work"
            if changed
            else f"clean branch {branch['stdout'] or '(detached)'}"
        ),
    }


def _action(
    *,
    id: str,
    title: str,
    state: str,
    mode: str,
    command: str,
    safe_to_apply: bool,
    reason: str,
    writes: list[str] | None = None,
    applied: bool = False,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "state": state,
        "mode": mode,
        "command": command,
        "safe_to_apply": safe_to_apply,
        "reason": reason,
        "writes": writes or [],
        "applied": applied,
        "result": result or {},
    }


def _section(
    id: str,
    title: str,
    state: str,
    summary: str,
    *,
    checks: list[dict[str, Any]] | None = None,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "state": state,
        "summary": summary,
        "checks": checks or [],
        "actions": actions or [],
    }


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
                "brief this repo, but current schema features may be limited. "
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


def _legacy_campaigns_check(repo: Path) -> dict[str, Any]:
    """Detect legacy `campaigns/` records as drift from the canonical `pushes/` shape.

    Per the push primitive decision, ``pushes/`` is the canonical engine
    primitive. ``campaigns/`` records remain as compatibility reads but new
    coordinated work should land in ``pushes/``. This check warns when a repo
    has any legacy campaign records so the operator can preview the migration.
    """
    campaigns_dir = repo / "campaigns"
    if not campaigns_dir.is_dir():
        return {
            "name": "legacy-campaigns",
            "ok": True,
            "detail": "no legacy campaigns/ records",
            "severity": "ok",
        }

    plan = migrate_mod.plan_campaigns_to_pushes(repo)
    legacy_records: list[str] = []
    ambiguous_files: list[str] = []
    blocker_paths: list[str] = []

    for move in plan.get("moves", []):
        from_path = str(move["from"])
        legacy_records.append(f"{from_path}/campaign.md")
        ambiguous_files.extend(str(path) for path in move.get("review_inside_folder", []))

    for ambiguous in plan.get("ambiguous", []):
        ambiguous_files.append(str(ambiguous["from"]))

    for blocker in plan.get("blockers", []):
        from_path = str(blocker["from"])
        blocker_paths.append(from_path)
        record = repo / from_path / "campaign.md"
        if record.is_file():
            legacy_records.append(f"{from_path}/campaign.md")

    legacy_records = sorted(set(legacy_records))
    ambiguous_files = sorted(set(ambiguous_files))
    blocker_paths = sorted(set(blocker_paths))

    total = len(legacy_records) + len(ambiguous_files) + len(blocker_paths)
    if total == 0:
        # Empty campaigns/ folder (e.g. just a .gitkeep). No drift to warn.
        return {
            "name": "legacy-campaigns",
            "ok": True,
            "detail": "campaigns/ folder is empty",
            "severity": "ok",
        }

    parts: list[str] = []
    if legacy_records:
        parts.append(
            f"{len(legacy_records)} legacy campaign record(s) found. "
            "Main Branch now writes pushes/. Run "
            "`mb migrate campaigns --plan` to preview a safe move."
        )
    if ambiguous_files:
        parts.append(
            f"{len(ambiguous_files)} ambiguous path(s) under campaigns/ that may "
            "belong in pushes/, documents/, or stay in place; "
            "review with `mb migrate campaigns --plan`."
        )
    if blocker_paths:
        parts.append(
            f"{len(blocker_paths)} blocker(s) under campaigns/ require operator input "
            "before migration can be planned."
        )

    return {
        "name": "legacy-campaigns",
        "ok": False,
        "detail": " ".join(parts),
        "severity": "warn",
        "legacy_records": legacy_records,
        "ambiguous_files": ambiguous_files,
        "blockers": blocker_paths,
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


def _missing_gitignore_entries(repo: Path) -> list[str]:
    entries = _read_gitignore_entries(repo)
    if ".mb/" in entries:
        mb_entries = {entry for entry in LOCAL_GITIGNORE_ENTRIES if entry.startswith(".mb/")}
    else:
        mb_entries = set()
    return [
        entry
        for entry in LOCAL_GITIGNORE_ENTRIES
        if entry not in entries and entry not in mb_entries
    ]


def _local_state_summary(repo: Path) -> dict[str, Any]:
    local = [
        {"path": rel, "exists": (repo / rel).exists() or (repo / rel).is_symlink()}
        for rel in LOCAL_STATE_PATHS
    ]
    durable = [
        {"path": rel, "exists": (repo / rel).exists() or (repo / rel).is_symlink()}
        for rel in DURABLE_MB_PATHS
    ]
    missing_gitignore = [
        item["path"]
        for item in local
        if item["exists"] and item["path"] not in _read_gitignore_entries(repo)
    ]
    return {
        "state": "warn" if missing_gitignore else "ok",
        "summary": (
            f"{len(missing_gitignore)} local .mb path(s) need gitignore coverage"
            if missing_gitignore
            else ".mb local operational state is separated from durable markers"
        ),
        "local": local,
        "durable": durable,
        "missing_gitignore": missing_gitignore,
    }


def _legacy_reference_state(repo: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for rel, expected_target in REFERENCE_COMPAT_LINKS.items():
        path = repo / rel
        if not path.exists() and not path.is_symlink():
            checks.append(
                {
                    "path": rel,
                    "state": "ok",
                    "summary": "absent",
                    "kind": "absent",
                }
            )
            continue
        if path.is_symlink():
            target = path.readlink().as_posix()
            exists = path.exists()
            if target == expected_target and exists:
                state = "info"
                summary = f"compatibility link -> {target}"
                kind = "compat-link"
            elif not exists:
                state = "warn"
                summary = f"broken symlink -> {target}"
                kind = "broken-link"
            else:
                state = "warn"
                summary = f"unexpected symlink -> {target}"
                kind = "unexpected-link"
            checks.append({"path": rel, "state": state, "summary": summary, "kind": kind})
            continue
        if path.is_dir():
            files = [
                child.relative_to(repo).as_posix()
                for child in path.rglob("*")
                if child.is_file() and not child.is_symlink()
            ]
            canonical_rel = expected_target.removeprefix("../")
            canonical = repo / canonical_rel
            state = "warn"
            kind = "legacy-content"
            if canonical.exists():
                summary = (
                    f"{len(files)} legacy file(s) remain alongside {canonical_rel}; "
                    "check for split truth before migrating"
                )
                kind = "split-truth"
            else:
                summary = f"{len(files)} legacy file(s) can be reviewed by `mb migrate --check`"
            checks.append(
                {
                    "path": rel,
                    "state": state,
                    "summary": summary,
                    "kind": kind,
                    "files": files,
                }
            )
            continue
        checks.append(
            {
                "path": rel,
                "state": "error",
                "summary": "exists but is neither a directory nor a symlink",
                "kind": "unexpected-file",
            }
        )
    return {
        "state": _max_state([str(item["state"]) for item in checks]),
        "checks": checks,
    }


def _legacy_claude_symlinks(repo: Path) -> dict[str, Any]:
    root = engine_mod.engine_root()
    active_root = root or Path("/")
    findings: list[dict[str, Any]] = []
    for rel_dir in LEGACY_CLAUDE_LINK_DIRS:
        directory = repo / rel_dir
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir()):
            if not entry.is_symlink():
                continue
            raw_target = entry.readlink()
            target = raw_target
            if not target.is_absolute():
                target = entry.parent / target
            target_text = str(target)
            target_parts = {part.lower() for part in Path(target_text).parts}
            raw_parts = {part.lower() for part in Path(str(raw_target)).parts}
            clone_named = bool((target_parts | raw_parts) & {"mb-vip", "mainbranch"})
            try:
                inside_active_root = target.resolve(strict=True).is_relative_to(
                    active_root.resolve(strict=True)
                )
            except (FileNotFoundError, OSError):
                inside_active_root = False
            stale = (
                False
                if inside_active_root
                else engine_mod.is_stale_engine_path(target_text, active_root)
                or (
                    engine_mod.looks_like_missing_legacy_engine_path(str(raw_target))
                    or engine_mod.looks_like_missing_legacy_engine_path(target_text)
                    or clone_named
                )
            )
            if stale:
                state = "warn"
                safe = True
                summary = "stale Main Branch clone-path symlink can be moved to backup"
            else:
                state = "info"
                safe = False
                summary = "third-party or user-authored symlink; inspect manually"
            findings.append(
                {
                    "path": _rel(repo, entry),
                    "target": str(raw_target),
                    "resolved_target": target_text,
                    "state": state,
                    "safe_to_repair": safe,
                    "summary": summary,
                }
            )
    return {
        "state": _max_state([str(item["state"]) for item in findings]),
        "findings": findings,
        "repairable": sum(1 for item in findings if item["safe_to_repair"]),
    }


def _repair_legacy_claude_symlinks(repo: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    repairable = [item for item in findings if item.get("safe_to_repair")]
    if not repairable:
        return {"ok": True, "moved": [], "backup_dir": "", "errors": []}
    backup_dir = repo / ".mb" / "backups" / f"doctor-repair-{_utc_stamp()}" / "claude-links"
    moved: list[dict[str, str]] = []
    errors: list[str] = []
    for item in repairable:
        source = repo / str(item["path"])
        dest = backup_dir / str(item["path"])
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(dest))
            moved.append(
                {
                    "path": str(item["path"]),
                    "target": str(item["target"]),
                    "backup_path": _rel(repo, dest),
                }
            )
        except OSError as exc:
            errors.append(f"{item['path']}: {exc}")
    if moved:
        manifest = backup_dir / "manifest.json"
        manifest.write_text(json.dumps({"moved": moved}, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": not errors,
        "moved": moved,
        "backup_dir": _rel(repo, backup_dir) if moved else "",
        "errors": errors,
    }


def _validation_summary(repo: Path) -> dict[str, Any]:
    try:
        report = validate_mod.run(str(repo), cross_refs=True)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        return {
            "ok": False,
            "state": "error",
            "summary": f"validation failed to run: {exc}",
            "report": {},
        }
    summary = report.get("summary", {})
    errors = int(summary.get("errors", 0) or 0)
    warnings = int(summary.get("warnings", 0) or 0)
    state = "error" if errors else ("warn" if warnings else "ok")
    return {
        "ok": report["ok"],
        "state": state,
        "summary": f"{errors} error(s), {warnings} warning(s)",
        "report": {
            "summary": summary,
            "files": len(report.get("files", [])),
            "legacy_repair": report.get("legacy_repair"),
            "cross_refs": {
                "enabled": report.get("cross_refs", {}).get("enabled", False),
                "warnings": len(report.get("cross_refs", {}).get("warnings", [])),
                "orphan_offers": len(report.get("cross_refs", {}).get("orphan_offers", [])),
            },
        },
    }


def _graph_summary(repo: Path) -> dict[str, Any]:
    try:
        index = graph_mod.build_index(str(repo))
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        return {
            "ok": False,
            "state": "warn",
            "summary": f"graph summary failed to run: {exc}",
            "report": {},
        }
    unresolved = sum(1 for node in index.get("nodes", []) if node.get("type") == "wikilink")
    state = "warn" if unresolved else "ok"
    summary = index.get("summary", {})
    return {
        "ok": unresolved == 0,
        "state": state,
        "summary": (
            f"{summary.get('files', 0)} file(s), {summary.get('edges', 0)} edge(s), "
            f"{unresolved} unresolved wikilink(s)"
        ),
        "report": {"summary": summary, "unresolved_wikilinks": unresolved},
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

    gh_context = connect_mod.github_context(repo)
    integration_status = connect_mod.status_all(repo, github=gh_context)
    checks.append(
        {
            "name": "github-context",
            "ok": bool(gh_context["ok"]),
            "detail": gh_context["summary"],
            "severity": "warn",
            "state": gh_context["state"],
            "repair": gh_context["repair"],
            "repair_command": gh_context["repair_command"],
            "safe_to_share": True,
        }
    )

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
    shadow_summary = wiring.get("shadow_report", {}).get("summary", {})
    active_shadows = int(shadow_summary.get("active_shadows", 0) or 0)
    legacy_globals = int(shadow_summary.get("legacy_globals", 0) or 0)
    checks.append(
        {
            "name": "skill-wiring",
            "ok": wiring_ok,
            "detail": (
                f"mb-start skill linked via {wiring['engine_root']}"
                if wiring_ok
                else (
                    "Claude Code skill links missing or shadowed. Run "
                    "`mb skill repair --repo .`, then `mb skill link --repo .`."
                )
            ),
            "severity": "ok"
            if wiring_ok
            else ("warn" if not (repo / "CLAUDE.md").exists() else "error"),
        }
    )
    if active_shadows or legacy_globals:
        checks.append(
            {
                "name": "skill-shadowing",
                "ok": active_shadows == 0,
                "detail": (
                    f"{active_shadows} active personal skill shadow(s), "
                    f"{legacy_globals} legacy personal skill trap(s). "
                    "Run `mb skill repair --repo .` for details."
                ),
                "severity": "error" if active_shadows else "warn",
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
    checks.append(_legacy_campaigns_check(repo))
    checks.append(connect_mod.doctor_check(repo, status=integration_status))
    onboarding = onboard_mod.onboarding_status(repo)
    onboarding_summary = onboarding["summary"]
    checks.append(
        {
            "name": "onboarding-progress",
            "ok": onboarding_summary["status"] == "ready",
            "detail": (
                "core onboarding complete"
                if onboarding_summary["status"] == "ready"
                else (
                    f"{onboarding_summary['completed_required']}/"
                    f"{onboarding_summary['total_required']} required steps complete; "
                    "run `mb onboard status`."
                )
            ),
            "severity": "warn",
        }
    )

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
        "integrations": integration_status,
        "onboarding": onboarding,
        "update": update,
        "python": sys.version.split()[0],
    }


def repair_plan(
    repo: str | Path = ".",
    *,
    mode: str = "plan",
    applied_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the guided reconciliation plan without writing repo status markers."""
    target = Path(repo).expanduser().resolve()
    doctor_report = run(str(target))
    actions: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []

    update = doctor_report.get("update", {})
    install_checks = [
        {
            "name": check["name"],
            "state": _state_from_check(check),
            "summary": check["detail"],
        }
        for check in doctor_report["checks"]
        if check["name"]
        in {"mainbranch-version", "claude-code", "github-context", "network", "librsvg"}
    ]
    if str(update.get("severity")) in {"required", "recommended"}:
        actions.append(
            _action(
                id="mainbranch-update",
                title="Update Main Branch install",
                state="error" if update.get("severity") == "required" else "warn",
                mode="write",
                command=str(update.get("command") or "mb update"),
                safe_to_apply=False,
                reason="package updates are explicit operator actions outside doctor repair",
            )
        )
    sections.append(
        _section(
            "install",
            "Install And Environment",
            _max_state([str(item["state"]) for item in install_checks]),
            "Main Branch install, runtime tools, GitHub, network, and optional render tooling",
            checks=install_checks,
        )
    )

    migration = migrate_mod.check(target, include_diff=False)
    reference_state = _legacy_reference_state(target)
    legacy_campaigns_check = next(
        (check for check in doctor_report["checks"] if check["name"] == "legacy-campaigns"),
        None,
    )
    layout_checks = [
        {
            "name": check["name"],
            "state": _state_from_check(check),
            "summary": check["detail"],
        }
        for check in doctor_report["checks"]
        if check["name"] in {"repo-layout", "schema-version", "legacy-campaigns"}
    ]
    layout_checks.extend(
        {
            "name": item["path"],
            "state": item["state"],
            "summary": item["summary"],
            "kind": item["kind"],
        }
        for item in reference_state["checks"]
    )
    if migration.get("plan", {}).get("has_changes") or migration.get("pending"):
        actions.append(
            _action(
                id="migration-preview",
                title="Preview layout migration",
                state="warn",
                mode="read",
                command="mb migrate --repo . --check",
                safe_to_apply=True,
                reason="migration preview is read-only and should be reviewed before apply",
            )
        )
        actions.append(
            _action(
                id="migration-apply",
                title="Apply approved layout migration",
                state="warn",
                mode="write",
                command="mb migrate --repo . --apply",
                safe_to_apply=False,
                reason=(
                    "migration moves user-authored files; run doctor repair with "
                    "`--apply --include-migration` only after reviewing the preview"
                ),
                writes=["core/", "reference/core", "reference/offers", ".mb/schema_version"],
            )
        )
    if legacy_campaigns_check and not legacy_campaigns_check["ok"]:
        actions.append(
            _action(
                id="legacy_campaigns_to_pushes",
                title="Preview campaigns -> pushes migration",
                state="warn",
                mode="read",
                command="mb migrate campaigns --plan",
                safe_to_apply=True,
                reason=(
                    "campaigns/ is legacy compatibility; new coordinated work "
                    "writes to pushes/. Preview the move before applying."
                ),
            )
        )
    sections.append(
        _section(
            "repo-shape",
            "Repo Shape And Migration",
            _max_state([str(item["state"]) for item in layout_checks]),
            f"schema {migration.get('current_version')} -> {migration.get('latest_version')}",
            checks=layout_checks,
        )
    )

    missing_gitignore = _missing_gitignore_entries(target)
    gitignore_actions: list[dict[str, Any]] = []
    if missing_gitignore:
        action = _action(
            id="gitignore-local-state",
            title="Protect Main Branch local state in .gitignore",
            state="warn",
            mode="write",
            command="mb doctor repair --apply",
            safe_to_apply=True,
            reason="these entries are local operational state and should not be committed",
            writes=[".gitignore"],
        )
        actions.append(action)
        gitignore_actions.append(action)
    sections.append(
        _section(
            "gitignore",
            "Local State Gitignore",
            "warn" if missing_gitignore else "ok",
            (
                f"{len(missing_gitignore)} missing local-state entrie(s)"
                if missing_gitignore
                else "Main Branch local state is ignored"
            ),
            checks=[
                {
                    "name": entry,
                    "state": "warn" if entry in missing_gitignore else "ok",
                    "summary": "missing" if entry in missing_gitignore else "covered",
                }
                for entry in LOCAL_GITIGNORE_ENTRIES
            ],
            actions=gitignore_actions,
        )
    )

    wiring = link_status(target)
    shadow_report = wiring.get("shadow_report", {})
    legacy_links = _legacy_claude_symlinks(target)
    wiring_checks = [
        {
            "name": "project-local-skills",
            "state": "ok" if wiring.get("ok") else "error",
            "summary": (
                "Claude Code can discover mb-start"
                if wiring.get("ok")
                else "project-local skill wiring is missing or shadowed"
            ),
        },
        {
            "name": "personal-skill-shadowing",
            "state": "ok"
            if not int(shadow_report.get("summary", {}).get("findings", 0) or 0)
            else (
                "warn"
                if int(shadow_report.get("summary", {}).get("repairable", 0) or 0)
                else "error"
            ),
            "summary": (
                f"{shadow_report.get('summary', {}).get('findings', 0)} finding(s), "
                f"{shadow_report.get('summary', {}).get('repairable', 0)} repairable"
            ),
        },
        {
            "name": "legacy-claude-reference-links",
            "state": legacy_links["state"],
            "summary": (
                f"{len(legacy_links['findings'])} symlink finding(s), "
                f"{legacy_links['repairable']} repairable"
            ),
        },
    ]
    if not wiring.get("ok"):
        actions.append(
            _action(
                id="skill-link",
                title="Refresh project-local Claude Code skill wiring",
                state="error",
                mode="write",
                command="mb skill link --repo . --json",
                safe_to_apply=True,
                reason="relinks bundled skills and repairs Main Branch local gitignore entries",
                writes=[
                    ".claude/settings.local.json",
                    ".claude/skills/",
                    ".gitignore",
                ],
            )
        )
    if int(shadow_report.get("summary", {}).get("repairable", 0) or 0):
        actions.append(
            _action(
                id="skill-shadow-repair",
                title="Move stale personal Main Branch skill symlinks to backup",
                state="warn",
                mode="write",
                command="mb skill repair --repo . --apply",
                safe_to_apply=True,
                reason="only stale or broken Main Branch personal symlinks are moved",
                writes=[str(shadow_report.get("personal_skills_dir") or "~/.claude/skills")],
            )
        )
    if int(legacy_links["repairable"]):
        actions.append(
            _action(
                id="legacy-claude-link-repair",
                title="Move old clone-path lens/reference symlinks to backup",
                state="warn",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason="only stale Main Branch clone-path symlinks are moved; user files stay put",
                writes=[".claude/lenses/", ".claude/reference/", ".mb/backups/"],
            )
        )
    sections.append(
        _section(
            "claude-wiring",
            "Claude Code Wiring",
            _max_state([str(item["state"]) for item in wiring_checks]),
            "Project-local skills, personal shadowing, and old clone-path symlinks",
            checks=wiring_checks,
        )
    )

    local_state = _local_state_summary(target)
    sections.append(
        _section(
            "mb-state",
            ".mb State",
            local_state["state"],
            local_state["summary"],
            checks=[
                {
                    "name": item["path"],
                    "state": "info" if item["exists"] else "ok",
                    "summary": "local operational state" if item["exists"] else "absent",
                }
                for item in local_state["local"]
            ]
            + [
                {
                    "name": item["path"],
                    "state": "info" if item["exists"] else "ok",
                    "summary": "durable repo marker" if item["exists"] else "absent",
                }
                for item in local_state["durable"]
            ],
        )
    )

    validation = _validation_summary(target)
    if validation["state"] != "ok":
        actions.append(
            _action(
                id="validate-frontmatter",
                title="Repair validation and frontmatter debt",
                state=validation["state"],
                mode="manual",
                command="mb validate --json",
                safe_to_apply=False,
                reason="validation failures are user-authored content repairs",
            )
        )
    sections.append(
        _section(
            "validation",
            "Validation And Cross-Refs",
            validation["state"],
            validation["summary"],
            checks=[{"name": "mb validate --cross-refs", **validation}],
        )
    )

    graph = _graph_summary(target)
    if graph["state"] != "ok":
        actions.append(
            _action(
                id="graph-links",
                title="Review graph and wikilink health",
                state=graph["state"],
                mode="manual",
                command="mb graph --json",
                safe_to_apply=False,
                reason="link meaning belongs to the operator or agent reviewing content",
            )
        )
    sections.append(
        _section(
            "graph",
            "Graph And Link Health",
            graph["state"],
            graph["summary"],
            checks=[{"name": "mb graph --json", **graph}],
        )
    )

    git = _git_summary(target)
    sections.append(
        _section(
            "git",
            "Git Review State",
            git["state"],
            git["summary"],
            checks=[
                {
                    "name": "branch",
                    "state": git["state"],
                    "summary": git["branch"] or "(none)",
                },
                {
                    "name": "dirty-state",
                    "state": git["state"],
                    "summary": f"{len(git['changed_files'])} changed file(s)",
                },
            ],
        )
    )

    states = [str(section["state"]) for section in sections]
    summary = {
        "ok": sum(1 for state in states if state == "ok"),
        "info": sum(1 for state in states if state == "info"),
        "warn": sum(1 for state in states if state == "warn"),
        "error": sum(1 for state in states if state == "error"),
        "actions": len(actions),
        "write_actions": sum(1 for action in actions if action["mode"] == "write"),
        "safe_apply_actions": sum(
            1 for action in actions if action["mode"] == "write" and action["safe_to_apply"]
        ),
    }
    return {
        "schema": REPAIR_SCHEMA,
        "schema_version": REPAIR_SCHEMA_VERSION,
        "ok": summary["error"] == 0,
        "mode": mode,
        "read_only": mode == "plan",
        "repo": str(target),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": summary,
        "sections": sections,
        "actions": actions,
        "applied_actions": applied_actions or [],
        "post_apply": {
            "structural_verification": "mb doctor repair --plan --json",
            "validation_frontmatter_debt": "mb validate --cross-refs",
            "runtime_smoke_required": (
                "Static repair does not prove Claude Code runtime behavior. "
                "From the business repo, run `claude`, confirm `/mb-start` is discoverable, "
                "and verify it reads repo context without writing into the engine repo."
            ),
            "git_review": [
                "git status --short",
                "git diff",
                "git add <reviewed repair files>",
                "git commit -m '[fix] Reconcile Main Branch repo wiring'",
            ],
        },
        "raw": {
            "migration": migration,
            "legacy_reference": reference_state,
            "legacy_claude_links": legacy_links,
            "validation": validation.get("report", {}),
            "graph": graph.get("report", {}),
            "git": git,
        },
    }


def repair_apply(repo: str | Path = ".", *, include_migration: bool = False) -> dict[str, Any]:
    """Apply safe doctor repairs and return a fresh reconciliation report."""
    target = Path(repo).expanduser().resolve()
    before = repair_plan(target)
    applied: list[dict[str, Any]] = []

    missing_gitignore = _missing_gitignore_entries(target)
    if missing_gitignore:
        changed = _append_unique_lines(target / ".gitignore", missing_gitignore)
        applied.append(
            _action(
                id="gitignore-local-state",
                title="Protected Main Branch local state in .gitignore",
                state="ok",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason="added missing local-state gitignore entries",
                writes=[".gitignore"],
                applied=changed,
                result={"added": missing_gitignore},
            )
        )

    shadow = engine_mod.inspect_personal_skill_conflicts(target, apply=True)
    if int(shadow.get("summary", {}).get("repaired", 0) or 0):
        applied.append(
            _action(
                id="skill-shadow-repair",
                title="Moved stale personal Main Branch skill symlinks to backup",
                state="ok" if shadow["ok"] else "error",
                mode="write",
                command="mb skill repair --repo . --apply",
                safe_to_apply=True,
                reason="repaired stale or broken Main Branch personal symlinks",
                writes=[str(shadow.get("personal_skills_dir") or "~/.claude/skills")],
                applied=True,
                result=shadow,
            )
        )

    if not link_status(target).get("ok"):
        linked = engine_mod.link_skills(target)
        applied.append(
            _action(
                id="skill-link",
                title="Refreshed project-local Claude Code skill wiring",
                state="ok" if linked["ok"] else "error",
                mode="write",
                command="mb skill link --repo . --json",
                safe_to_apply=True,
                reason="refreshed Main Branch skill links and local settings",
                writes=[".claude/settings.local.json", ".claude/skills/", ".gitignore"],
                applied=True,
                result=linked,
            )
        )

    legacy_links = _legacy_claude_symlinks(target)
    repaired_links = _repair_legacy_claude_symlinks(target, legacy_links["findings"])
    if repaired_links["moved"] or repaired_links["errors"]:
        _append_unique_lines(target / ".gitignore", [".mb/backups/"])
        applied.append(
            _action(
                id="legacy-claude-link-repair",
                title="Moved old clone-path lens/reference symlinks to backup",
                state="ok" if repaired_links["ok"] else "error",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason="moved stale symlink entries, not user-authored files",
                writes=[".claude/lenses/", ".claude/reference/", ".mb/backups/"],
                applied=bool(repaired_links["moved"]),
                result=repaired_links,
            )
        )

    if include_migration:
        migrated = migrate_mod.apply(target)
        applied.append(
            _action(
                id="migration-apply",
                title="Applied approved layout migration",
                state="ok" if migrated["ok"] else "error",
                mode="write",
                command="mb migrate --repo . --apply",
                safe_to_apply=False,
                reason="operator explicitly opted into migration apply",
                writes=["core/", "reference/core", "reference/offers", ".mb/schema_version"],
                applied=bool(migrated.get("applied")),
                result=migrated,
            )
        )

    after = repair_plan(target, mode="apply", applied_actions=applied)
    after["before_summary"] = before["summary"]
    return after


def render_repair(report: dict[str, Any]) -> None:
    """Print the doctor repair plan/apply report for humans."""
    from rich.console import Console

    console = Console()
    mode = "read-only plan" if report["read_only"] else "apply summary"
    console.print(f"\n[bold]mb doctor repair[/bold]  {mode}")
    console.print(f"repo: {report['repo']}\n")
    for section in report["sections"]:
        state = str(section["state"])
        mark = {
            "ok": "[green]ok[/green]",
            "info": "[blue]info[/blue]",
            "warn": "[yellow]warn[/yellow]",
            "error": "[red]error[/red]",
        }.get(state, "[red]error[/red]")
        console.print(f"  {mark}  [bold]{section['title']}[/bold] - {section['summary']}")
        for check in section.get("checks", [])[:6]:
            check_state = str(check.get("state", "ok"))
            if check_state == "ok":
                prefix = "ok"
            elif check_state == "info":
                prefix = "info"
            elif check_state == "warn":
                prefix = "warn"
            else:
                prefix = "error"
            console.print(f"       {prefix:<5} {check['name']}: {check['summary']}")
    if report.get("applied_actions"):
        console.print("\n[bold]Applied safe repairs[/bold]")
        for action in report["applied_actions"]:
            console.print(f"  - {action['title']}: {action['command']}")
    if report["actions"]:
        console.print("\n[bold]Repair plan[/bold]")
        for action in report["actions"]:
            mutability = "read-only" if action["mode"] == "read" else action["mode"]
            safe = "safe apply" if action["safe_to_apply"] else "manual approval"
            console.print(f"  - [{mutability}; {safe}] {action['title']}")
            console.print(f"    command: {action['command']}")
            console.print(f"    why: {action['reason']}")
    else:
        console.print("\n[green]No repair actions needed.[/green]")
    console.print("\n[bold]After apply[/bold]")
    console.print(f"  structural: {report['post_apply']['structural_verification']}")
    console.print(f"  validation: {report['post_apply']['validation_frontmatter_debt']}")
    console.print(f"  runtime: {report['post_apply']['runtime_smoke_required']}")
    console.print("  git:")
    for command in report["post_apply"]["git_review"]:
        console.print(f"    {command}")


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
