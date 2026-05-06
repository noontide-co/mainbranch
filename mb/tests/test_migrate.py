"""``mb migrate`` schema migration contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import migrate as migrate_mod
from mb import migrations
from mb.cli import app

runner = CliRunner()


def _legacy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "legacy"
    (repo / "reference" / "core").mkdir(parents=True)
    (repo / "reference" / "offers" / "flagship").mkdir(parents=True)
    (repo / "reference" / "proof" / "angles").mkdir(parents=True)
    (repo / "reference" / "brand").mkdir(parents=True)
    (repo / "reference" / "strategy").mkdir(parents=True)
    (repo / "reference" / "visual-identity").mkdir(parents=True)
    (repo / "reference" / "domain" / "funnel").mkdir(parents=True)
    (repo / "research").mkdir()
    (repo / "decisions").mkdir()
    (repo / "reference" / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")
    (repo / "reference" / "core" / "audience.md").write_text("# Audience\n", encoding="utf-8")
    (repo / "reference" / "offers" / "flagship" / "offer.md").write_text(
        "# Flagship\n",
        encoding="utf-8",
    )
    (repo / "reference" / "proof" / "testimonials.md").write_text(
        "# Testimonials\n",
        encoding="utf-8",
    )
    (repo / "reference" / "proof" / "angles" / "clarity.md").write_text(
        "# Clarity\n",
        encoding="utf-8",
    )
    (repo / "reference" / "visual-identity" / "visual-style.md").write_text(
        "# Visual Style\n",
        encoding="utf-8",
    )
    (repo / "reference" / "brand" / "voice-system.md").write_text(
        "# Voice System\n",
        encoding="utf-8",
    )
    (repo / "reference" / "strategy" / "market-position.md").write_text(
        "# Market Position\n",
        encoding="utf-8",
    )
    (repo / "reference" / "domain" / "content-strategy.md").write_text(
        "# Content Strategy\n",
        encoding="utf-8",
    )
    (repo / "reference" / "domain" / "product-ladder.md").write_text(
        "# Product Ladder\n",
        encoding="utf-8",
    )
    (repo / "reference" / "domain" / "funnel" / "skool-surfaces.md").write_text(
        "# Skool Surfaces\n",
        encoding="utf-8",
    )
    (repo / "CLAUDE.md").write_text(
        "Read `reference/core/*.md` and `reference/offers/flagship/offer.md`.\n",
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text(".env\n", encoding="utf-8")
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


def test_migrate_check_prints_privacy_safe_summary_when_pending(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check"])

    assert result.exit_code == 1
    assert "pending migration changes:" in result.stdout
    assert "move_file: reference/core/offer.md -> core/offer.md" in result.stdout
    assert (
        "move_file: reference/proof/testimonials.md -> core/proof/testimonials.md" in result.stdout
    )
    assert (
        "move_file: reference/domain/content-strategy.md -> core/content-strategy.md"
        in result.stdout
    )
    assert "Run `mb migrate --check --diff`" in result.stdout
    assert "--- a/reference/core/offer.md" not in result.stdout
    assert "# Offer" not in result.stdout


def test_migrate_check_diff_is_explicit(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check", "--diff"])

    assert result.exit_code == 1
    assert "--- a/reference/core/offer.md" in result.stdout
    assert "+++ b/core/offer.md" in result.stdout
    assert "+++ b/core/offers/flagship/offer.md" in result.stdout
    assert "+++ b/core/proof/testimonials.md" in result.stdout
    assert "+++ b/core/brand/visual-style.md" in result.stdout
    assert "+++ b/core/content-strategy.md" in result.stdout
    assert "+++ b/core/product-ladder.md" in result.stdout
    assert "+++ b/core/operations/funnel/skool-surfaces.md" in result.stdout
    assert "+++ b/.gitignore" in result.stdout
    assert "+.mb/backups/" in result.stdout
    assert "+++ b/.mb/schema_version" in result.stdout
    assert "+++ b/decisions/2026-05-02-mainbranch-v02-path-migration.md" in result.stdout


def test_migrate_check_json_exposes_same_plan(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["action"] == "check"
    assert payload["plan"]["has_changes"] is True
    assert payload["plan"]["diff_included"] is False
    assert payload["plan"]["diff"] == ""
    assert "Full file diffs are hidden by default" in payload["plan"]["privacy_note"]
    assert payload["plan"]["migrations"][0]["migration"]["id"] == "001"


def test_migrate_check_json_diff_is_explicit(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(
        app,
        ["migrate", "--repo", str(repo), "--check", "--diff", "--json"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["plan"]["diff_included"] is True
    assert "b/core/offer.md" in payload["plan"]["diff"]


def test_migrate_status_honors_root_repo_option(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    current = tmp_path / "current"
    (current / "core").mkdir(parents=True)
    (current / ".mb").mkdir()
    (current / ".mb" / "schema_version").write_text("0.2\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["migrate", "--repo", str(repo), "status", "--json"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["repo"] == str(repo.resolve())
    assert payload["current_version"] == "0.1"


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
    assert (backup / ".gitignore").exists()
    assert (repo / ".mb" / "schema_version").read_text(encoding="utf-8") == "0.2\n"
    assert ".mb/backups/" in (repo / ".gitignore").read_text(encoding="utf-8")
    assert (repo / "core" / "offer.md").read_text(encoding="utf-8") == "# Offer\n"
    assert (repo / "core" / "offers" / "flagship" / "offer.md").exists()
    assert (repo / "core" / "proof" / "testimonials.md").exists()
    assert (repo / "core" / "proof" / "angles" / "clarity.md").exists()
    assert (repo / "core" / "brand" / "visual-style.md").exists()
    assert (repo / "core" / "brand" / "voice-system.md").exists()
    assert (repo / "core" / "strategy" / "market-position.md").exists()
    assert (repo / "core" / "content-strategy.md").exists()
    assert (repo / "core" / "product-ladder.md").exists()
    assert (repo / "core" / "operations" / "funnel" / "skool-surfaces.md").exists()
    assert (repo / "reference" / "core").is_symlink()
    assert (repo / "reference" / "offers").is_symlink()
    assert not (repo / "reference" / "proof").exists()
    assert not (repo / "reference" / "brand").exists()
    assert not (repo / "reference" / "strategy").exists()
    assert not (repo / "reference" / "visual-identity").exists()
    assert not (repo / "reference" / "domain").exists()
    assert "core/*.md" in (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert (repo / "decisions" / "2026-05-02-mainbranch-v02-path-migration.md").exists()

    rerun = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])
    assert rerun.exit_code == 0
    rerun_payload = json.loads(rerun.stdout)
    assert rerun_payload["applied"] == []
    assert rerun_payload["pending"] == []


def test_migrate_ignores_os_metadata_files(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    (repo / "reference" / "offers" / ".DS_Store").write_text("metadata", encoding="utf-8")
    (repo / "reference" / "core" / "._offer.md").write_text("metadata", encoding="utf-8")
    (repo / "reference" / "offers" / "flagship" / "assets").mkdir()
    (repo / "reference" / "offers" / "flagship" / "assets" / ".DS_Store").write_text(
        "metadata",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--check", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    changes = payload["plan"]["migrations"][0]["changes"]
    assert not any(".DS_Store" in str(change) for change in changes)
    assert not any("._offer.md" in str(change) for change in changes)

    applied = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])
    assert applied.exit_code == 0
    applied_payload = json.loads(applied.stdout)
    assert applied_payload["ok"] is True
    assert (repo / "reference" / "core").is_symlink()
    assert (repo / "reference" / "offers").is_symlink()
    backup = Path(applied_payload["backup"]["path"])
    assert (backup / "reference" / "offers" / ".DS_Store").exists()
    assert (backup / "reference" / "core" / "._offer.md").exists()
    assert (backup / "reference" / "offers" / "flagship" / "assets" / ".DS_Store").exists()


def test_migrate_diff_rejects_status_subcommand(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--diff", "status"])

    assert result.exit_code == 2
    assert "--diff can only be used with --check" in result.stderr


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


def test_migrate_apply_reports_structured_error_when_legacy_dir_is_not_empty(
    tmp_path: Path,
) -> None:
    repo = _legacy_repo(tmp_path)
    (repo / "reference" / "core" / "linked").symlink_to(repo / "outside")

    result = runner.invoke(app, ["migrate", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "reference/core is not empty" in payload["errors"][0]
    assert payload["backup"]["path"]


def test_migrate_status_clean_current_repo(tmp_path: Path) -> None:
    repo = tmp_path / "current"
    (repo / "core").mkdir(parents=True)
    (repo / ".mb").mkdir()
    (repo / ".mb" / "schema_version").write_text("0.2\n", encoding="utf-8")

    result = migrate_mod.status(repo)

    assert result["current_version"] == "0.2"
    assert result["pending"] == []


def test_migration_version_map_is_derived_from_registered_metadata() -> None:
    assert migrations.version_map()["0.1"] == "mb.migrations.001_v01_to_v02_path_config"
