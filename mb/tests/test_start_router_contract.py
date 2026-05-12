"""Product-contract guards for the `/mb-start` business router."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
START_SKILL = REPO_ROOT / ".claude" / "skills" / "mb-start" / "SKILL.md"
ROUTER_REF = REPO_ROOT / ".claude" / "skills" / "mb-start" / "references" / "router-and-language.md"
UPDATE_REF = REPO_ROOT / ".claude" / "skills" / "mb-start" / "references" / "pull-engine-updates.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_mb_start_delegates_router_detail_without_bloating_skill_body() -> None:
    start = _read(START_SKILL)

    assert len(start.splitlines()) <= 500
    assert "references/router-and-language.md" in start
    assert "bookkeeping setup runs `mb books check`" in start
    assert "private admin repo" not in start.lower()


def test_router_contract_covers_books_save_sync_and_updates() -> None:
    router = _read(ROUTER_REF)

    required_phrases = [
        "saved checkpoint",
        "unsaved local work",
        "catch up with the shared repo",
        "reconcile local saved work",
        "proposal/review path",
        "ad hoc PR-instruction attachments",
        "Update strongly recommended",
        'Run `mb books check --repo "$REPO_PATH" --json`',
        "`storage_mode`",
        "hub registry",
        "child descriptor `.mainbranch/repo.json`",
        "topology role `finance` with visibility `restricted` or `local_only`",
        'generic "set up"',
    ]
    for phrase in required_phrases:
        assert phrase in router

    assert "noontide-admin" not in router.lower()


def test_start_router_no_longer_blindly_pulls_business_repo() -> None:
    start = _read(START_SKILL)
    update = _read(UPDATE_REF)

    combined = f"{start}\n{update}"
    assert 'git -C "$REPO_PATH" pull origin main' not in combined
    assert "blindly pull or rebase the business repo" in start
