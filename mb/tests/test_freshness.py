"""Package freshness metadata and update alert copy."""

from __future__ import annotations

from pathlib import Path

import pytest

from mb.freshness import compare_versions, format_update_alert, package_update_status


def test_required_update_status_for_version_below_minimum(tmp_path: Path) -> None:
    update = package_update_status(
        tmp_path,
        installed_version="0.1.2",
        latest_version="0.2.1",
        mode="pipx",
    )

    assert update["installed"] == "0.1.2"
    assert update["latest"] == "0.2.1"
    assert update["minimum_supported"] == "0.2.0"
    assert update["severity"] == "required"
    assert update["command"] == "pipx upgrade mainbranch"
    assert update["update_check_command"] == "mb update --check --json"
    assert update["post_update_commands"] == ["mb skill link --repo .", "mb doctor"]
    assert update["latest_source"] == "provided"
    assert update["release_notes_url"].endswith("/oe-v0.2.1")
    assert update["reason"] == (
        "Installed version predates mb update and the current skill-link repair flow."
    )

    alert = format_update_alert(update)
    assert "Update required." in alert
    assert "setup and skills may not work correctly" in alert
    assert "pipx upgrade mainbranch" in alert
    assert "mb update is not available in 0.1.2" in alert
    assert "mb skill link --repo ." in alert
    assert "mb doctor" in alert


def test_required_update_without_repo_still_has_generic_repair_commands() -> None:
    update = package_update_status(
        None,
        installed_version="0.1.2",
        latest_version="0.2.1",
        mode="pipx",
    )

    assert update["post_update_commands"] == ["mb skill link --repo .", "mb doctor"]
    alert = format_update_alert(update)
    assert "Then, from your business repo:" in alert
    assert "mb skill link --repo ." in alert
    assert "mb doctor" in alert


def test_recommended_update_status_for_supported_stale_version(tmp_path: Path) -> None:
    update = package_update_status(
        tmp_path,
        installed_version="0.2.0",
        latest_version="0.2.1",
        mode="pipx",
    )

    assert update["severity"] == "recommended"
    assert update["command"] == "mb update"
    assert update["update_check_command"] == "mb update --check --json"
    assert update["installed"] == "0.2.0"
    assert update["latest"] == "0.2.1"
    assert update["minimum_supported"] == "0.2.0"
    assert update["latest_source"] == "provided"
    assert update["release_notes_url"].endswith("/oe-v0.2.1")

    alert = format_update_alert(update)
    assert "Update recommended." in alert
    assert "Your install is still supported" in alert
    assert "mb update" in alert


def test_current_source_install_does_not_render_alert(tmp_path: Path) -> None:
    update = package_update_status(
        tmp_path,
        installed_version="0.2.0",
        latest_version="0.2.1",
        mode="source",
    )

    assert update["severity"] == "current"
    assert update["latest"] == "0.2.1"
    assert update["latest_source"] == "not_applicable"
    assert update["update_check_command"] == ""
    assert format_update_alert(update) == ""


@pytest.mark.parametrize(
    ("mode", "command"),
    [
        ("pipx", "pipx upgrade mainbranch"),
        ("uv", "uv tool install --refresh-package mainbranch mainbranch@latest"),
        ("wheel", "pip install --upgrade mainbranch"),
    ],
)
def test_required_update_names_the_command_for_the_install_mode(mode: str, command: str) -> None:
    # #965: the required-update command follows the install, not always pipx.
    update = package_update_status(
        None, installed_version="0.1.0", latest_version="0.6.2", mode=mode
    )

    assert update["severity"] == "required"
    assert update["install_mode"] == mode
    assert update["command"] == command
    alert = format_update_alert(update)
    assert f"  {command}" in alert
    assert ("must use pipx" in alert) is (mode == "pipx")
    if mode != "pipx":
        assert "pipx" not in alert


def test_required_update_unknown_mode_gets_mode_neutral_copy() -> None:
    update = package_update_status(
        None, installed_version="0.1.0", latest_version="0.6.2", mode="unknown"
    )

    assert update["severity"] == "required"
    assert update["command"] == ""
    alert = format_update_alert(update)
    assert "with the tool that installed it (pipx, uv or pip)" in alert
    assert "Run this first:" not in alert
    assert "must use pipx" not in alert


@pytest.mark.parametrize("mode", ["clone", "source"])
def test_required_update_does_not_apply_to_clone_or_source(mode: str) -> None:
    update = package_update_status(
        None, installed_version="0.1.0", latest_version="0.6.2", mode=mode
    )

    assert update["severity"] == "current"
    assert update["command"] == ""
    assert format_update_alert(update) == ""


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("0.6.3rc1", "0.6.2", 1),
        ("0.6.3rc1", "0.6.3", -1),
        ("0.6.3.dev0", "0.6.3rc1", -1),
        ("0.6.3", "0.6.3.0", 0),
        ("0.6.3.post1", "0.6.3", 1),
        ("0.6.3+local", "0.6.3", 1),
        ("0.6.10", "0.6.9", 1),
    ],
)
def test_compare_versions_follows_pep440(left: str, right: str, expected: int) -> None:
    assert compare_versions(left, right) == expected
