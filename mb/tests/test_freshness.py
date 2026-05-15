"""Package freshness metadata and update alert copy."""

from __future__ import annotations

from pathlib import Path

from mb.freshness import format_update_alert, package_update_status


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
