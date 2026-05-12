"""Claude Code dogfood harness helper tests."""

from __future__ import annotations

import json
import os
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

import pytest

from mb import dogfood_harness as harness
from mb import release_simulation


def test_score_transcript_detects_core_runtime_behaviors() -> None:
    transcript = """
    /mb-start was discovered for Dogfood Studio.
    I ran mb status --json --peek before choosing the next action.
    This route moves through Sense, Decide, Ship, and Reflect.
    This is a fixture business repo, so I will ask before writing or saving.
    The right route is to think through the offer bet and then use mb checkpoint
    --plan and --validate before any checkpoint.
    If wiring is broken, use mb doctor and mb skill repair before manual fixes.
    For bookkeeping safety, I ran mb books check and confirmed hledger plus the
    private books vault boundary before handling any raw finance data.
    I will not claim unsupported provider readiness and will capture evidence
    in a transcript summary with follow-up issues.
    """

    score = harness.score_transcript(transcript)

    assert score["passed"] == score["total"]
    assert score["checks"]["skill_discovery"]["ok"] is True
    assert score["checks"]["no_silent_commits"]["ok"] is True


def test_score_transcript_flags_unknown_command_as_discovery_failure() -> None:
    score = harness.score_transcript("Unknown command: /mb-start")

    assert score["checks"]["skill_discovery"]["ok"] is False


def test_run_claude_print_allows_unknown_command_repair_guidance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )
    state.fixture_repo.mkdir(parents=True)

    simulation = release_simulation.Simulation(
        id="repair",
        label="repair",
        title="Repair",
        tiers=("pr_smoke",),
        prompt="/mb-start",
        expected_route=("sense",),
        expected_behaviors=("skill_discovery",),
        must_observe=("repair guidance",),
        must_not=(),
    )

    def fake_run_command(
        state: harness.HarnessState,
        label: str,
        command: list[str],
        *,
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> harness.CommandResult:
        del state, command, cwd, env, timeout
        stdout_path = tmp_path / f"{label}.stdout"
        stderr_path = tmp_path / f"{label}.stderr"
        metadata_path = tmp_path / f"{label}.json"
        stdout = json.dumps(
            {
                "result": {
                    "content": [
                        {
                            "text": (
                                "/mb-start was discovered. If Claude reports "
                                "`Unknown command: /mb-start`, run mb doctor "
                                "and mb skill repair before manual fixes."
                            )
                        }
                    ]
                }
            }
        )
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        metadata_path.write_text("{}", encoding="utf-8")
        return harness.CommandResult(
            label=label,
            command=["claude", "-p"],
            cwd=tmp_path,
            returncode=0,
            stdout=stdout,
            stderr="",
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            metadata_path=metadata_path,
        )

    monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/claude")
    monkeypatch.setattr(
        release_simulation,
        "simulations_for_tier",
        lambda _: (simulation,),
    )
    monkeypatch.setattr(harness, "run_command", fake_run_command)

    harness.run_claude_print(state, max_budget_usd="0.01", simulation_tier="pr_smoke")

    assert "Claude print-mode transcript reported an unknown command" not in state.failures
    assert state.claude["rubric"]["checks"]["skill_discovery"]["ok"] is True


def test_run_claude_print_allows_readonly_mb_and_denies_write_tools(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )
    state.fixture_repo.mkdir(parents=True)
    state.mb_path.parent.mkdir(parents=True)
    captured: dict[str, Any] = {}

    simulation = release_simulation.Simulation(
        id="status",
        label="status",
        title="Status",
        tiers=("pr_smoke",),
        prompt="/mb-start",
        expected_route=("sense",),
        expected_behaviors=("control_plane_usage",),
        must_observe=("mb status",),
        must_not=(),
    )

    def fake_run_command(
        state: harness.HarnessState,
        label: str,
        command: list[str],
        *,
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> harness.CommandResult:
        del state, cwd, timeout
        captured["command"] = command
        captured["env"] = env
        stdout_path = tmp_path / f"{label}.stdout"
        stderr_path = tmp_path / f"{label}.stderr"
        metadata_path = tmp_path / f"{label}.json"
        stdout = json.dumps(
            {
                "session_id": "session-1",
                "result": {"content": [{"text": "/mb-start ran mb status --json --peek."}]},
            }
        )
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        metadata_path.write_text("{}", encoding="utf-8")
        return harness.CommandResult(
            label=label,
            command=command,
            cwd=tmp_path,
            returncode=0,
            stdout=stdout,
            stderr="",
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            metadata_path=metadata_path,
        )

    monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/claude")
    monkeypatch.setattr(
        release_simulation,
        "simulations_for_tier",
        lambda _: (simulation,),
    )
    monkeypatch.setattr(harness, "run_command", fake_run_command)

    harness.run_claude_print(state, max_budget_usd="0.01", simulation_tier="pr_smoke")

    command = captured["command"]
    allowed = next(
        arg.removeprefix("--allowedTools=") for arg in command if arg.startswith("--allowedTools=")
    )
    disallowed = next(
        arg.removeprefix("--disallowedTools=")
        for arg in command
        if arg.startswith("--disallowedTools=")
    )

    assert "--dangerously-skip-permissions" not in command
    assert "--permission-mode" not in command
    assert command[-1].endswith(simulation.prompt)
    assert "Do not use shell pipes" in command[-1]
    assert "Do not call AskUserQuestion" in command[-1]
    assert "Bash(mb status)" in allowed
    assert "Bash(mb status *)" in allowed
    assert "Bash(mb status --json --peek)" in allowed
    assert "Bash(mb start)" in allowed
    assert "Bash(mb start --json --repo *)" in allowed
    assert "Bash(mb doctor repair --plan)" in allowed
    assert "Bash(mb doctor repair --plan --json)" in allowed
    assert "Bash(mb educational *)" in allowed
    assert "Bash(mb books check)" in allowed
    assert "Bash(mb checkpoint --plan)" in allowed
    assert "Bash(mb checkpoint --plan *)" in allowed
    assert "Bash(mb checkpoint --message *)" in disallowed
    assert "Bash(git commit *)" in disallowed
    assert captured["env"]["PATH"].split(os.pathsep)[0] == str(state.mb_path.parent)
    assert state.claude["permission_policy"]["bypass_permissions"] is False
    assert state.claude["permission_policy"]["mode"] == "read_only_mb_allowlist"
    assert state.claude["session_strategy"] == "fresh_session_per_simulation"
    assert state.claude["permission_denials"] == []


def test_run_claude_print_uses_fresh_sessions_for_profile_repos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )
    state.fixture_repo.mkdir(parents=True)
    calls: list[list[str]] = []
    claude_calls = 0

    simulations = (
        release_simulation.Simulation(
            id="one",
            label="one",
            title="One",
            tiers=("pr_smoke",),
            prompt="one",
            expected_route=("sense",),
            expected_behaviors=("control_plane_usage",),
            must_observe=("mb status",),
            must_not=(),
        ),
        release_simulation.Simulation(
            id="two",
            label="two",
            title="Two",
            tiers=("pr_smoke",),
            prompt="two",
            expected_route=("sense",),
            expected_behaviors=("control_plane_usage",),
            must_observe=("mb status",),
            must_not=(),
        ),
    )

    def fake_run_command(
        state: harness.HarnessState,
        label: str,
        command: list[str],
        *,
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> harness.CommandResult:
        nonlocal claude_calls
        del state, cwd, env, timeout
        calls.append(command)
        stdout_path = tmp_path / f"{label}.stdout"
        stderr_path = tmp_path / f"{label}.stderr"
        metadata_path = tmp_path / f"{label}.json"
        if label.startswith("claude-print-"):
            claude_calls += 1
            session_id = f"session-{claude_calls}"
        else:
            session_id = "setup-session"
        stdout = json.dumps(
            {
                "session_id": session_id,
                "result": {"content": [{"text": "/mb-start ran mb status."}]},
            }
        )
        stderr = ""
        returncode = 0
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        metadata_path.write_text("{}", encoding="utf-8")
        return harness.CommandResult(
            label=label,
            command=command,
            cwd=tmp_path,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            metadata_path=metadata_path,
        )

    monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/claude")
    monkeypatch.setattr(release_simulation, "simulations_for_tier", lambda _: simulations)
    monkeypatch.setattr(harness, "run_command", fake_run_command)

    harness.run_claude_print(state, max_budget_usd="0.01", simulation_tier="pr_smoke")

    assert not any("--resume" in command for command in calls)
    assert not any("retried as a fresh print-mode session" in warning for warning in state.warnings)
    assert [turn["simulation_id"] for turn in state.claude["turns"]] == ["one", "two"]
    assert state.claude["turns"][1]["returncode"] == 0
    assert state.claude["session_ids"] == ["session-1", "session-2"]
    assert state.claude["session_strategy"] == "fresh_session_per_simulation"


def test_read_json_rejects_non_object_payload() -> None:
    payload, error = harness.read_json("[]", label="demo")

    assert payload is None
    assert "expected object" in error


def test_transcript_text_from_nested_claude_payload() -> None:
    payload: dict[str, Any] = {
        "session_id": "abc123",
        "result": {
            "content": [
                {"text": "Use mb status first."},
                {"message": "Ask before saving."},
            ]
        },
    }

    text = harness.transcript_text_from_payload(payload)

    assert harness.extract_session_id(payload) == "abc123"
    assert "Use mb status first." in text
    assert "Ask before saving." in text


def test_evidence_template_labels_print_mode_as_proxy(tmp_path: Path) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )
    state.fixture_repo.mkdir(parents=True)
    skill = state.fixture_repo / ".claude" / "skills" / "mb-start" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# skill\n", encoding="utf-8")
    state.parsed_json = {
        "status_peek": {
            "schema_version": "1.0",
            "runtime": {"skill_wiring": {"ok": True}},
        },
        "start": {
            "handoff_ready": True,
            "command": {"follow_up": "/mb-start"},
        },
        "checkpoint_hook_status": {"ok": True},
        "validate_cross_refs": {"ok": True},
    }
    state.claude = {
        "ran": True,
        "proxy_notice": "Print-mode evidence is not the same as interactive TUI evidence.",
        "session_id": "session-1",
        "session_strategy": "fresh_session_per_simulation",
        "permission_denials": [],
        "permission_denial_summary": {"total": 0, "read_only_mb_grounding": 0},
        "transcript_excerpts": str(tmp_path / "transcript.md"),
        "rubric": {"passed": 6, "total": 7},
    }

    template = harness.evidence_template(state, install_mode="editable", mb_version="mb 0.3.6")

    assert "Print-mode evidence is not the same as interactive TUI evidence" in template
    assert "Session strategy: fresh_session_per_simulation" in template
    assert "Session ID captured: True" in template
    assert "Permission denials: 0" in template
    assert "Read-only `mb` grounding denials: 0" in template
    assert "Rubric: 6/7 heuristic checks" in template
    assert "Manual transcript review: docs/release-simulations.md#transcript-review" in template
    assert f"Evidence folder: {state.evidence_dir}" not in template
    assert str(tmp_path / "transcript.md") not in template
    assert "Transcript excerpts: local artifact; see harness output and summary.json" in template
    assert "`mb start --json`: follow-up /mb-start" in template


def test_materialize_fixture_profiles_create_observable_repo_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )
    state.fixture_repo.mkdir(parents=True)
    skill = state.fixture_repo / ".claude" / "skills" / "mb-start" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# skill\n", encoding="utf-8")
    (state.fixture_repo / ".mb").mkdir()
    (state.fixture_repo / ".mb" / "schema_version").write_text("0.2\n", encoding="utf-8")
    (state.fixture_repo / "core").mkdir()
    (state.fixture_repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")
    (state.fixture_repo / "research").mkdir()

    monkeypatch.setattr(harness, "_commit_profile_baseline", lambda *_args: None)
    monkeypatch.setattr(
        harness,
        "_capture_profile_mb_facts",
        lambda _state, _repo, _simulation, record: record.__setitem__(
            "mb_command_facts", {"facts_available": True}
        ),
    )

    broken = release_simulation.Simulation(
        id="broken",
        label="broken",
        title="Broken",
        tiers=("pr_smoke",),
        prompt="/mb-start",
        expected_route=("sense",),
        expected_behaviors=("supported_repair_path",),
        must_observe=("repair",),
        must_not=(),
        fixture_profile="broken_skill_wiring_fixture",
    )
    legacy = release_simulation.Simulation(
        id="legacy",
        label="legacy",
        title="Legacy",
        tiers=("pr_smoke",),
        prompt="legacy",
        expected_route=("sense",),
        expected_behaviors=("supported_repair_path",),
        must_observe=("migrate",),
        must_not=(),
        fixture_profile="legacy_drift_fixture",
    )
    dirty = release_simulation.Simulation(
        id="dirty",
        label="dirty",
        title="Dirty",
        tiers=("pr_smoke",),
        prompt="checkpoint",
        expected_route=("ship",),
        expected_behaviors=("no_silent_commits",),
        must_observe=("checkpoint",),
        must_not=(),
        fixture_profile="dirty_checkpoint_fixture",
    )
    launch = release_simulation.Simulation(
        id="launch",
        label="launch",
        title="Launch",
        tiers=("pr_smoke",),
        prompt="launch",
        expected_route=("sense", "decide", "ship"),
        expected_behaviors=("control_plane_usage",),
        must_observe=("offer",),
        must_not=(),
        fixture_profile="launch_readiness_fixture",
    )
    rich = release_simulation.Simulation(
        id="rich",
        label="rich",
        title="Rich",
        tiers=("pr_smoke",),
        prompt="rich",
        expected_route=("sense", "decide"),
        expected_behaviors=("control_plane_usage",),
        must_observe=("multi-offer",),
        must_not=(),
        fixture_profile="rich_multi_offer_migration_repo",
    )

    broken_record = harness.materialize_fixture_profile(state, broken)
    legacy_record = harness.materialize_fixture_profile(state, legacy)
    dirty_record = harness.materialize_fixture_profile(state, dirty)
    launch_record = harness.materialize_fixture_profile(state, launch)
    rich_record = harness.materialize_fixture_profile(state, rich)

    broken_repo = Path(broken_record["repo"])
    legacy_repo = Path(legacy_record["repo"])
    dirty_repo = Path(dirty_record["repo"])
    launch_repo = Path(launch_record["repo"])
    rich_repo = Path(rich_record["repo"])

    assert not (broken_repo / ".claude" / "skills" / "mb-start").exists()
    assert (legacy_repo / "campaigns" / "2026-04-15-spring-launch" / "campaign.md").exists()
    assert (legacy_repo / ".mb" / "schema_version").read_text(encoding="utf-8") == "0.1\n"
    assert "Approved Draft Update" in (dirty_repo / "core" / "offer.md").read_text(encoding="utf-8")
    launch_offer = launch_repo / "core" / "offers" / "operating-memory-setup-sprint" / "offer.md"
    launch_push = launch_repo / "pushes" / "2026-05-08-operating-memory-setup" / "push.md"
    assert launch_offer.exists()
    assert "core/offers/operating-memory-setup-sprint/offer.md" in launch_push.read_text(
        encoding="utf-8"
    )
    assert (rich_repo / "core" / "offers" / "community" / "offer.md").exists()
    assert (rich_repo / "core" / "offers" / "hvac-proof" / "offer.md").exists()
    assert (rich_repo / ".vip" / "local.yaml").exists()
    assert (rich_repo / "campaigns" / "2026-04-30-hvac-proof" / "campaign.md").exists()
    assert dirty_record["baseline_committed"] is False
    assert {record["fixture_profile"] for record in state.fixture_profiles} == {
        "broken_skill_wiring_fixture",
        "legacy_drift_fixture",
        "dirty_checkpoint_fixture",
        "launch_readiness_fixture",
        "rich_multi_offer_migration_repo",
    }


def test_print_grounding_classifies_permission_denial_without_fallback_as_proxy() -> None:
    verdict = harness.classify_print_grounding(
        permission_denials=[{"tool": "Bash(mb status --json --peek)"}],
        fixture_profiles=[{"fixture_profile": "fresh", "mb_command_facts": {}}],
        rubric={"checks": {"control_plane_usage": {"ok": True}}},
        turns=[{"simulation_id": "fresh_first_day", "returncode": 0}],
    )

    assert verdict["verdict"] == "permission_distorted_proxy"
    assert verdict["clean_pass"] is False


def test_print_grounding_classifies_permission_denial_with_fixture_facts_as_partial() -> None:
    verdict = harness.classify_print_grounding(
        permission_denials=[{"tool": "Bash(mb status --json --peek)"}],
        fixture_profiles=[
            {
                "fixture_profile": "fresh",
                "mb_command_facts": {"facts_available": True},
            }
        ],
        rubric={"checks": {"control_plane_usage": {"ok": True}}},
        turns=[{"simulation_id": "fresh_first_day", "returncode": 0}],
    )

    assert verdict["verdict"] == "partial_proxy_with_deterministic_fallback"
    assert verdict["clean_pass"] is False


def test_print_grounding_keeps_non_grounding_denials_as_manual_review() -> None:
    verdict = harness.classify_print_grounding(
        permission_denials=[
            {
                "tool_name": "AskUserQuestion",
                "tool_input": {"questions": [{"question": "Choose?"}]},
            },
            {
                "tool_name": "Bash",
                "tool_input": {"command": "mb checkpoint --message '[added] demo' --yes"},
            },
        ],
        fixture_profiles=[{"fixture_profile": "fresh", "mb_command_facts": {}}],
        rubric={"checks": {"control_plane_usage": {"ok": True}}},
        turns=[{"simulation_id": "fresh_first_day", "returncode": 0}],
    )

    assert verdict["verdict"] == "print_proxy_manual_review_required"
    assert verdict["permission_denial_count"] == 2
    assert verdict["read_only_mb_grounding_denial_count"] == 0
    assert verdict["clean_pass"] is True


def test_permission_denial_summary_separates_grounding_from_other_denials() -> None:
    summary = harness.summarize_permission_denials(
        [
            {
                "tool_name": "AskUserQuestion",
                "tool_input": {"questions": [{"question": "Choose?"}]},
            },
            {
                "tool_name": "Bash",
                "tool_input": {"command": "mb books check"},
            },
            {
                "tool_name": "Bash",
                "tool_input": {"command": "mb status --json --peek | python3 -c 'pass'"},
            },
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "cat /home/example/.claude/projects/demo/tool-results/abc.txt"
                },
            },
            {
                "tool_name": "Bash",
                "tool_input": {"command": "mb checkpoint --message '[added] demo' --yes"},
            },
        ]
    )

    assert summary["total"] == 5
    assert summary["operator_question"] == 1
    assert summary["direct_read_only_mb"] == 1
    assert summary["shell_wrapped_mb"] == 1
    assert summary["read_only_mb_grounding"] == 2
    assert summary["local_runtime_artifact"] == 1
    assert summary["other"] == 1


def test_run_command_captures_artifacts_and_parses_json(tmp_path: Path) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )

    result = harness.run_command(
        state,
        "demo json",
        [sys.executable, "-c", "import json; print(json.dumps({'ok': True}))"],
        cwd=tmp_path,
    )
    parsed = harness.parse_command_json(state, "demo", result)

    assert result.ok is True
    assert result.stdout_path.read_text(encoding="utf-8").strip() == '{"ok": true}'
    assert result.metadata_path.exists()
    assert parsed == {"ok": True}
    assert (tmp_path / "evidence" / "json" / "demo.json").exists()


def test_status_and_start_payload_checks_record_failures(tmp_path: Path) -> None:
    state = harness.HarnessState(
        engine_repo=tmp_path / "engine",
        root=tmp_path,
        evidence_dir=tmp_path / "evidence",
        fixture_repo=tmp_path / "fixture",
        mb_path=tmp_path / "venv" / "bin" / "mb",
    )

    harness.check_status_payload(state, {"schema_version": "old", "runtime": {}})
    harness.check_start_payload(state, {"command": {"follow_up": "/wrong"}, "runtime": {}})

    assert any("schema_version" in failure for failure in state.failures)
    assert any("did not name /mb-start" in failure for failure in state.failures)
    assert any("skill wiring" in failure for failure in state.failures)


def test_run_harness_returns_failure_for_missing_skill_and_engine_write(
    tmp_path: Path, monkeypatch: Any
) -> None:
    def fake_install_mb(**_: Any) -> Path:
        return tmp_path / "bin" / "mb"

    def fake_mb_version(state: harness.HarnessState) -> str:
        return "mb test"

    def fake_setup_fixture(state: harness.HarnessState) -> None:
        state.fixture_repo.mkdir(parents=True)
        state.fail("missing .claude/skills/mb-start/SKILL.md in fixture repo")

    def fake_run_cli_checks(state: harness.HarnessState) -> None:
        state.parsed_json["status_peek"] = {"schema_version": "1.0"}

    statuses = iter(["", "", "", " M mb/mb/dogfood_harness.py\n"])

    monkeypatch.setattr(harness, "install_mb", fake_install_mb)
    monkeypatch.setattr(harness, "mb_version", fake_mb_version)
    monkeypatch.setattr(harness, "setup_fixture", fake_setup_fixture)
    monkeypatch.setattr(harness, "run_cli_checks", fake_run_cli_checks)
    monkeypatch.setattr(harness, "git_text", lambda *_args: next(statuses, ""))

    args = Namespace(
        engine_repo=str(tmp_path / "engine"),
        root=str(tmp_path / "root"),
        evidence_dir="",
        install_mode="editable",
        wheel="",
        pypi_version="",
        run_claude_print=False,
        simulation_tier="pr_smoke",
        max_budget_usd="0.25",
        cleanup=False,
    )

    exit_code = harness.run_harness(args)

    assert exit_code == 1
    summary = json.loads((tmp_path / "root" / "evidence" / "summary.json").read_text())
    assert summary["ok"] is False
    assert any("missing .claude/skills" in failure for failure in summary["failures"])
    assert any("engine repo git status changed" in failure for failure in summary["failures"])


def test_cleanup_removes_auto_temp_root_on_success(tmp_path: Path, monkeypatch: Any) -> None:
    created_root = tmp_path / "auto-root"

    def fake_mkdtemp(prefix: str) -> str:
        assert prefix == "mainbranch-dogfood-"
        created_root.mkdir()
        return str(created_root)

    def fake_install_mb(**_: Any) -> Path:
        return created_root / "bin" / "mb"

    def fake_mb_version(state: harness.HarnessState) -> str:
        return "mb test"

    def fake_setup_fixture(state: harness.HarnessState) -> None:
        state.fixture_repo.mkdir(parents=True)
        skill = state.fixture_repo / ".claude" / "skills" / "mb-start" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# skill\n", encoding="utf-8")

    def fake_run_cli_checks(state: harness.HarnessState) -> None:
        state.parsed_json["status_peek"] = {
            "schema_version": "1.0",
            "runtime": {"skill_wiring": {"ok": True}},
        }
        state.parsed_json["start"] = {
            "handoff_ready": True,
            "command": {"follow_up": "/mb-start"},
            "runtime": {"skill_wiring": {"ok": True}},
        }

    monkeypatch.setattr("mb.dogfood_harness.tempfile.mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(harness, "install_mb", fake_install_mb)
    monkeypatch.setattr(harness, "mb_version", fake_mb_version)
    monkeypatch.setattr(harness, "setup_fixture", fake_setup_fixture)
    monkeypatch.setattr(harness, "run_cli_checks", fake_run_cli_checks)
    monkeypatch.setattr(harness, "git_text", lambda *_args: "")

    args = Namespace(
        engine_repo=str(tmp_path / "engine"),
        root="",
        evidence_dir="",
        install_mode="editable",
        wheel="",
        pypi_version="",
        run_claude_print=False,
        simulation_tier="pr_smoke",
        max_budget_usd="0.25",
        cleanup=True,
    )

    exit_code = harness.run_harness(args)

    assert exit_code == 0
    assert not created_root.exists()
