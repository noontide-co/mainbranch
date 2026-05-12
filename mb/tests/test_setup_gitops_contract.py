"""Product-contract guards for `/mb-setup` save and review guidance."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_SKILL = REPO_ROOT / ".claude" / "skills" / "mb-setup" / "SKILL.md"
SETUP_REFERENCES = REPO_ROOT / ".claude" / "skills" / "mb-setup" / "references"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _setup_gitops_text() -> str:
    paths = [
        SETUP_SKILL,
        SETUP_REFERENCES / "git-workflow.md",
        SETUP_REFERENCES / "migration-multi-offer.md",
    ]
    return "\n".join(_read(path) for path in paths)


def test_mb_setup_uses_checkpoint_first_save_guidance() -> None:
    text = _setup_gitops_text()

    required_phrases = [
        "mb checkpoint --plan --json",
        'mb checkpoint --validate "[added] initial business repo foundation" --json',
        'mb checkpoint --message "[added] initial business repo foundation" --yes',
        'mb checkpoint --validate "[updated] offer structure" --json',
        "Save only after operator approval",
        "Pull requests are proposals or review conversations",
        "The planned `mb publish --plan` command",
        "packaged publish",
        "not shipped yet",
        "and the saved checkpoint",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_mb_setup_does_not_teach_stale_business_repo_save_style() -> None:
    text = _setup_gitops_text()

    stale_phrases = [
        "Co-Authored-By",
        "[init] Bootstrap business repo",
        "[type] Brief description",
        "[refactor] Migrate to multi-offer structure",
        "Always use HEREDOC",
        "and commit",
    ]
    for phrase in stale_phrases:
        assert phrase not in text

    assert "git commit" not in text
    assert "git add" not in text
