"""Shared JSON envelope coverage for high-value ``mb --json`` surfaces."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import onboard as onboard_mod
from mb import start as start_mod
from mb import status as status_mod
from mb.cli import app
from mb.init import run as init_run
from mb.json_result import JSON_RESULT_ENVELOPE_VERSION

runner = CliRunner()


def _tool_path(name: str) -> str:
    if name == "git":
        return shutil.which("git") or ""
    return ""


def _with_claude(name: str) -> str:
    if name == "claude":
        return "/usr/local/bin/claude"
    return shutil.which(name) or ""


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


def _load_json(result: Any) -> dict[str, Any]:
    assert result.stdout
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    return payload


def _assert_envelope(
    payload: dict[str, Any],
    *,
    command: str,
    expected_result_status: str | None = None,
    schema_name: str | None = None,
) -> None:
    assert payload["result_envelope_version"] == JSON_RESULT_ENVELOPE_VERSION
    assert payload["result_schema"] == {
        "name": schema_name or f"{command.replace(' ', '.')}.result",
        "version": JSON_RESULT_ENVELOPE_VERSION,
    }
    assert payload["mb_command"] == command
    assert isinstance(payload["ok"], bool)
    assert payload["result_status"] == (
        expected_result_status or ("ok" if payload["ok"] else "error")
    )
    assert isinstance(payload["errors"], list)
    assert isinstance(payload["warnings"], list)
    assert isinstance(payload["actions"], list)


def test_status_json_uses_shared_result_envelope(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(payload, command="mb status", schema_name="mainbranch.status")
    assert payload["schema"]["name"] == "mainbranch.status"
    assert payload["repo"]["looks_like_mainbranch_repo"] is True
    assert "ranked_actions" in payload


def test_start_json_uses_shared_result_envelope(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(payload, command="mb start", schema_name="mainbranch.start.result")
    assert payload["handoff_ready"] is True
    assert payload["runtime"]["skill_wiring"]["ok"] is True


def test_start_json_launch_conflict_preserves_error_envelope(
    tmp_path: Path, monkeypatch: Any
) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json", "--launch"])

    assert result.exit_code == 2
    payload = _load_json(result)
    _assert_envelope(
        payload,
        command="mb start",
        expected_result_status="error",
        schema_name="mainbranch.start.result",
    )
    assert payload["ok"] is False
    assert payload["errors"] == [
        "`--json` cannot be combined with `--launch`; run without `--json` to launch."
    ]
    assert payload["launch"]["requested"] is True
    assert payload["launch"]["blocked_reason"] == payload["errors"][0]


def test_checkpoint_json_uses_shared_result_envelope(tmp_path: Path) -> None:
    repo = tmp_path / "acme"
    repo.mkdir()
    assert _git(repo, "init").returncode == 0
    (repo / "research").mkdir()
    (repo / "research" / "market.md").write_text("# Market\n", encoding="utf-8")

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(
        payload,
        command="mb checkpoint",
        schema_name="mainbranch.checkpoint.result",
    )
    assert payload["status"] == "ready"
    assert payload["summary"]["surfaces"] == {"research": 1}
    assert payload["proposal"]["message"] == "[added] market.md"


def test_issue_draft_json_uses_shared_result_envelope(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "issue",
            "draft",
            "bug",
            "--repo",
            str(repo),
            "--title",
            "bug: status failed",
            "--command",
            "mb status",
            "--what-happened",
            "failed",
            "--expected",
            "status should render",
            "--no-doctor",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(payload, command="mb issue draft", schema_name="mainbranch.issue.draft.result")
    assert payload["privacy"]["requires_operator_review"] is True
    assert payload["next_command"].startswith("mb issue open .mb/issue-drafts/")


def test_doctor_json_uses_shared_result_envelope(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", str(tmp_path), "--json"])

    assert result.exit_code in {0, 1}
    payload = _load_json(result)
    _assert_envelope(payload, command="mb doctor", schema_name="mainbranch.doctor.result")
    assert payload["repo"] == str(tmp_path.resolve())
    assert "checks" in payload


def test_doctor_repair_json_preserves_domain_schema_shape(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", "repair", "--repo", str(tmp_path), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = _load_json(result)
    _assert_envelope(
        payload,
        command="mb doctor repair",
        schema_name="mainbranch.doctor.repair.result",
    )
    assert payload["schema"] == "mb.doctor.repair"
    assert payload["schema_version"] == 1
    assert payload["mode"] == "plan"


def test_onboard_json_uses_shared_result_envelope(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    monkeypatch.setattr(onboard_mod, "is_interactive", lambda: False)
    repo = tmp_path / "acme"

    result = runner.invoke(
        app,
        ["onboard", "--yes", "--name", "Acme Brewing", "--path", str(repo), "--json"],
    )

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(
        payload,
        command="mb onboard",
        expected_result_status="ok",
        schema_name="mainbranch.onboard.result",
    )
    assert payload["status"] == "ok"
    assert payload["path"] == str(repo.resolve())
    assert payload["onboarding"]["summary"]["status"] == "in_progress"


def test_issue_open_json_fallback_uses_shared_result_envelope(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    draft = runner.invoke(
        app,
        [
            "issue",
            "draft",
            "question",
            "--repo",
            str(repo),
            "--title",
            "question: fallback",
            "--question",
            "How?",
            "--json",
        ],
    )
    draft_payload = _load_json(draft)

    result = runner.invoke(app, ["issue", "open", draft_payload["path"], "--json"])

    assert result.exit_code == 0
    payload = _load_json(result)
    _assert_envelope(payload, command="mb issue open", schema_name="mainbranch.issue.open.result")
    assert payload["submitted"] is False
    assert payload["fallback"] is True


def test_json_result_helper_preserves_existing_domain_schema_and_status() -> None:
    from mb.json_result import envelope

    payload = envelope(
        {
            "ok": True,
            "schema": "mb.doctor.repair",
            "schema_version": 1,
            "status": {"state": "connected"},
        },
        command="mb doctor repair",
        schema_name="mainbranch.doctor.repair.result",
    )

    assert payload["schema"] == "mb.doctor.repair"
    assert payload["schema_version"] == 1
    assert payload["status"] == {"state": "connected"}
    assert payload["result_envelope_version"] == JSON_RESULT_ENVELOPE_VERSION
    assert payload["result_schema"] == {
        "name": "mainbranch.doctor.repair.result",
        "version": JSON_RESULT_ENVELOPE_VERSION,
    }
    assert payload["mb_command"] == "mb doctor repair"
    assert payload["result_status"] == "ok"


def test_json_result_helper_collapses_falsy_lists() -> None:
    from mb.json_result import envelope

    payload = envelope(
        {"errors": False, "warnings": 0, "actions": ""},
        command="mb status",
        schema_name="mainbranch.status",
    )

    assert payload["errors"] == []
    assert payload["warnings"] == []
    assert payload["actions"] == []
