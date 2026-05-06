"""``mb doctor`` smoke + cloud-backup detection."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import doctor as doctor_mod
from mb.cli import app
from mb.doctor import _detect_cloud_paths, _repo_layout_check, run
from mb.init import run as init_run

runner = CliRunner()


def test_doctor_runs_on_empty_dir(tmp_path: Path) -> None:
    report = run(path=str(tmp_path))
    assert "checks" in report
    names = {c["name"] for c in report["checks"]}
    assert {"claude-code", "github-context", "network", "anti-cloud-backup"}.issubset(names)
    assert "skill-wiring" in names
    assert "mainbranch-version" in names
    assert "repo-layout" in names
    assert "schema-version" in names
    assert "update" in report


def test_doctor_reuses_github_context_for_integrations(tmp_path: Path, monkeypatch) -> None:
    calls = 0

    def fake_context(repo: Path) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {
            "ok": False,
            "state": "missing_github_remote",
            "summary": "This repo does not have a GitHub origin remote.",
            "repair": "Add a GitHub origin remote before relying on GitHub tasks or proposals.",
            "repair_command": "gh repo create --source . --remote origin --push",
            "safe_to_share": True,
        }

    monkeypatch.setattr(doctor_mod.connect_mod, "github_context", fake_context)

    report = run(path=str(tmp_path))

    assert calls == 1
    assert report["integrations"]["github"]["state"] == "missing_github_remote"


def test_cloud_path_detection_via_symlink(tmp_path: Path, monkeypatch) -> None:
    # Build a fake repo whose core/finance/ is a symlink pointing at a path
    # whose realpath includes "Dropbox".
    fake_home = tmp_path / "home"
    cloud = fake_home / "Dropbox" / "Stuff"
    cloud.mkdir(parents=True)
    repo = tmp_path / "biz"
    (repo / "core").mkdir(parents=True)
    (repo / "core" / "finance").symlink_to(cloud)

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    hits = _detect_cloud_paths(repo)
    assert "Dropbox" in hits


def test_doctor_clean_finance_passes(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / "core" / "finance").mkdir(parents=True)
    report = run(path=str(repo))
    cloud = next(c for c in report["checks"] if c["name"] == "anti-cloud-backup")
    assert cloud["ok"] is True


def test_doctor_skill_wiring_passes_after_init(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    report = run(path=str(repo))
    wiring = next(c for c in report["checks"] if c["name"] == "skill-wiring")
    assert wiring["ok"] is True


def test_repo_layout_warns_on_legacy_reference_core(tmp_path: Path) -> None:
    repo = tmp_path / "legacy"
    (repo / "reference" / "core").mkdir(parents=True)

    check = _repo_layout_check(repo)

    assert check["ok"] is False
    assert check["severity"] == "warn"
    assert "legacy reference/core" in check["detail"]


def test_repo_layout_accepts_current_core(tmp_path: Path) -> None:
    repo = tmp_path / "current"
    (repo / "core").mkdir(parents=True)

    check = _repo_layout_check(repo)

    assert check["ok"] is True
    assert "current core/" in check["detail"]


def test_doctor_warns_on_schema_drift(tmp_path: Path) -> None:
    repo = tmp_path / "legacy"
    (repo / "reference" / "core").mkdir(parents=True)

    report = run(path=str(repo))

    check = next(c for c in report["checks"] if c["name"] == "schema-version")
    assert check["ok"] is False
    assert check["severity"] == "warn"
    assert "mb migrate --check" in check["detail"]


def test_doctor_json_and_human_output_include_required_update(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        doctor_mod,
        "package_update_status",
        lambda repo: {
            "installed": "0.1.0",
            "latest": "0.2.1",
            "minimum_supported": "0.2.0",
            "severity": "required",
            "command": "pipx upgrade mainbranch",
            "post_update_commands": ["mb skill link --repo .", "mb doctor"],
            "reason": (
                "Installed version predates mb update and the current skill-link repair flow."
            ),
        },
    )

    report = doctor_mod.run(path=str(tmp_path))

    assert report["ok"] is False
    assert report["update"]["severity"] == "required"
    version_check = next(
        check for check in report["checks"] if check["name"] == "mainbranch-version"
    )
    assert version_check["severity"] == "error"
    assert "minimum supported" in version_check["detail"]

    doctor_mod.render_human(report)
    output = capsys.readouterr().out
    assert "Update required." in output
    assert "pipx upgrade mainbranch" in output


def test_doctor_command_still_runs_after_repair_subcommand_added(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", str(tmp_path), "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    assert payload["repo"] == str(tmp_path.resolve())
    assert "checks" in payload


def test_doctor_repair_plan_is_read_only_for_status_marker(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    marker = repo / ".mb" / "last-status-seen.json"
    assert not marker.exists()

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    assert payload["schema"] == "mb.doctor.repair"
    assert payload["read_only"] is True
    assert not marker.exists()


def test_doctor_repair_adds_connect_yaml_to_gitignore(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    gitignore = repo / ".gitignore"
    gitignore.write_text(
        gitignore.read_text(encoding="utf-8").replace(".mb/connect.yaml\n", ""),
        encoding="utf-8",
    )

    plan = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert plan.exit_code in {0, 1}
    plan_payload = json.loads(plan.stdout)
    checks = {
        check["name"]: check
        for section in plan_payload["sections"]
        if section["id"] == "gitignore"
        for check in section["checks"]
    }
    assert checks[".mb/connect.yaml"]["state"] == "warn"

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    assert ".mb/connect.yaml" in gitignore.read_text(encoding="utf-8")


def test_doctor_repair_untracks_existing_connect_yaml(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    connect_path = repo / ".mb" / "connect.yaml"
    connect_path.write_text("version: 1\nrepo_id: legacy\nproviders: {}\n", encoding="utf-8")
    doctor_mod._run_git(repo, ["add", "-f", ".mb/connect.yaml"])

    plan = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert plan.exit_code in {0, 1}
    plan_payload = json.loads(plan.stdout)
    checks = {
        check["name"]: check
        for section in plan_payload["sections"]
        if section["id"] == "gitignore"
        for check in section["checks"]
    }
    assert checks[".mb/connect.yaml"]["summary"] == "tracked; repair will untrack"

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "gitignore-local-state-untrack" in applied
    assert connect_path.exists()
    assert not doctor_mod._run_git(repo, ["ls-files", "--error-unmatch", ".mb/connect.yaml"])["ok"]


def test_doctor_warns_on_legacy_campaigns_records(tmp_path: Path) -> None:
    repo = tmp_path / "legacy-pushes"
    init_run(path=str(repo), name="Acme")
    legacy = repo / "campaigns" / "2026-04-spring-launch"
    legacy.mkdir(parents=True)
    (legacy / "campaign.md").write_text(
        "---\nslug: spring-launch\nstatus: active\n---\n# spring launch\n",
        encoding="utf-8",
    )

    report = doctor_mod.run(path=str(repo))

    legacy_check = next(c for c in report["checks"] if c["name"] == "legacy-campaigns")
    assert legacy_check["ok"] is False
    assert legacy_check["severity"] == "warn"
    assert "1 legacy campaign record" in legacy_check["detail"]
    assert "mb migrate campaigns --plan" in legacy_check["detail"]
    assert legacy_check["legacy_records"] == ["campaigns/2026-04-spring-launch/campaign.md"]


def test_doctor_uses_campaigns_migration_plan_for_ambiguous_artifacts(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "legacy-pushes-with-artifacts"
    init_run(path=str(repo), name="Acme")
    legacy = repo / "campaigns" / "2026-04-15-spring-launch"
    legacy.mkdir(parents=True)
    (legacy / "campaign.md").write_text(
        "---\nslug: spring-launch\nstatus: active\n---\n# spring launch\n",
        encoding="utf-8",
    )
    (legacy / "ads.md").write_text("# ads\n", encoding="utf-8")
    (legacy / "random-notes.md").write_text("# random\n", encoding="utf-8")

    report = doctor_mod.run(path=str(repo))

    legacy_check = next(c for c in report["checks"] if c["name"] == "legacy-campaigns")
    assert legacy_check["ok"] is False
    assert legacy_check["legacy_records"] == ["campaigns/2026-04-15-spring-launch/campaign.md"]
    assert "campaigns/2026-04-15-spring-launch/ads.md" not in legacy_check["ambiguous_files"]
    assert "campaigns/2026-04-15-spring-launch/random-notes.md" in legacy_check["ambiguous_files"]


def test_doctor_clean_repo_has_no_legacy_campaigns_warning(tmp_path: Path) -> None:
    repo = tmp_path / "fresh"
    init_run(path=str(repo), name="Acme")

    report = doctor_mod.run(path=str(repo))

    legacy_check = next(c for c in report["checks"] if c["name"] == "legacy-campaigns")
    # `mb init` no longer scaffolds campaigns/, so there is nothing to warn on.
    assert legacy_check["ok"] is True
    assert legacy_check.get("severity") in {"ok", None}


def test_doctor_repair_plan_exposes_legacy_campaigns_to_pushes_action(tmp_path: Path) -> None:
    repo = tmp_path / "legacy-pushes-repair"
    init_run(path=str(repo), name="Acme")
    legacy = repo / "campaigns" / "2026-04-spring-launch"
    legacy.mkdir(parents=True)
    (legacy / "campaign.md").write_text(
        "---\nslug: spring-launch\nstatus: active\n---\n# spring launch\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    actions = {action["id"]: action for action in payload["actions"]}
    assert "legacy_campaigns_to_pushes" in actions
    item = actions["legacy_campaigns_to_pushes"]
    assert item["mode"] == "read"
    assert item["safe_to_apply"] is True
    assert item["command"] == "mb migrate campaigns --plan"


def test_doctor_repair_plan_distinguishes_read_and_write_actions(tmp_path: Path) -> None:
    repo = tmp_path / "legacy"
    (repo / "reference" / "core").mkdir(parents=True)

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["migration-preview"]["mode"] == "read"
    assert actions["migration-apply"]["mode"] == "write"
    assert actions["migration-apply"]["safe_to_apply"] is False


def test_doctor_repair_apply_moves_old_clone_symlink_to_backup(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    old_engine = tmp_path / "mb-vip"
    old_lens = old_engine / ".claude" / "lenses" / "ops"
    old_lens.mkdir(parents=True)
    stale_link = repo / ".claude" / "lenses" / "ops"
    stale_link.parent.mkdir(parents=True, exist_ok=True)
    stale_link.symlink_to(old_lens, target_is_directory=True)

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied_ids = {action["id"] for action in payload["applied_actions"]}
    assert "legacy-claude-link-repair" in applied_ids
    assert not stale_link.exists()
    backups = list((repo / ".mb" / "backups").rglob("claude-links/.claude/lenses/ops"))
    assert backups
    assert ".mb/backups/" in (repo / ".gitignore").read_text(encoding="utf-8")


def test_doctor_rejects_unknown_options_on_existing_path() -> None:
    result = runner.invoke(app, ["doctor", "--jsonn"])

    assert result.exit_code == 2
    assert "unknown option" in result.stderr


def test_doctor_repair_exits_nonzero_when_json_report_is_red(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        doctor_mod,
        "repair_plan",
        lambda repo=".": {
            "ok": False,
            "read_only": True,
            "repo": str(tmp_path),
            "summary": {"error": 1},
        },
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(tmp_path), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False


def test_doctor_legacy_symlink_keeps_current_active_engine_root(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    active_root = tmp_path / "Documents" / "GitHub" / "mainbranch"
    active_lens = active_root / ".claude" / "lenses" / "ops"
    active_lens.mkdir(parents=True)
    lens_link = repo / ".claude" / "lenses" / "ops"
    lens_link.parent.mkdir(parents=True)
    lens_link.symlink_to(active_lens, target_is_directory=True)

    monkeypatch.setattr(doctor_mod.engine_mod, "engine_root", lambda: active_root)

    result = doctor_mod._legacy_claude_symlinks(repo)

    assert result["repairable"] == 0
    assert result["findings"][0]["state"] == "info"
    assert result["findings"][0]["safe_to_repair"] is False
