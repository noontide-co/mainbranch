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
REQUIRED_LIFECYCLE_GUIDANCE = (
    "## Codex Lifecycle Workflow Index",
    "## Codex Status Workflow",
    "## Codex Think Route",
    "mb checkpoint --plan --json",
    "Do not create `.agents/skills`",
    "do not claim these workflows are ported to",
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
activity, provider signals, recent work, MoneyPath, ranked actions, bets,
pushes, and checkpoint state. Do not replace those facts with ad hoc shell
inspection unless `mb` says a section is unavailable or the command itself is
missing.

Read-only commands can be run without asking first. Commands that write files,
refresh local runtime wiring, update packages, migrate business files, create
checkpoints, publish, spend money, contact customers, email, or mutate provider
accounts require explicit operator approval before applying.

Do the technical work in technical commands, then translate the result back into
business-owner language. Speak first in terms of bets, goals, offers, pushes,
playbooks, outcomes, decisions, next actions, and saved checkpoints. Treat git,
branches, pull requests, provider refs, and local wiring as the hidden memory
layer unless the operator asks for the plumbing.

Default translations for normal owner answers:
- `git is clean`, `repo is clean`, `working tree clean`, or `working tree: clean`
  -> nothing unsaved locally;
- `branch main`, `branch: main`, or `current branch: main` -> current business
  folder or workspace;
- `No GitHub origin remote` or `No origin remote` -> no connected GitHub backup
  or shared task source;
- `PR/issue facts` or `PR and issue facts` -> GitHub task and proposal context.

When finishing first-run setup, lead with the owner outcome before the receipt:
created, saved, synced to GitHub when requested, and ready to open in Claude
Code. Put commands, remotes, branches, validation checks, and local wiring in a
short technical receipt after that outcome.

Use the `vocabulary` block from `mb status --json --peek` when present. If
`core/vocabulary.md` says this business calls pushes drops, launches,
challenges, or promos, use that word in operator-facing prose while preserving
canonical paths, frontmatter, JSON keys, validator rules, and command names.

## Codex Lifecycle Workflow Index

This tracked `AGENTS.md` file is the current Codex lifecycle discovery surface.
It is owned by `mb init`, `mb onboard`, `mb doctor repair`, and the operator.
Keep it compact: route to lifecycle workflows and `mb` facts here, but do not
duplicate the full Main Branch skill tree.

Do not create `.agents/skills`, Codex plugin manifests, generated runtime
files, or symlinked Claude skills unless a future `mb` command or issue says
that surface is supported for this repo.

Use this index to map natural Codex requests:

- **Start the day / what next / get oriented:** use the Codex Start Workflow
  below. Run `mb status --json --peek` first, then `mb start --json` when
  runtime handoff or adapter-readiness facts matter.
- **Inspect status / what changed / what is stale:** use the Codex Status
  Workflow below. Answer from `ranked_actions`, `since_last_check`, `journal`,
  `money_path`, `content_strategy`, `integrations`, `readiness`, and
  `drift.items`.
- **Think / research / decide / codify:** use the Codex Think Route below.
  Start from `mb` facts, choose a research depth, and ask before writing
  durable business files.
- **Site, ads, organic production, provider mutation, publishing, spend,
  domains, or customer contact:** do not claim these workflows are ported to
  Codex. Use read-only `mb` facts for planning and ask before any action.

## Codex Start Workflow

This is the Codex-native port of `/mb-start`. It is a workflow, not a slash
command.

1. Run `mb status --json --peek` from the current working directory. Use the
   repo markers in that JSON to confirm this is the business repo. If the
   status report says this is not a Main Branch repo or the command is missing,
   ask for the business repo path instead of guessing.
2. Use the status JSON as the source of truth for
   readiness, drift, onboarding, update severity, GitHub facts, provider
   readiness, recent work, MoneyPath, ranked actions, bets, pushes,
   vocabulary, and checkpoint state.
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

## Codex Status Workflow

This is the Codex-native status route. It is a workflow, not a slash command.

1. Run `mb status --json --peek`.
2. Treat the JSON as the source of truth for setup, update, drift, GitHub,
   onboarding, integrations, bets, recent work, since-last-check,
   `content_strategy`, `money_path`, vocabulary, checkpoint state, and
   `ranked_actions`.
3. Lead with the top `ranked_actions` entry when the operator asks what to do
   next. Include the reason and cited signal summaries.
4. For "what changed?" answer from `since_last_check.journal` first, then
   top-level `journal` for recent context.
5. For provider questions, read `integrations` first. Run `mb connect plan` or
   `mb connect doctor --json` only when the operator needs choices or repair
   commands.
6. Use `money_path` for customer progress, offer, proof, CTA, channel, push,
   playbook, page readiness, and outcome feedback questions. Keep language
   evidence-based: legible, supported, connected, instrumented.
7. Use `content_strategy` for content strategy health, layered channel/account
   files, stale platform rules, or disconnected content layers.

Do not mutate the last-check marker unless the operator explicitly says this is
the daily check-in and wants it recorded.

## Codex Think Route

This is Codex-native guidance for the existing `mb-think` shared workflow
source. It is not a slash command, and it does not mean all Main Branch skills
work in Codex.

Use it when the operator asks to think through an offer, research a market,
compare providers, make a decision, or codify what was learned.

Before advice, run the read-only facts that fit the situation:

```bash
mb status --json --peek
mb start --json
mb doctor repair --plan
```

If the task touches provider readiness, run `mb connect doctor --json`. Before
recommending a saved checkpoint, run `mb checkpoint --plan --json`. These
commands provide facts and plans; they do not authorize writes.

Choose the smallest honest research depth:

- Level 0: operator memory is enough for a low-risk move.
- Level 1: existing repo context and `mb` facts are enough.
- Level 2: lightweight public or operator-provided research is needed.
- Level 3: multi-source synthesis is needed.
- Level 4: structured approved-source collection is justified.
- Level 5: high-resolution market analysis or field evidence is needed.

Read only the business files needed for the question: `core/`, `research/`,
`decisions/`, `bets/`, `pushes/`, `log/`, and `documents/`. Do not inspect
secrets, raw provider exports, raw finance/legal records, customer/member
records, private DMs, gated communities, local runtime settings, or credentials
unless the operator gives explicit permission and the source belongs in the
business repo.

Ask before creating, editing, moving, deleting, archiving, codifying, or
checkpointing business files. Ask before publishing, opening a public issue,
submitting a proposal, spending money, mutating provider state, or contacting
customers.

## Routing Rules

- If `ranked_actions` has entries, lead with the first action, its reason, and
  the cited signal summaries.
- Use `money_path` when the next move depends on customer progress, offer,
  proof, CTA, channel, push, playbook, page readiness, or outcome feedback.
  Keep the language evidence-based: legible, supported, connected,
  instrumented.
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
- `core/proof/` - testimonials, typicality, and reusable proof. Use
  structured permission and offer-link fields when proof should be detectable
  by `mb status`.
- `core/content-strategy.md` - business-level content strategy and index.
- `core/marketing/` - optional distribution, channel, and account strategy.
- `core/people/` - optional founder/person voice source material, beliefs,
  stories, and proof.
- `research/` - dated notes from when you went looking.
- `decisions/` - dated choices, with rationale.
- `bets/` - operating bets with appetite, metric, target, and outcome.
- `pushes/` - coordinated pushes such as launches, drops, challenges, promos.
- `log/` - running activity log.
- `documents/` - anything that does not belong above.

Use `core/content-strategy.md` as the default solo-operator content strategy.
When the business needs more layers, read or write
`core/marketing/distribution-strategy.md`,
`core/marketing/channels/<channel>.md`,
`core/marketing/accounts/<platform>-<account>.md`, and
`core/people/<person>.md`. Weekly content planning should reference those files,
then put specific execution in `pushes/` and results in `log/`.

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
    missing_lifecycle_guidance = [
        phrase for phrase in REQUIRED_LIFECYCLE_GUIDANCE if phrase not in text
    ]
    lifecycle_discovery_ok = bool(exists and not missing_lifecycle_guidance)
    fact_grounding_ok = bool(
        exists and not missing_commands and approval_ok and slash_ok and lifecycle_discovery_ok
    )
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
        "missing_lifecycle_guidance": missing_lifecycle_guidance,
        "lifecycle_discovery_ok": lifecycle_discovery_ok,
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
