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
from importlib import resources
from pathlib import Path
from typing import Any

ENGINE_MARKER = Path(".claude") / "skills" / "start" / "SKILL.md"
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


def _write_settings(repo: Path, root: Path) -> bool:
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
    cleaned = [str(p) for p in existing if isinstance(p, str) and p != root_str]
    permissions["additionalDirectories"] = [root_str, *cleaned]

    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    changed = not settings_path.exists() or settings_path.read_text(encoding="utf-8") != rendered
    if changed:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(rendered, encoding="utf-8")
    return changed


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
    if _write_settings(target, root):
        created.append(".claude/settings.local.json")

    linked: list[str] = []
    copied: list[str] = []
    skipped: list[str] = []

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
        *[f".claude/skills/{name}" for name in bundled_skills()],
    ]
    if _append_unique_gitignore(target, gitignore_entries):
        created.append(".gitignore")

    return {
        "ok": True,
        "repo": str(target),
        "engine_root": str(root),
        "created": created,
        "linked": linked,
        "copied": copied,
        "skipped": skipped,
        "errors": [],
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
    start_link = target / ".claude" / "skills" / "start"
    start_skill = start_link / "SKILL.md"
    start_link_ok = start_skill.is_file()

    return {
        "ok": settings_has_engine and start_link_ok,
        "repo": str(target),
        "engine_root": root_str or None,
        "settings_path": str(settings_path),
        "settings_has_engine": settings_has_engine,
        "start_link_ok": start_link_ok,
        "start_link": str(start_link),
    }


def install_mode() -> str:
    """Best-effort install mode label for diagnostics and skill prose."""
    root = engine_root()
    if root is None:
        return "unknown"
    if packaged_engine_root() is not None:
        prefix = Path(os.environ.get("PIPX_HOME", "")).expanduser()
        root_text = str(root)
        if "pipx" in root_text or (str(prefix) and str(prefix) in root_text):
            return "pipx"
        return "wheel"
    if (root / ".git").exists():
        return "clone"
    return "source"
