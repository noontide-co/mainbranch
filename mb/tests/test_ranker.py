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

    assert len(actions) == 1
    action = actions[0]
    assert action["id"] == "not_enough_signal"
    assert action["confidence"] == "low"
    assert action["safe_to_share"] is True
    assert action["signals"][0]["id"] == "ranker.low_signal_floor"
    assert action["signals"][0]["evidence"] == ["readiness=ready"]


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


def test_ranker_surfaces_playbook_health() -> None:
    report = _base_report()
    report["playbook_health"] = {
        "gaps": [
            {
                "id": "pushes_without_playbook",
                "severity": "warn",
                "summary": "1 active/planned push(es) need a playbook run.",
                "safe_to_share": True,
            }
        ]
    }

    actions = ranker.rank_status_report(report)

    assert actions[0]["id"] == "review_playbook_health"
    assert actions[0]["signals"][0]["id"] == "playbook_health.gaps"
    assert actions[0]["signals"][0]["evidence"] == ["pushes_without_playbook"]


def test_ranker_surfaces_money_path_below_repair_blockers() -> None:
    report = _base_report()
    report["update"] = {
        "severity": "required",
        "command": "pipx upgrade mainbranch",
        "reason": "Installed version is below the supported floor.",
        "installed": "0.1.0",
        "latest": "0.2.6",
    }
    report["money_path"] = {
        "ranked_actions": [
            {
                "id": "define-cta-path",
                "title": "Define the CTA path",
                "reason": "Offer and audience facts need a next step.",
                "route": "/mb-think",
                "component": "cta_path",
                "confidence": "high",
                "missing": ["conversion_endpoint"],
                "safe_to_share": True,
            }
        ]
    }

    actions = ranker.rank_status_report(report)

    assert actions[0]["id"] == "mainbranch_update_required"
    money_path = next(action for action in actions if action["id"] == "review_money_path_cta_path")
    assert money_path["command"] == "/mb-think"
    assert money_path["signals"][0]["id"] == "money_path.objects.cta_path"
    assert money_path["score"] < actions[0]["score"]


def test_ranker_action_carries_audience_and_operator_summary() -> None:
    action = ranker._action(
        action_id="any.id",
        title="Do the thing",
        command="mb something",
        severity="warn",
        score=60,
        reason="Three pushes need attention.",
        signals=[],
    )
    assert action["audience"] == "operator_decision"
    assert action["operator_summary"] == "Three pushes need attention."

    overridden = ranker._action(
        action_id="any.id",
        title="Do the thing",
        command="mb something",
        severity="info",
        score=10,
        reason="Heads up.",
        signals=[],
        audience="informational",
        operator_summary="Just a status note.",
    )
    assert overridden["audience"] == "informational"
    assert overridden["operator_summary"] == "Just a status note."
