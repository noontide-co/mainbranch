"""``mb init`` — non-interactive scaffold for a Main Branch business repo.

Per master decision, v0.1 asks ONE question (business name). Path-config
flexibility is locked; folder names are canonical. Re-running on
an existing repo returns ``status=already-initialized`` (idempotent).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

from mb import checkpoint as checkpoint_mod
from mb.engine import link_skills
from mb.migrate import LATEST_SCHEMA_VERSION, SCHEMA_MARKER

# The canonical business folders. Keep these stable unless a schema migration lands.
DATA_FOLDERS = [
    "core",
    "core/offers",
    "core/proof",
    "core/brand",
    "core/strategy",
    "core/operations",
    "core/finance",
    "research",
    "decisions",
    "bets",
    "log",
    "pushes",
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
.claude/worktrees/
.mb/backups/
.mb/connect.yaml
.mb/onboarding.json
.mb/last-status-seen.json
.mb/issue-drafts/
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
    """Scaffold ``path`` as a Main Branch business repo.

    Returns a dict with ``status`` ∈ {ok, already-initialized, error},
    ``path`` (absolute), and ``created`` (list of relative paths created).
    """
    target = Path(path).resolve()
    target.mkdir(parents=True, exist_ok=True)

    if (target / "CLAUDE.md").exists():
        link_result = link_skills(target)
        return {
            "status": "already-initialized",
            "path": str(target),
            "created": link_result["created"],
            "skill_link": link_result,
            "checkpoint_hook": checkpoint_mod.hook_status(target),
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
            keep.write_text("", encoding="utf-8")
            created.append(f"{sub}/.gitkeep")

    marker = target / SCHEMA_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(LATEST_SCHEMA_VERSION + "\n", encoding="utf-8")
    created.append(SCHEMA_MARKER)

    mapping = {
        "BUSINESS_NAME": business_name,
        "GH_USERNAME": gh_user,
    }

    claude_tmpl = _read_template("CLAUDE.md.tmpl") or _DEFAULT_CLAUDE
    (target / "CLAUDE.md").write_text(_render(claude_tmpl, mapping), encoding="utf-8")
    created.append("CLAUDE.md")

    vocabulary_tmpl = _read_template("core_vocabulary.md.tmpl")
    if vocabulary_tmpl:
        vocabulary_path = target / "core" / "vocabulary.md"
        vocabulary_path.parent.mkdir(parents=True, exist_ok=True)
        if not vocabulary_path.exists():
            vocabulary_path.write_text(_render(vocabulary_tmpl, mapping), encoding="utf-8")
            created.append("core/vocabulary.md")

    codeowners_tmpl = _read_template("CODEOWNERS.tmpl") or f"* @{gh_user}\n"
    github_dir = target / ".github"
    github_dir.mkdir(exist_ok=True)
    (github_dir / "CODEOWNERS").write_text(_render(codeowners_tmpl, mapping), encoding="utf-8")
    created.append(".github/CODEOWNERS")

    gitignore_tmpl = _read_template(".gitignore.tmpl") or DEFAULT_GITIGNORE
    (target / ".gitignore").write_text(_render(gitignore_tmpl, mapping), encoding="utf-8")
    created.append(".gitignore")

    link_result = link_skills(target)
    created.extend(path for path in link_result["created"] if path not in created)

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

    checkpoint_hook = (
        checkpoint_mod.install_commit_hook(target)
        if (target / ".git").exists()
        else checkpoint_mod.hook_status(target)
    )
    if checkpoint_hook.get("changed"):
        created.append(".git/hooks/commit-msg")

    return {
        "status": "ok",
        "path": str(target),
        "created": created,
        "business_name": business_name,
        "skill_link": link_result,
        "checkpoint_hook": checkpoint_hook,
    }


# Embedded fallback CLAUDE.md so ``mb init`` works even without bundled
# templates resolving (early dev installs, source checkouts).
_DEFAULT_CLAUDE = """\
# {{BUSINESS_NAME}}

Your business as files. Claude reads these; you edit them; git remembers them.

## Folders

- `core/` — the business brain: offer, audience, voice, soul, proof, brand,
  strategy, operations, finance
- `core/offers/` — per-offer specifics
- `core/proof/` — testimonials, typicality, and reusable proof
- `core/brand/` — visual identity, voice guardrails, and brand systems
- `core/strategy/` — strategic context that should remain evergreen
- `core/operations/` — operating context such as fulfillment, classroom, funnel, or membership notes
- `core/finance/` — ledger and tax artifacts
- `research/` — dated notes from when you went looking
- `decisions/` — dated choices, with rationale
- `bets/` — operating bets with appetite, metric, target, and outcome
- `log/` — running activity log
- `pushes/` — coordinated pushes (launches, drops, challenges, promos, etc.)
- `documents/` — anything that doesn't belong above

If your repo was created before the push primitive decision, you may also have
a legacy `campaigns/` folder. `mb` continues to read it; new coordinated work
should land in `pushes/`. Run `mb doctor` to see whether your repo is on the
canonical shape and `mb migrate campaigns --plan` to preview a safe move.

## Optional: operator vocabulary

`core/vocabulary.md` is an optional file where the business names what it
calls coordinated pushes. A coach might call them *drops*; a creator might
call them *launches*; a community might call them *challenges*. The file
shape:

    ---
    type: vocabulary
    status: active
    terms:
      push:
        singular: drop
        plural: drops
      statuses:
        active: live
        completed: shipped
    ---

    Optional prose explanation goes here.

Vocabulary changes how skills and `mb status` speak in conversation. It does
not rename folders, frontmatter types, link fields, JSON keys, validator
rules, or commands. Engine internals stay canonical.

## Conventions

- Decisions, research, bets, and offers carry a small block of metadata at the top
  (frontmatter). Run `mb validate` to check it.
- Status field: proposed | running | scaling | killed | graduated | died.
- One owner per file (CODEOWNERS pattern).

## Connected accounts

Treat this repo as the boundary for connected business tools. When you switch
business repos, switch the accounts, tokens, and MCP servers that can act on
that business.

Keep non-secret IDs in repo files when they help agents choose the right
account: Stripe account/product/price IDs in `core/offers/<offer>/stripe.md`,
Google Ads customer and campaign IDs (provider's term for their object) in
`pushes/<push>/push.md` `provider_refs:`, ad pixel IDs beside the site or
push files they belong to, and MCP server names/scopes in local setup notes.

Never commit API keys, OAuth refresh tokens, service-account JSON, webhook
secrets, MCP tokens, or bearer tokens. Put secrets in a runtime local config,
OS keychain, 1Password, `.env`, or `.claude/settings.local.json`; those files
should stay gitignored. If a tool can spend money, publish, email, or mutate a
customer account, verify it is tethered to this repo before using it.

## Helpful commands

```
mb doctor                  # see if anything is off in this repo
mb validate                # check the metadata on your files
mb graph --open            # see what links to what
```

Visit https://mainbranch.io for the full system docs.

Owner: @{{GH_USERNAME}}
"""
