"""``mb init`` — non-interactive scaffold for a Main Branch consumer repo.

Per master decision, v0.1 asks ONE question (business name). Path-config
flexibility is locked; folder names are the canonical six. Re-running on
an existing repo returns ``status=already-initialized`` (idempotent).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

# The canonical six. v0.1 lock; v0.2 unlocks via .vip/config.yaml paths block.
DATA_FOLDERS = [
    "core",
    "core/offers",
    "core/finance",
    "research",
    "decisions",
    "log",
    "campaigns",
    "documents",
]

DEFAULT_GITIGNORE = """\
# Main Branch defaults
.env
.env.*
*.beancount
.DS_Store
__pycache__/
.mypy_cache/
.ruff_cache/
.pytest_cache/
node_modules/
.venv/
"""


def _gh_username() -> str:
    """Best-effort gh-cli username probe. Returns empty string on miss."""
    try:
        out = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return ""


def _read_template(name: str) -> str:
    """Read a bundled template by relative path under ``_data/templates/``."""
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(name)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        # Fallback to repo-relative path during dev (-e install).
        here = Path(__file__).resolve().parent / "_data" / "templates" / name
        if here.exists():
            return here.read_text(encoding="utf-8")
        return ""


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, val in mapping.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def run(path: str, name: str) -> dict[str, Any]:
    """Scaffold ``path`` as a Main Branch consumer repo.

    Returns a dict with ``status`` ∈ {ok, already-initialized, error},
    ``path`` (absolute), and ``created`` (list of relative paths created).
    """
    target = Path(path).resolve()
    target.mkdir(parents=True, exist_ok=True)

    if (target / "CLAUDE.md").exists():
        return {
            "status": "already-initialized",
            "path": str(target),
            "created": [],
        }

    business_name = name.strip() or os.environ.get("MB_BUSINESS_NAME", "").strip()
    if not business_name:
        try:
            business_name = input("business name: ").strip()
        except (EOFError, KeyboardInterrupt):
            return {"status": "error", "path": str(target), "error": "no business name"}
    if not business_name:
        return {"status": "error", "path": str(target), "error": "empty business name"}

    gh_user = _gh_username() or "your-gh-username"

    created: list[str] = []
    for sub in DATA_FOLDERS:
        d = target / sub
        d.mkdir(parents=True, exist_ok=True)
        # .gitkeep so empty folders survive git
        keep = d / ".gitkeep"
        if not keep.exists():
            keep.write_text("")
            created.append(f"{sub}/.gitkeep")

    mapping = {
        "BUSINESS_NAME": business_name,
        "GH_USERNAME": gh_user,
    }

    claude_tmpl = _read_template("CLAUDE.md.tmpl") or _DEFAULT_CLAUDE
    (target / "CLAUDE.md").write_text(_render(claude_tmpl, mapping))
    created.append("CLAUDE.md")

    codeowners_tmpl = _read_template("CODEOWNERS.tmpl") or f"* @{gh_user}\n"
    github_dir = target / ".github"
    github_dir.mkdir(exist_ok=True)
    (github_dir / "CODEOWNERS").write_text(_render(codeowners_tmpl, mapping))
    created.append(".github/CODEOWNERS")

    gitignore_tmpl = _read_template(".gitignore.tmpl") or DEFAULT_GITIGNORE
    (target / ".gitignore").write_text(_render(gitignore_tmpl, mapping))
    created.append(".gitignore")

    if shutil.which("git") and not (target / ".git").exists():
        try:
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=target,
                check=True,
                timeout=10,
            )
            created.append(".git/")
        except subprocess.SubprocessError:
            # git init failure is not fatal for scaffolding
            pass

    return {
        "status": "ok",
        "path": str(target),
        "created": created,
        "business_name": business_name,
    }


# Embedded fallback CLAUDE.md so ``mb init`` works even without bundled
# templates resolving (early dev installs, source checkouts).
_DEFAULT_CLAUDE = """\
# {{BUSINESS_NAME}}

This is a Main Branch consumer repo. Your business is a tree of files.

## Folder taxonomy

- `core/` — long-lived truth (offer, audience, voice, soul)
- `core/offers/` — per-offer specifics
- `core/finance/` — ledger and tax artifacts
- `research/` — dated investigations
- `decisions/` — dated choices, frontmatter status enum
- `log/` — running activity log
- `campaigns/` — paid + organic campaign artifacts
- `documents/` — anything that doesn't belong above

## Conventions

- Decisions, research, and offers carry frontmatter. Run `mb validate` to
  check shape.
- Status enum: proposed | running | scaling | killed | graduated | died.
- One owner per file (CODEOWNERS pattern).

## Helpful commands

```
mb doctor                  # diagnose this repo
mb validate                # check frontmatter shape
mb graph --open            # see the link graph
```

Visit https://mainbranch.io for the full system docs.

Owner: @{{GH_USERNAME}}
"""
