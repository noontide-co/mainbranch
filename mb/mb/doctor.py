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

import yaml

from mb import checkpoint as checkpoint_mod
from mb import codex as codex_mod
from mb import connect as connect_mod
from mb import engine as engine_mod
from mb import graph as graph_mod
from mb import migrate as migrate_mod
from mb import migration_lint
from mb import onboard as onboard_mod
from mb import related_links as related_links_mod
from mb import topology as topology_mod
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
    ".mb/connect.yaml",
    ".mb/onboarding.json",
    ".mb/last-status-seen.json",
    ".mb/issue-drafts/",
    ".vip/local.yaml",
)
LOCAL_STATE_PATHS = (
    ".mb/backups",
    ".mb/connect.yaml",
    ".mb/onboarding.json",
    ".mb/last-status-seen.json",
    ".mb/issue-drafts",
    ".vip/local.yaml",
)
DURABLE_MB_PATHS = (".mb/schema_version",)
LEGACY_VIP_LOCAL_STATE_PATHS = (".vip/local.yaml",)
LEGACY_VIP_AUDIT_PATHS = (".vip/local.yaml", ".vip/config.yaml")
LEGACY_CLAUDE_LINK_DIRS = (".claude/lenses", ".claude/reference")
REFERENCE_COMPAT_LINKS = {
    "reference/core": "../core",
    "reference/offers": "../core/offers",
}
STATE_ORDER = {"ok": 0, "info": 1, "warn": 2, "error": 3}
AUDIENCE_VALUES = frozenset({"mechanical", "operator_decision", "informational"})


def _derive_audience(mode: str, safe_to_apply: bool) -> str:
    """Classify a repair action for operator-facing routing.

    See ``decisions/2026-05-11-operator-facing-gitops-and-migration-planning.md``
    for the contract. ``audience`` is a routing signal; ``safe_to_apply`` is the
    safety gate and stays authoritative.
    """
    if mode == "read":
        return "informational"
    if mode == "manual":
        return "operator_decision"
    if safe_to_apply:
        return "mechanical"
    return "operator_decision"


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
    audience: str | None = None,
    operator_summary: str = "",
) -> dict[str, Any]:
    resolved_audience = (
        audience if audience in AUDIENCE_VALUES else _derive_audience(mode, safe_to_apply)
    )
    return {
        "id": id,
        "title": title,
        "state": state,
        "mode": mode,
        "command": command,
        "safe_to_apply": safe_to_apply,
        "reason": reason,
        "audience": resolved_audience,
        "operator_summary": operator_summary or reason or title,
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

    def covered(entry: str) -> bool:
        if entry in entries:
            return True
        return any(parent.endswith("/") and entry.startswith(parent) for parent in entries)

    return [entry for entry in LOCAL_GITIGNORE_ENTRIES if not covered(entry)]


def _tracked_local_state_paths(repo: Path) -> list[str]:
    tracked: list[str] = []
    for rel in LOCAL_STATE_PATHS:
        result = _run_git(repo, ["ls-files", "--error-unmatch", rel])
        if result["ok"]:
            tracked.append(rel)
    return tracked


def _untrack_local_state_path(repo: Path, rel: str) -> dict[str, Any]:
    path = repo / rel
    result = _run_git(repo, ["rm", "--cached", "--", rel])
    return {
        "path": rel,
        "ok": bool(result["ok"]),
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "exists_on_disk": path.exists() or path.is_symlink(),
    }


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
        if item["exists"] and item["path"] in _missing_gitignore_entries(repo)
    ]
    tracked = _tracked_local_state_paths(repo)
    return {
        "state": "warn" if missing_gitignore or tracked else "ok",
        "summary": (
            f"{len(missing_gitignore)} local state path(s) need gitignore coverage"
            if missing_gitignore
            else f"{len(tracked)} local state path(s) are still tracked"
            if tracked
            else "local operational state is separated from durable markers"
        ),
        "local": local,
        "durable": durable,
        "missing_gitignore": missing_gitignore,
        "tracked": tracked,
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


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_markdown_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}
    try:
        parsed = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _flatten_yaml_keys(data: dict[str, Any], *, prefix: str = "") -> list[str]:
    keys: list[str] = []
    for key, value in data.items():
        key_text = str(key)
        path = f"{prefix}.{key_text}" if prefix else key_text
        if isinstance(value, dict) and value:
            keys.extend(_flatten_yaml_keys(value, prefix=path))
        else:
            keys.append(path)
    return keys


def _legacy_vip_key_classification(key: str) -> dict[str, str]:
    parts = key.split(".")
    root = parts[0] if parts else key

    if key == "current_offer":
        return {
            "family": "current_offer",
            "classification": "local-session-state",
            "destination": (
                "Use an explicit per-run offer choice, status/start routing, or a future "
                "Main Branch session-state contract; do not treat `.vip/local.yaml` as canonical."
            ),
            "action": "manual_review",
        }
    if root in {"default_repo", "recent_repos", "user", "media", "last_seen_version", "vip_path"}:
        return {
            "family": f"{root}.*" if len(parts) > 1 else root,
            "classification": "machine-local-preference",
            "destination": (
                "Keep only in machine-local runtime config if still useful; never move into "
                "tracked business files."
            ),
            "action": "keep_local_or_delete",
        }
    if root == "session":
        return {
            "family": "session.*",
            "classification": "machine-local-session-state",
            "destination": "Keep as runtime-local preference/session state if retained.",
            "action": "keep_local_or_delete",
        }
    if root in {"business_type", "business_name", "offer_structure", "skool_url"} or root.endswith(
        "_url"
    ):
        return {
            "family": root,
            "classification": "durable-business-truth",
            "destination": (
                "Review manually and move still-current, non-private facts into `core/`, "
                "`core/operations/`, or onboarding state."
            ),
            "action": "manual_move_if_current",
        }
    if root == "tools":
        return {
            "family": "tools.*",
            "classification": "stale-runtime-snapshot",
            "destination": "Prefer current `mb connect`, `mb status`, and runtime facts.",
            "action": "delete_after_review",
        }
    if root == "mcps":
        return {
            "family": "mcps.*",
            "classification": "provider-readiness-hint",
            "destination": (
                "Move only durable, non-secret requirements to generated `CLAUDE.md`, "
                "`core/operations/`, or provider docs; keep credentials local."
            ),
            "action": "manual_review",
        }
    if root == "infrastructure":
        return {
            "family": "infrastructure.*",
            "classification": "provider-or-infra-hint",
            "destination": (
                "Classify manually. Non-secret provider identifiers may belong in operation "
                "or provider notes; secrets and account-private details stay local."
            ),
            "action": "manual_review",
        }
    if root in {"content", "skills"}:
        return {
            "family": f"{root}.*",
            "classification": "legacy-skill-default",
            "destination": "Use explicit skill inputs or documented workflow defaults, not `.vip`.",
            "action": "manual_review",
        }
    if root in {"clients", "client_repos", "child_repos", "repos"}:
        return {
            "family": f"{root}.*",
            "classification": "repo-topology-hint",
            "destination": (
                "Review manually before moving to topology docs, graph links, or provider-safe "
                "notes; sanitize client/private paths."
            ),
            "action": "manual_review",
        }
    if root == "reference_structure":
        return {
            "family": "reference_structure.*",
            "classification": "stale-legacy-layout",
            "destination": (
                "Use `mb doctor`, `mb migrate --check`, and current `core/` layout facts."
            ),
            "action": "delete_after_review",
        }
    if root in {"paths", "path_config"}:
        return {
            "family": f"{root}.*",
            "classification": "legacy-compatibility-fallback",
            "destination": "Prefer current repo layout and `mb` path resolution.",
            "action": "manual_review",
        }
    return {
        "family": f"{root}.*" if len(parts) > 1 else root,
        "classification": "manual-review",
        "destination": (
            "Inspect manually. Do not move raw values into durable files until privacy and "
            "current relevance are clear."
        ),
        "action": "manual_review",
    }


def _legacy_vip_audit_state(repo: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for rel in LEGACY_VIP_AUDIT_PATHS:
        path = repo / rel
        if not path.exists() and not path.is_symlink():
            checks.append(
                {
                    "name": rel,
                    "state": "ok",
                    "summary": "absent",
                    "kind": "absent",
                    "entries": [],
                    "deletion": {
                        "safe": False,
                        "reason": "file is absent",
                    },
                }
            )
            continue
        if path.is_symlink():
            checks.append(
                {
                    "name": rel,
                    "state": "warn",
                    "summary": "legacy `.vip` YAML is a symlink; manual review required",
                    "kind": "legacy-vip-yaml",
                    "entries": [],
                    "deletion": {
                        "safe": False,
                        "reason": "symlink target may be machine-local or private",
                    },
                }
            )
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            checks.append(
                {
                    "name": rel,
                    "state": "warn",
                    "summary": "legacy `.vip` YAML exists but could not be parsed",
                    "kind": "legacy-vip-yaml",
                    "parse_error": type(exc).__name__,
                    "entries": [],
                    "deletion": {
                        "safe": False,
                        "reason": "parse before deleting or migrating",
                    },
                }
            )
            continue
        if not isinstance(raw, dict):
            checks.append(
                {
                    "name": rel,
                    "state": "warn",
                    "summary": "legacy `.vip` YAML is not a mapping; manual review required",
                    "kind": "legacy-vip-yaml",
                    "entries": [],
                    "deletion": {
                        "safe": False,
                        "reason": "unexpected YAML shape",
                    },
                }
            )
            continue

        entries = [
            {
                "key": key,
                **_legacy_vip_key_classification(key),
                "value_included": False,
            }
            for key in sorted(_flatten_yaml_keys(raw))
        ]
        actions = {str(entry["action"]) for entry in entries}
        manual_count = sum(1 for entry in entries if str(entry["action"]).startswith("manual"))
        local_count = sum(
            1 for entry in entries if str(entry["classification"]).startswith("machine-local")
        )
        stale_count = sum(1 for entry in entries if entry["action"] == "delete_after_review")
        safe_to_delete = bool(entries) and not any(
            action in actions for action in {"manual_review", "manual_move_if_current"}
        )
        if not entries:
            deletion = {
                "safe": True,
                "reason": "file has no keys; delete after confirming no runtime still expects it",
            }
        elif safe_to_delete:
            deletion = {
                "safe": True,
                "reason": (
                    "only local/session/stale fallback keys were found; delete after reviewing "
                    "that no active runtime depends on them"
                ),
            }
        else:
            deletion = {
                "safe": False,
                "reason": (
                    "manual-review or durable-business keys remain; classify and move only "
                    "still-current, non-private facts first"
                ),
            }
        checks.append(
            {
                "name": rel,
                "state": "warn",
                "summary": (
                    f"{len(entries)} legacy key(s): {manual_count} manual review, "
                    f"{local_count} local/session, {stale_count} stale/delete"
                ),
                "kind": "legacy-vip-yaml",
                "entries": entries,
                "deletion": deletion,
            }
        )
    return {
        "state": _max_state([str(item["state"]) for item in checks]),
        "summary": (
            "legacy `.vip` config/state needs review"
            if any(item["state"] != "ok" for item in checks)
            else "no legacy `.vip` config/state files found"
        ),
        "checks": checks,
    }


def _offer_topology_state(repo: Path) -> dict[str, Any]:
    """Return migration guidance for active-offer state and multi-offer drift."""
    checks: list[dict[str, Any]] = []
    offer_records: list[dict[str, Any]] = []
    active_offers: list[str] = []

    for rel in LEGACY_VIP_LOCAL_STATE_PATHS:
        path = repo / rel
        if not path.exists() and not path.is_symlink():
            checks.append(
                {
                    "name": rel,
                    "state": "ok",
                    "summary": "absent",
                    "kind": "absent",
                }
            )
            continue
        data = _read_yaml_mapping(path)
        current_offer = str(data.get("current_offer") or "").strip()
        current_offer_present = bool(current_offer and current_offer != "null")
        if current_offer_present:
            active_offers.append(current_offer)
        checks.append(
            {
                "name": rel,
                "state": "warn",
                "summary": (
                    "legacy repo-local session offer state; read as fallback, "
                    "but do not let skills write it silently"
                ),
                "kind": "legacy-vip-local-state",
                "current_offer_present": current_offer_present,
                "value_included": False,
            }
        )

    offers_dir = repo / "core" / "offers"
    if offers_dir.is_dir():
        for offer_file in sorted(offers_dir.glob("*/offer.md")):
            folder_slug = offer_file.parent.name
            meta = _read_markdown_frontmatter(offer_file)
            declared_slug = str(meta.get("slug") or "").strip()
            record = {
                "path": _rel(repo, offer_file),
                "folder_slug": folder_slug,
                "declared_slug": declared_slug,
                "status": str(meta.get("status") or "").strip(),
            }
            offer_records.append(record)
            if declared_slug and declared_slug != folder_slug:
                checks.append(
                    {
                        "name": _rel(repo, offer_file),
                        "state": "warn",
                        "summary": (
                            f"folder slug `{folder_slug}` differs from frontmatter "
                            f"slug `{declared_slug}`; review before renaming or routing"
                        ),
                        "kind": "offer-slug-drift",
                        **record,
                    }
                )

    existing_folders = {str(record["folder_slug"]) for record in offer_records}
    for active_offer in active_offers:
        if active_offer not in existing_folders:
            checks.append(
                {
                    "name": "active-offer-target",
                    "state": "warn",
                    "summary": (
                        "legacy active-offer state has no matching per-offer file "
                        "under core/offers/"
                    ),
                    "kind": "missing-active-offer",
                    "value_included": False,
                }
            )

    brand_offer = repo / "core" / "offer.md"
    brand_meta = _read_markdown_frontmatter(brand_offer) if brand_offer.is_file() else {}
    brand_slug = str(brand_meta.get("slug") or "").strip()
    if active_offers and len(offer_records) > 1 and brand_offer.is_file():
        checks.append(
            {
                "name": "multi-offer-context",
                "state": "warn",
                "summary": (
                    f"legacy active offer `{active_offers[0]}` exists alongside "
                    f"brand-level core/offer.md and {len(offer_records)} per-offer "
                    "files; confirm brand-level vs offer-specific scope before writing"
                ),
                "kind": "multi-offer-review",
                "current_offer_present": True,
                "value_included": False,
                "brand_offer": "core/offer.md",
                "offers": [record["path"] for record in offer_records],
            }
        )
    if brand_slug and brand_slug in existing_folders:
        checks.append(
            {
                "name": "core/offer.md",
                "state": "warn",
                "summary": (
                    f"brand-level core/offer.md declares slug `{brand_slug}`, which "
                    "also exists as a per-offer folder; review split truth"
                ),
                "kind": "brand-offer-slug-overlap",
                "brand_slug": brand_slug,
            }
        )

    if not checks:
        checks.append(
            {
                "name": "core/offers",
                "state": "ok",
                "summary": "no multi-offer topology guidance needed",
                "kind": "absent",
            }
        )

    return {
        "state": _max_state([str(item["state"]) for item in checks]),
        "checks": checks,
        "offers": offer_records,
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


def _migration_drift_from_checks(
    checks: list[dict[str, Any]],
    repo: Path,
) -> dict[str, Any] | None:
    check = next((item for item in checks if item.get("name") == "migration-drift"), None)
    if check is None:
        return None
    findings = check.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    summary = check.get("summary")
    if not isinstance(summary, dict):
        summary = {
            "warnings": len(findings),
            "categories": sorted({str(item.get("category")) for item in findings}),
        }
    return {
        "ok": not findings,
        "repo": str(repo),
        "findings": findings,
        "summary": summary,
    }


def _topology_drift_state(repo: Path) -> dict[str, Any]:
    """Surface repo topology drift evidence for ``mb doctor repair --plan``.

    Reads the topology view via :func:`mb.topology.collect` and maps its
    findings into the doctor section vocabulary (``ok``/``info``/``warn``/
    ``error``). Preview-only: this helper never renames, deletes, or rewrites
    topology files or descriptors.
    """
    payload = topology_mod.collect(str(repo))
    findings = payload.get("findings") or []
    summary = payload.get("summary") or {}

    severity_to_state = {"info": "info", "warn": "warn", "error": "error"}
    checks: list[dict[str, Any]] = []
    for finding in findings:
        severity = str(finding.get("severity") or "info")
        checks.append(
            {
                "name": str(finding.get("code") or ""),
                "state": severity_to_state.get(severity, "info"),
                "summary": str(finding.get("summary") or ""),
                "path": str(finding.get("path") or ""),
                "detail": str(finding.get("detail") or ""),
                "repair_command": str(finding.get("repair_command") or ""),
                "safe_to_share": True,
            }
        )

    registry_found = bool(summary.get("registry_found"))
    registry_ok = bool(summary.get("registry_ok"))
    descriptor_found = bool(summary.get("descriptor_found"))
    warnings = int(summary.get("warnings", 0) or 0)
    errors = int(summary.get("errors", 0) or 0)

    codes_by_severity: dict[str, list[str]] = {}
    for finding in findings:
        severity = str(finding.get("severity") or "info")
        code = str(finding.get("code") or "")
        if not code:
            continue
        codes_by_severity.setdefault(severity, []).append(code)
    warn_codes = sorted(set(codes_by_severity.get("warn", [])))
    error_codes = sorted(set(codes_by_severity.get("error", [])))

    if errors:
        state = "error"
        section_summary = (
            f"{errors} topology drift error(s): {', '.join(error_codes)}"
            if error_codes
            else f"{errors} topology drift error(s)"
        )
    elif warnings:
        state = "warn"
        section_summary = (
            f"{warnings} topology drift warning(s): {', '.join(warn_codes)}"
            if warn_codes
            else f"{warnings} topology drift warning(s)"
        )
    elif not registry_found and not descriptor_found:
        state = "info"
        section_summary = "no topology registry yet (optional)"
    elif registry_found and registry_ok:
        state = "ok"
        section_summary = "topology registry parses; no drift detected"
    else:
        state = "info"
        section_summary = "no topology registry yet (optional)"

    return {
        "state": state,
        "summary": section_summary,
        "checks": checks,
        "findings": findings,
        "child_repo_count": int(summary.get("child_repo_count", 0) or 0),
        "restricted_repo_count": int(summary.get("restricted_repo_count", 0) or 0),
        "summary_payload": {
            "registry_found": registry_found,
            "registry_ok": registry_ok,
            "descriptor_found": descriptor_found,
            "child_repo_count": int(summary.get("child_repo_count", 0) or 0),
            "restricted_repo_count": int(summary.get("restricted_repo_count", 0) or 0),
            "warnings": warnings,
            "errors": errors,
        },
    }


def _validation_summary(
    repo: Path,
    *,
    migration_drift_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        report = validate_mod.run(
            str(repo),
            cross_refs=True,
            migration_drift_report=migration_drift_report,
        )
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
    categories = report.get("validation_categories") or {}
    top_category = categories.get("top_category")
    state = "error" if errors else ("warn" if warnings else "ok")
    return {
        "ok": report["ok"],
        "state": state,
        "summary": (
            f"{errors} error(s), {warnings} warning(s)"
            + (f"; top category: {top_category}" if top_category else "")
        ),
        "report": {
            "summary": summary,
            "validation_categories": report.get("validation_categories", {}),
            "files": len(report.get("files", [])),
            "legacy_repair": report.get("legacy_repair"),
            "cross_refs": {
                "enabled": report.get("cross_refs", {}).get("enabled", False),
                "warnings": len(report.get("cross_refs", {}).get("warnings", [])),
                "orphan_offers": len(report.get("cross_refs", {}).get("orphan_offers", [])),
            },
            "migration_drift": report.get("migration_drift", {}).get("summary", {}),
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

    codex_readiness = codex_mod.readiness(repo)
    codex_executable = codex_readiness["executable"]
    codex_instructions = codex_readiness["instructions"]
    checks.append(
        {
            "name": "codex-cli",
            "ok": bool(codex_executable["found"]),
            "detail": codex_executable["path"] or "codex not on PATH",
            "severity": "info",
            "repair": codex_executable["repair"],
            "safe_to_share": True,
        }
    )
    checks.append(
        {
            "name": "codex-agents-md",
            "ok": bool(codex_instructions["ok"]),
            "detail": "AGENTS.md is current and points Codex to mb facts"
            if codex_instructions["ok"]
            else (
                "AGENTS.md is missing, stale, or missing required mb fact commands. "
                "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`."
            ),
            "severity": "ok" if codex_instructions["ok"] else "warn",
            "repair": codex_instructions["repair"],
            "safe_to_share": True,
            "status": codex_instructions,
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
    drift = migration_lint.run(repo)
    checks.append(
        {
            "name": "migration-drift",
            "ok": bool(drift["ok"]),
            "detail": (
                "no migration-shape drift found"
                if drift["ok"]
                else (
                    f"{drift['summary']['warnings']} migration drift warning(s): "
                    + ", ".join(drift["summary"]["categories"])
                )
            ),
            "severity": "ok" if drift["ok"] else "warn",
            "findings": drift["findings"],
            "summary": drift["summary"],
            "safe_to_share": True,
        }
    )
    checkpoint_hook = checkpoint_mod.hook_status(repo)
    hook_state = str(checkpoint_hook.get("state"))
    checks.append(
        {
            "name": "checkpoint-hook",
            "ok": bool(checkpoint_hook["ok"]),
            "detail": str(checkpoint_hook["summary"]),
            "severity": "ok"
            if checkpoint_hook["ok"]
            else "info"
            if hook_state == "engine_repo"
            else "warn",
            "state": hook_state,
            "repair": str(checkpoint_hook.get("summary") or ""),
            "repair_command": str(checkpoint_hook.get("repair_command") or ""),
            "safe_to_share": True,
        }
    )
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
    migration_drift = _migration_drift_from_checks(
        doctor_report["checks"], target
    ) or migration_lint.run(target)
    reference_state = _legacy_reference_state(target)
    offer_topology = _offer_topology_state(target)
    legacy_vip = _legacy_vip_audit_state(target)
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

    drift_actions: list[dict[str, Any]] = []
    if migration_drift["findings"]:
        action = _action(
            id="migration-drift-review",
            title="Review business repo migration drift",
            state="warn",
            mode="manual",
            command="mb doctor repair --plan --json && mb validate --json",
            safe_to_apply=False,
            reason=(
                "migration drift warnings name stale paths and categories without "
                "copying private file contents; operators should approve moves or "
                "frontmatter repairs explicitly"
            ),
        )
        actions.append(action)
        drift_actions.append(action)
    sections.append(
        _section(
            "migration-drift",
            "Migration Drift Lint",
            "warn" if migration_drift["findings"] else "ok",
            (
                f"{migration_drift['summary']['warnings']} warning(s): "
                + ", ".join(migration_drift["summary"]["categories"])
                if migration_drift["findings"]
                else "no legacy active-write or stale runtime guidance drift found"
            ),
            checks=[
                {
                    "name": str(item["code"]),
                    "state": "warn",
                    "summary": str(item["message"]),
                    "path": str(item["path"]),
                    "category": str(item["category"]),
                    "repair_command": str(item["repair_command"]),
                    "content_included": False,
                }
                for item in migration_drift["findings"]
            ],
            actions=drift_actions,
        )
    )

    topology_drift = _topology_drift_state(target)
    topology_actions: list[dict[str, Any]] = []
    if topology_drift["state"] in {"warn", "error"}:
        action = _action(
            id="topology-drift-review",
            title="Review repo topology drift",
            state=topology_drift["state"],
            mode="manual",
            command="mb status --json --peek && mb validate --json",
            safe_to_apply=False,
            reason=(
                "topology drift names hub/child mismatches, unsafe metadata, "
                "or orphaned descriptors; doctor surfaces evidence but does "
                "not rename, delete, or rewrite repos or descriptors"
            ),
        )
        actions.append(action)
        topology_actions.append(action)
    sections.append(
        _section(
            "topology-drift",
            "Repo Topology Drift",
            topology_drift["state"],
            topology_drift["summary"],
            checks=topology_drift["checks"],
            actions=topology_actions,
        )
    )

    offer_actions: list[dict[str, Any]] = []
    if offer_topology["state"] != "ok":
        action = _action(
            id="offer-topology-review",
            title="Review active-offer and multi-offer migration guidance",
            state=offer_topology["state"],
            mode="manual",
            command="mb status --json --peek && mb validate --cross-refs",
            safe_to_apply=False,
            reason=(
                "active offer, brand offer, and per-offer topology are strategy "
                "choices; doctor surfaces evidence but does not rename or rewrite them"
            ),
        )
        actions.append(action)
        offer_actions.append(action)
    sections.append(
        _section(
            "offer-topology",
            "Offer Topology And Session State",
            offer_topology["state"],
            (
                "operator review needed for active-offer or multi-offer drift"
                if offer_topology["state"] != "ok"
                else "no offer topology migration guidance needed"
            ),
            checks=offer_topology["checks"],
            actions=offer_actions,
        )
    )

    legacy_vip_actions: list[dict[str, Any]] = []
    if legacy_vip["state"] != "ok":
        action = _action(
            id="legacy-vip-audit",
            title="Review legacy .vip YAML config/state",
            state=legacy_vip["state"],
            mode="manual",
            command="mb doctor repair --plan --json",
            safe_to_apply=False,
            reason=(
                ".vip YAML can contain private paths, provider notes, client context, "
                "or stale runtime snapshots; doctor classifies keys but does not copy "
                "raw values or migrate content automatically"
            ),
        )
        actions.append(action)
        legacy_vip_actions.append(action)
    sections.append(
        _section(
            "legacy-vip",
            "Legacy .vip Config And State",
            legacy_vip["state"],
            legacy_vip["summary"],
            checks=legacy_vip["checks"],
            actions=legacy_vip_actions,
        )
    )

    missing_gitignore = _missing_gitignore_entries(target)
    tracked_local_state = _tracked_local_state_paths(target)
    gitignore_actions: list[dict[str, Any]] = []
    if missing_gitignore or tracked_local_state:
        action = _action(
            id="gitignore-local-state",
            title="Protect Main Branch local state in .gitignore",
            state="warn",
            mode="write",
            command="mb doctor repair --apply",
            safe_to_apply=True,
            reason=(
                "these entries are local operational state; doctor repair adds "
                "gitignore coverage and untracks any already-committed local state"
            ),
            writes=[".gitignore", *tracked_local_state],
        )
        actions.append(action)
        gitignore_actions.append(action)
    gitignore_state = "warn" if missing_gitignore or tracked_local_state else "ok"
    sections.append(
        _section(
            "gitignore",
            "Local State Gitignore",
            gitignore_state,
            (
                f"{len(missing_gitignore)} missing gitignore entrie(s), "
                f"{len(tracked_local_state)} tracked local-state file(s)"
                if missing_gitignore
                else f"{len(tracked_local_state)} tracked local-state file(s)"
                if tracked_local_state
                else "Main Branch local state is ignored"
            ),
            checks=[
                {
                    "name": entry,
                    "state": "warn"
                    if entry in missing_gitignore or entry in tracked_local_state
                    else "ok",
                    "summary": (
                        "tracked; repair will untrack"
                        if entry in tracked_local_state
                        else "missing"
                        if entry in missing_gitignore
                        else "covered"
                    ),
                }
                for entry in LOCAL_GITIGNORE_ENTRIES
            ],
            actions=gitignore_actions,
        )
    )

    checkpoint_hook = checkpoint_mod.hook_status(target)
    checkpoint_state = str(checkpoint_hook.get("state"))
    hook_check_state = (
        "ok"
        if checkpoint_hook.get("ok")
        else "info"
        if checkpoint_state == "engine_repo"
        else "warn"
        if checkpoint_state in {"missing", "broken", "blocked_existing_hook"}
        else "error"
    )
    hook_actions: list[dict[str, Any]] = []
    if checkpoint_state in {"missing", "broken"}:
        action = _action(
            id="checkpoint-hook-install",
            title="Install business checkpoint commit-message hook",
            state="warn",
            mode="write",
            command="mb checkpoint --install-hook",
            safe_to_apply=True,
            reason=(
                "the repo-local commit-msg hook validates manual git commits "
                "against the same business-readable checkpoint contract"
            ),
            writes=[".git/hooks/commit-msg"],
        )
        actions.append(action)
        hook_actions.append(action)
    elif checkpoint_state == "blocked_existing_hook":
        action = _action(
            id="checkpoint-hook-existing",
            title="Review existing commit-message hook before installing checkpoint validation",
            state="warn",
            mode="manual",
            command="review .git/hooks/commit-msg, then run mb checkpoint --install-hook",
            safe_to_apply=False,
            reason=(
                "Main Branch will not overwrite an existing user hook; preserve or "
                "compose it intentionally before installing checkpoint validation"
            ),
            writes=[".git/hooks/commit-msg"],
        )
        actions.append(action)
        hook_actions.append(action)
    sections.append(
        _section(
            "checkpoint-hook",
            "Checkpoint Commit Hook",
            hook_check_state,
            str(checkpoint_hook.get("summary") or "checkpoint hook status unavailable"),
            checks=[
                {
                    "name": "commit-msg",
                    "state": hook_check_state,
                    "summary": str(checkpoint_hook.get("summary") or ""),
                    "hook": str(checkpoint_hook.get("hook") or ""),
                    "repair_command": str(checkpoint_hook.get("repair_command") or ""),
                }
            ],
            actions=hook_actions,
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

    codex_status = codex_mod.readiness(target)
    codex_instruction_status = codex_status["instructions"]
    codex_checks = [
        {
            "name": "codex-cli",
            "state": "ok" if codex_status["executable"]["found"] else "info",
            "summary": codex_status["executable"]["path"] or "codex not on PATH",
        },
        {
            "name": "AGENTS.md",
            "state": "ok" if codex_instruction_status["ok"] else "warn",
            "summary": (
                "Codex instructions are current and include mb fact grounding"
                if codex_instruction_status["ok"]
                else "Codex instructions are missing, stale, or missing mb fact grounding"
            ),
            "missing_fact_commands": codex_instruction_status["missing_fact_commands"],
            "approval_boundary_ok": codex_instruction_status["approval_boundary_ok"],
            "codex_native_ok": codex_instruction_status["codex_native_ok"],
        },
    ]
    codex_actions: list[dict[str, Any]] = []
    if not codex_instruction_status["ok"]:
        action = _action(
            id="codex-agents-md",
            title="Refresh Codex AGENTS.md instructions",
            state="warn",
            mode="write",
            command="mb doctor repair --apply",
            safe_to_apply=True,
            reason=(
                "AGENTS.md is the tracked Codex entrypoint; repair writes the current "
                "CLI-first start workflow and approval boundaries"
            ),
            writes=["AGENTS.md"],
        )
        actions.append(action)
        codex_actions.append(action)
    sections.append(
        _section(
            "codex-wiring",
            "Codex CLI Adapter",
            _max_state([str(item["state"]) for item in codex_checks]),
            "Experimental CLI-first adapter instructions and executable readiness",
            checks=codex_checks,
            actions=codex_actions,
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

    validation = _validation_summary(target, migration_drift_report=migration_drift)
    related_links = related_links_mod.plan(target)
    related_actions: list[dict[str, Any]] = []
    if related_links["summary"]["missing_links"]:
        action = _action(
            id="related-links-mirror",
            title="Mirror frontmatter links into Related links",
            state="warn",
            mode="write",
            command="mb doctor repair --apply",
            safe_to_apply=True,
            reason=(
                "frontmatter stays canonical; doctor only adds missing body-level "
                "Markdown links for GitHub, Obsidian, and human browsing"
            ),
            writes=[str(item["path"]) for item in related_links["files"]],
        )
        actions.append(action)
        related_actions.append(action)
    validation_categories = (
        validation.get("report", {}).get("validation_categories", {}).get("by_category", {})
    )
    only_related_link_warnings = set(validation_categories) == {
        related_links_mod.MISSING_RELATED_LINK_MIRROR_CATEGORY
    }
    if validation["state"] != "ok" and not only_related_link_warnings:
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

    sections.append(
        _section(
            "related-links",
            "Related Links Mirrors",
            "warn" if related_links["summary"]["missing_links"] else "ok",
            (
                f"{related_links['summary']['missing_links']} frontmatter link(s) missing "
                f"from {related_links['summary']['files']} Related links section(s)"
                if related_links["summary"]["missing_links"]
                else "Related links mirrors match frontmatter"
            ),
            checks=[
                {
                    "name": str(item["path"]),
                    "state": "warn",
                    "summary": f"{len(item['missing'])} missing mirror link(s)",
                    "missing": item["missing"],
                    "content_included": False,
                }
                for item in related_links["files"]
            ],
            actions=related_actions,
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
            "related_links_mirrors": "mb doctor repair --plan --json",
            "runtime_smoke_required": (
                "Static repair does not prove Claude Code runtime behavior. "
                "From the business repo, run `claude`, confirm `/mb-start` is discoverable, "
                "and verify it reads repo context without writing into the engine repo. "
                "For Codex, run read-only `codex exec --json --ephemeral --sandbox read-only "
                "-c 'approval_policy=\"never\"' -C <repo>` and verify the repo stays clean."
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
            "migration_drift": migration_drift,
            "offer_topology": offer_topology,
            "legacy_vip": legacy_vip,
            "legacy_claude_links": legacy_links,
            "validation": validation.get("report", {}),
            "related_links": related_links,
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
    tracked_local_state = _tracked_local_state_paths(target)
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
    if tracked_local_state:
        results = [_untrack_local_state_path(target, rel) for rel in tracked_local_state]
        applied.append(
            _action(
                id="gitignore-local-state-untrack",
                title="Untracked Main Branch local state from git",
                state="ok" if all(item["ok"] for item in results) else "error",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason=(
                    "removed local operational state from the git index while "
                    "leaving the files on disk"
                ),
                writes=tracked_local_state,
                applied=any(item["ok"] for item in results),
                result={"untracked": results},
            )
        )

    checkpoint_hook = checkpoint_mod.hook_status(target)
    if checkpoint_hook.get("state") in {"missing", "broken"}:
        installed = checkpoint_mod.install_commit_hook(target)
        applied.append(
            _action(
                id="checkpoint-hook-install",
                title="Installed business checkpoint commit-message hook",
                state="ok" if installed["ok"] else "error",
                mode="write",
                command="mb checkpoint --install-hook",
                safe_to_apply=True,
                reason="installed repo-local validation for business-readable checkpoint subjects",
                writes=[".git/hooks/commit-msg"],
                applied=bool(installed.get("changed")),
                result=installed,
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

    codex_instruction_status = codex_mod.instructions_status(target)
    if not codex_instruction_status["ok"]:
        agents = codex_mod.write_agents_md(target)
        applied.append(
            _action(
                id="codex-agents-md",
                title="Refreshed Codex AGENTS.md instructions",
                state="ok" if agents["ok"] else "error",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason="wrote the current CLI-first Codex start workflow and approval boundaries",
                writes=["AGENTS.md"],
                applied=bool(agents["changed"]),
                result=agents,
            )
        )

    related_links_result = related_links_mod.apply(target)
    if related_links_result["changed"] or related_links_result["errors"]:
        applied.append(
            _action(
                id="related-links-mirror",
                title="Mirrored frontmatter links into Related links",
                state="ok" if related_links_result["ok"] else "error",
                mode="write",
                command="mb doctor repair --apply",
                safe_to_apply=True,
                reason=(
                    "added missing Markdown body links from frontmatter; "
                    "frontmatter remains authoritative"
                ),
                writes=[str(item["path"]) for item in related_links_result["changed"]],
                applied=bool(related_links_result["changed"]),
                result=related_links_result,
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
