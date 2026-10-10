"""`mb status` and `mb spine` suggested commands name the business repo (#1083).

Every case runs from a folder that is not the business repo, so a bare
`--repo .` or a command with no repo would act on the wrong folder.
"""

from __future__ import annotations

import json
import shlex
import shutil
import socket
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import codex, doctor, engine, freshness, status, update
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


@pytest.fixture
def business(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(home / ".codex"))
    monkeypatch.setattr(doctor, "_net", lambda: (True, "offline fixture"))
    monkeypatch.setattr(freshness, "latest_pypi_version", lambda: "99.0.0")
    monkeypatch.setattr(update, "_latest_pypi_version", lambda: "99.0.0")
    monkeypatch.setattr(codex, "_which", lambda name: "")
    for module in (doctor, engine, freshness, update, status):
        monkeypatch.setattr(module, "install_mode", lambda: "pipx")

    def no_network(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("unexpected network request")

    monkeypatch.setattr(socket, "create_connection", no_network)
    repo = tmp_path / "Acme's café & studio"
    init_run(path=str(repo), name="Acme")
    shutil.rmtree(repo / ".claude" / "skills")
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    return repo.resolve()


def _status(business: Path) -> dict[str, Any]:
    result = runner.invoke(app, ["status", str(business), "--peek", "--json"])
    assert result.exit_code in {0, 1}, result.output
    payload: dict[str, Any] = json.loads(result.stdout)
    return payload


def _names_the_business_once(text: str, business: Path) -> None:
    """Each `mb` command in a command line or sentence names the business exactly once."""
    quoted = shlex.quote(str(business))
    commands = [part for part in text.split("`")[1::2] if part.startswith("mb ")] or [text]
    for command in commands:
        assert command.count(quoted) == 1, text
        assert " --repo ." not in command, text


def test_status_wiring_repairs_name_the_business_from_another_folder(business: Path) -> None:
    report = _status(business)
    wiring = report["runtime"]["skill_wiring"]
    assert not wiring["ok"]
    _names_the_business_once(wiring["repair_command"], business)
    assert wiring["repair_command"].startswith("mb skill link --repo ")
    for item in report["drift"]["items"]:
        if item["id"] == "broken_skill_wiring":
            _names_the_business_once(item["repair"], business)
            break
    else:
        pytest.fail("no broken_skill_wiring drift item")


def test_status_ranked_action_and_update_commands_name_the_business(business: Path) -> None:
    report = _status(business)
    repair = next(a for a in report["ranked_actions"] if a["id"] == "repair_skill_wiring")
    _names_the_business_once(repair["command"], business)
    assert report["update"]["command"] == f"mb update --repo {shlex.quote(str(business))}"
    assert (
        report["update"]["update_check_command"]
        == f"mb update --repo {shlex.quote(str(business))} --check --json"
    )


def test_status_emitted_skill_link_acts_on_the_business_not_the_folder(business: Path) -> None:
    cwd = Path.cwd()
    command = _status(business)["runtime"]["skill_wiring"]["repair_command"]
    result = runner.invoke(app, [*shlex.split(command)[1:], "--json"])
    assert result.exit_code == 0, result.output
    assert (business / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file()
    assert list(cwd.iterdir()) == []


def test_status_inside_the_repo_keeps_its_bare_commands(
    business: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(business)
    report = _status(business)
    assert report["runtime"]["skill_wiring"]["repair_command"] == "mb skill link --repo ."
    assert report["update"]["command"] == "mb update"
    assert report["update"]["update_check_command"] == "mb update --check --json"


def test_status_leaves_commands_it_does_not_own_as_written(business: Path) -> None:
    report = _status(business)
    assert report["mb_command"] == "mb status"
    commands = report["runtime"]["codex_cli"]["fact_commands"]
    assert "mb status --json --peek" in commands
    inventory = report["runtime"]["codex_cli"]["workflow_inventory"]
    assert "mb start --json" in json.dumps(inventory)


def test_spine_show_summary_names_the_business_and_its_command_declares_there(
    business: Path,
) -> None:
    cwd = Path.cwd()
    result = runner.invoke(app, ["spine", "show", "--repo", str(business), "--json"])
    assert result.exit_code == 1, result.output
    summary = json.loads(result.stdout)["summary"]
    suggested = summary.split("`")[1]
    _names_the_business_once(suggested, business)
    words = shlex.split(suggested)
    declared = runner.invoke(app, [*words[1:], "--store", "none", "--intentional", "--json"])
    assert declared.exit_code == 0, declared.output
    assert (business / "core" / "operations" / "spine.md").is_file()
    assert list(cwd.iterdir()) == []


def test_spine_init_summary_names_the_business(business: Path) -> None:
    result = runner.invoke(app, ["spine", "init", "--owned", "--repo", str(business), "--json"])
    assert result.exit_code == 0, result.output
    summary = json.loads(result.stdout)["summary"]
    _names_the_business_once(summary.split("`")[1], business)
