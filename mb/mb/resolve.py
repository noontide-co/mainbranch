"""``mb resolve`` — path resolution for reference files and skills.

Resolution order for a key like ``voice``:
1. ``~/curated/voice/voice.md`` (paid private repo, collaborator-gated)
2. ``<repo>/core/voice.md`` (local override the user wrote)
3. ``<site-packages>/mb/_data/stubs/voice.md`` (MIT shipped stub)

If only the stub matches, ``is_stub=True`` and the caller knows to
display the upgrade banner.

``v0.1`` ships with the canonical six-folder names locked. Per the
master decision, path-config flexibility is a v0.2 unlock; this module
reads ``.vip/config.yaml``'s ``paths:`` block defensively but defaults
to the lock.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from mb.engine import bundled_skills as _bundled_skills
from mb.engine import skill_path as _skill_path

CANONICAL_PATHS = {
    "core": "core",
    "research": "research",
    "decisions": "decisions",
    "log": "log",
    "campaigns": "campaigns",
    "documents": "documents",
}


def _curated_root() -> Path:
    return Path.home() / "curated"


def _read_paths_block(repo: Path) -> dict[str, str]:
    """v0.2 unlock entry point. v0.1 returns the canonical lock."""
    cfg = repo / ".vip" / "config.yaml"
    if not cfg.exists():
        return CANONICAL_PATHS
    try:
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return CANONICAL_PATHS
    block = data.get("paths") if isinstance(data, dict) else None
    if isinstance(block, dict):
        # v0.2: honor the override. v0.1: still lock.
        merged = dict(CANONICAL_PATHS)
        for k, v in block.items():
            if isinstance(v, str):
                merged[k] = v
        return merged
    return CANONICAL_PATHS


def run(key: str, repo: str = ".") -> dict[str, Any]:
    """Resolve a reference key. Returns dict with ``resolved``, ``path``, ``is_stub``."""
    repo_path = Path(repo).resolve()
    paths = _read_paths_block(repo_path)
    core = paths.get("core", "core")

    # 1. Curated paid repo
    curated = _curated_root() / key / f"{key}.md"
    if curated.exists():
        return {"resolved": True, "path": str(curated), "is_stub": False, "tier": "curated"}

    # 2. Local override
    local = repo_path / core / f"{key}.md"
    if local.exists():
        return {"resolved": True, "path": str(local), "is_stub": False, "tier": "local"}

    # 3. Bundled stub
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("stubs").joinpath(f"{key}.md")
        if ref.is_file():
            return {
                "resolved": True,
                "path": str(ref),
                "is_stub": True,
                "tier": "stub",
            }
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    # Source-checkout fallback
    here = Path(__file__).resolve().parent / "_data" / "stubs" / f"{key}.md"
    if here.exists():
        return {"resolved": True, "path": str(here), "is_stub": True, "tier": "stub"}

    return {"resolved": False, "path": None, "is_stub": False, "tier": None}


def skill_path(name: str) -> Path | None:
    """Return on-disk path to a bundled skill's directory."""
    return _skill_path(name)


def bundled_skills() -> list[str]:
    """Names of bundled skills (alphabetical)."""
    return _bundled_skills()
