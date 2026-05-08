"""Static guards for user-facing slash-command references."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MAIN_BRANCH_COMMAND_RE = re.compile(
    r"(?<![\w/.\->])/"
    r"(?P<name>mb-[a-z0-9-]+|newsletter|ads|bet|end|help|organic|pull|setup|site|start|status|think|update|vsl|wiki)"
    r"(?=$|[`<\s,).:;])"
)
GUIDED_ORCHESTRATION_FORMS = ("/mb-start launch",)
GUIDED_ORCHESTRATION_CONTEXT_MARKERS = (
    "guided",
    "orchestration",
    "skill orchestration",
    "guided skill",
    "follows the same contract",
)


def _bundled_slash_commands() -> set[str]:
    skills_dir = REPO_ROOT / ".claude" / "skills"
    return {
        skill_dir.name
        for skill_dir in skills_dir.iterdir()
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()
    }


def _scan_paths() -> list[Path]:
    docs = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "CLAUDE.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "mb" / "mb" / "_data" / "templates" / "CLAUDE.md.tmpl",
    ]
    docs.extend(
        path
        for path in sorted((REPO_ROOT / "docs").rglob("*.md"))
        # Historical plans and dogfood reports can mention retired commands as
        # evidence. Live guidance is scanned recursively.
        if "prd" not in path.relative_to(REPO_ROOT / "docs").parts
        and "reports" not in path.relative_to(REPO_ROOT / "docs").parts
    )
    docs.extend(sorted((REPO_ROOT / "templates").rglob("*.md")))
    docs.extend(sorted((REPO_ROOT / ".claude" / "playbooks").rglob("*.md")))
    docs.extend(sorted((REPO_ROOT / ".claude" / "reference").rglob("*.md")))
    docs.extend(sorted((REPO_ROOT / ".claude" / "skills").rglob("*.md")))
    return [path for path in docs if path.is_file()]


def _line_context(lines: list[str], index: int) -> str:
    return " ".join(lines[max(0, index - 2) : min(len(lines), index + 3)]).lower()


def test_runtime_docs_reference_only_bundled_main_branch_slash_commands() -> None:
    bundled = _bundled_slash_commands()
    failures: list[str] = []

    for path in _scan_paths():
        rel = path.relative_to(REPO_ROOT)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in MAIN_BRANCH_COMMAND_RE.finditer(line):
                command_name = match.group("name")
                if command_name in bundled:
                    continue
                failures.append(f"{rel}:{line_number}: /{command_name} is not a bundled skill")

    assert failures == []


def test_runtime_docs_mark_mb_start_launch_as_guided_skill_orchestration() -> None:
    failures: list[str] = []

    for path in _scan_paths():
        rel = path.relative_to(REPO_ROOT)
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not any(form in line for form in GUIDED_ORCHESTRATION_FORMS):
                continue
            context = _line_context(lines, index)
            if not any(marker in context for marker in GUIDED_ORCHESTRATION_CONTEXT_MARKERS):
                failures.append(
                    f"{rel}:{index + 1}: /mb-start launch must be framed as "
                    "guided skill orchestration"
                )

    assert failures == []
