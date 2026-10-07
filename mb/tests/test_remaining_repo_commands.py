"""Remaining #1083 suggestions act on the named business repo from any folder."""

from __future__ import annotations

import json
import re
import shlex
import shutil
import socket
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import codex, doctor, engine, freshness, onboard, update
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
    for module in (doctor, engine, freshness, update):
        monkeypatch.setattr(module, "install_mode", lambda: "pipx")

    def no_network(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("unexpected network request")

    monkeypatch.setattr(socket, "create_connection", no_network)
    repo = tmp_path / "Acme's café & studio"
    init_run(path=str(repo), name="Acme")
    campaign = repo / "campaigns" / "spring" / "campaign.md"
    campaign.parent.mkdir(parents=True)
    campaign.write_text("---\ntype: campaign\nstatus: draft\n---\n# Spring\n")
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    return repo.resolve()


def _json(args: list[str]) -> dict[str, Any]:
    result = runner.invoke(app, [*args, "--json"])
    assert result.exit_code in {0, 1}, result.output
    assert result.exception is None or isinstance(result.exception, SystemExit), result.exception
    payload: dict[str, Any] = json.loads(result.stdout)
    return payload


@pytest.mark.parametrize("inside", [False, True], ids=["outside", "inside"])
@pytest.mark.parametrize("surface", ["freshness", "doctor", "status"])
def test_post_update_commands_target_the_business(
    business: Path, monkeypatch: pytest.MonkeyPatch, inside: bool, surface: str
) -> None:
    if inside:
        monkeypatch.chdir(business)
    if surface == "freshness":
        payload = freshness.package_update_status(business)
    elif surface == "doctor":
        payload = _json(["doctor", str(business)])["update"]
    else:
        payload = _json(["status", str(business), "--peek"])["update"]
    flag = "" if inside else f" --repo {shlex.quote(str(business))}"
    assert payload["post_update_commands"] == [
        f"mb skill link{flag or ' --repo .'}",
        "mb doctor" if inside else f"mb doctor {shlex.quote(str(business))}",
    ]


def test_emitted_skill_link_writes_into_business_and_leaves_cwd_empty(business: Path) -> None:
    shutil.rmtree(business / ".claude" / "skills")
    cwd = Path.cwd()
    command = freshness.package_update_status(business)["post_update_commands"][0]
    result = runner.invoke(app, shlex.split(command)[1:])
    assert result.exit_code == 0, result.output
    assert (business / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file()
    assert list(cwd.iterdir()) == []
    doctor_command = freshness.package_update_status(business)["post_update_commands"][1]
    assert _json(shlex.split(doctor_command)[1:])["repo"] == str(business)
    assert list(cwd.iterdir()) == []


@pytest.mark.parametrize("inside", [False, True], ids=["outside", "inside"])
@pytest.mark.parametrize("surface", ["doctor", "status", "onboard"])
def test_onboarding_next_actions_name_the_business(
    business: Path, monkeypatch: pytest.MonkeyPatch, inside: bool, surface: str
) -> None:
    if inside:
        monkeypatch.chdir(business)
    if surface == "doctor":
        payload = _json(["doctor", str(business)])["onboarding"]
    elif surface == "status":
        payload = _json(["status", str(business), "--peek"])["onboarding"]
    else:
        payload = onboard.onboarding_status(business)
    steps = {step["id"]: step["next_action"] for step in payload["checklist"]}
    flag = "" if inside else f" --repo {shlex.quote(str(business))}"
    assert steps["runtime_handoff"] == (
        f"Run `mb skill link{flag or ' --repo .'}`, then `mb start{flag} --json`."
    )
    assert steps["checkpoint_hook"] == (
        f"Run `mb doctor repair{flag} --plan`, then `mb doctor repair{flag} --apply`."
    )
    assert steps["core_reference"] == (
        "Collect just enough to draft core offer, audience, voice, soul, and proof files."
    )


@pytest.mark.parametrize("inside", [False, True], ids=["outside", "inside"])
def test_doctor_check_details_agree_with_update_and_migration_commands(
    business: Path, monkeypatch: pytest.MonkeyPatch, inside: bool
) -> None:
    if inside:
        monkeypatch.chdir(business)
    payload = _json(["doctor", str(business)])
    checks = {check["name"]: check for check in payload["checks"]}
    flag = "" if inside else f" --repo {shlex.quote(str(business))}"
    assert payload["update"]["command"] == f"mb update{flag}"
    assert f"`{payload['update']['command']}`" in checks["mainbranch-version"]["detail"]
    assert f"`mb migrate{flag} campaigns --plan`" in checks["legacy-campaigns"]["detail"]


@pytest.mark.parametrize("inside", [False, True], ids=["outside", "inside"])
def test_repair_receipt_details_and_fallback_commands_name_the_business(
    business: Path, monkeypatch: pytest.MonkeyPatch, inside: bool
) -> None:
    if inside:
        monkeypatch.chdir(business)
    payload = _json(["doctor", "repair", "--repo", str(business), "--plan"])
    flag = "" if inside else f" --repo {shlex.quote(str(business))}"
    assert payload["receipt"]["skipped_surfaces"] == [
        f"claude: run mb doctor repair{flag} --apply --only claude",
        f"codex: run mb doctor repair{flag} --apply --only codex",
    ]
    checks = {
        check["name"]: check
        for section in payload["sections"]
        for check in section.get("checks", [])
    }
    assert f"`mb update{flag}`" in checks["mainbranch-version"]["summary"]
    assert f"`mb migrate{flag} campaigns --plan`" in checks["legacy-campaigns"]["summary"]
    expected = [
        f"mb start{flag} --json",
        f"mb doctor repair{flag} --plan",
        f"mb doctor repair{flag} --apply",
    ]
    assert checks["project-local-skills"]["fallback_commands"] == expected
    assert engine.link_status(business)["fallback_commands"] == expected
    assert "--repo" not in json.dumps(payload["raw"]["migration_drift"])


def test_prose_rewriter_leaves_free_text_and_diagnostic_copies_alone(business: Path) -> None:
    text = "Discussion of mb update and mb migrate campaigns --plan is free text."
    payload = {
        "receipt": {"skipped_surfaces": ["codex", text]},
        "raw": {"skipped_surfaces": ["claude: run mb doctor repair --apply --only claude"]},
        "result": {"command": "mb update"},
    }
    before = json.dumps(payload)
    doctor._qualify_report(payload, business)
    assert json.dumps(payload) == before
    assert doctor._qualify_prose(text, business) == text
    assert re.findall(r"`([^`]+)`", doctor._qualify_prose("Run `mb update`.", business)) == [
        f"mb update --repo {shlex.quote(str(business))}"
    ]
