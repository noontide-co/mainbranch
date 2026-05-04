"""Deterministic next-action ranker."""

from __future__ import annotations

from mb import ranker


def _base_report() -> dict[str, object]:
    return {
        "repo": {"looks_like_mainbranch_repo": True, "missing_markers": []},
        "git": {"inside_work_tree": True, "dirty": False, "dirty_count": 0, "dirty_files": []},
        "update": {
            "severity": "current",
            "command": "",
            "reason": "",
            "installed": "0.2.6",
            "latest": "0.2.6",
        },
        "runtime": {
            "skill_wiring": {"ok": True, "repair": "", "missing": []},
            "claude_code": {"found": True, "repair": ""},
        },
        "onboarding": {"summary": {"status": "ready"}},
        "integrations": {"providers": []},
        "github": {
            "authenticated": True,
            "context": {"ok": True},
            "sections": {
                "attention_requests": [],
                "assigned_tasks": [],
                "blocked_or_stale_tasks": [],
            },
        },
        "brain": {
            "bets": {"overdue": [], "due_soon": []},
        },
        "drift": {"items": []},
        "since_last_check": {
            "first_run": False,
            "summary": {"commits": 0, "files_changed": 0, "brain_count_changes": 0},
        },
        "readiness": {"level": "ready"},
    }


def test_ranker_prioritizes_repair_before_business_work() -> None:
    report = _base_report()
    report["update"] = {
        "severity": "required",
        "command": "pipx upgrade mainbranch",
        "reason": "Installed version is below the supported floor.",
        "installed": "0.1.0",
        "latest": "0.2.6",
    }
    report["brain"] = {
        "bets": {
            "overdue": [
                {
                    "title": "Launch test",
                    "deadline": "2026-05-01",
                    "days_overdue": 3,
                }
            ],
            "due_soon": [],
        }
    }

    actions = ranker.rank_status_report(report)

    assert actions[0]["id"] == "mainbranch_update_required"
    assert actions[0]["priority"] == "urgent"
    assert actions[0]["command"] == "pipx upgrade mainbranch"
    assert actions[0]["signals"][0]["id"] == "update.severity"
    assert actions[1]["id"] == "update_overdue_bets"
    assert actions[1]["safe_to_share"] is False


def test_ranker_surfaces_low_confidence_floor_when_no_signals() -> None:
    actions = ranker.rank_status_report(_base_report())

    assert actions == [
        {
            "id": "not_enough_signal",
            "title": "Choose the next workflow manually",
            "command": "claude",
            "priority": "medium",
            "severity": "info",
            "score": 1,
            "confidence": "low",
            "reason": (
                "Status did not find enough repair, deadline, GitHub, drift, or recent-change "
                "signal to rank work confidently. Readiness is ready."
            ),
            "signals": [
                {
                    "id": "ranker.low_signal_floor",
                    "severity": "info",
                    "summary": "not enough deterministic signal to rank work",
                    "evidence": ["readiness=ready"],
                    "weight": 1,
                    "safe_to_share": True,
                }
            ],
            "safe_to_share": True,
        }
    ]


def test_ranker_uses_github_status_sections() -> None:
    report = _base_report()
    report["github"] = {
        "authenticated": True,
        "context": {"ok": True},
        "sections": {
            "attention_requests": [{"number": 12, "title": "Review proposal"}],
            "assigned_tasks": [{"number": 13, "title": "Write docs"}],
            "blocked_or_stale_tasks": [],
        },
    }

    actions = ranker.rank_status_report(report)

    assert actions[0]["id"] == "review_github_attention"
    assert actions[0]["signals"][0]["evidence"] == ["#12: Review proposal"]
    assert actions[0]["safe_to_share"] is False
