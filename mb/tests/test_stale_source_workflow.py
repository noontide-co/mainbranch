"""Contract checks for stale-source cleanup guidance."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
THINK_SKILL = REPO_ROOT / ".claude" / "skills" / "mb-think" / "SKILL.md"
STALE_REF = REPO_ROOT / ".claude" / "skills" / "mb-think" / "references" / "stale-source-cleanup.md"
CODIFY_REF = REPO_ROOT / ".claude" / "skills" / "mb-think" / "references" / "codify-phase.md"
ROUTER_REF = REPO_ROOT / ".claude" / "skills" / "mb-start" / "references" / "router-and-language.md"
THINK_WORKFLOW = REPO_ROOT / "workflows" / "mb-think" / "workflow.md"
SMOKE_FIXTURE = REPO_ROOT / "mb" / "tests" / "fixtures" / "stale-source-cleanup" / "manual-smoke.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_stale_source_cleanup_is_routed_from_start_to_think() -> None:
    think = _read(THINK_SKILL)
    router = _read(ROUTER_REF)
    workflow = _read(THINK_WORKFLOW)

    assert "retire stale source" in think
    assert "stale-source-cleanup.md" in think
    assert '| "add context", "enrich", "I have new info" | Codify |' in think
    assert "obsolete claim" in think
    assert "Stale source, claim, or angle cleanup" in router
    assert "Route to `/mb-think` stale-source cleanup" in router
    assert "stale source" in workflow
    assert "obsolete claim" in workflow


def test_stale_source_cleanup_reference_covers_reconcile_decision_checkpoint_loop() -> None:
    text = _read(STALE_REF)
    codify = _read(CODIFY_REF)

    required = [
        "Name the stale item",
        "Name the replacement truth",
        "Find downstream usage",
        "Record a decision when truth changes",
        "Codify after approval",
        "Mark the decision codified",
        "Verify read-back",
        "Checkpoint",
        "Do not require the operator to inspect a git diff",
        "ingestion/privacy rail",
        "core/offers/<slug>/offer.md",
        "decisions/YYYY-MM-DD-retire-<slug>.md",
        "status: codified",
        "[updated] offer truth after stale-source cleanup",
    ]
    for phrase in required:
        assert phrase in text

    assert "stale-source-cleanup.md" in codify


def test_stale_source_manual_smoke_fixture_covers_full_acceptance_path() -> None:
    text = _read(SMOKE_FIXTURE)

    required = [
        "legacy same-day guarantee",
        "Run `mb status --json --peek`",
        "Search active and source files",
        "Add a stale note",
        "status: accepted",
        "Remove the stale claim",
        "Mark `core/proof/angles/legacy-speed-angle.md` as retired",
        "status: codified",
        "Run `mb checkpoint --plan --json`",
        "[updated] offer truth after stale-source cleanup",
        "business-readable",
    ]
    for phrase in required:
        assert phrase in text
