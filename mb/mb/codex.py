"""Experimental Codex CLI-first adapter helpers.

Codex support starts with repo instructions and deterministic ``mb`` facts.
This module intentionally does not invoke Codex or manage model conversation.
"""

from __future__ import annotations

import shlex
import shutil
from importlib import resources
from pathlib import Path
from typing import Any

AGENTS_TEMPLATE = "AGENTS.md.tmpl"
AGENTS_RELATIVE_PATH = "AGENTS.md"
REQUIRED_FACT_COMMANDS = (
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
)


_DEFAULT_AGENTS = """\
# {{BUSINESS_NAME}}

Main Branch business repo instructions for Codex.

## Codex Operating Contract

Main Branch CLI facts are the source of truth for repo health, setup, runtime
wiring, updates, graph/status signals, provider readiness, and repair paths.
When the operator asks to start, begin, get oriented, triage the day, or decide
what to do next, use this Codex-native start workflow. Do not pretend Claude
Code slash commands exist in Codex.

Start in this repo. Before setup, routing, migration, update, or repair advice,
run the read-only checks that fit the situation:

```bash
mb --version
mb status --json --peek
mb start --json
mb doctor repair --plan
```

Use `mb status --json --peek` as the default daily briefing before routing the
operator. It names readiness, drift, onboarding progress, update state, GitHub
activity, provider signals, recent work, ranked actions, bets, pushes, and
checkpoint state. Do not replace those facts with ad hoc shell inspection unless
`mb` says a section is unavailable or the command itself is missing.

Read-only commands can be run without asking first. Commands that write files,
refresh local runtime wiring, update packages, migrate business files, create
checkpoints, publish, spend money, contact customers, email, or mutate provider
accounts require explicit operator approval before applying.

Do the technical work in technical commands, then translate the result back into
business-owner language. Speak first in terms of bets, goals, offers, pushes,
playbooks, outcomes, decisions, next actions, and saved checkpoints. Treat git,
branches, pull requests, provider refs, and local wiring as the hidden memory
layer unless the operator asks for the plumbing.

Use the `vocabulary` block from `mb status --json --peek` when present. If
`core/vocabulary.md` says this business calls pushes drops, launches,
challenges, or promos, use that word in operator-facing prose while preserving
canonical paths, frontmatter, JSON keys, validator rules, and command names.

## Codex Start Workflow

This is the Codex-native port of `/mb-start`. It is a workflow, not a slash
command.

1. Run `mb status --json --peek` from the current working directory. Use the
   repo markers in that JSON to confirm this is the business repo. If the
   status report says this is not a Main Branch repo or the command is missing,
   ask for the business repo path instead of guessing.
2. Use the status JSON as the source of truth for
   readiness, drift, onboarding, update severity, GitHub facts, provider
   readiness, recent work, ranked actions, bets, pushes, vocabulary, and
   checkpoint state.
3. Run `mb start --json` when you need runtime handoff, repo-boundary, or
   adapter-readiness facts.
4. Run `mb doctor repair --plan` before recommending setup or repair. Quote the
   exact repair command from the plan. Ask before any write/apply command.
5. If status says an update is required, route to the cited `mb update` command
   and ask before running it. After an approved update, rerun
   `mb status --json --peek`.
6. Resume onboarding from status facts. In rich repos, read existing `core/`
   files before asking bounded missing-profile questions.
7. Present one clear business route: frame a bet, think through a decision,
   advance a push, draft a playbook, repair the repo, review provider
   readiness, save a checkpoint, or inspect a specific offer.

Use numbered lists for operator choices, with one active choice namespace per
turn. If the operator replies with an ambiguous number, ask what they meant
before acting.

## Routing Rules

- If `ranked_actions` has entries, lead with the first action, its reason, and
  the cited signal summaries.
- If readiness is blocked or drift has errors, handle repair before output
  work.
- If onboarding is incomplete, use the `onboarding.summary` and checklist from
  status instead of inventing a setup interview.
- If legacy `campaigns/` records exist, surface the doctor warning and suggest
  `mb migrate campaigns --plan` before creating new coordinated work.
- If the operator asks for publishing, spend, provider mutation, customer
  contact, migration, checkpoint creation, or file writes, plan first and ask
  for explicit approval.
- If the operator brings a live idea and it is unclear where it belongs, route
  by business meaning: offers are what the business may keep selling; bets are
  time-boxed wagers; pushes are coordinated execution; proof is evidence; and
  decisions explain durable changes.

## Business Folders

- `core/` - the business brain: offer, audience, voice, soul, proof, brand,
  strategy, operations, finance.
- `core/offers/` - per-offer specifics when this is a multi-offer repo.
- `core/proof/` - testimonials, typicality, and reusable proof.
- `research/` - dated notes from when you went looking.
- `decisions/` - dated choices, with rationale.
- `bets/` - operating bets with appetite, metric, target, and outcome.
- `pushes/` - coordinated pushes such as launches, drops, challenges, promos.
- `log/` - running activity log.
- `documents/` - anything that does not belong above.

## Connected Accounts

Never commit API keys, OAuth refresh tokens, service-account JSON, webhook
secrets, MCP tokens, or bearer tokens. Keep secrets in the runtime's local
config, an OS keychain, 1Password, `.env`, or another gitignored local file. If
a tool can spend money, publish, email, or mutate a customer account, verify it
is tethered to this repo and ask for approval before using it.

## Repo Owner

`@{{GH_USERNAME}}`
"""


def _read_template(name: str) -> str:
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(name)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        here = Path(__file__).resolve().parent / "_data" / "templates" / name
        if here.exists():
            return here.read_text(encoding="utf-8")
        return ""


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, val in mapping.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _markdown_h1(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    except OSError:
        return ""
    return ""


def _repo_owner(repo: Path) -> str:
    codeowners = repo / ".github" / "CODEOWNERS"
    try:
        for raw_line in codeowners.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            for part in parts[1:]:
                if part.startswith("@"):
                    return part.removeprefix("@")
    except OSError:
        pass
    agents = repo / AGENTS_RELATIVE_PATH
    try:
        lines = agents.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "your-gh-username"
    for line in lines:
        stripped = line.strip().strip("`")
        if stripped.startswith("@") and " " not in stripped:
            return stripped.removeprefix("@")
    return "your-gh-username"


def business_name(repo: str | Path) -> str:
    target = Path(repo).expanduser().resolve()
    for relative in ("CLAUDE.md", "AGENTS.md"):
        name = _markdown_h1(target / relative)
        if name and "instructions" not in name.lower():
            return name
    return target.name or "Business"


def render_agents_md(repo: str | Path, *, name: str = "", gh_username: str = "") -> str:
    target = Path(repo).expanduser().resolve()
    template = _read_template(AGENTS_TEMPLATE) or _DEFAULT_AGENTS
    mapping = {
        "BUSINESS_NAME": name.strip() or business_name(target),
        "GH_USERNAME": gh_username.strip() or _repo_owner(target),
    }
    return _render(template, mapping)


def agents_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / AGENTS_RELATIVE_PATH


def executable_status() -> dict[str, Any]:
    path = _which("codex")
    return {
        "found": bool(path),
        "path": path,
        "executable": "codex",
        "repair": "" if path else "Install Codex CLI before using the experimental Codex adapter.",
    }


def instructions_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    path = agents_path(target)
    expected = render_agents_md(target)
    exists = path.is_file()
    try:
        text = path.read_text(encoding="utf-8") if exists else ""
    except OSError as exc:
        text = ""
        read_error = str(exc)
    else:
        read_error = ""
    missing_commands = [command for command in REQUIRED_FACT_COMMANDS if command not in text]
    approval_ok = "explicit operator approval" in text
    slash_ok = "Do not pretend Claude" in text and "slash commands exist in Codex." in text
    fact_grounding_ok = bool(exists and not missing_commands and approval_ok and slash_ok)
    template_match = bool(exists and text == expected)
    current = fact_grounding_ok
    return {
        "ok": fact_grounding_ok,
        "exists": exists,
        "current": current,
        "template_match": template_match,
        "fact_grounding_ok": fact_grounding_ok,
        "path": AGENTS_RELATIVE_PATH,
        "absolute_path": str(path),
        "missing_fact_commands": missing_commands,
        "approval_boundary_ok": approval_ok,
        "codex_native_ok": slash_ok,
        "repair": ""
        if fact_grounding_ok
        else "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`.",
        "repair_command": "mb doctor repair --apply",
        "read_error": read_error,
        "safe_to_share": True,
    }


def readiness(repo: str | Path) -> dict[str, Any]:
    executable = executable_status()
    instructions = instructions_status(repo)
    ok = bool(executable["found"] and instructions["ok"])
    return {
        "ok": ok,
        "status": "ready" if ok else "needs_setup",
        "support_level": "experimental_cli_first_adapter",
        "executable": executable,
        "instructions": instructions,
        "fact_commands": list(REQUIRED_FACT_COMMANDS),
        "repair": "" if ok else instructions["repair"] or executable["repair"],
        "start_command": f"codex -C {shlex.quote(str(Path(repo).expanduser().resolve()))}",
        "smoke_command": (
            "codex exec --json --ephemeral --sandbox read-only "
            "-c 'approval_policy=\"never\"' "
            f"-C {shlex.quote(str(Path(repo).expanduser().resolve()))} "
            "'Start this Main Branch business day. Run only read-only mb checks "
            "and do not edit files.'"
        ),
        "safe_to_share": True,
    }


def write_agents_md(
    repo: str | Path,
    *,
    name: str = "",
    gh_username: str = "",
) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    path = agents_path(target)
    rendered = render_agents_md(target, name=name, gh_username=gh_username)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    changed = existing != rendered
    if changed:
        path.write_text(rendered, encoding="utf-8")
    return {
        "ok": True,
        "path": AGENTS_RELATIVE_PATH,
        "changed": changed,
        "status": instructions_status(target),
    }
