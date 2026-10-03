"""`mb feedback` — local friction log (#986)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import feedback as feedback_mod
from mb.cli import app

runner = CliRunner()


@pytest.fixture
def state_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    state = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    return state


def _log(state: Path) -> Path:
    return state / "mainbranch" / "feedback.jsonl"


def _lines(state: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in _log(state).read_text(encoding="utf-8").splitlines()]


def test_feedback_appends_one_line_under_xdg_state_home(state_home: Path, tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["feedback", "status said ready", "but", "test failed", "--command", "mb connect test"],
    )
    assert result.exit_code == 0, result.output
    assert "nothing was sent" in result.stdout
    [entry] = _lines(state_home)
    assert entry["kind"] == "feedback"
    assert entry["command"] == "mb connect test"
    assert entry["text"] == "status said ready but test failed"
    assert entry["repo_kind"] in {"hub", "unknown"}
    assert isinstance(entry["mb_version"], str) and entry["mb_version"]
    assert str(entry["time"]).endswith("Z")
    assert set(entry) == {"schema", "kind", "time", "mb_version", "command", "repo_kind", "text"}


def test_feedback_default_state_dir_is_local_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert (
        feedback_mod.feedback_path()
        == tmp_path / ".local" / "state" / "mainbranch" / "feedback.jsonl"
    )


def test_feedback_json_envelope(state_home: Path) -> None:
    result = runner.invoke(app, ["feedback", "confusing message", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mb_command"] == "mb feedback"
    assert payload["result_schema"]["name"] == "mainbranch.feedback.v1"
    assert payload["sent"] is False
    assert payload["entry"]["command"] is None
    assert payload["path"] == "$XDG_STATE_HOME/mainbranch/feedback.jsonl"
    assert str(state_home) not in result.stdout


def test_feedback_empty_text_exits_two(state_home: Path) -> None:
    assert runner.invoke(app, ["feedback"]).exit_code == 2
    assert runner.invoke(app, ["feedback", "   "]).exit_code == 2
    assert not _log(state_home).exists()


@pytest.mark.parametrize(
    "secret_text",
    [
        "token=abcd1234efgh5678ijkl",
        "Authorization: Bearer abcd1234efgh5678ijkl",
        "api_key: abcd1234efgh5678ijkl",
        "pasted ghp_abcd1234efgh5678ijkl by mistake",
        "the access token abcd1234efgh5678ijkl was refused",
    ],
)
def test_feedback_scrubs_secret_values(state_home: Path, secret_text: str) -> None:
    result = runner.invoke(app, ["feedback", secret_text, "--command", f"mb connect {secret_text}"])
    assert result.exit_code == 0
    raw = _log(state_home).read_text(encoding="utf-8")
    assert "abcd1234efgh5678ijkl" not in raw
    assert "<redacted>" in raw


def test_feedback_replaces_home_paths(
    state_home: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    home = tmp_path / "home" / "someone"
    monkeypatch.setenv("HOME", str(home))
    text = f"mb status crashed in {home}/Work/biz and /Users/other/biz and /home/third/biz"
    result = runner.invoke(app, ["feedback", text])
    assert result.exit_code == 0
    [entry] = _lines(state_home)
    assert entry["text"] == "mb status crashed in ~/Work/biz and ~/biz and ~/biz"
    assert str(home) not in _log(state_home).read_text(encoding="utf-8")
    assert "/Users/other" not in entry["text"]


def test_feedback_file_is_private(state_home: Path) -> None:
    runner.invoke(app, ["feedback", "hello"])
    assert _log(state_home).stat().st_mode & 0o777 == 0o600


def test_write_failure_exits_one(state_home: Path) -> None:
    state_home.mkdir(parents=True)
    (state_home / "mainbranch").write_text("not a directory", encoding="utf-8")
    result = runner.invoke(app, ["feedback", "hello", "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["errors"][0]["code"] == "feedback_write_failed"


def test_feedback_scrubs_other_absolute_paths_and_url_secrets(state_home: Path) -> None:
    text = "log at /private/tmp/run/x.log and C:\\work\\biz, url https://x.test/?token=abcd1234efgh"
    assert runner.invoke(app, ["feedback", text]).exit_code == 0
    [entry] = _lines(state_home)
    assert "/private/tmp" not in entry["text"]
    assert "C:\\work" not in entry["text"]
    assert "abcd1234efgh" not in entry["text"]
    assert entry["text"].count("<local-path>") == 2
