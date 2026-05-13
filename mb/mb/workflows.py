"""Shared workflow source validation and snapshot rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_LOOP_SLUGS = {"sense", "decide", "ship", "reflect"}
REQUIRED_FRONTMATTER_FIELDS = {
    "name",
    "title",
    "description",
    "loops",
    "runtime_support",
    "required_mb_commands",
    "json_facts",
    "writes_business_files",
    "provider_mutation",
    "publishing_or_spend",
}
REQUIRED_SECTIONS = {
    "Intent And Triggers",
    "Required Mb Commands",
    "Required JSON Fact Paths",
    "Routing Rules",
    "Read Boundaries",
    "Write Boundaries",
    "Approval Gates",
    "Handoff Format",
    "Validation Commands",
    "Runtime-Specific Notes",
}
REQUIRED_RUNTIME_SUPPORT = {
    "claude_code": "supported_shell",
    "codex_cli": "experimental_shell",
}
MINIMUM_MB_COMMANDS = {
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
}
MINIMUM_JSON_FACTS = {
    "money_path",
    "money_path.objects.proof.quality",
    "content_strategy",
    "ranked_actions",
    "update",
    "readiness",
    "drift.items",
}
REQUIRED_SHELL_PHRASES_BY_WORKFLOW: dict[str, dict[str, str]] = {
    "mb-think": {
        "research-depth ladder": "research depth recommendation",
        "parallel research file pattern": "parallel research files",
        "decision writing": "decision",
        "codification": "codify",
        "public/private boundary": "public/private",
        "approval gates": "approval",
        "checkpoint approval": "checkpoint",
        "Codex slash-command boundary": "Do not tell Codex users to run Claude slash commands.",
    },
}
CODEX_FORBIDDEN_PHRASES_BY_WORKFLOW: dict[str, tuple[str, ...]] = {
    "mb-think": (
        "Run `/mb-think`",
        "Claude Code skills work in Codex",
        "slash-command parity",
    ),
}
PUBLIC_PRIVATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local user path", re.compile(r"/Users/[^\s`)]+")),
    ("private maintainer handle", re.compile(r"devonmeadows", re.I)),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Stripe key", re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{12,}")),
    (
        "inline secret assignment",
        re.compile(r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*\S+"),
    ),
)


@dataclass(frozen=True)
class WorkflowSource:
    """Parsed workflow source file."""

    path: Path
    frontmatter: dict[str, Any]
    body: str

    @property
    def name(self) -> str:
        return str(self.frontmatter["name"])

    @property
    def title(self) -> str:
        return str(self.frontmatter["title"])

    @property
    def required_mb_commands(self) -> list[str]:
        return [str(item) for item in self.frontmatter["required_mb_commands"]]

    @property
    def json_facts(self) -> list[str]:
        return [str(item) for item in self.frontmatter["json_facts"]]


class WorkflowValidationError(ValueError):
    """Raised when a workflow source cannot be rendered safely."""


def _split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    if not text.startswith("---\n"):
        return None, text, "missing YAML frontmatter"
    end = text.find("\n---", 4)
    if end == -1:
        return None, text, "unterminated YAML frontmatter"
    try:
        parsed = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        return None, text, f"frontmatter does not parse as YAML: {exc}"
    if not isinstance(parsed, dict):
        return None, text, "frontmatter must be a mapping"
    return parsed, text[end + len("\n---") :].lstrip("\n"), None


def _coerce_string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return [str(item) for item in value]


def _section_titles(body: str) -> set[str]:
    return {
        match.group("title").strip()
        for match in re.finditer(r"^## (?P<title>.+?)\s*$", body, flags=re.MULTILINE)
    }


def read_workflow(path: Path) -> WorkflowSource:
    """Read a workflow source without validating every contract rule."""

    text = path.read_text(encoding="utf-8")
    frontmatter, body, error = _split_frontmatter(text)
    if error is not None or frontmatter is None:
        raise WorkflowValidationError(error or "invalid workflow frontmatter")
    return WorkflowSource(path=path, frontmatter=frontmatter, body=body)


def validate_workflow(path: Path) -> list[str]:
    """Return workflow source validation errors."""

    errors: list[str] = []
    if not path.is_file():
        return [f"{path}: workflow source does not exist"]

    text = path.read_text(encoding="utf-8")
    frontmatter, body, frontmatter_error = _split_frontmatter(text)
    if frontmatter_error is not None or frontmatter is None:
        return [frontmatter_error or "invalid workflow frontmatter"]

    for field in sorted(REQUIRED_FRONTMATTER_FIELDS):
        if field not in frontmatter:
            errors.append(f"missing frontmatter field: {field}")

    loops = _coerce_string_list(frontmatter.get("loops"))
    if loops is None:
        errors.append("frontmatter field loops must be a list of strings")
    else:
        invalid_loops = sorted(set(loops) - VALID_LOOP_SLUGS)
        if invalid_loops:
            errors.append(f"frontmatter field loops has invalid slugs: {invalid_loops}")
        if len(set(loops)) != len(loops):
            errors.append("frontmatter field loops must not contain duplicate slugs")

    runtime_support = frontmatter.get("runtime_support")
    if not isinstance(runtime_support, dict):
        errors.append("frontmatter field runtime_support must be a mapping")
    else:
        for runtime, expected in REQUIRED_RUNTIME_SUPPORT.items():
            actual = runtime_support.get(runtime)
            if actual != expected:
                errors.append(f"runtime_support.{runtime} must be {expected!r}, got {actual!r}")

    commands = _coerce_string_list(frontmatter.get("required_mb_commands"))
    if commands is None:
        errors.append("frontmatter field required_mb_commands must be a list of strings")
    else:
        missing_commands = sorted(MINIMUM_MB_COMMANDS - set(commands))
        if missing_commands:
            errors.append(f"required_mb_commands missing minimum commands: {missing_commands}")

    facts = _coerce_string_list(frontmatter.get("json_facts"))
    if facts is None:
        errors.append("frontmatter field json_facts must be a list of strings")
    else:
        missing_facts = sorted(MINIMUM_JSON_FACTS - set(facts))
        if missing_facts:
            errors.append(f"json_facts missing minimum paths: {missing_facts}")

    for field in ("writes_business_files", "provider_mutation", "publishing_or_spend"):
        if field in frontmatter and not isinstance(frontmatter[field], bool):
            errors.append(f"frontmatter field {field} must be true or false")

    missing_sections = sorted(REQUIRED_SECTIONS - _section_titles(body))
    for section in missing_sections:
        errors.append(f"missing workflow section: {section}")

    errors.extend(public_private_boundary_errors(text))
    return errors


def load_workflow(path: Path) -> WorkflowSource:
    """Validate and read a workflow source."""

    errors = validate_workflow(path)
    if errors:
        raise WorkflowValidationError("; ".join(errors))
    return read_workflow(path)


def shell_drift_errors(workflow: WorkflowSource, shell_text: str) -> list[str]:
    """Return missing required commands or JSON facts for a rendered shell."""

    errors: list[str] = []
    for command in workflow.required_mb_commands:
        if not _has_exact_bullet_item(shell_text, command):
            errors.append(f"shell missing required mb command: {command}")
    for fact in workflow.json_facts:
        if not _has_exact_bullet_item(shell_text, fact):
            errors.append(f"shell missing required JSON fact path: {fact}")
    for label, phrase in REQUIRED_SHELL_PHRASES_BY_WORKFLOW.get(workflow.name, {}).items():
        if phrase.lower() not in shell_text.lower():
            errors.append(f"shell missing required workflow rule: {label}")
    return errors


def codex_shell_policy_errors(workflow: WorkflowSource, shell_text: str) -> list[str]:
    """Return Codex guidance phrases that would overclaim support."""

    errors: list[str] = []
    for phrase in CODEX_FORBIDDEN_PHRASES_BY_WORKFLOW.get(workflow.name, ()):
        if phrase.lower() in shell_text.lower():
            errors.append(f"Codex shell contains forbidden support phrase: {phrase}")
    return errors


def _has_exact_bullet_item(text: str, item: str) -> bool:
    expected = f"- `{item}`"
    return any(line.strip() == expected for line in text.splitlines())


def public_private_boundary_errors(text: str) -> list[str]:
    """Flag obvious private paths, tokens, or inline secret assignments."""

    errors: list[str] = []
    for label, pattern in PUBLIC_PRIVATE_PATTERNS:
        if pattern.search(text):
            errors.append(f"public/private boundary violation: {label}")
    return errors


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- `{item}`" for item in items)


def _display_path(path: Path) -> str:
    parts = path.parts
    if "workflows" in parts:
        index = parts.index("workflows")
        return Path(*parts[index:]).as_posix()
    return path.as_posix()


def render_claude_shell(workflow: WorkflowSource) -> str:
    """Render a Claude Code shell snapshot for a workflow source."""

    if workflow.name == "mb-think":
        return _render_think_claude_shell(workflow)
    return _render_start_money_path_claude_shell(workflow)


def _render_start_money_path_claude_shell(workflow: WorkflowSource) -> str:
    """Render the start-to-MoneyPath Claude shell snapshot."""

    output = f"""# Generated Claude Shell: {workflow.title}

Source workflow: `{_display_path(workflow.path)}`
Runtime support: `claude_code: supported_shell`

Use from `/mb-start` when the operator asks about revenue, offer readiness, the
next dollar, or the path to money. Preserve slash-command-native language and
handoff to `/mb-think` only when the next useful move is to clarify, decide,
research, or codify durable business truth.

This snapshot does not replace shipped `.claude/skills` prose.

## Required mb Commands

{_bullet_list(workflow.required_mb_commands)}

## Required JSON Fact Paths

{_bullet_list(workflow.json_facts)}

## Routing

1. Run hard gates first: required updates, broken repo wiring, repair blockers,
   validation blockers, relationship-health blockers, unsafe provider
   operations, private-data boundaries, and destructive-operation requests.
2. Start MoneyPath interpretation from `money_path.overall_level`,
   `money_path.overall_label`, the required `money_path.objects.*` paths, and
   `money_path.ranked_actions`.
3. Compare top-level `ranked_actions` with the MoneyPath bottleneck. If they
   disagree, name the gate or route taking priority.
4. Read supporting markdown only after deterministic facts identify the
   bottleneck.
5. Hand off to `/mb-think` with the MoneyPath snapshot when the next move is a
   decision, research pass, or codify write.

## Handoff Shape

```text
MoneyPath snapshot: overall <level> / <label>.
Bottleneck: <object or gate>.
Proof: <generic/specific/offer-linked/typicality/outcome-feedback facts>.
Offer and ladder: <structured facts and missing fields>.
CTA/channel/push: <connection facts>.
Outcome feedback: <instrumentation facts>.
Ranked actions: <agreement or disagreement with MoneyPath bottleneck>.
Recommended route: use /mb-think to <decision or write target>.
Approval needed before writes: yes.
```

Avoid subjective conversion judgment. Do not say an offer is bad, will convert,
or will not convert.
"""
    return output


def render_codex_shell(workflow: WorkflowSource) -> str:
    """Render a Codex CLI guidance snapshot for a workflow source."""

    if workflow.name == "mb-think":
        return _render_think_codex_shell(workflow)
    return _render_start_money_path_codex_shell(workflow)


def _render_start_money_path_codex_shell(workflow: WorkflowSource) -> str:
    """Render the start-to-MoneyPath Codex shell snapshot."""

    output = f"""# Generated Codex Workflow Guidance: {workflow.title}

Source workflow: `{_display_path(workflow.path)}`
Runtime support: `codex_cli: experimental_shell`

Codex remains experimental and CLI-first. This guidance is a generated snapshot
for validation; it does not mean `/mb-start` slash commands work inside Codex
and it does not claim selected Codex workflow support.

Start from deterministic `mb` facts before reading business markdown or giving
path-to-money advice.

## Required mb Commands

{_bullet_list(workflow.required_mb_commands)}

## Required JSON Fact Paths

{_bullet_list(workflow.json_facts)}

## Codex Route

1. Use the business repo `AGENTS.md` bootstrap posture: read facts first, keep
   writes approval-gated, and translate git/provider details into business
   language.
2. Run hard gates before MoneyPath interpretation: required updates, repair
   blockers, readiness blockers, unsafe provider operations, private-data
   boundaries, and destructive-operation requests.
3. Use `money_path`, `money_path.objects.proof.quality`, `content_strategy`,
   `ranked_actions`, `update`, `readiness`, and `drift.items` as cited facts.
4. If a thinking/codification step is needed, propose the route in Codex-native
   language instead of pretending Claude slash commands are available.
5. Ask before writing business files, saving checkpoints, opening public
   issues, publishing, mutating providers, spending money, or contacting
   customers.

## Handoff Shape

```text
MoneyPath snapshot: overall <level> / <label>.
Bottleneck: <object or gate>.
Proof: <generic/specific/offer-linked/typicality/outcome-feedback facts>.
Offer and ladder: <structured facts and missing fields>.
CTA/channel/push: <connection facts>.
Outcome feedback: <instrumentation facts>.
Ranked actions: <agreement or disagreement with MoneyPath bottleneck>.
Recommended route: clarify or codify <decision or write target> after approval.
Approval needed before writes: yes.
```

Runtime smoke is required before docs say this selected workflow is supported
or available in Codex.
"""
    return output


def _render_think_claude_shell(workflow: WorkflowSource) -> str:
    """Render a Claude Code shell snapshot for the thinking workflow."""

    output = f"""# Generated Claude Shell: {workflow.title}

Source workflow: `{_display_path(workflow.path)}`
Runtime support: `claude_code: supported_shell`

Use from `/mb-think` when the operator asks to research, decide, figure out,
compare, codify, sharpen an offer, or turn learning into durable business
truth. Preserve slash-command-native language for Claude Code only.

This snapshot does not replace shipped `.claude/skills/mb-think/SKILL.md`.

## Required mb Commands

{_bullet_list(workflow.required_mb_commands)}

## Required JSON Fact Paths

{_bullet_list(workflow.json_facts)}

## Routing

1. Run hard gates first: required updates, broken repo wiring, repair blockers,
   validation blockers, unsafe provider operations, private-data boundaries,
   and destructive-operation requests.
2. Read deterministic `mb` facts before raw markdown. Then read only relevant
   `core/`, `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and `docs/`
   files.
3. Give a Research Depth Recommendation from 0-5 before outside research:
   memory, repo context, lightweight public/manual research, multi-source
   synthesis, structured approved-source collection, or high-resolution market
   analysis.
4. Use parallel research files for multiple sources, then synthesize in the
   main thread. Each source file records source quality, access/permission,
   caveats, promotion limits, and public/private handling.
5. Write a decision when durable business truth changes. Codify only after the
   operator accepts the direction.
6. Ask for approval before creating or editing business files, promoting
   research into core truth, using structured collection, or saving a
   checkpoint.

## Handoff Shape

```text
Thinking task: <research, decision, codify, or full flow>.
Repo facts read: <status/start/connect/repair/checkpoint facts used>.
Current bottleneck: <MoneyPath, content strategy, readiness, drift, or user question>.
Research depth recommendation: <0-5>, because <reason>.
Useful sources: <repo files, public/manual sources, approved providers, or operator input>.
Stop condition: <what is enough signal>.
Durable targets: <research/, decisions/, core/, bets/, pushes/, log/, or documents/>.
Approval needed before writes: yes.
```

Use business language. Do not say an offer is bad, will convert, or will not
convert. Do not tell Codex users to run Claude slash commands.
"""
    return output


def _render_think_codex_shell(workflow: WorkflowSource) -> str:
    """Render Codex CLI guidance for the thinking workflow."""

    output = f"""# Generated Codex Workflow Guidance: {workflow.title}

Source workflow: `{_display_path(workflow.path)}`
Runtime support: `codex_cli: experimental_shell`

Codex remains experimental and CLI-first. This guidance tells Codex how to
treat a natural-language request as a Main Branch thinking task through
`AGENTS.md` posture and deterministic `mb` facts. It does not claim Claude
Code slash commands work inside Codex or that all Main Branch workflows are
available in Codex.

## Required mb Commands

{_bullet_list(workflow.required_mb_commands)}

## Required JSON Fact Paths

{_bullet_list(workflow.json_facts)}

## Codex Route

1. Use the business repo `AGENTS.md` bootstrap posture: read facts first, keep
   writes approval-gated, and translate git/provider details into business
   language.
2. Run hard gates first: required updates, repair blockers, readiness
   blockers, unsafe provider operations, private-data boundaries, and
   destructive-operation requests.
3. Read deterministic `mb` facts before raw markdown. Then read only relevant
   `core/`, `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and `docs/`
   files.
4. Give a Research Depth Recommendation from 0-5 before outside research:
   memory, repo context, lightweight public/manual research, multi-source
   synthesis, structured approved-source collection, or high-resolution market
   analysis.
5. Use parallel research files for multiple sources, then synthesize in the
   main thread. Each source file records source quality, access/permission,
   caveats, promotion limits, and public/private handling.
6. Write a decision when durable business truth changes. Codify only after the
   operator accepts the direction.
7. Ask for approval before creating or editing business files, promoting
   research into core truth, using structured collection, opening public
   issues, publishing, mutating providers, spending money, contacting
   customers, or saving a checkpoint.

## Handoff Shape

```text
Thinking task: <research, decision, codify, or full flow>.
Repo facts read: <status/start/connect/repair/checkpoint facts used>.
Current bottleneck: <MoneyPath, content strategy, readiness, drift, or user question>.
Research depth recommendation: <0-5>, because <reason>.
Useful sources: <repo files, public/manual sources, approved providers, or operator input>.
Stop condition: <what is enough signal>.
Durable targets: <research/, decisions/, core/, bets/, pushes/, log/, or documents/>.
Approval needed before writes: yes.
```

Do not tell Codex users to run Claude slash commands. Runtime smoke is required
before docs say this selected workflow is supported or available in Codex.
"""
    return output
