"""Claude Code dogfood harness helper tests."""

from __future__ import annotations

import json
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
        timeout: int | None = None,
    ) -> harness.CommandResult:
        del state, command, cwd, timeout
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
        "transcript_excerpts": str(tmp_path / "transcript.md"),
        "rubric": {"passed": 6, "total": 7},
    }

    template = harness.evidence_template(state, install_mode="editable", mb_version="mb 0.3.6")

    assert "Print-mode evidence is not the same as interactive TUI evidence" in template
    assert "Session ID preserved: True" in template
    assert "Rubric: 6/7 heuristic checks" in template
    assert "Manual transcript review: docs/release-simulations.md#transcript-review" in template
    assert f"Evidence folder: {state.evidence_dir}" not in template
    assert str(tmp_path / "transcript.md") not in template
    assert "Transcript excerpts: local artifact; see harness output and summary.json" in template
    assert "`mb start --json`: follow-up /mb-start" in template


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
