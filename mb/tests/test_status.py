"""``mb status`` daily briefing."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import connect as connect_mod
from mb import graph as graph_mod
from mb import status as status_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def _without_github_or_claude(name: str) -> str:
    if name in {"gh", "claude"}:
        return ""
    return shutil.which(name) or ""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def _configure_git_user(repo: Path) -> None:
    assert _git(repo, "config", "user.email", "test@example.com").returncode == 0
    assert _git(repo, "config", "user.name", "Test User").returncode == 0


def _commit(repo: Path, relative_path: str, content: str, subject: str, body: str = "") -> None:
    target = repo / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    assert _git(repo, "add", relative_path).returncode == 0
    args = ["commit", "--no-verify", "-m", subject]
    if body:
        args.extend(["-m", body])
    result = _git(repo, *args)
    assert result.returncode == 0, result.stderr


def _write_push(
    repo: Path,
    slug: str,
    *,
    status: str = "active",
    offer: str = "core/offers/coaching/offer.md",
) -> Path:
    push = repo / "pushes" / slug
    push.mkdir(parents=True, exist_ok=True)
    (push / "push.md").write_text(
        (
            "---\n"
            "type: push\n"
            f"slug: {slug[11:]}\n"
            "kind: launch\n"
            f"status: {status}\n"
            "health: on-track\n"
            "goal:\n"
            "  metric: booked calls\n"
            "  target: 5 booked calls\n"
            "  by: 2026-05-20\n"
            "owner: Operator\n"
            "audience: founders\n"
            f"offer: {offer}\n"
            "promise: Ship a sanitized launch.\n"
            "started: 2026-05-06\n"
            "review_on: 2026-05-20\n"
            "---\n\n"
            "# Launch push\n"
        ),
        encoding="utf-8",
    )
    return push


def _write_playbook(
    push: Path,
    *,
    status: str = "active",
    provider_boundary: str = "candidate-adapter",
    approval_status: str = "approved",
    linked_outcomes: str = "[]",
) -> None:
    playbooks = push / "playbooks"
    playbooks.mkdir(parents=True, exist_ok=True)
    (playbooks / "launch.md").write_text(
        (
            "---\n"
            "type: playbook\n"
            f"status: {status}\n"
            "push: ../push.md\n"
            "platform: email\n"
            "provider: manual\n"
            f"provider_boundary: {provider_boundary}\n"
            "trigger:\n"
            "  kind: operator_launch_request\n"
            "resource:\n"
            "  kind: document\n"
            "  value: documents/launch.md\n"
            "approval:\n"
            "  required: true\n"
            f"  status: {approval_status}\n"
            "  approved_by: Operator\n"
            "  approved_at: 2026-05-06\n"
            "state:\n"
            "  provider_refs: []\n"
            "  activated_at:\n"
            "  retired_at:\n"
            "validation:\n"
            "  dry_run: passed\n"
            "  smoke_evidence: []\n"
            f"linked_outcomes: {linked_outcomes}\n"
            "---\n\n"
            "# Launch playbook\n"
        ),
        encoding="utf-8",
    )


def test_status_json_degrades_without_github(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "decisions" / "2026-05-01-pricing.md").write_text(
        "---\ndate: 2026-05-01\nstatus: accepted\n---\n\n# Pricing\n",
        encoding="utf-8",
    )
    (repo / "research" / "2026-05-01-market.md").write_text(
        "---\ndate: 2026-05-01\nsource: desk\n---\n\n# Market\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["schema_version"] == "1.0"
    assert report["schema"]["name"] == "mainbranch.status"
    assert report["generated_at"]
    assert report["repo"]["looks_like_mainbranch_repo"] is True
    assert report["runtime"]["skill_wiring"]["ok"] is True
    assert report["github"]["authenticated"] is False
    assert report["github"]["source"] == "gh"
    assert "assigned_tasks" in report["github"]["sections"]
    assert report["brain"]["counts"]["decisions"] == 1
    assert report["brain"]["counts"]["bets"] == 0
    assert report["brain"]["recent_research"][0]["title"] == "Market"
    assert report["since_last_check"]["first_run"] is True
    assert report["marker_update"]["ok"] is True
    assert (repo / ".mb" / "last-status-seen.json").is_file()
    assert "readiness" in report
    assert "update" in report
    assert report["ranked_actions"]
    assert report["ranked_actions"][0]["signals"]
    assert "safe_to_share" in report["ranked_actions"][0]


def test_status_schema_v1_matches_golden_fixture(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    payload = status_mod.run(
        path=str(repo),
        now=datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
        update_marker=False,
    )
    actual = {
        "schema_version": payload["schema_version"],
        "schema_name": payload["schema"]["name"],
        "top_level_keys": sorted(payload.keys()),
        "section_keys": {
            key: sorted(payload[key].keys())
            for key in [
                "repo",
                "install",
                "update",
                "runtime",
                "git",
                "git_activity",
                "journal",
                "brain",
                "onboarding",
                "integrations",
                "measurement",
                "github",
                "since_last_check",
                "drift",
                "readiness",
                "relationship_health",
                "playbook_health",
                "ranked_actions",
                "marker_update",
            ]
            if isinstance(payload[key], dict)
        },
    }
    expected = json.loads(
        (FIXTURES / "status" / "schema-v1-basic.json").read_text(encoding="utf-8")
    )

    assert actual == expected


def test_status_json_exposes_push_and_legacy_campaign_facts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    push = repo / "pushes" / "2026-05-06-workshop"
    push.mkdir(parents=True)
    (push / "push.md").write_text(
        "---\n"
        "type: push\n"
        "slug: workshop\n"
        "kind: launch\n"
        "status: active\n"
        "health: on-track\n"
        "goal:\n"
        "  metric: qualified calls\n"
        "  target: 10 qualified calls\n"
        "  by: 2026-05-20\n"
        "owner: Devon\n"
        "audience: founders\n"
        "offer: core/offers/workshop/offer.md\n"
        "promise: Own the launch memory in git.\n"
        "---\n"
        "# Workshop\n",
        encoding="utf-8",
    )
    campaign = repo / "campaigns" / "2026-05-legacy"
    campaign.mkdir(parents=True)
    (campaign / "campaign.md").write_text(
        "---\ntype: campaign\nslug: legacy\nstatus: active\n---\n# Legacy\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["push_count"] == 2
    assert report["canonical_push_count"] == 1
    assert report["campaign_count"] == 1
    assert report["deprecated_campaign_keys"] is True
    assert report["push_compatibility"]["legacy_campaign_keys_deprecated"] is True
    assert report["pushes"][0]["path"] == "pushes/2026-05-06-workshop/push.md"
    assert report["pushes"][0]["date"] == "2026-05-06"
    assert report["campaigns"][0]["path"] == "campaigns/2026-05-legacy/campaign.md"
    assert {item["path"] for item in report["active_pushes"]} == {
        "pushes/2026-05-06-workshop/push.md",
        "campaigns/2026-05-legacy/campaign.md",
    }


def test_status_playbook_health_accepts_healthy_active_push_playbook(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    offer = repo / "core" / "offers" / "coaching"
    offer.mkdir(parents=True)
    (offer / "offer.md").write_text(
        "---\nslug: coaching\nstatus: running\n---\n\n# Coaching\n",
        encoding="utf-8",
    )
    push = _write_push(repo, "2026-05-06-launch")
    _write_playbook(push, status="active", approval_status="approved")

    report = status_mod.run(path=str(repo), update_marker=False)

    health = report["playbook_health"]
    assert health["ok"] is True
    assert health["summary"]["playbooks"] == 1
    assert health["summary"]["pushes_without_playbook"] == 0
    assert health["summary"]["pending_playbook_statuses"] == 0
    assert health["summary"]["playbook_approval_needed"] == 0
    assert health["gaps"] == []

    human = runner.invoke(app, ["status", str(repo), "--no-color", "--peek"])
    assert human.exit_code == 0
    assert "Playbook health" not in human.stdout


def test_status_playbook_health_flags_active_push_without_playbook(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    push = _write_push(repo, "2026-05-06-launch")

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    health = report["playbook_health"]
    assert health["ok"] is False
    assert health["summary"]["pushes_without_playbook"] == 1
    assert health["sections"]["pushes"]["without_playbook"][0]["path"] == (
        "pushes/2026-05-06-launch/push.md"
    )
    assert any(item["id"] == "playbook_health_gaps" for item in report["drift"]["items"])
    assert any(action["id"] == "review_playbook_health" for action in report["ranked_actions"])

    human = runner.invoke(app, ["status", str(repo), "--no-color", "--peek"])

    assert human.exit_code == 0
    assert "Playbook health" in human.stdout
    assert "active/planned push(es) need a playbook run" in human.stdout
    assert push.is_dir()


def test_status_playbook_health_flags_pending_and_completed_without_outcome(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    planned = _write_push(repo, "2026-05-06-planned", status="planned")
    _write_playbook(
        planned,
        status="draft",
        provider_boundary="plan-only",
        approval_status="needed",
    )
    completed = _write_push(repo, "2026-05-07-completed", status="completed")
    _write_playbook(completed, status="completed", approval_status="approved")

    report = status_mod.run(path=str(repo), update_marker=False)

    health = report["playbook_health"]
    assert health["summary"]["pending_playbook_statuses"] == 1
    assert health["summary"]["playbook_approval_needed"] == 1
    assert health["summary"]["completed_playbooks_without_outcome"] == 1
    assert health["summary"]["manual_provider_boundaries"] == 1
    assert health["sections"]["playbooks"]["pending_status"][0]["path"] == (
        "pushes/2026-05-06-planned/playbooks/launch.md"
    )
    assert health["sections"]["playbooks"]["completed_without_outcome"][0]["path"] == (
        "pushes/2026-05-07-completed/playbooks/launch.md"
    )


def test_status_playbook_health_ignores_retired_playbook_approval(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    push = _write_push(repo, "2026-05-06-launch")
    _write_playbook(
        push,
        status="retired",
        provider_boundary="plan-only",
        approval_status="",
    )

    report = status_mod.run(path=str(repo), update_marker=False)

    health = report["playbook_health"]
    assert health["summary"]["playbook_approval_needed"] == 0
    assert health["summary"]["manual_provider_boundaries"] == 0
    assert health["gaps"] == []


def test_status_relationship_health_flags_active_bet_and_offer_gaps(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    offer = repo / "core" / "offers" / "coaching"
    offer.mkdir(parents=True)
    (offer / "offer.md").write_text(
        "---\nslug: coaching\nstatus: running\n---\n\n# Coaching\n",
        encoding="utf-8",
    )
    (repo / "bets" / "2026-05-01-launch.md").write_text(
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-01\n"
            "deadline: 2026-05-31\n"
            "appetite: 2 weeks\n"
            "hypothesis: A launch push will create calls.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_pushes: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: true\n"
            "channels: []\n"
            "tags: []\n"
            "---\n\n"
            "# Launch bet\n"
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    health = report["relationship_health"]
    assert health["ok"] is False
    assert health["summary"]["active_bets_without_push"] == 1
    assert health["summary"]["offers_without_current_push_or_playbook"] == 1
    assert health["sections"]["bets"]["active_without_push"][0]["path"] == (
        "bets/2026-05-01-launch.md"
    )
    assert any(item["id"] == "relationship_health_gaps" for item in report["drift"]["items"])
    assert any(action["id"] == "review_relationship_health" for action in report["ranked_actions"])

    human = runner.invoke(app, ["status", str(repo), "--no-color", "--peek"])

    assert human.exit_code == 0
    assert "Relationship health" in human.stdout
    assert "active bet(s) need a linked push" in human.stdout


def test_status_relationship_health_flags_completed_and_stale_pushes(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    offer = repo / "core" / "offers" / "coaching"
    offer.mkdir(parents=True)
    (offer / "offer.md").write_text(
        "---\nslug: coaching\nstatus: running\n---\n\n# Coaching\n",
        encoding="utf-8",
    )
    completed = repo / "pushes" / "2026-05-01-completed"
    completed.mkdir(parents=True)
    (completed / "push.md").write_text(
        (
            "---\n"
            "type: push\n"
            "slug: completed\n"
            "kind: launch\n"
            "status: completed\n"
            "health: on-track\n"
            "goal: booked calls\n"
            "owner: Devon\n"
            "audience: founders\n"
            "offer: core/offers/coaching/offer.md\n"
            "started: 2026-05-01\n"
            "review_on: 2026-05-07\n"
            "---\n\n"
            "# Completed push\n"
        ),
        encoding="utf-8",
    )
    stale = repo / "pushes" / "2026-04-01-stale"
    stale.mkdir(parents=True)
    (stale / "push.md").write_text(
        (
            "---\n"
            "type: push\n"
            "slug: stale\n"
            "kind: launch\n"
            "status: active\n"
            "health: at-risk\n"
            "goal: booked calls\n"
            "owner: Devon\n"
            "audience: founders\n"
            "offer: core/offers/coaching/offer.md\n"
            "started: 2026-04-01\n"
            "review_on: 2026-04-15\n"
            "---\n\n"
            "# Stale push\n"
        ),
        encoding="utf-8",
    )

    report = status_mod.run(
        path=str(repo),
        now=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        update_marker=False,
    )

    summary = report["relationship_health"]["summary"]
    assert summary["completed_pushes_without_outcome"] == 1
    assert summary["stale_pushes_without_outcome"] == 1
    assert summary["offers_without_current_push_or_playbook"] == 0
    assert (
        report["relationship_health"]["sections"]["pushes"]["stale_without_outcome"][0]["path"]
        == "pushes/2026-04-01-stale/push.md"
    )


def test_status_relationship_health_accepts_offer_side_push_links(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    offer = repo / "core" / "offers" / "coaching"
    offer.mkdir(parents=True)
    (offer / "offer.md").write_text(
        (
            "---\n"
            "slug: coaching\n"
            "status: running\n"
            "linked_pushes:\n"
            "  - pushes/2026-05-01-launch/push.md\n"
            "---\n\n"
            "# Coaching\n"
        ),
        encoding="utf-8",
    )
    push = repo / "pushes" / "2026-05-01-launch"
    push.mkdir(parents=True)
    (push / "push.md").write_text(
        (
            "---\n"
            "type: push\n"
            "slug: launch\n"
            "kind: launch\n"
            "status: active\n"
            "health: on-track\n"
            "goal: booked calls\n"
            "owner: Devon\n"
            "audience: founders\n"
            "offer: ''\n"
            "started: 2026-05-01\n"
            "review_on: 2026-05-20\n"
            "---\n\n"
            "# Launch\n"
        ),
        encoding="utf-8",
    )

    report = status_mod.run(
        path=str(repo),
        now=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        update_marker=False,
    )

    assert report["relationship_health"]["summary"]["offers_without_current_push_or_playbook"] == 0


def test_status_relationship_health_ignores_non_live_offer_stubs(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "core" / "offer.md").write_text(
        "---\ntype: offer\nstatus: stub\n---\n\n# Offer stub\n",
        encoding="utf-8",
    )

    report = status_mod.run(path=str(repo), update_marker=False)

    assert report["relationship_health"]["summary"]["offers_without_current_push_or_playbook"] == 0


def test_status_relationship_health_flags_closed_bet_without_outcome(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "bets" / "2026-05-01-closed.md").write_text(
        (
            "---\n"
            "status: closed\n"
            "opened: 2026-05-01\n"
            "deadline: 2026-05-07\n"
            "appetite: 1 week\n"
            "hypothesis: A follow-up push will create calls.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "result: win\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_pushes: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n\n"
            "# Closed bet\n"
        ),
        encoding="utf-8",
    )

    report = status_mod.run(path=str(repo), update_marker=False)

    assert report["relationship_health"]["summary"]["closed_bets_without_outcome"] == 1
    assert (
        report["relationship_health"]["sections"]["bets"]["closed_without_outcome"][0]["path"]
        == "bets/2026-05-01-closed.md"
    )


def test_status_relationship_health_uses_lightweight_scan_on_large_repos(
    tmp_path: Path, monkeypatch
) -> None:
    def fail_if_graph_builds(_path: str) -> None:
        raise AssertionError("status built the full graph")

    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    monkeypatch.setattr(graph_mod, "build_index", fail_if_graph_builds)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    documents = repo / "documents"
    documents.mkdir(exist_ok=True)
    large_body = "# Notes\n\n" + ("Relationship-free working note.\n" * 100)
    for index in range(300):
        (documents / f"2026-05-01-note-{index:03d}.md").write_text(
            large_body,
            encoding="utf-8",
        )
    (repo / "bets" / "2026-05-01-launch.md").write_text(
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-01\n"
            "deadline: 2026-05-31\n"
            "appetite: 2 weeks\n"
            "hypothesis: A launch push will create calls.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "linked_pushes:\n"
            "  - pushes/missing-launch/push.md\n"
            "---\n\n"
            "# Launch bet\n"
        ),
        encoding="utf-8",
    )

    report = status_mod.run(path=str(repo), update_marker=False)

    health = report["relationship_health"]
    assert report["brain"]["counts"]["documents"] == 300
    assert health["summary"]["active_bets_without_push"] == 1
    assert health["summary"]["missing_relationship_targets"] == 1
    assert health["sections"]["outcomes"]["missing_targets"][0] == {
        "source": "bets/2026-05-01-launch.md",
        "relationship": "push",
        "field": "linked_pushes",
        "target": "pushes/missing-launch/push.md",
    }


def test_status_human_output_mentions_core_sections(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["status", str(repo)])

    assert result.exit_code == 0
    assert "mb status" in result.stdout
    assert "Repo" in result.stdout
    assert "Since last check" in result.stdout
    assert "Drift" in result.stdout
    assert "Runtime" in result.stdout
    assert "GitHub" in result.stdout
    assert "Next" in result.stdout
    assert "why:" in result.stdout
    assert "next:" in result.stdout


def test_status_since_last_check_uses_repo_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    first = runner.invoke(app, ["status", str(repo), "--json"])
    assert first.exit_code == 0
    first_payload = json.loads(first.stdout)
    assert first_payload["since_last_check"]["first_run"] is True

    (repo / "research" / "2026-05-02-market.md").write_text("# Market\n", encoding="utf-8")
    second = runner.invoke(app, ["status", str(repo), "--json"])

    assert second.exit_code == 0
    second_payload = json.loads(second.stdout)
    assert second_payload["since_last_check"]["first_run"] is False
    assert second_payload["since_last_check"]["previous_seen_at"] == first_payload["generated_at"]
    assert {
        "folder": "research",
        "before": 0,
        "after": 1,
        "delta": 1,
    } in second_payload["since_last_check"]["brain_count_changes"]


def test_status_since_last_check_includes_grouped_journal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _configure_git_user(repo)
    assert _git(repo, "add", ".").returncode == 0
    result = _git(repo, "commit", "--no-verify", "-m", "[added] business scaffold")
    assert result.returncode == 0, result.stderr

    first = runner.invoke(app, ["status", str(repo), "--json"])
    assert first.exit_code == 0

    _commit(
        repo,
        "pushes/workshop/push.md",
        "# Workshop\n",
        "[shipped] workshop lander",
        "Refs:\n- pushes/workshop/push.md\n- https://github.com/noontide-co/mainbranch/issues/303",
    )
    second = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert second.exit_code == 0
    payload = json.loads(second.stdout)
    journal = payload["since_last_check"]["journal"]
    assert payload["since_last_check"]["summary"]["journal_events"] == 1
    assert journal["schema_version"] == "0.current"
    assert journal["events"][0]["verb"] == "shipped"
    assert journal["events"][0]["loop"] == "ship"
    assert journal["events"][0]["refs"][0]["kind"] == "push"
    assert journal["events"][0]["refs"][1]["kind"] == "github_issue"
    assert journal["groups"][0]["label"] == "Shipped work"


def test_status_human_output_summarizes_since_last_journal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _configure_git_user(repo)
    assert _git(repo, "add", ".").returncode == 0
    result = _git(repo, "commit", "--no-verify", "-m", "[added] business scaffold")
    assert result.returncode == 0, result.stderr
    first = runner.invoke(app, ["status", str(repo), "--json"])
    assert first.exit_code == 0
    _commit(repo, "bets/workshop.md", "# Bet\n", "[opened] bet workshop")

    human = runner.invoke(app, ["status", str(repo), "--verbose", "--no-color", "--peek"])

    assert human.exit_code == 0
    assert "journal:" in human.stdout
    assert "Made decisions: 1 event(s)" in human.stdout
    assert "Opened bet workshop" in human.stdout


def test_status_peek_does_not_update_seen_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    first = runner.invoke(app, ["status", str(repo), "--json"])
    marker_before = (repo / ".mb" / "last-status-seen.json").read_text(encoding="utf-8")
    peek = runner.invoke(app, ["status", str(repo), "--json", "--peek"])
    marker_after = (repo / ".mb" / "last-status-seen.json").read_text(encoding="utf-8")

    assert first.exit_code == 0
    assert peek.exit_code == 0
    payload = json.loads(peek.stdout)
    assert payload["marker_update"]["reason"] == "disabled"
    assert marker_after == marker_before


def test_marker_gitignore_state_honors_broader_gitignore_patterns(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    runner.invoke(app, ["init", str(repo), "--name", "Acme"])
    (repo / ".gitignore").write_text(".mb/\n", encoding="utf-8")

    state = status_mod._marker_gitignore_state(repo)

    assert state["ok"] is True
    assert state["repair"] == ""


def test_status_no_color_and_verbose_output(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "decisions" / "2026-05-01-pricing.md").write_text(
        "---\ndate: 2026-05-01\nstatus: accepted\n---\n\n# Pricing\n",
        encoding="utf-8",
    )

    terse = runner.invoke(app, ["status", str(repo), "--no-color"])
    verbose = runner.invoke(app, ["status", str(repo), "--verbose", "--no-color"])

    assert terse.exit_code == 0
    assert "\x1b[" not in terse.stdout
    assert "Recent decisions" not in terse.stdout
    assert verbose.exit_code == 0
    assert "Recent decisions" in verbose.stdout


def test_status_required_update_json_and_human_copy(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    monkeypatch.setattr(
        status_mod,
        "package_update_status",
        lambda repo: {
            "installed": "0.1.0",
            "latest": "0.2.1",
            "minimum_supported": "0.2.0",
            "severity": "required",
            "command": "pipx upgrade mainbranch",
            "post_update_commands": ["mb skill link --repo .", "mb doctor"],
            "reason": (
                "Installed version predates mb update and the current skill-link repair flow."
            ),
        },
    )
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    json_result = runner.invoke(app, ["status", str(repo), "--json"])

    assert json_result.exit_code == 0
    payload = json.loads(json_result.stdout)
    assert payload["update"]["severity"] == "required"
    assert payload["update"]["command"] == "pipx upgrade mainbranch"
    assert any(
        "pipx upgrade mainbranch" in action for action in payload["readiness"]["next_actions"]
    )
    assert payload["ranked_actions"][0]["id"] == "mainbranch_update_required"

    human_result = runner.invoke(app, ["status", str(repo), "--verbose"])

    assert human_result.exit_code == 0
    assert "Update required." in human_result.stdout
    assert "pipx upgrade mainbranch" in human_result.stdout
    assert "mb skill link --repo ." in human_result.stdout


def test_status_names_integration_repairs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    connect_mod.connect_provider("cloudflare", repo=repo)

    json_result = runner.invoke(app, ["status", str(repo), "--json"])

    assert json_result.exit_code == 0
    payload = json.loads(json_result.stdout)
    assert payload["integrations"]["providers"][0]["state"] == "missing_secret"
    assert any(item["id"] == "unhealthy_integrations" for item in payload["drift"]["items"])
    assert any(
        "mb connect cloudflare --token-stdin" in action
        for action in payload["readiness"]["next_actions"]
    )
    assert any(
        action["id"] == "repair_unhealthy_integrations" for action in payload["ranked_actions"]
    )

    human_result = runner.invoke(app, ["status", str(repo), "--verbose"])

    assert human_result.exit_code == 0
    assert "cloudflare: missing_secret" in human_result.stdout
    assert "mb connect cloudflare --token-stdin" in human_result.stdout


def test_status_drift_aligns_unhealthy_integrations_with_readiness(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    provider = {
        "provider": "cloudflare",
        "ok": False,
        "connected": True,
        "state": "unvalidated",
        "repair_command": "mb connect test cloudflare",
    }
    report = status_mod.run(path=str(repo), update_marker=False)
    report["integrations"]["providers"] = [provider]
    report["integrations"]["summary"] = {
        "configured": 1,
        "healthy": 0,
        "needs_repair": 1,
        "unvalidated": 1,
    }

    drift = status_mod._drift(report)
    readiness = status_mod._readiness(report)

    assert any(item["id"] == "unhealthy_integrations" for item in drift["items"])
    assert any("mb connect test cloudflare" in action for action in readiness["next_actions"])


def test_status_detects_non_business_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    report = status_mod.run(path=str(tmp_path))

    assert report["repo"]["looks_like_mainbranch_repo"] is False
    assert report["readiness"]["level"] == "not_ready"
    assert any("mb init" in action for action in report["readiness"]["next_actions"])


def test_status_brain_includes_active_bets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "decisions").mkdir(parents=True)
    old_date = date.today().replace(year=date.today().year - 1)
    (repo / "decisions" / f"{old_date.isoformat()}-old.md").write_text(
        f"---\ndate: {old_date.isoformat()}\nstatus: proposed\n---\n\n# Old proposal\n",
        encoding="utf-8",
    )
    (repo / "research").mkdir()
    (repo / "research" / "2026-05-01-market.md").write_text("# Market\n", encoding="utf-8")
    deadline = date.today().replace(year=date.today().year + 1)
    (repo / "bets").mkdir()
    (repo / "bets" / "2026-05-01-launch.md").write_text(
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-01\n"
            f"deadline: {deadline.isoformat()}\n"
            "appetite: 2 weeks\n"
            "hypothesis: Launching a demo will create calls.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: true\n"
            "channels:\n"
            "  - site\n"
            "tags: []\n"
            "---\n\n"
            "# Launch bet\n"
        ),
        encoding="utf-8",
    )

    brain = status_mod._brain(repo)

    assert brain["recent_decisions"][0]["title"] == "Old proposal"
    assert brain["stale_decisions"][0]["age_days"] > status_mod.STALE_DECISION_DAYS
    assert brain["recent_research"][0]["title"] == "Market"
    assert brain["bets"]["active"][0]["title"] == "Launch bet"
    assert brain["bets"]["active"][0]["deadline"] == deadline.isoformat()


def test_status_frontmatter_reader_accepts_delimiter_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "note.md"
    path.write_text("--- \nstatus: open\n--- \n# Note\n", encoding="utf-8")

    assert status_mod._read_frontmatter(path)["status"] == "open"


def test_status_readiness_mentions_due_bets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "bets").mkdir(parents=True)
    today = date.today()
    (repo / "bets" / f"{today.isoformat()}-due.md").write_text(
        (
            "---\n"
            "status: open\n"
            f"opened: {today.isoformat()}\n"
            f"deadline: {today.isoformat()}\n"
            "appetite: 1 day\n"
            "hypothesis: Fast follow-up increases replies.\n"
            "metric: replies\n"
            "target: 3 replies\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n\n"
            "# Due bet\n"
        ),
        encoding="utf-8",
    )
    report = {
        "repo": {"looks_like_mainbranch_repo": True},
        "git": {"inside_work_tree": True, "dirty": False},
        "install": {"ok": True},
        "update": {"severity": "current", "command": ""},
        "runtime": {
            "skill_wiring": {"ok": True, "repair": ""},
            "claude_code": {"found": True, "repair": ""},
        },
        "brain": status_mod._brain(repo),
        "onboarding": {"summary": {"status": "ready"}},
        "integrations": {"providers": []},
        "github": {"authenticated": True, "context": {"ok": True}},
    }

    readiness = status_mod._readiness(report)

    assert any("active bets" in action for action in readiness["next_actions"])


def test_status_ranker_mentions_due_bets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        status_mod,
        "_git_info",
        lambda repo: {
            "available": True,
            "inside_work_tree": True,
            "branch": "main",
            "commit": "abc123",
            "dirty": False,
            "dirty_count": 0,
            "dirty_files": [],
            "remote": "https://github.com/example/acme.git",
            "error": "",
        },
    )
    monkeypatch.setattr(
        status_mod,
        "_git_recent_activity",
        lambda repo, git: {"available": True, "items": [], "error": ""},
    )
    monkeypatch.setattr(
        status_mod,
        "_github",
        lambda repo, git: {
            "available": True,
            "authenticated": True,
            "degraded": False,
            "source": "gh",
            "repo": "example/acme",
            "summary": {
                "assigned_tasks": 0,
                "attention_requests": 0,
                "open_proposals": 0,
                "shipped_this_week": 0,
                "recently_closed_tasks": 0,
                "blocked_or_stale_tasks": 0,
            },
            "sections": {
                "assigned_tasks": [],
                "attention_requests": [],
                "open_proposals": [],
                "shipped_this_week": [],
                "recently_closed_tasks": [],
                "blocked_or_stale_tasks": [],
            },
            "errors": [],
            "assigned_issues": [],
            "review_requests": [],
            "recent_merged_prs": [],
            "context": {"ok": True, "state": "ready"},
        },
    )
    monkeypatch.setattr(
        status_mod.onboard_mod,  # type: ignore[attr-defined]
        "onboarding_status",
        lambda repo: {"summary": {"status": "ready"}, "checklist": []},
    )
    repo = tmp_path / "repo"
    init_run(path=str(repo), name="Acme")
    today = date.today()
    (repo / "bets" / f"{today.isoformat()}-due.md").write_text(
        (
            "---\n"
            "status: open\n"
            f"opened: {today.isoformat()}\n"
            f"deadline: {today.isoformat()}\n"
            "appetite: 1 day\n"
            "hypothesis: Fast follow-up increases replies.\n"
            "metric: replies\n"
            "target: 3 replies\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n\n"
            "# Due bet\n"
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any(action["id"] == "review_due_bets" for action in payload["ranked_actions"])


def test_status_empty_bet_deadline_does_not_fall_back_to_opened_filename(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "bets").mkdir(parents=True)
    (repo / "bets" / "2020-01-01-no-deadline.md").write_text(
        (
            "---\n"
            "status: open\n"
            "opened: 2020-01-01\n"
            "deadline: ''\n"
            "appetite: 1 week\n"
            "hypothesis: A no-deadline bet should stay active but not due.\n"
            "metric: replies\n"
            "target: 3 replies\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n\n"
            "# No deadline\n"
        ),
        encoding="utf-8",
    )

    bets = status_mod._brain(repo)["bets"]

    assert bets["active"][0]["title"] == "No deadline"
    assert bets["active"][0]["deadline"] == ""
    assert bets["due_soon"] == []
    assert bets["overdue"] == []


def test_status_low_level_helpers_handle_edge_cases(tmp_path: Path, monkeypatch) -> None:
    assert status_mod._repo_full_name("git@github.com:noontide-co/mainbranch.git") == (
        "noontide-co/mainbranch"
    )
    assert status_mod._repo_full_name("https://github.com/noontide-co/mainbranch.git") == (
        "noontide-co/mainbranch"
    )
    assert status_mod._repo_full_name("https://github.com/noontide-co/some.io.git") == (
        "noontide-co/some.io"
    )
    assert status_mod._repo_full_name("") == ""

    missing = tmp_path / "missing.md"
    plain = tmp_path / "plain.md"
    plain.write_text("# Plain\n", encoding="utf-8")
    unclosed = tmp_path / "unclosed.md"
    unclosed.write_text("---\nstatus: proposed\n", encoding="utf-8")
    bad_yaml = tmp_path / "bad.md"
    bad_yaml.write_text("---\n:\n---\n", encoding="utf-8")

    assert status_mod._read_frontmatter(missing) == {}
    assert status_mod._read_frontmatter(plain) == {}
    assert status_mod._read_frontmatter(unclosed) == {}
    assert status_mod._read_frontmatter(bad_yaml) == {}

    assert status_mod._parse_date(datetime(2026, 5, 2, 8, 30), plain) == date(2026, 5, 2)
    assert status_mod._parse_date(date(2026, 5, 2), plain) == date(2026, 5, 2)
    assert status_mod._parse_date("not-a-date", tmp_path / "2026-05-01-note.md") == date(2026, 5, 1)
    assert status_mod._parse_date("not-a-date", tmp_path / "note.md") is None

    external = tmp_path / "external.md"
    external.write_text("no heading\n", encoding="utf-8")
    summary = status_mod._file_summary(tmp_path / "repo", external)
    assert summary["path"] == str(external)
    assert summary["title"] == "external"

    def raise_missing(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_missing)
    assert status_mod._run_command(["missing-bin"])["returncode"] == 127

    def raise_timeout(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(cmd="slow", timeout=1)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    assert status_mod._run_command(["slow"])["returncode"] == 124

    def raise_subprocess(*args: object, **kwargs: object) -> object:
        raise subprocess.SubprocessError("boom")

    monkeypatch.setattr(subprocess, "run", raise_subprocess)
    assert status_mod._run_command(["boom"])["stderr"] == "boom"


def test_status_git_activity_parser_and_failure(tmp_path: Path, monkeypatch) -> None:
    def fake_run_command(
        args: list[str], cwd: Path | None = None, timeout: float = 3.0
    ) -> dict[str, Any]:
        assert args[1] == "log"
        return {
            "ok": True,
            "stdout": (
                "abc123\t2026-05-02\tUpdate offer\n"
                "core/offer.md\n"
                "research/2026-05-01-market.md\n\n"
                "def456\t2026-05-01\tAdd decision\n"
                "decisions/2026-05-01-pricing.md\n"
            ),
            "stderr": "",
        }

    monkeypatch.setattr(status_mod, "_run_command", fake_run_command)
    activity = status_mod._git_recent_activity(tmp_path, {"inside_work_tree": True})

    assert activity["available"] is True
    assert activity["items"][0]["commit"] == "abc123"
    assert activity["items"][0]["files"] == [
        "core/offer.md",
        "research/2026-05-01-market.md",
    ]
    assert activity["items"][1]["subject"] == "Add decision"
    assert (
        status_mod._git_recent_activity(tmp_path, {"inside_work_tree": False, "error": "no git"})[
            "error"
        ]
        == "no git"
    )

    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": False, "stdout": "", "stderr": "bad log"},
    )
    assert (
        status_mod._git_recent_activity(tmp_path, {"inside_work_tree": True})["error"] == "bad log"
    )


def test_status_brain_marks_stale_decisions(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    decisions = repo / "decisions"
    decisions.mkdir(parents=True)
    old_date = date.today().replace(year=date.today().year - 1)
    (decisions / f"{old_date.isoformat()}-old.md").write_text(
        f"---\ndate: {old_date.isoformat()}\nstatus: proposed\n---\n\n# Old proposal\n",
        encoding="utf-8",
    )
    (repo / "research").mkdir()
    old_research_date = date.today().replace(year=date.today().year - 1)
    (repo / "research" / f"{old_research_date.isoformat()}-market.md").write_text(
        f"---\ndate: {old_research_date.isoformat()}\n---\n\n# Market\n",
        encoding="utf-8",
    )

    brain = status_mod._brain(repo)

    assert brain["recent_decisions"][0]["title"] == "Old proposal"
    assert brain["stale_decisions"][0]["age_days"] > status_mod.STALE_DECISION_DAYS
    assert brain["recent_research"][0]["title"] == "Market"
    assert brain["stale_research"][0]["age_days"] > status_mod.STALE_RESEARCH_DAYS


def test_status_github_authenticated_branches(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        connect_mod,
        "github_context",
        lambda repo, **kwargs: {
            "ok": True,
            "state": "ready",
            "summary": "GitHub ready",
            "repair": "",
            "repair_command": "",
            "safe_to_share": True,
        },
    )
    monkeypatch.setattr(status_mod, "_which", lambda name: "/usr/bin/gh" if name == "gh" else "")
    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": True, "stdout": "", "stderr": ""},
    )

    def fake_gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
        if args[1:3] == ["issue", "list"] and "--assignee" in args:
            return True, [{"number": 173, "title": "Status", "url": "u"}], ""
        if args[1:3] == ["pr", "list"] and "review-requested:@me" in args:
            return False, None, "search failed"
        if args[1:3] == ["issue", "list"]:
            return True, [], ""
        if args[1:3] == ["pr", "list"] and "--state" in args and "open" in args:
            return True, [], ""
        return (
            True,
            [
                {
                    "number": 190,
                    "title": "Older",
                    "body": "older",
                    "mergedAt": "2026-05-01T10:00:00Z",
                },
                {
                    "number": 192,
                    "title": "Briefing",
                    "body": "## Scope\n- Shipped status",
                    "mergedAt": "2026-05-02T10:00:00Z",
                },
            ],
            "",
        )

    monkeypatch.setattr(status_mod, "_gh_json", fake_gh_json)
    github = status_mod._github(
        tmp_path,
        {"remote": "https://github.com/noontide-co/mainbranch.git"},
    )

    assert github["authenticated"] is True
    assert github["repo"] == "noontide-co/mainbranch"
    assert github["assigned_issues"][0]["number"] == 173
    assert github["sections"]["assigned_tasks"][0]["type"] == "task"
    assert github["summary"]["assigned_tasks"] == 1
    assert github["recent_merged_prs"][0]["number"] == 192
    assert github["recent_merged_prs"][0]["what_shipped"] == "Shipped status"
    assert github["errors"] == ["review requests: search failed"]

    assert (
        status_mod._summarize_pr({"title": "Fallback title", "body": "# Heading"})["what_shipped"]
        == "Fallback title"
    )
    assert [
        pr["number"]
        for pr in status_mod._recent_merged_prs(
            [
                {"number": index, "title": str(index), "mergedAt": f"2026-05-{index:02d}T00:00:00Z"}
                for index in range(1, 8)
            ]
        )
    ] == [7, 6, 5, 4, 3]

    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": False, "stdout": "", "stderr": "no auth"},
    )
    assert status_mod._github(tmp_path, {"remote": ""})["authenticated"] is False


def test_status_github_activity_business_sections(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        connect_mod,
        "github_context",
        lambda repo, **kwargs: {
            "ok": True,
            "state": "ready",
            "summary": "GitHub ready",
            "repair": "",
            "repair_command": "",
            "safe_to_share": True,
        },
    )
    monkeypatch.setattr(status_mod, "_which", lambda name: "/usr/bin/gh" if name == "gh" else "")
    monkeypatch.setattr(
        status_mod,
        "_run_command",
        lambda args, cwd=None, timeout=3.0: {"ok": True, "stdout": "", "stderr": ""},
    )

    def value_after(args: list[str], flag: str) -> str:
        if flag not in args:
            return ""
        return args[args.index(flag) + 1]

    def fake_gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
        state = value_after(args, "--state")
        search = value_after(args, "--search")
        if args[1:3] == ["issue", "list"]:
            if "--assignee" in args:
                return True, [{"number": 1, "title": "Assigned", "labels": []}], ""
            if state == "closed":
                return True, [{"number": 2, "title": "Closed", "closedAt": "2026-05-02"}], ""
            if search == "mentions:@me":
                return True, [{"number": 3, "title": "Mentioned task"}], ""
            if search == "label:blocked":
                return (
                    True,
                    [{"number": 4, "title": "Blocked", "labels": [{"name": "blocked"}]}],
                    "",
                )
            if search == "label:stale":
                return True, [{"number": 5, "title": "Stale", "labels": [{"name": "stale"}]}], ""
        if args[1:3] == ["pr", "list"]:
            if search == "review-requested:@me":
                return True, [{"number": 6, "title": "Review me", "author": {"login": "devon"}}], ""
            if search == "mentions:@me":
                return True, [{"number": 7, "title": "Mentioned proposal"}], ""
            if "--author" in args:
                return True, [{"number": 8, "title": "Open proposal"}], ""
            if state == "merged":
                return (
                    True,
                    [
                        {
                            "number": index,
                            "title": f"Merged {index}",
                            "body": f"- Launched {index}",
                            "mergedAt": f"2026-05-0{index}T00:00:00Z",
                        }
                        for index in range(1, 8)
                    ],
                    "",
                )
        return True, [], ""

    monkeypatch.setattr(status_mod, "_gh_json", fake_gh_json)
    github = status_mod._github(
        tmp_path,
        {"remote": "https://github.com/noontide-co/mainbranch.git"},
    )

    sections = github["sections"]
    assert github["summary"] == {
        "assigned_tasks": 1,
        "attention_requests": 3,
        "open_proposals": 1,
        "shipped_this_week": 7,
        "recently_closed_tasks": 1,
        "blocked_or_stale_tasks": 2,
    }
    assert sections["assigned_tasks"][0]["business_status"] == "assigned"
    assert sections["attention_requests"][0]["type"] == "proposal"
    assert sections["open_proposals"][0]["business_status"] == "open_proposal"
    assert len(sections["shipped_this_week"]) == 5
    assert sections["shipped_this_week"][0]["number"] == 7
    assert sections["shipped_this_week"][0]["what_shipped"] == "Launched 7"
    assert sections["recently_closed_tasks"][0]["business_status"] == "closed"
    assert sections["blocked_or_stale_tasks"][0]["labels"] == ["blocked"]


def test_status_github_context_stops_before_low_level_remote_errors(
    tmp_path: Path, monkeypatch
) -> None:
    context = {
        "ok": False,
        "state": "missing_github_remote",
        "summary": "This repo does not have a GitHub origin remote.",
        "repair": "Add a GitHub origin remote before relying on GitHub tasks or proposals.",
        "repair_command": "gh repo create --source . --remote origin --push",
        "safe_to_share": True,
    }
    monkeypatch.setattr(connect_mod, "github_context", lambda repo, **kwargs: context)

    def fail_gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
        raise AssertionError(args)

    monkeypatch.setattr(status_mod, "_gh_json", fail_gh_json)

    github = status_mod._github(tmp_path, {"remote": ""})

    assert github["authenticated"] is True
    assert github["context"]["state"] == "missing_github_remote"
    assert github["errors"] == ["This repo does not have a GitHub origin remote."]
    assert "no git remotes found" not in json.dumps(github)


def test_status_reuses_github_context_for_integrations(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    calls = 0

    def fake_context(repo: Path, **kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {
            "ok": False,
            "state": "missing_cli",
            "summary": "GitHub CLI is not installed.",
            "repair": "Install GitHub CLI, then run `gh auth login`.",
            "repair_command": "gh auth login",
            "safe_to_share": True,
        }

    monkeypatch.setattr(connect_mod, "github_context", fake_context)

    report = status_mod.run(path=str(repo))

    assert calls == 1
    assert report["integrations"]["github"] == report["github"]["context"]


def test_status_renderer_prints_optional_sections(capsys) -> None:
    report: dict[str, Any] = {
        "repo": {"path": "/tmp/biz", "looks_like_mainbranch_repo": True},
        "install": {"detail": "mb 0.1.2 (wheel mode)"},
        "runtime": {
            "claude_code": {"found": True},
            "skill_wiring": {"ok": True},
        },
        "git": {"inside_work_tree": False, "dirty": False, "error": "not a git work tree"},
        "brain": {
            "counts": {
                "core": 1,
                "reference/core": 1,
                "research": 1,
                "decisions": 1,
                "bets": 1,
                "campaigns": 1,
                "log": 1,
                "documents": 1,
            },
            "recent_decisions": [
                {"date": "2026-05-01", "updated_at": "", "title": "Pricing", "status": "accepted"}
            ],
            "stale_decisions": [
                {"path": "decisions/old.md", "age_days": 30},
            ],
            "recent_research": [
                {"date": "2026-05-01", "updated_at": "", "title": "Market"},
            ],
            "bets": {
                "active": [
                    {
                        "deadline": "2026-05-08",
                        "title": "Launch bet",
                        "status": "open",
                    }
                ],
                "due_soon": [],
                "overdue": [],
                "recent": [],
            },
        },
        "git_activity": {
            "items": [
                {
                    "date": "2026-05-02",
                    "commit": "abc123",
                    "subject": "Update brain",
                    "files": ["core/offer.md", "research/a.md", "decisions/b.md"],
                }
            ]
        },
        "github": {
            "available": True,
            "authenticated": True,
            "assigned_issues": [{"number": 173, "title": "Status"}],
            "review_requests": [],
            "recent_merged_prs": [{"number": 192, "what_shipped": "Daily briefing"}],
            "errors": ["merged PRs: degraded"],
        },
        "readiness": {"level": "ready", "score": 100, "next_actions": ["Run `claude`."]},
        "ranked_actions": [
            {
                "id": "review_due_bets",
                "title": "Review bets due this week",
                "command": "/mb-bet update",
                "reason": "1 active bet has a deadline soon.",
            }
        ],
    }

    status_mod.render_human(report, verbose=True, no_color=True)

    output = capsys.readouterr().out
    assert "Recent decisions" in output
    assert "Stale proposed/running decisions" in output
    assert "Recent research" in output
    assert "Active bets" in output
    assert "Recent git activity" in output
    assert "tasks assigned: 1" in output
    assert "shipped this week: 1" in output
    assert "task #173" in output
    assert "shipped #192" in output
    assert "Review bets due this week" in output


def test_status_renderer_falls_back_to_readiness_actions_for_legacy_reports(capsys) -> None:
    report: dict[str, Any] = {
        "repo": {"path": "/tmp/biz", "looks_like_mainbranch_repo": True},
        "install": {"detail": "mb 0.2.6 (wheel mode)"},
        "runtime": {
            "claude_code": {"found": True},
            "skill_wiring": {"ok": True},
        },
        "git": {"inside_work_tree": True, "branch": "main", "dirty": False},
        "brain": {
            "counts": {
                "core": 0,
                "reference/core": 0,
                "research": 0,
                "decisions": 0,
                "bets": 0,
                "campaigns": 0,
                "log": 0,
                "documents": 0,
            },
            "recent_decisions": [],
            "stale_decisions": [],
            "stale_research": [],
            "recent_research": [],
            "bets": {"active": [], "due_soon": [], "overdue": [], "recent": []},
        },
        "git_activity": {"items": []},
        "github": {
            "available": False,
            "authenticated": False,
            "errors": [],
        },
        "readiness": {
            "level": "ready",
            "score": 100,
            "next_actions": ["Run `claude` in this repo, then `/mb-start`."],
        },
    }

    status_mod.render_human(report, no_color=True)

    output = capsys.readouterr().out
    assert "Run `claude` in this repo, then `/mb-start`." in output


_VALID_TOPOLOGY_REGISTRY = """\
---
type: repo_topology
status: active
schema: mb.repo_topology.v0
home: github:example-co/example
business_display_name: Example Business
repos:
  - slug: example
    display_name: Example Business
    role: business
    lifecycle: active
    github_owner: example-co
    repo_name: example
    remote: github:example-co/example
    visibility: team_private
    relationship: hub_for
    purpose: Hub repo for company strategy and decisions.
  - slug: workshop-site
    display_name: Workshop site
    role: site
    lifecycle: active
    relationship: execution_vehicle_for
    parent: example
    github_owner: example-co
    repo_name: workshop-site
    remote: github:example-co/workshop-site
    visibility: public
---
# Topology
"""


def test_status_exposes_topology_section_when_registry_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    # Ensure no topology registry exists.
    registry_path = repo / "core" / "operations" / "repo-topology.md"
    if registry_path.exists():
        registry_path.unlink()

    report = status_mod.run(path=str(repo), update_marker=False)
    topology = report["topology"]

    assert topology["schema"] == "mb.topology.view.v0"
    assert topology["safe_to_share"] is True
    assert topology["summary"]["registry_found"] is False
    assert topology["summary"]["warnings"] == 0
    assert topology["current_repo"]["matched"] is False
    assert topology["registry"]["found"] is False
    assert topology["registry"]["ok"] is False
    assert topology["local"]["repo_path"] == str(repo.resolve())
    assert topology["local"]["safe_to_share"] is False


def test_status_exposes_topology_section_with_valid_registry(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    registry_path = repo / "core" / "operations" / "repo-topology.md"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(_VALID_TOPOLOGY_REGISTRY, encoding="utf-8")

    report = status_mod.run(path=str(repo), update_marker=False)
    topology = report["topology"]

    assert topology["summary"]["registry_ok"] is True
    assert topology["summary"]["child_repo_count"] >= 1
    # The hub itself should match by github_owner/repo_name fall-through (no
    # remote configured in tmp git), or fall through to descriptor. Either way
    # the registry recorded the hub role for this owner/repo pair.
    registry_repos = topology["registry"]["repos"]
    business_entries = [entry for entry in registry_repos if entry.get("role") == "business"]
    assert business_entries, "expected at least one business role entry"

    public_payload = json.dumps({key: topology[key] for key in topology if key != "local"})
    assert "/Users/" not in public_payload
    assert str(repo.resolve()) not in public_payload


def test_status_human_output_mentions_business_map(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    quiet = runner.invoke(app, ["status", str(repo)])
    assert quiet.exit_code == 0
    assert "Business map" in quiet.stdout

    loud = runner.invoke(app, ["status", str(repo), "--verbose"])
    assert loud.exit_code == 0
    assert "Business map" in loud.stdout
