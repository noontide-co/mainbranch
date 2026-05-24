"""Regression guards for first-run setup intent guidance."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _setup_section(text: str) -> str:
    start = text.index("setup intent")
    return text[start : start + 1400]


def test_beginner_setup_uses_owner_friendly_setup_prompt() -> None:
    text = _read("docs/beginner-setup.md")
    normalized = _normalize(text)

    required = [
        "## Setup with an agent",
        "Open or select the business folder in Claude Code or Codex.",
        "I want to set up Main Branch for this business in this folder.",
        "Treat this as setup intent, not as a document to save.",
        "check whether `mb` is available",
        "Use this folder as the business folder unless I say otherwise.",
        "GitHub CLI is installed, authenticated, and signed in to the account I expect",
        "GitHub does not need to cost anything",
        "the business brain has cloud backup and readable saved history",
        "AI tools with GitHub connectors can read the business brain",
        "Do not save that prompt as a markdown document.",
        "A checkpoint is an approved saved point in the business history.",
        "Main Branch updates change the engine and skills",
        "system-architecture.md#repo-topology",
    ]
    for phrase in required:
        assert phrase in normalized
    assert "mb onboard --github --push" not in normalized


def test_runtime_guidance_routes_pasted_setup_to_onboarding() -> None:
    for relative in (
        "mb/mb/_data/templates/CLAUDE.md.tmpl",
        "mb/mb/_data/templates/AGENTS.md.tmpl",
    ):
        text = _read(relative)
        normalized = _normalize(text)
        assert "setup intent" in normalized
        assert "not as a document to save" in normalized
        assert "mb --version" in normalized
        assert "pipx install mainbranch" in normalized
        assert "mb onboard --help" in normalized
        assert "mb onboard plan" not in _normalize(_setup_section(text))
        assert "gh auth status" in normalized
        assert "gh api user --jq .login" in normalized
        assert "GitHub is strongly recommended" in normalized
        assert "connector-friendly copy of the business brain" in normalized
        assert "mb onboard --github <owner/repo> --push" in normalized
        assert "mb onboard --github --push" not in normalized


def test_setup_skill_keeps_onboard_plan_after_approval() -> None:
    text = _read(".claude/skills/mb-setup/SKILL.md")
    normalized = _normalize(text)

    assert "setup intent" in normalized
    assert "not as a document to save" in normalized
    assert "mb onboard --help" in normalized
    assert "Use `mb onboard plan` only after the operator approves" in normalized
    assert "After the operator approves saving setup progress" in normalized
    assert "mb onboard --github <owner/repo> --push" in normalized
    assert "mb onboard --github --push" not in normalized


def test_readme_points_empty_folder_users_to_bootstrap() -> None:
    text = _read("README.md")
    normalized = _normalize(text)

    assert "Start with the folder that should become your business brain" in normalized
    assert "Tell the agent what you are setting up" in normalized
    assert "not save your note as another document" in normalized
    assert "GitHub backup/sync is strongly recommended" in normalized
    assert "AI tools with GitHub connectors can read" in normalized
    assert "gh auth status" in normalized
    assert "gh api user --jq .login" in normalized
    assert "mb onboard --github --push" not in normalized
