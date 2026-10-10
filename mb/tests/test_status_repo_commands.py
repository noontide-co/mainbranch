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
    _names_the_business_once(wiring["mb_installs"]["repair_command"], business)
    _names_the_business_once(wiring["shadow_report"]["repair_command"], business)
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


def test_status_validation_repairs_name_the_business(business: Path) -> None:
    campaign = business / "campaigns" / "spring" / "campaign.md"
    campaign.parent.mkdir(parents=True)
    campaign.write_text("---\ntype: campaign\nstatus: draft\n---\n# Spring\n")
    result = runner.invoke(app, ["status", str(business), "--json"])
    assert result.exit_code in {0, 1}, result.output
    validation = json.loads(result.stdout)["validation"]
    drift = validation["validation_categories"]["by_category"]["migration_drift"]
    _names_the_business_once(drift["repair"], business)
    _names_the_business_once(drift["operator_summary"], business)
    steps = [s for s in validation["legacy_repair"]["next_steps"] if "`mb " in s]
    assert steps
    for step in steps:
        _names_the_business_once(step, business)


def test_status_qualifies_any_provider_repair_command_in_its_own_report(business: Path) -> None:
    """The walker covers `repair_command` and `repair` everywhere, connect providers included."""
    report: dict[str, Any] = {
        "integrations": {
            "providers": [
                {"repair_command": "mb connect hydrate --repo ."},
                {"repair": "Run `mb connect hydrate --repo .` from this workspace."},
            ]
        },
        "mb_command": "mb status",
        "runtime": {"codex_cli": {"fact_commands": ["mb status --json --peek"]}},
    }
    status.qualify_commands(report, business)
    providers = report["integrations"]["providers"]
    _names_the_business_once(providers[0]["repair_command"], business)
    _names_the_business_once(providers[1]["repair"], business)
    assert report["mb_command"] == "mb status"
    assert report["runtime"]["codex_cli"]["fact_commands"] == ["mb status --json --peek"]


def _plan_command_words(command: str) -> list[str]:
    return shlex.split(command)[1:]


def test_readiness_next_actions_name_the_business_and_the_plan_runs_there(business: Path) -> None:
    cwd = Path.cwd()
    actions = _status(business)["readiness"]["next_actions"]
    repairs = [a for a in actions if "mb doctor repair" in a]
    assert repairs
    for action in repairs:
        _names_the_business_once(action, business)
    plan = [part for part in repairs[0].split("`")[1::2] if "--plan" in part][0]
    result = runner.invoke(app, [*_plan_command_words(plan), "--json"])
    assert result.exit_code in {0, 1}, result.output
    assert json.loads(result.stdout)["repo"] == str(business)
    assert list(cwd.iterdir()) == []


def test_readiness_next_actions_in_the_human_fallback_name_the_business(
    business: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COLUMNS", "400")
    report = status.run(path=str(business), update_marker=False, validation_cross_refs=False)
    report["ranked_actions"] = []  # no ranked actions: the plain readiness list is printed
    status.qualify_commands(report, business)
    status.render_human(report, no_color=True)
    printed = [line for line in capsys.readouterr().out.splitlines() if "mb doctor repair" in line]
    assert printed
    for line in printed:
        _names_the_business_once(line, business)


def test_start_json_names_the_business_and_its_skill_link_runs_there(business: Path) -> None:
    cwd = Path.cwd()
    result = runner.invoke(app, ["start", "--repo", str(business), "--json"])
    assert result.exit_code in {0, 1}, result.output
    report = json.loads(result.stdout)
    wiring = report["runtime"]["skill_wiring"]
    _names_the_business_once(wiring["repair_command"], business)
    _names_the_business_once(wiring["shadow_report"]["repair_command"], business)
    assert report["update"]["command"] == f"mb update --repo {shlex.quote(str(business))}"
    for action in report["next_actions"]:
        assert " --repo ." not in action
    assert any(f"--repo {shlex.quote(str(business))}" in a for a in report["next_actions"])
    linked = runner.invoke(app, [*_plan_command_words(wiring["repair_command"]), "--json"])
    assert linked.exit_code == 0, linked.output
    assert (business / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file()
    assert list(cwd.iterdir()) == []


def test_start_json_launch_conflict_names_the_business(business: Path) -> None:
    result = runner.invoke(app, ["start", "--repo", str(business), "--json", "--launch"])
    assert result.exit_code == 2, result.output
    command = json.loads(result.stdout)["runtime"]["skill_wiring"]["repair_command"]
    _names_the_business_once(command, business)


def test_start_inside_the_repo_keeps_its_bare_commands(
    business: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(business)
    result = runner.invoke(app, ["start", "--json"])
    report = json.loads(result.stdout)
    assert report["runtime"]["skill_wiring"]["repair_command"] == "mb skill link --repo ."
    assert report["update"]["command"] == "mb update"
    assert report["books"]["next_command"] in {
        "mb books status --json",
        "mb books doctor --plan --json",
    }


def test_legacy_repair_next_steps_in_the_repair_plan_name_the_business(business: Path) -> None:
    campaign = business / "campaigns" / "spring" / "campaign.md"
    campaign.parent.mkdir(parents=True)
    campaign.write_text("---\ntype: campaign\nstatus: draft\n---\n# Spring\n")
    result = runner.invoke(app, ["doctor", "repair", "--repo", str(business), "--plan", "--json"])
    assert result.exit_code in {0, 1}, result.output
    plan = json.loads(result.stdout)
    steps: list[str] = []

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            steps.extend(node["next_steps"]) if "next_steps" in node else None
            for key, value in node.items():
                if key != "raw":
                    collect(value)
        elif isinstance(node, list):
            for item in node:
                collect(item)

    collect(plan)
    commands = [s for s in steps if "`mb " in s]
    assert commands
    for step in commands:
        _names_the_business_once(step, business)
    raw = plan["raw"]["validation"]["legacy_repair"]["next_steps"]
    assert "Run `mb validate --json` and group failures by missing key or status enum." in raw
    emitted = [part for part in commands[0].split("`")[1::2] if part.startswith("mb ")][0]
    validated = runner.invoke(app, _plan_command_words(emitted))
    assert json.loads(validated.stdout)["repo"] == str(business)


def test_books_next_command_names_the_business_and_runs_there(business: Path) -> None:
    command = _status(business)["books"]["next_command"]
    assert command.startswith("mb books ")
    assert command.endswith(f" {shlex.quote(str(business))}")
    assert command.count(shlex.quote(str(business))) == 1
    result = runner.invoke(app, _plan_command_words(command))
    assert result.exit_code in {0, 1}, result.output
    assert json.loads(result.stdout)["repo"] == str(business)


def _site_record(business: Path, site: Path) -> None:
    (site / ".mainbranch").mkdir(parents=True)
    (site / ".mainbranch" / "conversion.json").write_text(json.dumps({"schema_version": "1.0"}))
    push = business / "pushes" / "spring" / "push.md"
    push.parent.mkdir(parents=True)
    push.write_text(f"---\ntype: push\nstatus: active\nsite_repo_path: {site}\n---\n# Spring\n")


def test_measurement_repair_command_names_the_business_and_the_site(
    business: Path, tmp_path: Path
) -> None:
    site = tmp_path / "site repo"
    _site_record(business, site)
    command = _status(business)["measurement"]["repair_command"]
    quoted = shlex.quote(str(business))
    assert command == f'mb site check "{site}" --business-repo {quoted}'
    assert command.count(quoted) == 1
    words = _plan_command_words(command)
    assert words[2] == str(site)
    result = runner.invoke(app, [*words, "--json"])
    assert result.exit_code in {0, 1}, result.output
    assert json.loads(result.stdout)["business_repo"] == str(business)


def test_measurement_site_path_with_shell_characters_is_shell_quoted(tmp_path: Path) -> None:
    plain = tmp_path / "site"
    assert status._shell_arg(plain) == f'"{plain}"'
    odd = tmp_path / "it's $HOME `x`"
    assert shlex.split(status._shell_arg(odd)) == [str(odd)]


def test_status_inside_the_repo_keeps_the_bare_site_and_books_commands(
    business: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    site = tmp_path / "site"
    _site_record(business, site)
    monkeypatch.chdir(business)
    report = _status(business)
    assert report["measurement"]["repair_command"] == f'mb site check "{site}" --business-repo .'
    assert report["books"]["next_command"] in {
        "mb books status --json",
        "mb books doctor --plan --json",
    }
    assert "--repo" not in " ".join(report["readiness"]["next_actions"])


def test_status_leaves_commands_under_skipped_keys_as_written(business: Path) -> None:
    """A key that would be qualified stays as written under every skipped key."""
    bare = {
        "command": "mb skill link --repo .",
        "repair_command": "mb update",
        "repair": "Run `mb skill link --repo .`.",
        "next_steps": ["Run `mb validate --json`."],
    }
    skip_keys = (
        "raw",
        "result",
        "mb_command",
        "workflow_inventory",
        "fact_commands",
        "missing_markers",
        "smoke_command",
    )  # spelled out: the test must not read the skip list it guards
    report: dict[str, Any] = {key: {"nested": dict(bare)} for key in skip_keys}
    report["owned"] = dict(bare)
    status.qualify_commands(report, business)
    for key in skip_keys:
        assert report[key] == {"nested": bare}, key
    assert report["owned"] != bare
    _names_the_business_once(report["owned"]["command"], business)


def test_status_qualifies_only_the_next_actions_it_owns(business: Path) -> None:
    report: dict[str, Any] = {
        "readiness": {"next_actions": ["Run `mb doctor repair --plan`."]},
        "launch": {
            "next_actions": ["mb site check <site-repo> --business-repo <business-repo> --json"]
        },
        "ads": {"next_actions": ["mb update"]},
        "update": {"next_actions": ["mb update"]},
    }
    status.qualify_commands(report, business)
    _names_the_business_once(report["readiness"]["next_actions"][0], business)
    assert report["launch"]["next_actions"] == [
        "mb site check <site-repo> --business-repo <business-repo> --json"
    ]
    assert report["ads"]["next_actions"] == ["mb update"]
    assert report["update"]["next_actions"] == ["mb update"]
