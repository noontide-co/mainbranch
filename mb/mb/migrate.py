"""Schema-versioned repo migrations for ``mb migrate``."""

from __future__ import annotations

import difflib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from mb import migrations
from mb.migrations.base import MigrationInfo, MigrationPlan, PlannedChange

ENVELOPE_SCHEMA = "mb.migrate"
ENVELOPE_SCHEMA_VERSION = 1
LATEST_SCHEMA_VERSION = "0.2"
SCHEMA_MARKER = ".mb/schema_version"


def _marker_path(repo: Path) -> Path:
    return repo / SCHEMA_MARKER


def read_schema_version(repo: str | Path) -> str:
    """Read or infer the business-repo schema version."""
    target = Path(repo).resolve()
    marker = _marker_path(target)
    if marker.exists():
        value = marker.read_text(encoding="utf-8").strip()
        return value or "unknown"
    if (target / "reference" / "core").exists() and not (
        target / "reference" / "core"
    ).is_symlink():
        return "0.1"
    if (target / "reference" / "offers").exists() and not (
        target / "reference" / "offers"
    ).is_symlink():
        return "0.1"
    if (target / "core").is_dir():
        return LATEST_SCHEMA_VERSION
    return "unknown"


def _migration_dict(info: MigrationInfo) -> dict[str, str]:
    return {
        "id": info.id,
        "name": info.name,
        "from_version": info.from_version,
        "to_version": info.to_version,
        "description": info.description,
    }


def pending_migrations(repo: str | Path) -> list[tuple[MigrationInfo, Any]]:
    """Return registered migrations pending for ``repo``."""
    version = read_schema_version(repo)
    pending: list[tuple[MigrationInfo, Any]] = []
    for info, module in migrations.registered():
        registered_module = migrations.VERSION_MAP.get(version)
        if version == info.from_version and registered_module == module.__name__:
            pending.append((info, module))
            version = info.to_version
    return pending


def _read_text_for_diff(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def _diff_for_change(repo: Path, change: PlannedChange) -> list[str]:
    if change.kind == "move_file":
        source = repo / change.source
        old_lines = _read_text_for_diff(source)
        new_lines = old_lines
        delete_diff = list(
            difflib.unified_diff(
                old_lines,
                [],
                fromfile=f"a/{change.source}",
                tofile="/dev/null",
                lineterm="",
            )
        )
        add_diff = list(
            difflib.unified_diff(
                [],
                new_lines,
                fromfile="/dev/null",
                tofile=f"b/{change.target}",
                lineterm="",
            )
        )
        return delete_diff + add_diff
    if change.kind == "delete_file":
        old_lines = _read_text_for_diff(repo / change.path)
        return list(
            difflib.unified_diff(
                old_lines,
                [],
                fromfile=f"a/{change.path}",
                tofile="/dev/null",
                lineterm="",
            )
        )
    if change.kind == "write_file":
        old_lines = _read_text_for_diff(repo / change.path)
        new_lines = change.content.splitlines(keepends=True)
        return list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{change.path}" if old_lines else "/dev/null",
                tofile=f"b/{change.path}",
                lineterm="",
            )
        )
    if change.kind == "symlink":
        new_lines = [f"symlink -> {change.target}\n"]
        return list(
            difflib.unified_diff(
                [],
                new_lines,
                fromfile="/dev/null",
                tofile=f"b/{change.path}",
                lineterm="",
            )
        )
    return []


def _unified_diff(repo: Path, plans: list[MigrationPlan], include_marker: bool) -> str:
    lines: list[str] = []
    for plan in plans:
        for change in plan.changes:
            lines.extend(_diff_for_change(repo, change))
    if include_marker:
        marker_change = PlannedChange(
            kind="write_file",
            path=SCHEMA_MARKER,
            content=LATEST_SCHEMA_VERSION + "\n",
        )
        lines.extend(_diff_for_change(repo, marker_change))
    return "\n".join(lines) + ("\n" if lines else "")


def _plan_dict(plan: MigrationPlan) -> dict[str, Any]:
    return {
        "migration": _migration_dict(plan.migration),
        "has_changes": plan.has_changes,
        "changes": [
            {
                "kind": change.kind,
                "path": change.path,
                "source": change.source,
                "target": change.target,
            }
            for change in plan.changes
        ],
        "errors": plan.errors,
    }


def _base_envelope(repo: Path, action: str) -> dict[str, Any]:
    pending = pending_migrations(repo)
    return {
        "schema": ENVELOPE_SCHEMA,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "ok": True,
        "action": action,
        "repo": str(repo),
        "current_version": read_schema_version(repo),
        "latest_version": LATEST_SCHEMA_VERSION,
        "pending": [_migration_dict(info) for info, _module in pending],
        "plan": None,
        "applied": [],
        "backup": None,
        "errors": [],
    }


def status(repo: str | Path = ".") -> dict[str, Any]:
    """Return current schema version and pending migrations."""
    target = Path(repo).resolve()
    return _base_envelope(target, "status")


def check(repo: str | Path = ".") -> dict[str, Any]:
    """Plan pending migrations without writing files."""
    target = Path(repo).resolve()
    result = _base_envelope(target, "check")
    pending = pending_migrations(target)
    plans = [migrations.plan_for(info, module, target) for info, module in pending]
    errors = [error for plan in plans for error in plan.errors]
    result["ok"] = not errors
    result["plan"] = {
        "has_changes": any(plan.has_changes for plan in plans),
        "migrations": [_plan_dict(plan) for plan in plans],
        "diff": _unified_diff(target, plans, include_marker=bool(pending)),
        "errors": errors,
    }
    result["errors"] = errors
    return result


def _backup_path(repo: Path, migration_ids: list[str]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "-".join(migration_ids) if migration_ids else "noop"
    return repo / ".mb" / "backups" / f"{stamp}-{suffix}"


def _backup_existing_paths(repo: Path, backup_dir: Path, plans: list[MigrationPlan]) -> list[str]:
    copied: list[str] = []
    paths: set[str] = {SCHEMA_MARKER}
    for plan in plans:
        for change in plan.changes:
            if change.kind in {"move_file", "delete_file"} and change.source:
                paths.add(change.source)
            elif change.kind in {"write_file", "symlink"}:
                paths.add(change.path)

    for rel in sorted(paths):
        source = repo / rel
        if not source.exists() and not source.is_symlink():
            continue
        dest = backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            dest.write_text(f"symlink -> {source.readlink().as_posix()}\n", encoding="utf-8")
        elif source.is_dir():
            shutil.copytree(source, dest, symlinks=True, dirs_exist_ok=True)
        else:
            shutil.copy2(source, dest)
        copied.append(rel)
    return copied


def _apply_change(repo: Path, change: PlannedChange) -> None:
    path = repo / change.path
    if change.kind == "mkdir":
        path.mkdir(parents=True, exist_ok=True)
        return
    if change.kind == "move_file":
        source = repo / change.source
        target = repo / change.target
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and source.exists() and source.read_bytes() == target.read_bytes():
            source.unlink()
            return
        source.rename(target)
        return
    if change.kind == "delete_file":
        if path.exists():
            path.unlink()
        return
    if change.kind == "write_file":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(change.content, encoding="utf-8")
        return
    if change.kind == "remove_empty_dir":
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
        return
    if change.kind == "symlink":
        if path.is_symlink() and path.readlink().as_posix() == change.target:
            return
        path.symlink_to(change.target, target_is_directory=True)


def apply(repo: str | Path = ".") -> dict[str, Any]:
    """Apply pending migrations after creating a repo-local backup."""
    target = Path(repo).resolve()
    result = check(target)
    result["action"] = "apply"
    plans = [
        migrations.plan_for(info, module, target) for info, module in pending_migrations(target)
    ]
    if result["errors"]:
        result["ok"] = False
        return result
    if not plans:
        result["ok"] = True
        return result

    backup_dir = _backup_path(target, [plan.migration.id for plan in plans])
    backup_dir.mkdir(parents=True, exist_ok=False)
    copied = _backup_existing_paths(target, backup_dir, plans)
    (backup_dir / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "copied": copied}, indent=2) + "\n",
        encoding="utf-8",
    )

    for plan in plans:
        for change in plan.changes:
            _apply_change(target, change)

    marker = _marker_path(target)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(LATEST_SCHEMA_VERSION + "\n", encoding="utf-8")

    result["ok"] = True
    result["current_version"] = LATEST_SCHEMA_VERSION
    result["pending"] = []
    result["applied"] = [_migration_dict(plan.migration) for plan in plans]
    result["backup"] = {"path": str(backup_dir), "copied": copied}
    return result


def render_status(result: dict[str, Any]) -> None:
    print(f"schema version: {result['current_version']}")
    pending = result.get("pending", [])
    if pending:
        print("pending migrations:")
        for item in pending:
            print(f"  {item['id']} {item['name']} ({item['from_version']} -> {item['to_version']})")
    else:
        print("pending migrations: none")


def render_check(result: dict[str, Any]) -> None:
    plan = result.get("plan") or {}
    errors = result.get("errors", [])
    if errors:
        for error in errors:
            print(f"error: {error}")
        return
    diff = str(plan.get("diff", ""))
    if diff:
        print(diff, end="")
    else:
        print("no migrations pending")


def render_apply(result: dict[str, Any]) -> None:
    if result.get("errors"):
        for error in result["errors"]:
            print(f"error: {error}")
        return
    applied = result.get("applied", [])
    if not applied:
        print("no migrations pending")
        return
    print(f"applied {len(applied)} migration(s)")
    backup = result.get("backup") or {}
    if backup.get("path"):
        print(f"backup: {backup['path']}")
    print(f"schema version: {result['current_version']}")
