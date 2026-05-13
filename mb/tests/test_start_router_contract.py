"""Product-contract guards for the `/mb-start` business router."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
START_SKILL = REPO_ROOT / ".claude" / "skills" / "mb-start" / "SKILL.md"
ROUTER_REF = REPO_ROOT / ".claude" / "skills" / "mb-start" / "references" / "router-and-language.md"
UPDATE_REF = REPO_ROOT / ".claude" / "skills" / "mb-start" / "references" / "pull-engine-updates.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    lines = [line.removeprefix("> ").strip() for line in text.splitlines()]
    return " ".join(" ".join(lines).split())


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


def test_start_router_routes_money_intent_from_moneypath_facts() -> None:
    start = _read(START_SKILL)
    router = _read(ROUTER_REF)
    normalized_start = _normalize(start)
    normalized_router = _normalize(router)

    assert "Parse the full JSON once" in normalized_start
    assert "do not slice status output with `head` or `sed`" in normalized_start

    required_phrases = [
        "Path to money, revenue, offer readiness",
        "path to money",
        "next dollar",
        "offer readiness",
        "Keep hard gates first",
        "Required update, broken install/runtime/wiring, repair blockers, validation "
        "blockers, relationship health blockers, playbook health blockers, and unsafe "
        "provider/private-data blockers all win before MoneyPath routing.",
        "`money_path.overall_level`",
        "`money_path.overall_label`",
        "`money_path.objects.offer`",
        "`money_path.objects.proof`",
        "`money_path.objects.product_ladder`",
        "`money_path.objects.cta_path`",
        "`money_path.objects.channel_strategy`",
        "`money_path.objects.active_push`",
        "`money_path.objects.outcome_feedback_loop`",
        "`money_path.ranked_actions`",
        "without conversion judgment",
        "Explain whether top-level `ranked_actions` agree with the MoneyPath bottleneck",
        "include a MoneyPath snapshot in the handoff",
        "Product ladder is stated but has no clear paid entry step",
        "Channel strategy exists, but no active push is attached",
        "Outcome feedback loop is missing",
        "Recommended route: use `/mb-think`",
    ]
    for phrase in required_phrases:
        assert phrase in normalized_router

    assert "Your offer is bad." in normalized_router
    assert "This will not convert." in normalized_router
    assert "This will convert." in normalized_router
    assert "The business is weak." in normalized_router
    assert "This is ready to win." in normalized_router


def test_start_router_no_longer_blindly_pulls_business_repo() -> None:
    start = _read(START_SKILL)
    update = _read(UPDATE_REF)

    combined = f"{start}\n{update}"
    assert 'git -C "$REPO_PATH" pull origin main' not in combined
    assert "blindly pull or rebase the business repo" in start
