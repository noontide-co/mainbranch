"""Locate and link the bundled Main Branch engine payload.

The public wheel carries a synthetic engine root at ``mb/_engine`` whose
shape mirrors the source checkout enough for Claude Code skills:

```
mb/_engine/.claude/skills/...
mb/_engine/.claude/reference/...
mb/_engine/.claude/lenses/...
```

Source checkouts use the repository root directly. Keeping both install
modes behind this module lets ``mb init`` and ``mb skill link`` wire the
same Claude Code discovery surface for pipx users and clone-based users.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

SKILL_PREFIX = "mb-"
PRIMARY_SKILL = "mb-start"
LEGACY_SKILL_NAMES = (
    "ads",
    "end",
    "help",
    "organic",
    "pull",
    "setup",
    "site",
    "skill-brief-draft",
    "skill-concept",
    "skill-review",
    "start",
    "think",
    "wiki",
)
RETIRED_PROJECT_SKILL_LINK_NAMES = (
    "mb-pull",
    "mb-vsl",
    "vsl",
)
ENGINE_MARKER = Path(".claude") / "skills" / PRIMARY_SKILL / "SKILL.md"
GITIGNORE_HEADER = "# Main Branch local Claude wiring"


def _is_engine_root(path: Path) -> bool:
    return (path / ENGINE_MARKER).is_file()


def source_engine_root() -> Path | None:
    """Return the repo root when running from a source checkout."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if _is_engine_root(parent):
            return parent
    return None


def packaged_engine_root() -> Path | None:
    """Return the installed wheel's synthetic engine root, if present."""
    try:
        ref = resources.files("mb").joinpath("_engine")
        root = Path(str(ref))
        if _is_engine_root(root):
            return root
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    return None


def engine_root() -> Path | None:
    """Return the best engine root for this install.

    Prefer the packaged payload when it exists so pipx installs win over
    stale clone paths. Source checkouts fall back to the repository root.
    """
    return packaged_engine_root() or source_engine_root()


def skills_dir(root: Path | None = None) -> Path | None:
    root = root or engine_root()
    if root is None:
        return None
    candidate = root / ".claude" / "skills"
    return candidate if candidate.is_dir() else None


def bundled_skills() -> list[str]:
    """Names of bundled skills, alphabetically."""
    root = skills_dir()
    if root is None:
        return []
    return sorted(d.name for d in root.iterdir() if d.is_dir())


def legacy_skill_name(name: str) -> str:
    """Return the pre-prefix skill name for a bundled skill name."""
    return name[len(SKILL_PREFIX) :] if name.startswith(SKILL_PREFIX) else name


def skill_path(name: str) -> Path | None:
    """Return on-disk path to a bundled skill's directory."""
    root = skills_dir()
    if root is None:
        return None
    candidate = root / name
    return candidate if candidate.is_dir() else None


def _read_settings(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _looks_like_engine_root_path(path: Path) -> bool:
    has_skill_marker = any(
        (path / ".claude" / "skills" / name / "SKILL.md").is_file()
        for name in (PRIMARY_SKILL, "start")
    )
    if not has_skill_marker:
        return False
    source_markers = [
        path / "mb" / "mb" / "__init__.py",
        path / "mb" / "pyproject.toml",
        path / "AGENTS.md",
        path / "CHANGELOG.md",
    ]
    packaged_markers = [
        path.parent / "__init__.py",
        path.parent / "py.typed",
    ]
    return any(marker.exists() for marker in source_markers) or (
        path.name == "_engine" and any(marker.exists() for marker in packaged_markers)
    )


def _looks_like_missing_legacy_engine_path(value: str) -> bool:
    parts = {part.lower() for part in Path(value).parts}
    return bool(parts & {"mb-vip", "mainbranch"})


def looks_like_missing_legacy_engine_path(value: str) -> bool:
    """Return whether a missing path looks like an old Main Branch engine clone."""
    return _looks_like_missing_legacy_engine_path(value)


def _is_stale_engine_path(value: str, active_root: Path) -> bool:
    candidate = Path(value).expanduser()
    try:
        if candidate.exists() and candidate.resolve() == active_root.resolve():
            return False
    except OSError:
        return False
    if candidate.exists():
        return _looks_like_engine_root_path(candidate)
    return _looks_like_missing_legacy_engine_path(value)


def is_stale_engine_path(value: str, active_root: Path) -> bool:
    """Return whether ``value`` points at a stale Main Branch engine root."""
    return _is_stale_engine_path(value, active_root)


def _write_settings(repo: Path, root: Path) -> tuple[bool, list[str]]:
    settings_path = repo / ".claude" / "settings.local.json"
    data = _read_settings(settings_path)
    permissions = data.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        permissions = {}
        data["permissions"] = permissions

    existing = permissions.get("additionalDirectories", [])
    if not isinstance(existing, list):
        existing = []

    root_str = str(root)
    removed_stale = [
        str(p)
        for p in existing
        if isinstance(p, str) and p != root_str and _is_stale_engine_path(p, root)
    ]
    cleaned = [
        str(p) for p in existing if isinstance(p, str) and p != root_str and p not in removed_stale
    ]
    permissions["additionalDirectories"] = [root_str, *cleaned]

    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    changed = not settings_path.exists() or settings_path.read_text(encoding="utf-8") != rendered
    if changed:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(rendered, encoding="utf-8")
    return changed, removed_stale


def _append_unique_gitignore(repo: Path, entries: list[str]) -> bool:
    gitignore = repo / ".gitignore"
    existing_text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    existing_lines = set(existing_text.splitlines())

    to_add = [entry for entry in entries if entry not in existing_lines]
    if not to_add:
        return False

    prefix = "" if not existing_text or existing_text.endswith("\n") else "\n"
    block = [GITIGNORE_HEADER, *to_add]
    if GITIGNORE_HEADER in existing_lines:
        block = to_add
    gitignore.write_text(existing_text + prefix + "\n".join(block) + "\n", encoding="utf-8")
    return True


def _remove_gitignore_entries(repo: Path, entries: list[str]) -> bool:
    gitignore = repo / ".gitignore"
    if not gitignore.exists():
        return False

    existing_text = gitignore.read_text(encoding="utf-8")
    remove = set(entries)
    lines = existing_text.splitlines()
    kept = [line for line in lines if line not in remove]
    if kept == lines:
        return False

    rendered = "\n".join(kept)
    if rendered:
        rendered += "\n"
    gitignore.write_text(rendered, encoding="utf-8")
    return True


def _link_or_copy(source: Path, dest: Path) -> str:
    if dest.is_symlink():
        try:
            if dest.resolve(strict=True) == source.resolve(strict=True):
                return "unchanged"
        except FileNotFoundError:
            pass
        dest.unlink()
    elif dest.exists():
        return "skipped"

    try:
        dest.symlink_to(source, target_is_directory=True)
        return "linked"
    except OSError:
        shutil.copytree(
            source,
            dest,
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
        )
        return "copied"


def _remove_legacy_project_links(skill_link_dir: Path) -> list[str]:
    """Remove old project-local bridge symlinks after the bundled rename."""
    removed: list[str] = []
    removable_names = sorted(set(LEGACY_SKILL_NAMES) | set(RETIRED_PROJECT_SKILL_LINK_NAMES))
    for name in removable_names:
        dest = skill_link_dir / name
        if dest.is_symlink():
            dest.unlink()
            removed.append(f".claude/skills/{name}")
    return removed


def _personal_skills_dir() -> Path:
    return Path.home() / ".claude" / "skills"


def _frontmatter_name(skill_file: Path) -> str:
    try:
        text = skill_file.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    for line in text[3:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return ""


def _infer_skill_root(skill_path: Path, name: str) -> Path | None:
    try:
        resolved = skill_path.resolve(strict=True)
    except FileNotFoundError:
        return None
    if resolved.name != name:
        return None
    if resolved.parent.name != "skills" or resolved.parent.parent.name != ".claude":
        return None
    return resolved.parent.parent.parent


def _looks_like_mainbranch_engine(root: Path | None, skill_path: Path, name: str) -> bool:
    if root is None:
        return False
    skill_file = skill_path / "SKILL.md"
    if not skill_file.is_file():
        return False
    frontmatter_name = _frontmatter_name(skill_file)
    if frontmatter_name and frontmatter_name != name:
        return False
    source_markers = [
        root / "mb" / "mb" / "__init__.py",
        root / "mb" / "pyproject.toml",
        root / "AGENTS.md",
        root / "CHANGELOG.md",
    ]
    packaged_markers = [
        root.parent / "__init__.py",
        root.parent / "py.typed",
    ]
    return any(marker.exists() for marker in source_markers) or (
        root.name == "_engine" and any(marker.exists() for marker in packaged_markers)
    )


def _classify_personal_skill(entry: Path, name: str) -> tuple[str, str]:
    if not entry.exists() and not entry.is_symlink():
        return "missing", ""
    if entry.is_symlink():
        try:
            resolved = entry.resolve(strict=True)
        except FileNotFoundError:
            return "broken-symlink", ""
        root = _infer_skill_root(entry, name)
        if _looks_like_mainbranch_engine(root, resolved, name):
            return "stale-mainbranch-link", str(resolved)
        return "not-mainbranch-link", str(resolved)
    return "not-mainbranch-link", str(entry)


def _backup_destination(global_dir: Path, name: str, timestamp: str) -> Path:
    base = global_dir / ".mainbranch-backups" / timestamp
    candidate = base / name
    if not candidate.exists() and not candidate.is_symlink():
        return candidate
    suffix = 1
    while True:
        candidate = base / f"{name}-{suffix}"
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
        suffix += 1


def _conflict_finding(
    *,
    name: str,
    kind: str,
    global_dir: Path,
    repo: Path,
    apply: bool,
    timestamp: str,
) -> dict[str, Any]:
    entry = global_dir / name
    classification, target = _classify_personal_skill(entry, name)
    safe_to_repair = classification in {"stale-mainbranch-link", "broken-symlink"}
    backup_path = ""
    repaired = False
    error = ""
    if apply and safe_to_repair:
        backup = _backup_destination(global_dir, name, timestamp)
        try:
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(entry), str(backup))
            repaired = True
            backup_path = str(backup)
        except OSError as exc:
            error = str(exc)

    current_name = f"{SKILL_PREFIX}{name}" if kind == "legacy-global" else name
    return {
        "name": name,
        "current_name": current_name,
        "kind": kind,
        "global_path": str(entry),
        "global_target": target,
        "project_path": str(repo / ".claude" / "skills" / current_name),
        "classification": classification,
        "safe_to_repair": safe_to_repair,
        "repaired": repaired,
        "backup_path": backup_path,
        "error": error,
        "message": (
            "personal skill shadows the project-local Main Branch skill"
            if kind == "active-shadow"
            else "legacy personal skill can still catch the old slash command"
        ),
    }


def inspect_personal_skill_conflicts(
    repo: str | Path,
    *,
    apply: bool = False,
    personal_skills_dir: Path | None = None,
) -> dict[str, Any]:
    """Inspect or repair personal Claude Code skills that can shadow Main Branch.

    ``apply`` only moves stale Main Branch symlinks and broken symlinks matching
    Main Branch's current or legacy skill names. User-authored or third-party
    skills are reported but never changed.
    """
    target = Path(repo).expanduser().resolve()
    global_dir = personal_skills_dir or _personal_skills_dir()
    current_names = bundled_skills()
    findings: list[dict[str, Any]] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for name in current_names:
        project_skill = target / ".claude" / "skills" / name / "SKILL.md"
        global_entry = global_dir / name
        if project_skill.is_file() and (global_entry.exists() or global_entry.is_symlink()):
            findings.append(
                _conflict_finding(
                    name=name,
                    kind="active-shadow",
                    global_dir=global_dir,
                    repo=target,
                    apply=apply,
                    timestamp=timestamp,
                )
            )

    current_legacy_names = {legacy_skill_name(name) for name in current_names}
    for name in LEGACY_SKILL_NAMES:
        global_entry = global_dir / name
        if name in current_legacy_names and (global_entry.exists() or global_entry.is_symlink()):
            findings.append(
                _conflict_finding(
                    name=name,
                    kind="legacy-global",
                    global_dir=global_dir,
                    repo=target,
                    apply=apply,
                    timestamp=timestamp,
                )
            )

    blocking = [
        item
        for item in findings
        if item["kind"] == "active-shadow" and not item.get("repaired", False)
    ]
    repairable = [
        item for item in findings if item["safe_to_repair"] and not item.get("repaired", False)
    ]
    errors = [item for item in findings if item["error"]]
    return {
        "ok": not blocking and not errors,
        "repo": str(target),
        "personal_skills_dir": str(global_dir),
        "checked_current_skills": current_names,
        "checked_legacy_skills": list(LEGACY_SKILL_NAMES),
        "apply": apply,
        "findings": findings,
        "summary": {
            "findings": len(findings),
            "active_shadows": sum(1 for item in findings if item["kind"] == "active-shadow"),
            "legacy_globals": sum(1 for item in findings if item["kind"] == "legacy-global"),
            "repairable": len(repairable),
            "repaired": sum(1 for item in findings if item["repaired"]),
            "blocked": len(blocking),
            "errors": len(errors),
        },
        "repair_command": "mb skill repair --repo . --apply",
    }


def link_skills(repo: str | Path) -> dict[str, Any]:
    """Wire bundled skills into a business repo for Claude Code discovery."""
    target = Path(repo).resolve()
    target.mkdir(parents=True, exist_ok=True)

    root = engine_root()
    if root is None:
        return {
            "ok": False,
            "repo": str(target),
            "engine_root": None,
            "created": [],
            "linked": [],
            "copied": [],
            "skipped": [],
            "errors": ["could not locate bundled Main Branch engine root"],
        }

    claude_dir = target / ".claude"
    skill_link_dir = claude_dir / "skills"
    skill_link_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    settings_changed, removed_stale_engine_paths = _write_settings(target, root)
    if settings_changed:
        created.append(".claude/settings.local.json")

    linked: list[str] = []
    copied: list[str] = []
    skipped: list[str] = []
    removed_legacy = _remove_legacy_project_links(skill_link_dir)

    for name in bundled_skills():
        source = root / ".claude" / "skills" / name
        dest = skill_link_dir / name
        mode = _link_or_copy(source, dest)
        rel = f".claude/skills/{name}"
        if mode == "linked":
            linked.append(rel)
            created.append(rel)
        elif mode == "copied":
            copied.append(rel)
            created.append(rel)
        elif mode == "skipped":
            skipped.append(rel)

    gitignore_entries = [
        ".claude/settings.local.json",
        ".claude/worktrees/",
        *[f".claude/skills/{name}" for name in bundled_skills()],
    ]
    retired_gitignore_entries = [
        f".claude/skills/{name}"
        for name in sorted(set(LEGACY_SKILL_NAMES) | set(RETIRED_PROJECT_SKILL_LINK_NAMES))
        if name not in bundled_skills()
    ]
    if _remove_gitignore_entries(target, retired_gitignore_entries):
        created.append(".gitignore")
    if _append_unique_gitignore(target, gitignore_entries):
        created.append(".gitignore")

    return {
        "ok": True,
        "repo": str(target),
        "engine_root": str(root),
        "created": list(dict.fromkeys(created)),
        "linked": linked,
        "copied": copied,
        "skipped": skipped,
        "removed_legacy": removed_legacy,
        "removed_stale_engine_paths": removed_stale_engine_paths,
        "errors": [],
        "shadow_report": inspect_personal_skill_conflicts(target, apply=True),
    }


def link_status(repo: str | Path) -> dict[str, Any]:
    """Return whether ``repo`` can discover Main Branch skills."""
    target = Path(repo).resolve()
    root = engine_root()
    settings_path = target / ".claude" / "settings.local.json"
    settings = _read_settings(settings_path)
    dirs = settings.get("permissions", {}).get("additionalDirectories", [])
    if not isinstance(dirs, list):
        dirs = []

    root_str = str(root) if root is not None else ""
    settings_has_engine = bool(root_str and root_str in dirs)
    start_link = target / ".claude" / "skills" / PRIMARY_SKILL
    start_skill = start_link / "SKILL.md"
    start_link_ok = start_skill.is_file()
    shadow_report = inspect_personal_skill_conflicts(target, apply=False)

    return {
        "ok": settings_has_engine and start_link_ok and shadow_report["ok"],
        "repo": str(target),
        "engine_root": root_str or None,
        "settings_path": str(settings_path),
        "settings_has_engine": settings_has_engine,
        "primary_skill": PRIMARY_SKILL,
        "primary_link_ok": start_link_ok,
        "primary_link": str(start_link),
        "start_link_ok": start_link_ok,
        "start_link": str(start_link),
        "shadow_report": shadow_report,
    }


def install_mode() -> str:
    """Best-effort install mode label for diagnostics and skill prose."""
    root = engine_root()
    if root is None:
        return "unknown"
    if packaged_engine_root() is not None:
        root_text = str(root)
        pipx_home = os.environ.get("PIPX_HOME", "").strip()
        prefix = Path(pipx_home).expanduser() if pipx_home else None
        if "pipx" in root_text or (prefix is not None and str(prefix) in root_text):
            return "pipx"
        return "wheel"
    if (root / ".git").exists():
        return "clone"
    return "source"
