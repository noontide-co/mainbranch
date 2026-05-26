"""Guard current agent guidance from retired Main Branch taxonomy."""

from pathlib import Path

from mb import codex as codex_mod

REPO_ROOT = Path(__file__).resolve().parents[2]

CURRENT_GUIDANCE_FILES = [
    *sorted((REPO_ROOT / ".claude" / "skills").rglob("*.md")),
    *sorted((REPO_ROOT / ".claude" / "reference" / "business-primitives").rglob("*.md")),
    REPO_ROOT / "docs" / "operator-loops.md",
    REPO_ROOT / "docs" / "roadmap.md",
    REPO_ROOT / "mb" / "README.md",
]

PRIMARY_SKILL_FILES = sorted((REPO_ROOT / ".claude" / "skills").glob("*/SKILL.md"))

GENERATED_GUIDANCE_FILES = [
    REPO_ROOT / "mb" / "mb" / "_data" / "templates" / "CLAUDE.md.tmpl",
    REPO_ROOT / "mb" / "mb" / "_data" / "templates" / "AGENTS.md.tmpl",
]

RETIRED_STRUCTURAL_TERMS = (
    "reference/core",
    "reference/offers",
    "reference/domain",
    "campaigns/",
    "outputs/",
    "ship-bet",
    "weekly-review",
)

RETIRED_REPO_STRUCTURE_TERMS = (
    "reference/core",
    "reference/offers",
    "reference/domain",
)

EXPLICIT_LEGACY_CONTEXT = (
    "legacy",
    "old ",
    "older ",
    "migration",
    "migrate",
    "doctor",
    "repair",
    "compatibility",
    "historical",
    "retired",
)

FORBIDDEN_ALIAS_PHRASES = (
    "compatibility bridges",
    "compatibility aliases",
    "treat them as aliases",
    "aliases, not duplicate",
    'test -d "core" || test -d "reference/core"',
)


def _window(lines: list[str], line_number: int) -> str:
    start = max(0, line_number - 3)
    end = min(len(lines), line_number + 2)
    return " ".join(lines[start:end]).lower()


def _generated_guidance_texts() -> list[tuple[str, str]]:
    rendered_global_skills = [
        (
            f"render_codex_global_skill_md:{skill_name}",
            codex_mod.render_codex_global_skill_md(skill_name),
        )
        for skill_name in codex_mod.CODEX_GLOBAL_SKILL_NAMES
    ]
    return [
        *[
            (str(path.relative_to(REPO_ROOT)), path.read_text())
            for path in GENERATED_GUIDANCE_FILES
        ],
        ("render_agents_md", codex_mod.render_agents_md(REPO_ROOT)),
        *rendered_global_skills,
    ]


def test_current_guidance_uses_retired_paths_only_in_explicit_legacy_context() -> None:
    violations: list[str] = []
    for path in CURRENT_GUIDANCE_FILES:
        text = path.read_text()
        lines = text.splitlines()
        for index, line in enumerate(lines, start=1):
            lowered = line.lower()
            if not any(term in lowered for term in RETIRED_STRUCTURAL_TERMS):
                continue
            context = _window(lines, index)
            if not any(marker in context for marker in EXPLICIT_LEGACY_CONTEXT):
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{index}: {line.strip()}")

    assert violations == []


def test_primary_skills_do_not_name_retired_repo_structure() -> None:
    violations: list[str] = []
    for path in PRIMARY_SKILL_FILES:
        text = path.read_text().lower()
        for term in RETIRED_REPO_STRUCTURE_TERMS:
            if term in text:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}: {term}")

    assert violations == []


def test_current_guidance_does_not_teach_legacy_aliases() -> None:
    violations: list[str] = []
    for path in CURRENT_GUIDANCE_FILES + GENERATED_GUIDANCE_FILES:
        text = path.read_text().lower()
        for phrase in FORBIDDEN_ALIAS_PHRASES:
            if phrase in text:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}: {phrase}")

    assert violations == []


def test_generated_guidance_omits_retired_structural_terms() -> None:
    violations: list[str] = []
    for name, rendered_text in _generated_guidance_texts():
        text = rendered_text.lower()
        for term in RETIRED_STRUCTURAL_TERMS:
            if term in text:
                violations.append(f"{name}: {term}")

    assert violations == []
