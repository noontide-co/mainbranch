"""``mb migrate`` schema migration contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import migrate as migrate_mod
from mb.cli import app

runner = CliRunner()


def _legacy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "legacy"
    (repo / "reference" / "core").mkdir(parents=True)
    (repo / "reference" / "offers" / "flagship").mkdir(parents=True)
    (repo / "research").mkdir()
    (repo / "decisions").mkdir()
    (repo / "reference" / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")
    (repo / "reference" / "core" / "audience.md").write_text("# Audience\n", encoding="utf-8")
    (repo / "reference" / "offers" / "flagship" / "offer.md").write_text(
        "# Flagship\n",
        encoding="utf-8",
    )
    (repo / "CLAUDE.md").write_text(
        "Read `reference/core/*.md` and `reference/offers/flagship/offer.md`.\n",
        encoding="utf-8",
    )
    return repo


def test_migrate_status_reports_pending_legacy_schema(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "status", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema"] == "mb.migrate"
    assert payload["schema_version"] == 1
    assert payload["current_version"] == "0.1"
    assert payload["latest_version"] == "0.2"
    assert payload["pending"][0]["name"] == "001_v01_to_v02_path_config"


def test_migrate_check_prints_diff_and_exits_nonzero_when_pending(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check"])

    assert result.exit_code == 1
    assert "--- a/reference/core/offer.md" in result.stdout
    assert "+++ b/core/offer.md" in result.stdout
    assert "+++ b/core/offers/flagship/offer.md" in result.stdout
    assert "+++ b/.mb/schema_version" in result.stdout
    assert "+++ b/decisions/2026-05-02-mainbranch-v02-path-migration.md" in result.stdout


def test_migrate_check_json_exposes_same_plan(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["action"] == "check"
    assert payload["plan"]["has_changes"] is True
    assert "b/core/offer.md" in payload["plan"]["diff"]
    assert payload["plan"]["migrations"][0]["migration"]["id"] == "001"


def test_migrate_apply_moves_files_backs_up_and_is_idempotent(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["current_version"] == "0.2"
    assert payload["applied"][0]["id"] == "001"
    backup = Path(payload["backup"]["path"])
    assert backup.is_dir()
    assert (backup / "reference" / "core" / "offer.md").exists()
    assert (repo / ".mb" / "schema_version").read_text(encoding="utf-8") == "0.2\n"
    assert (repo / "core" / "offer.md").read_text(encoding="utf-8") == "# Offer\n"
    assert (repo / "core" / "offers" / "flagship" / "offer.md").exists()
    assert (repo / "reference" / "core").is_symlink()
    assert (repo / "reference" / "offers").is_symlink()
    assert "core/*.md" in (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert (repo / "decisions" / "2026-05-02-mainbranch-v02-path-migration.md").exists()

    rerun = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])
    assert rerun.exit_code == 0
    rerun_payload = json.loads(rerun.stdout)
    assert rerun_payload["applied"] == []
    assert rerun_payload["pending"] == []


def test_migrate_apply_aborts_before_writes_on_conflict(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    (repo / "core").mkdir()
    (repo / "core" / "offer.md").write_text("# Different\n", encoding="utf-8")

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "core/offer.md already exists with different contents" in payload["errors"]
    assert not (repo / ".mb" / "backups").exists()
    assert (repo / "reference" / "core" / "offer.md").exists()


def test_migrate_status_clean_current_repo(tmp_path: Path) -> None:
    repo = tmp_path / "current"
    (repo / "core").mkdir(parents=True)
    (repo / ".mb").mkdir()
    (repo / ".mb" / "schema_version").write_text("0.2\n", encoding="utf-8")

    result = migrate_mod.status(repo)

    assert result["current_version"] == "0.2"
    assert result["pending"] == []
