"""Regression guards for first-run setup intent guidance."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def test_beginner_setup_uses_folder_first_bootstrap_prompt() -> None:
    text = _read("docs/beginner-setup.md")
    normalized = _normalize(text)

    required = [
        "## Folder-First Bootstrap",
        "I want to set up Main Branch for this business in the current folder.",
        "Treat this as setup intent, not as a document to save.",
        "check whether `mb` is available",
        "Use this folder as the business repo location unless I say otherwise.",
        "GitHub CLI is installed, authenticated, and signed in to the account I expect",
        "GitHub is strongly recommended",
        "connector-friendly copy of the business brain",
        "Main Branch can start locally without GitHub",
        "Do not save that prompt as a markdown document.",
        "A checkpoint is an approved saved point in the business history.",
        "Main Branch updates change the engine and skills",
        "system-architecture.md#repo-topology",
    ]
    for phrase in required:
        assert phrase in normalized


def test_runtime_guidance_routes_pasted_setup_to_onboarding() -> None:
    for relative in (
        "mb/mb/_data/templates/CLAUDE.md.tmpl",
        "mb/mb/_data/templates/AGENTS.md.tmpl",
        ".claude/skills/mb-setup/SKILL.md",
    ):
        text = _read(relative)
        normalized = _normalize(text)
        assert "setup intent" in normalized
        assert "not as a document to save" in normalized
        assert "mb --version" in normalized
        assert "pipx install mainbranch" in normalized
        assert "mb onboard" in normalized
        assert "gh auth status" in normalized
        assert "gh api user --jq .login" in normalized
        assert "GitHub is strongly recommended" in normalized
        assert "connector-friendly copy of the business brain" in normalized


def test_readme_points_empty_folder_users_to_bootstrap() -> None:
    text = _read("README.md")
    normalized = _normalize(text)

    assert "Start with the folder that should become your business brain" in normalized
    assert "folder-first bootstrap" in normalized
    assert "setup intent, not a document to save" in normalized
    assert "GitHub backup/sync is strongly recommended" in normalized
    assert "AI tools with GitHub connectors can read" in normalized
    assert "gh auth status" in normalized
    assert "gh api user --jq .login" in normalized
