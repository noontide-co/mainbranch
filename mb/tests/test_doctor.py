"""``mb doctor`` smoke + cloud-backup detection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import codex as codex_mod
from mb import doctor as doctor_mod
from mb import engine as engine_mod
from mb import migration_lint
from mb.cli import app
from mb.doctor import _detect_cloud_paths, _repo_layout_check, run
from mb.init import run as init_run

runner = CliRunner()


@pytest.fixture(autouse=True)
def codex_missing_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(codex_mod, "_which", lambda name: "" if name == "codex" else None)


def _with_codex(name: str) -> str:
    if name == "codex":
        return "/usr/local/bin/codex"
    return ""


def _codex_runtime_ok() -> dict[str, Any]:
    return {
        "checked": True,
        "ok": True,
        "state": "ok",
        "shell": "/bin/zsh",
        "command": "command -v mb && mb --version",
        "path": "/usr/local/bin/mb",
        "version": "0.3.31",
        "active_path": "/usr/local/bin/mb",
        "active_version": "0.3.31",
        "path_mismatch": False,
        "version_mismatch": False,
        "mismatch": False,
        "error": "",
        "summary": "Login-shell runtime resolves the active mb.",
        "repair": "",
        "safe_to_share": True,
    }


def _codex_runtime_path_mismatch_same_version() -> dict[str, Any]:
    return {
        "checked": True,
        "ok": False,
        "state": "warn",
        "shell": "/bin/zsh",
        "command": "command -v mb && mb --version",
        "path": "/tmp/smoke/bin/mb",
        "version": "0.3.34",
        "active_path": "/Users/example/.local/bin/mb",
        "active_version": "0.3.34",
        "path_mismatch": True,
        "version_mismatch": False,
        "mismatch": True,
        "error": "",
        "summary": "Login-shell runtime resolves a different mb than this process.",
        "repair": "Put the current Main Branch install earlier on the login-shell PATH.",
        "safe_to_share": True,
    }


def _codex_plugin_list_result(repo: Path, *, installed: bool = True) -> dict[str, Any]:
    marketplace = codex_mod.marketplace_path(repo)
    plugin = codex_mod.plugin_manifest_path(repo).parent
    status = "installed, enabled" if installed else "not installed"
    return {
        "ok": True,
        "returncode": 0,
        "stdout": (
            f"Marketplace `{codex_mod.CODEX_MARKETPLACE_NAME}`\n"
            f"{marketplace}\n\n"
            "PLUGIN                                    STATUS              VERSION  PATH\n"
            f"{codex_mod.CODEX_PLUGIN_SELECTOR}  {status}  0.1.0  {plugin}\n"
        ),
        "stderr": "",
        "command": f"codex plugin list --marketplace {codex_mod.CODEX_MARKETPLACE_NAME}",
    }


def _prepare_codex_global_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    codex_mod.write_global_plugin_source()


def _prepare_codex_global_skill_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "codex-skills"))


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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

    monkeypatch.setattr(
        doctor_mod.connect_mod,  # type: ignore[attr-defined]
        "github_context",
        fake_context,
    )

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
    codex_agents = next(c for c in report["checks"] if c["name"] == "codex-agents-md")
    assert codex_agents["ok"] is True
    checkpoint_hook = next(c for c in report["checks"] if c["name"] == "checkpoint-hook")
    assert checkpoint_hook["ok"] is True


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
    assert payload["plan_interpretation"]["state"] in {
        "clear",
        "plan_produced_with_findings",
        "plan_produced_with_blockers",
    }
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


def test_doctor_repair_protects_legacy_vip_local_state(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    gitignore = repo / ".gitignore"
    gitignore.write_text(
        gitignore.read_text(encoding="utf-8").replace(".vip/local.yaml\n", ""),
        encoding="utf-8",
    )
    vip_local = repo / ".vip" / "local.yaml"
    vip_local.parent.mkdir()
    vip_local.write_text("current_offer: community\n", encoding="utf-8")
    doctor_mod._run_git(repo, ["add", "-f", ".vip/local.yaml"])

    plan = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert plan.exit_code in {0, 1}
    plan_payload = json.loads(plan.stdout)
    checks = {
        check["name"]: check
        for section in plan_payload["sections"]
        if section["id"] == "gitignore"
        for check in section["checks"]
    }
    assert checks[".vip/local.yaml"]["summary"] == "tracked; repair will untrack"

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    assert ".vip/local.yaml" in gitignore.read_text(encoding="utf-8")
    assert vip_local.exists()
    assert not doctor_mod._run_git(repo, ["ls-files", "--error-unmatch", ".vip/local.yaml"])["ok"]


def test_doctor_repair_plan_reports_missing_checkpoint_hook(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / ".git" / "hooks" / "commit-msg").unlink()

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "checkpoint-hook")
    assert section["state"] == "warn"
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["checkpoint-hook-install"]["safe_to_apply"] is True


def test_doctor_repair_apply_restores_missing_claude_worktree_start_wiring(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    doctor_mod._run_git(repo, ["config", "user.email", "test@example.com"])
    doctor_mod._run_git(repo, ["config", "user.name", "Test User"])
    doctor_mod._run_git(repo, ["add", "AGENTS.md", "CLAUDE.md", "README.md", "core"])
    commit = doctor_mod._run_git(repo, ["commit", "-m", "[updated] setup -- baseline"])
    assert commit["ok"], commit["stderr"]
    worktree = repo / ".claude" / "worktrees" / "repair-start"
    added = doctor_mod._run_git(repo, ["worktree", "add", "-b", "repair-start", str(worktree)])
    assert added["ok"], added["stderr"]

    assert not (worktree / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()

    plan = doctor_mod.repair_plan(repo=worktree)
    section = next(section for section in plan["sections"] if section["id"] == "claude-wiring")
    start_check = next(
        check for check in section["checks"] if check["name"] == "project-local-skills"
    )
    actions = {action["id"]: action for action in plan["actions"]}

    assert section["state"] == "error"
    assert "git worktree" in start_check["summary"]
    assert "worktrees do not inherit" in start_check["summary"]
    assert "mb skill link --repo ." in start_check["summary"]
    assert "project-local /mb-start bridge" in start_check["summary"]
    assert start_check["fallback_commands"] == [
        "mb start --json",
        "mb doctor repair --plan",
        "mb doctor repair --apply",
    ]
    assert actions["skill-link"]["command"] == "mb doctor repair --apply --only claude"
    assert "/mb-start" in actions["skill-link"]["reason"]

    applied = doctor_mod.repair_apply(repo=worktree, only="claude")
    applied_actions = {action["id"]: action for action in applied["applied_actions"]}

    assert "skill-link" in applied_actions
    assert (worktree / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file()
    assert engine_mod.link_status(worktree)["ok"] is True


def test_doctor_repair_plan_reports_missing_codex_agents_md(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").unlink()

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    assert section["state"] == "warn"
    agents_check = next(check for check in section["checks"] if check["name"] == "AGENTS.md")
    assert agents_check["state"] == "warn"
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["codex-agents-md"]["safe_to_apply"] is True
    assert actions["codex-agents-md"]["command"] == "mb doctor repair --apply --only codex"
    assert "AGENTS.md" in actions["codex-agents-md"]["writes"]


def test_doctor_repair_only_codex_filters_unrelated_related_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")
    decision = repo / "decisions" / "2026-05-22-choice.md"
    _write_md(
        decision,
        "---\n"
        "type: decision\n"
        "date: 2026-05-22\n"
        "status: proposed\n"
        "linked_offers:\n"
        "  - ../core/offer.md\n"
        "---\n\n"
        "# Choice\n",
    )

    plan_result = runner.invoke(
        app,
        ["doctor", "repair", "--repo", str(repo), "--plan", "--only", "codex", "--json"],
    )

    assert plan_result.exit_code in {0, 1}
    plan = json.loads(plan_result.stdout)
    assert plan["only"] == "codex"
    assert [section["id"] for section in plan["sections"]] == ["codex-wiring", "git"]
    assert [action["id"] for action in plan["actions"]] == [
        "codex-agents-md",
        "codex-global-skill",
    ]

    apply_result = runner.invoke(
        app,
        ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"],
    )

    assert apply_result.exit_code in {0, 1}
    payload = json.loads(apply_result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert set(applied) == {"codex-agents-md", "codex-global-skill"}
    assert applied["codex-agents-md"]["command"] == "mb doctor repair --apply --only codex"
    assert "## Related links" not in decision.read_text(encoding="utf-8")


def test_doctor_repair_plan_lists_agent_surfaces_and_scope_choices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    surfaces = {surface["id"]: surface for surface in payload["agent_surfaces"]["surfaces"]}
    assert payload["agent_surfaces"]["scope_choices"] == [
        "mb doctor repair --plan --only claude",
        "mb doctor repair --plan --only codex",
        "mb doctor repair --plan --all-agents",
    ]
    assert surfaces["claude"]["label"] == "Claude Code project-local skills"
    assert surfaces["codex"]["label"] == "Codex global mb-* skills and repo AGENTS.md"
    assert "codex-agents-md" in surfaces["codex"]["planned_actions"]
    assert "codex-global-skill" in surfaces["codex"]["planned_actions"]
    assert "AGENTS.md" in surfaces["codex"]["touched_files"]
    assert str(tmp_path / "codex-skills") in surfaces["codex"]["touched_files"]


def test_doctor_repair_only_claude_filters_codex_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--plan", "--only", "claude", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    assert payload["only"] == "claude"
    assert [section["id"] for section in payload["sections"]] == ["claude-wiring", "git"]
    assert all(not action["id"].startswith("codex-") for action in payload["actions"])


def test_doctor_repair_rejects_mixed_agent_scope(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "doctor",
            "repair",
            "--repo",
            str(tmp_path),
            "--plan",
            "--only",
            "codex",
            "--all-agents",
        ],
    )

    assert result.exit_code == 2
    assert "--only cannot be combined with --all-agents" in result.stderr


def test_doctor_repair_apply_all_agents_installs_codex_without_codex_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(codex_mod, "_which", lambda name: "" if name == "codex" else None)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")
    old_playbook_skill = tmp_path / "codex-skills" / "weekly-review" / "SKILL.md"
    old_playbook_skill.parent.mkdir(parents=True, exist_ok=True)
    old_playbook_skill.write_text(
        "\n".join(codex_mod.CODEX_RETIRED_GLOBAL_SKILL_MARKERS["weekly-review"]) + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--all-agents", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "codex-agents-md" in applied
    assert "codex-global-skill" in applied
    receipt = payload["receipt"]
    assert "mb-start" in receipt["installed_skills"]
    assert "weekly-review" not in receipt["installed_skills"]
    assert "main-branch-owner-loop" not in receipt["installed_skills"]
    assert str(tmp_path / "codex-skills") in receipt["touched_files"]
    assert (tmp_path / "codex-skills" / "mb-start" / "SKILL.md").is_file()
    assert not old_playbook_skill.exists()


def test_doctor_repair_apply_default_does_not_silently_write_agent_surfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied_ids = {action["id"] for action in payload["applied_actions"]}
    assert "codex-agents-md" not in applied_ids
    assert "codex-global-skill" not in applied_ids
    assert not (tmp_path / "codex-skills" / "mb-start" / "SKILL.md").exists()
    assert payload["receipt"]["skipped_surfaces"] == [
        "claude: run mb doctor repair --apply --only claude",
        "codex: run mb doctor repair --apply --only codex",
    ]


def test_doctor_repair_plan_marks_codex_runtime_info_when_codex_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(codex_mod, "_which", lambda name: "" if name == "codex" else None)
    monkeypatch.setattr(
        codex_mod,
        "_login_shell_mb_diagnostics",
        lambda: {
            "checked": True,
            "ok": False,
            "state": "warn",
            "shell": "/bin/zsh",
            "command": "command -v mb && mb --version",
            "path": "/old/bin/mb",
            "version": "0.3.18",
            "active_path": "/new/bin/mb",
            "active_version": "0.3.29",
            "path_mismatch": True,
            "version_mismatch": True,
            "mismatch": True,
            "error": "",
            "summary": "Login-shell runtime resolves a different mb than this process.",
            "repair": "Put the current Main Branch install earlier on the login-shell PATH.",
            "safe_to_share": True,
        },
    )
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    runtime_check = next(
        check for check in section["checks"] if check["name"] == "codex-runtime-mb"
    )
    assert runtime_check["state"] == "info"
    assert "waits until Codex CLI is installed" in runtime_check["summary"]
    assert runtime_check["repair"] == ""


def test_doctor_repair_plan_installs_missing_codex_global_skills(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(codex_mod, "_which", _with_codex)
    monkeypatch.setattr(codex_mod, "_login_shell_mb_diagnostics", _codex_runtime_ok)
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--plan", "--only", "codex", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    actions = {action["id"]: action for action in payload["actions"]}
    assert "codex-global-skill" in actions
    assert actions["codex-global-skill"]["safe_to_apply"] is True
    assert actions["codex-global-skill"]["command"] == "mb doctor repair --apply --only codex"
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    skill_check = next(
        check for check in section["checks"] if check["name"] == "codex-global-skill"
    )
    assert skill_check["state"] == "warn"
    assert "mb-start/SKILL.md" in skill_check["missing"]


def test_doctor_repair_plan_installs_missing_codex_global_skills_with_runtime_path_warning(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(codex_mod, "_which", _with_codex)
    monkeypatch.setattr(
        codex_mod,
        "_login_shell_mb_diagnostics",
        _codex_runtime_path_mismatch_same_version,
    )
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--plan", "--only", "codex", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    actions = {action["id"]: action for action in payload["actions"]}
    assert "codex-global-skill" in actions
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    runtime_check = next(
        check for check in section["checks"] if check["name"] == "codex-runtime-mb"
    )
    skill_check = next(
        check for check in section["checks"] if check["name"] == "codex-global-skill"
    )
    assert runtime_check["state"] == "warn"
    assert skill_check["state"] == "warn"


def test_doctor_repair_apply_installs_missing_codex_global_skills(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(codex_mod, "_which", _with_codex)
    monkeypatch.setattr(codex_mod, "_login_shell_mb_diagnostics", _codex_runtime_ok)
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "codex-global-skill" in applied
    assert applied["codex-global-skill"]["state"] == "ok"
    assert applied["codex-global-skill"]["command"] == "mb doctor repair --apply --only codex"
    status = applied["codex-global-skill"]["result"]["status"]
    assert status["skills"]["mb-start"]["ok"] is True
    assert status["skills"]["mb-ads"]["ok"] is True


def test_doctor_repair_apply_installs_missing_codex_global_skills_with_runtime_path_warning(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(codex_mod, "_which", _with_codex)
    monkeypatch.setattr(
        codex_mod,
        "_login_shell_mb_diagnostics",
        _codex_runtime_path_mismatch_same_version,
    )
    _prepare_codex_global_skill_roots(tmp_path, monkeypatch)
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "codex-global-skill" in applied
    assert applied["codex-global-skill"]["state"] == "ok"


def test_doctor_repair_plan_reports_stale_codex_lifecycle_guidance(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    agents = repo / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace(
            "## Codex Lifecycle Workflow Index",
            "## Old Codex Notes",
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    agents_check = next(check for check in section["checks"] if check["name"] == "AGENTS.md")
    assert agents_check["state"] == "warn"
    assert agents_check["lifecycle_discovery_ok"] is False
    assert "## Codex Lifecycle Workflow Index" in agents_check["missing_lifecycle_guidance"]
    actions = {action["id"]: action for action in payload["actions"]}
    assert "codex-agents-md" in actions


def test_doctor_repair_plan_reports_stale_codex_guidance_metadata(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    agents = repo / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace(
            "template_hash=" + codex_mod.guidance_template_hash(),
            "template_hash=stale0000000000",
            1,
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    agents_check = next(check for check in section["checks"] if check["name"] == "AGENTS.md")
    assert agents_check["state"] == "warn"
    assert agents_check["guidance_metadata_ok"] is False
    assert agents_check["guidance_template_hash_ok"] is False
    assert agents_check["generated_version_ok"] is False
    assert agents_check["expected_template_hash"] == codex_mod.guidance_template_hash()
    assert "mainbranch:codex-guidance" in agents_check["expected_guidance_metadata"]
    actions = {action["id"]: action for action in payload["actions"]}
    assert "codex-agents-md" in actions


def test_codex_guidance_currentness_does_not_depend_on_package_patch_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    monkeypatch.setattr(codex_mod, "__version__", "99.99.99")

    status = codex_mod.instructions_status(repo)

    assert status["ok"] is True
    assert status["guidance_metadata_ok"] is True
    assert status["expected_version_marker"] == ""


def test_doctor_repair_plan_reports_pre_engine_source_boundary_codex_guidance(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    agents = repo / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace(
            "does not need to contain that engine source file. ",
            "",
            1,
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    agents_check = next(check for check in section["checks"] if check["name"] == "AGENTS.md")
    assert agents_check["state"] == "warn"
    assert agents_check["lifecycle_discovery_ok"] is False
    assert (
        "does not need to contain that engine source file"
        in agents_check["missing_lifecycle_guidance"]
    )
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["codex-agents-md"]["safe_to_apply"] is True
    assert "AGENTS.md" in actions["codex-agents-md"]["writes"]


def test_doctor_repair_plan_reports_custom_codex_agents_missing_source_item(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    agents = repo / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8").replace("- `runtime.codex_cli`\n", "", 1)
        + "\n## Local Notes\n\nKeep this operator-specific note.\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "codex-wiring")
    agents_check = next(check for check in section["checks"] if check["name"] == "AGENTS.md")
    assert agents_check["state"] == "warn"
    assert agents_check["lifecycle_discovery_ok"] is False
    assert "- `runtime.codex_cli`" in agents_check["missing_lifecycle_guidance"]
    actions = {action["id"]: action for action in payload["actions"]}
    assert "codex-agents-md" in actions


def test_doctor_repair_apply_refreshes_codex_agents_md(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"]
    )

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "codex-agents-md" in applied
    agents_text = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "## Codex Start Workflow" in agents_text
    assert "## Codex Lifecycle Workflow Index" in agents_text
    assert "## Codex Status Workflow" in agents_text
    assert "## Codex Think Route" in agents_text
    assert "mb status --json --peek" in agents_text
    assert not (repo / ".agents" / "plugins").exists()
    assert not (repo / ".agents" / "skills" / "main-branch-owner-loop").exists()


def test_doctor_repair_removes_stale_repo_local_codex_plugin(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    command = repo / ".agents" / "plugins" / "main-branch-owner-loop" / "commands" / "mb-start.md"
    command.parent.mkdir(parents=True, exist_ok=True)
    command.write_text("# stale\n", encoding="utf-8")

    plan_result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])
    assert plan_result.exit_code in {0, 1}
    plan = json.loads(plan_result.stdout)
    actions = {action["id"]: action for action in plan["actions"]}
    assert "codex-agents-md" in actions

    apply_result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"]
    )
    assert apply_result.exit_code in {0, 1}
    assert not command.exists()


def test_doctor_repair_preserves_custom_codex_agents_md_when_contract_is_current(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    agents = repo / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Local Notes\n\nKeep this operator-specific note.\n",
        encoding="utf-8",
    )

    plan_result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])
    assert plan_result.exit_code in {0, 1}
    plan = json.loads(plan_result.stdout)
    actions = {action["id"]: action for action in plan["actions"]}
    assert "codex-agents-md" not in actions

    apply_result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"]
    )
    assert apply_result.exit_code in {0, 1}
    applied = {
        action["id"]: action for action in json.loads(apply_result.stdout)["applied_actions"]
    }
    assert "codex-agents-md" not in applied
    assert "Keep this operator-specific note." in agents.read_text(encoding="utf-8")


def test_doctor_repair_apply_installs_checkpoint_hook(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    hook = repo / ".git" / "hooks" / "commit-msg"
    hook.unlink()

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "checkpoint-hook-install" in applied
    assert hook.exists()
    hook_text = hook.read_text(encoding="utf-8")
    assert "MB_BIN=" in hook_text
    assert '"$MB_CHECKPOINT" checkpoint --validate -' in hook_text


def test_doctor_repair_preserves_existing_checkpoint_hook(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    hook = repo / ".git" / "hooks" / "commit-msg"
    hook.write_text("#!/bin/sh\necho user hook\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["checkpoint-hook-existing"]["safe_to_apply"] is False
    assert hook.read_text(encoding="utf-8") == "#!/bin/sh\necho user hook\n"


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
    repo_shape = next(section for section in payload["sections"] if section["id"] == "repo-shape")
    legacy_check = next(
        check for check in repo_shape["checks"] if check["name"] == "legacy-campaigns"
    )
    assert legacy_check["state"] == "warn"


def test_doctor_repair_plan_reports_stale_generated_guidance_privately(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "stale-guidance"
    init_run(path=str(repo), name="Acme")
    (repo / "CLAUDE.md").write_text(
        "\n".join(
            [
                "# Acme",
                "",
                "## Folders",
                "",
                "- `reference/` - current business memory and active write target",
                "- `campaigns/` - current coordinated work",
                "",
                "Private customer note that should never appear in lint output.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "migration-drift")
    assert section["state"] == "warn"
    checks = {check["name"]: check for check in section["checks"]}
    assert "stale-claude-reference-guidance" in checks
    assert "stale-claude-campaigns-guidance" in checks
    assert checks["stale-claude-reference-guidance"]["content_included"] is False
    assert "Private customer note" not in result.stdout
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["migration-drift-review"]["mode"] == "manual"
    assert actions["migration-drift-review"]["safe_to_apply"] is False


def test_doctor_repair_plan_reports_migration_shape_drift(tmp_path: Path) -> None:
    repo = tmp_path / "shape-drift"
    init_run(path=str(repo), name="Acme")
    (repo / "reference" / "core").mkdir(parents=True)
    (repo / "reference" / "core" / "offer.md").write_text("# Legacy offer\n", encoding="utf-8")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "config.yaml").write_text(
        "reference_structure:\n  core: reference/core\n",
        encoding="utf-8",
    )
    legacy = repo / "campaigns" / "2026-04-launch"
    legacy.mkdir(parents=True)
    (legacy / "campaign.md").write_text(
        "---\nslug: launch\nstatus: active\n---\n# Launch\n",
        encoding="utf-8",
    )
    wrong_push = repo / "pushes" / "launch" / "push.md"
    wrong_push.parent.mkdir(parents=True)
    wrong_push.write_text(
        (
            "---\n"
            "type: push\n"
            "slug: launch\n"
            "kind: launch\n"
            "status: active\n"
            "health: unknown\n"
            "goal: {}\n"
            "owner: Devon\n"
            "audience: buyers\n"
            "offer: offer\n"
            "promise: promise\n"
            "---\n"
            "# Push\n"
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "migration-drift")
    codes = {check["name"] for check in section["checks"]}
    assert "legacy-reference-active-content" in codes
    assert "legacy-campaigns-active-content" in codes
    assert "legacy-vip-config" in codes
    assert "push-record-wrong-shape" in codes


def test_doctor_repair_plan_exposes_validation_top_category(tmp_path: Path) -> None:
    repo = tmp_path / "validation-categories"
    init_run(path=str(repo), name="Acme")
    for slug in ("one", "two"):
        offer = repo / "core" / "offers" / slug / "offer.md"
        offer.parent.mkdir(parents=True)
        offer.write_text("---\nstatus: running\n---\n# Offer\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "validation")
    check = section["checks"][0]
    assert "top category: missing_slug" in check["summary"]
    assert check["report"]["validation_categories"]["by_category"]["missing_slug"]["count"] == 2


def test_doctor_repair_plan_reports_related_links_mirror_action(tmp_path: Path) -> None:
    repo = tmp_path / "related-links-plan"
    init_run(path=str(repo), name="Acme")
    _write_md(
        repo / "research" / "2026-05-10-audience.md",
        "---\ndate: 2026-05-10\ntopic: audience\nsource: manual\n---\n# Audience\n",
    )
    _write_md(
        repo / "decisions" / "2026-05-10-audience.md",
        (
            "---\n"
            "date: 2026-05-10\n"
            "status: accepted\n"
            "linked_research:\n"
            "  - research/2026-05-10-audience.md\n"
            "---\n"
            "# Audience decision\n"
        ),
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "related-links")
    assert section["state"] == "warn"
    assert section["checks"][0]["name"] == "decisions/2026-05-10-audience.md"
    actions = {action["id"]: action for action in payload["actions"]}
    action = actions["related-links-mirror"]
    assert action["safe_to_apply"] is True
    assert action["writes"] == ["decisions/2026-05-10-audience.md"]
    assert "validate-frontmatter" not in actions


def test_doctor_repair_apply_adds_related_links_without_deleting_human_links(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "related-links-apply"
    init_run(path=str(repo), name="Acme")
    _write_md(
        repo / "research" / "2026-05-10-audience.md",
        "---\ndate: 2026-05-10\ntopic: audience\nsource: manual\n---\n# Audience Notes\n",
    )
    decision = repo / "decisions" / "2026-05-10-audience.md"
    _write_md(
        decision,
        (
            "---\n"
            "date: 2026-05-10\n"
            "status: accepted\n"
            "linked_research:\n"
            "  - research/2026-05-10-audience.md\n"
            "---\n"
            "# Audience decision\n"
            "\n"
            "## Related links\n"
            "\n"
            "- [Existing manual note](../documents/manual.md) - keep this prose.\n"
            "\n"
            "## Consequences\n"
            "\n"
            "Keep the rest of the file.\n"
        ),
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--apply", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    applied = {action["id"]: action for action in payload["applied_actions"]}
    assert "related-links-mirror" in applied
    text = decision.read_text(encoding="utf-8")
    assert "- [Existing manual note](../documents/manual.md) - keep this prose." in text
    assert "- [audience](../research/2026-05-10-audience.md)" in text
    assert "## Consequences\n\nKeep the rest of the file." in text


def test_doctor_repair_include_migration_requires_apply_guidance(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["doctor", "repair", "--repo", str(tmp_path), "--include-migration", "--plan"],
    )

    assert result.exit_code == 2
    assert "--apply --include-migration" in result.stderr


def test_doctor_repair_plan_reuses_migration_drift_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "reuse-drift"
    init_run(path=str(repo), name="Acme")
    calls = 0

    def fake_lint(path: Path) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {
            "ok": True,
            "repo": str(path),
            "findings": [],
            "summary": {"warnings": 0, "categories": []},
        }

    monkeypatch.setattr(migration_lint, "run", fake_lint)

    doctor_mod.repair_plan(repo)

    assert calls == 1


def test_doctor_repair_plan_exposes_reference_split_truth(tmp_path: Path) -> None:
    repo = tmp_path / "split-truth"
    (repo / "core").mkdir(parents=True)
    (repo / "reference" / "core").mkdir(parents=True)
    (repo / "core" / "offer.md").write_text("# Current offer\n", encoding="utf-8")
    (repo / "reference" / "core" / "offer.md").write_text("# Legacy offer\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "repo-shape")
    reference_check = next(
        check for check in section["checks"] if check["name"] == "reference/core"
    )
    assert reference_check["state"] == "warn"
    assert reference_check["kind"] == "split-truth"
    assert "split truth" in reference_check["summary"]


def test_doctor_repair_plan_reports_stale_vip_local_state(tmp_path: Path) -> None:
    repo = tmp_path / "legacy-vip"
    init_run(path=str(repo), name="Acme")
    (repo / "core" / "offers" / "community").mkdir(parents=True)
    (repo / "core" / "offers" / "community" / "offer.md").write_text(
        "---\nslug: community\nstatus: running\n---\n# Community\n",
        encoding="utf-8",
    )
    (repo / ".vip").mkdir()
    (repo / ".vip" / "local.yaml").write_text("current_offer: community\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "offer-topology")
    vip_check = next(check for check in section["checks"] if check["name"] == ".vip/local.yaml")
    assert vip_check["state"] == "warn"
    assert vip_check["kind"] == "legacy-vip-local-state"
    assert vip_check["current_offer_present"] is True
    assert vip_check["value_included"] is False
    assert "community" not in json.dumps(vip_check)
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["offer-topology-review"]["mode"] == "manual"
    assert actions["offer-topology-review"]["safe_to_apply"] is False


def test_doctor_repair_plan_flags_offer_slug_folder_drift(tmp_path: Path) -> None:
    repo = tmp_path / "offer-drift"
    init_run(path=str(repo), name="Acme")
    offer = repo / "core" / "offers" / "community" / "offer.md"
    offer.parent.mkdir(parents=True)
    offer.write_text(
        "---\nslug: noontide-community\nstatus: running\n---\n# Community\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "offer-topology")
    drift = next(check for check in section["checks"] if check["kind"] == "offer-slug-drift")
    assert drift["state"] == "warn"
    assert drift["folder_slug"] == "community"
    assert drift["declared_slug"] == "noontide-community"


def test_doctor_repair_plan_keeps_normal_multi_offer_repo_quiet(tmp_path: Path) -> None:
    repo = tmp_path / "normal-multi-offer"
    init_run(path=str(repo), name="Acme")
    (repo / "core" / "offer.md").write_text("# Brand offer thesis\n", encoding="utf-8")
    for slug in ("community", "agency"):
        offer = repo / "core" / "offers" / slug / "offer.md"
        offer.parent.mkdir(parents=True)
        offer.write_text(f"---\nslug: {slug}\nstatus: running\n---\n# {slug}\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "offer-topology")
    kinds = {check["kind"] for check in section["checks"]}
    assert section["state"] == "ok"
    assert "offer-slug-drift" not in kinds
    assert "multi-offer-review" not in kinds
    assert "brand-offer-slug-overlap" not in kinds


def test_doctor_repair_plan_flags_multi_offer_session_disagreement(tmp_path: Path) -> None:
    repo = tmp_path / "multi-offer"
    init_run(path=str(repo), name="Acme")
    (repo / "core" / "offer.md").write_text(
        "---\nslug: community\nstatus: running\n---\n# Brand thesis\n",
        encoding="utf-8",
    )
    for slug in ("community", "agency"):
        offer = repo / "core" / "offers" / slug / "offer.md"
        offer.parent.mkdir(parents=True)
        offer.write_text(f"---\nslug: {slug}\nstatus: running\n---\n# {slug}\n", encoding="utf-8")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "local.yaml").write_text("current_offer: community\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "offer-topology")
    kinds = {check["kind"] for check in section["checks"]}
    assert "multi-offer-review" in kinds
    assert "brand-offer-slug-overlap" in kinds
    assert section["state"] == "warn"


def test_doctor_repair_plan_audits_mixed_vip_yaml_without_values(tmp_path: Path) -> None:
    repo = tmp_path / "legacy-vip-audit"
    init_run(path=str(repo), name="Acme")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "local.yaml").write_text(
        "\n".join(
            [
                "current_offer: community",
                "user:",
                "  name: Example Operator",
                "session:",
                "  show_context_tips: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / ".vip" / "config.yaml").write_text(
        "\n".join(
            [
                "business_name: Example Business",
                "business_type: community",
                "offer_structure: multi",
                "tools:",
                "  apify:",
                "    status: installed",
                "mcps:",
                "  google_drive:",
                "    required_for: docs",
                "infrastructure:",
                "  site:",
                "    provider: cloudflare",
                "content:",
                "  default_channel: newsletter",
                "skills:",
                "  ads:",
                "    default_count: 5",
                "client_repos:",
                "  example_client: /private/path/redacted",
                "reference_structure:",
                "  core: reference/core",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    before_local = (repo / ".vip" / "local.yaml").read_text(encoding="utf-8")
    before_config = (repo / ".vip" / "config.yaml").read_text(encoding="utf-8")
    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    assert (repo / ".vip" / "local.yaml").read_text(encoding="utf-8") == before_local
    assert (repo / ".vip" / "config.yaml").read_text(encoding="utf-8") == before_config
    payload = json.loads(result.stdout)
    assert payload["read_only"] is True
    section = next(section for section in payload["sections"] if section["id"] == "legacy-vip")
    assert section["state"] == "warn"
    by_name = {check["name"]: check for check in section["checks"]}
    local_entries = {entry["key"]: entry for entry in by_name[".vip/local.yaml"]["entries"]}
    config_entries = {entry["key"]: entry for entry in by_name[".vip/config.yaml"]["entries"]}

    assert local_entries["current_offer"]["classification"] == "local-session-state"
    assert local_entries["user.name"]["classification"] == "machine-local-preference"
    assert local_entries["session.show_context_tips"]["classification"] == (
        "machine-local-session-state"
    )
    assert config_entries["business_name"]["classification"] == "durable-business-truth"
    assert config_entries["tools.apify.status"]["classification"] == "stale-runtime-snapshot"
    assert config_entries["mcps.google_drive.required_for"]["classification"] == (
        "provider-readiness-hint"
    )
    assert config_entries["infrastructure.site.provider"]["classification"] == (
        "provider-or-infra-hint"
    )
    assert config_entries["content.default_channel"]["classification"] == "legacy-skill-default"
    assert config_entries["skills.ads.default_count"]["classification"] == "legacy-skill-default"
    assert config_entries["client_repos.example_client"]["classification"] == "repo-topology-hint"
    assert config_entries["reference_structure.core"]["classification"] == "stale-legacy-layout"
    assert all(entry["value_included"] is False for entry in local_entries.values())
    assert all(entry["value_included"] is False for entry in config_entries.values())
    assert "Example Operator" not in result.stdout
    assert "/private/path" not in result.stdout
    actions = {action["id"]: action for action in payload["actions"]}
    assert actions["legacy-vip-audit"]["mode"] == "manual"
    assert actions["legacy-vip-audit"]["safe_to_apply"] is False


def test_doctor_repair_plan_handles_malformed_vip_yaml(tmp_path: Path) -> None:
    repo = tmp_path / "bad-vip"
    init_run(path=str(repo), name="Acme")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "config.yaml").write_text("tools: [unterminated\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "legacy-vip")
    check = next(check for check in section["checks"] if check["name"] == ".vip/config.yaml")
    assert check["state"] == "warn"
    assert check["parse_error"]
    assert check["deletion"]["safe"] is False


def test_doctor_repair_plan_handles_non_mapping_vip_yaml(tmp_path: Path) -> None:
    repo = tmp_path / "list-vip"
    init_run(path=str(repo), name="Acme")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "config.yaml").write_text("- one\n- two\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "legacy-vip")
    check = next(check for check in section["checks"] if check["name"] == ".vip/config.yaml")
    assert check["state"] == "warn"
    assert check["entries"] == []
    assert check["deletion"]["safe"] is False


def test_doctor_repair_plan_flags_vip_yaml_symlink_without_reading(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "symlink-vip"
    init_run(path=str(repo), name="Acme")
    private = tmp_path / "private-config.yaml"
    private.write_text("business_name: Private Business\n", encoding="utf-8")
    (repo / ".vip").mkdir()
    (repo / ".vip" / "config.yaml").symlink_to(private)

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    assert "Private Business" not in result.stdout
    payload = json.loads(result.stdout)
    section = next(section for section in payload["sections"] if section["id"] == "legacy-vip")
    check = next(check for check in section["checks"] if check["name"] == ".vip/config.yaml")
    assert check["state"] == "warn"
    assert check["entries"] == []
    assert check["deletion"]["safe"] is False
    assert "symlink" in check["summary"]


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

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "claude", "--json"]
    )

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


def test_doctor_repair_plan_json_frames_nonzero_plan_as_usable_findings(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Biz")
    (repo / "AGENTS.md").write_text("# stale\n\nNo facts here.\n", encoding="utf-8")

    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code in {0, 1}
    payload = json.loads(result.stdout)
    interpretation = payload["plan_interpretation"]
    assert interpretation["read_only_plan"] is True
    if payload["actions"]:
        assert interpretation["nonzero_exit_can_still_include_usable_plan"] is True
        assert interpretation["state"] in {
            "plan_produced_with_findings",
            "plan_produced_with_blockers",
        }


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

    monkeypatch.setattr(
        doctor_mod.engine_mod,  # type: ignore[attr-defined]
        "engine_root",
        lambda: active_root,
    )

    result = doctor_mod._legacy_claude_symlinks(repo)

    assert result["repairable"] == 0
    assert result["findings"][0]["state"] == "info"
    assert result["findings"][0]["safe_to_repair"] is False


# ---------------------------------------------------------------------------
# Topology drift section (MAIN-289)
# ---------------------------------------------------------------------------


_VALID_TOPOLOGY_REGISTRY = """\
---
type: repo_topology
status: active
schema: mb.repo_topology.v0
home: github:example-co/example
business_display_name: Example Business
repos:
  - slug: example
    display_name: Example Business
    role: business
    lifecycle: active
    github_owner: example-co
    repo_name: example
    remote: github:example-co/example
    visibility: team_private
    relationship: hub_for
  - slug: workshop-site
    display_name: Workshop site
    role: site
    lifecycle: active
    relationship: execution_vehicle_for
    parent: example
    github_owner: example-co
    repo_name: workshop-site
    remote: github:example-co/workshop-site
    visibility: public
---
# Topology
"""


def _write_registry(repo: Path, body: str) -> None:
    path = repo / "core" / "operations" / "repo-topology.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _write_child_descriptor(repo: Path, payload: dict[str, Any]) -> None:
    path = repo / ".mainbranch" / "repo.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _topology_section(payload: dict[str, Any]) -> dict[str, Any]:
    return next(section for section in payload["sections"] if section["id"] == "topology-drift")


def test_doctor_topology_drift_section_info_when_no_registry(tmp_path: Path) -> None:
    repo = tmp_path / "no-topology"
    (repo / "core").mkdir(parents=True)  # minimal business marker (doctor guards bare dirs)

    payload = doctor_mod.repair_plan(repo=str(repo))

    section = _topology_section(payload)
    assert section["state"] == "info"
    assert "optional" in section["summary"].lower() or "no topology" in section["summary"].lower()
    action_ids = {action["id"] for action in payload["actions"]}
    assert "topology-drift-review" not in action_ids


def test_doctor_topology_drift_section_ok_when_registry_clean(tmp_path: Path) -> None:
    repo = tmp_path / "clean-topology"
    repo.mkdir()
    _write_registry(repo, _VALID_TOPOLOGY_REGISTRY)

    payload = doctor_mod.repair_plan(repo=str(repo))

    section = _topology_section(payload)
    assert section["state"] == "ok"
    assert "no drift detected" in section["summary"].lower()
    action_ids = {action["id"] for action in payload["actions"]}
    assert "topology-drift-review" not in action_ids


def test_doctor_topology_drift_section_warn_when_descriptor_orphan(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "orphan-descriptor"
    repo.mkdir()
    _write_child_descriptor(
        repo,
        {
            "schema": "mb.child_repo.v0",
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "display_name": "Example Business",
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )

    payload = doctor_mod.repair_plan(repo=str(repo))

    section = _topology_section(payload)
    assert section["state"] == "warn"
    actions = {action["id"]: action for action in payload["actions"]}
    assert "topology-drift-review" in actions
    review = actions["topology-drift-review"]
    assert review["mode"] == "manual"
    assert review["safe_to_apply"] is False


def test_doctor_topology_drift_section_warn_on_descriptor_role_mismatch(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "role-mismatch"
    repo.mkdir()
    _write_registry(repo, _VALID_TOPOLOGY_REGISTRY)
    # Descriptor handle matches workshop-site (registry role: site) but
    # claims role=product, triggering topology_descriptor_role_mismatch.
    _write_child_descriptor(
        repo,
        {
            "schema": "mb.child_repo.v0",
            "role": "product",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "display_name": "Example Business",
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )

    payload = doctor_mod.repair_plan(repo=str(repo))

    section = _topology_section(payload)
    assert section["state"] == "warn"
    check_codes = {str(check.get("name")) for check in section.get("checks", [])}
    assert "topology_descriptor_role_mismatch" in check_codes


def test_doctor_topology_drift_preview_only(tmp_path: Path) -> None:
    repo = tmp_path / "preview-only"
    repo.mkdir()
    _write_child_descriptor(
        repo,
        {
            "schema": "mb.child_repo.v0",
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "display_name": "Example Business",
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )

    payload = doctor_mod.repair_plan(repo=str(repo))

    actions = {action["id"]: action for action in payload["actions"]}
    review = actions["topology-drift-review"]
    assert review["safe_to_apply"] is False
    assert review["mode"] == "manual"
    assert "does not rename" in review["reason"].lower()


def test_derive_audience_maps_mode_and_safety() -> None:
    assert doctor_mod._derive_audience("read", True) == "informational"
    assert doctor_mod._derive_audience("read", False) == "informational"
    assert doctor_mod._derive_audience("write", True) == "mechanical"
    assert doctor_mod._derive_audience("write", False) == "operator_decision"
    assert doctor_mod._derive_audience("manual", True) == "operator_decision"
    assert doctor_mod._derive_audience("manual", False) == "operator_decision"


def test_doctor_action_emits_audience_and_operator_summary() -> None:
    safe_write = doctor_mod._action(
        id="x",
        title="Apply mirror",
        state="warn",
        mode="write",
        command="mb doctor repair --apply",
        safe_to_apply=True,
        reason="Restores the Related links mirror.",
    )
    assert safe_write["audience"] == "mechanical"
    assert safe_write["operator_summary"] == "Restores the Related links mirror."

    read_only = doctor_mod._action(
        id="y",
        title="Inspect",
        state="ok",
        mode="read",
        command="mb doctor",
        safe_to_apply=True,
        reason="",
    )
    assert read_only["audience"] == "informational"
    # falls back to title when reason is empty
    assert read_only["operator_summary"] == "Inspect"

    manual = doctor_mod._action(
        id="z",
        title="Resolve cloud paths",
        state="error",
        mode="manual",
        command="open core/finance",
        safe_to_apply=False,
        reason="Operator must move files out of iCloud.",
    )
    assert manual["audience"] == "operator_decision"


def test_doctor_action_accepts_audience_override() -> None:
    override = doctor_mod._action(
        id="override",
        title="Custom",
        state="info",
        mode="write",
        command="mb x",
        safe_to_apply=True,
        reason="Default would be mechanical.",
        audience="informational",
        operator_summary="Just a heads-up.",
    )
    assert override["audience"] == "informational"
    assert override["operator_summary"] == "Just a heads-up."


def test_doctor_repair_plan_actions_always_carry_audience_and_summary(
    tmp_path: Path,
) -> None:
    """Every action emitted by repair_plan must have a valid audience and a
    non-empty operator_summary. Locks the contract agents read against."""
    repo = tmp_path / "fresh"
    (repo / "core").mkdir(parents=True)  # minimal business marker (doctor guards bare dirs)

    payload = doctor_mod.repair_plan(repo=str(repo))

    assert payload["actions"], "expected at least one action on a fresh repo"
    for action in payload["actions"]:
        assert action["audience"] in doctor_mod.AUDIENCE_VALUES, (
            f"action {action['id']} has invalid audience: {action['audience']!r}"
        )
        assert action["operator_summary"], f"action {action['id']} has empty operator_summary"


def test_dossier_section_absent_is_info(tmp_path: Path) -> None:
    section = doctor_mod._dossier_verify_section(tmp_path)

    assert section["id"] == "capability-dossier"
    assert section["state"] == "info"
    assert "mb-setup scaffolds" in section["summary"]


def test_dossier_verify_runs_only_mb_owned_commands(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    marker = tmp_path / "pwned"
    dossier = tmp_path / "core" / "operations" / "agent-access-dossier.md"
    dossier.parent.mkdir(parents=True)
    dossier.write_text(
        (
            "# Agent access dossier\n\n"
            "## Provider map (verify, don't assume)\n\n"
            "| Provider | Access level | Storage | Verify |\n"
            "|---|---|---|---|\n"
            "| Cloudflare | read | keychain | `mb connect test cloudflare` |\n"
            f"| Sneaky | full | env | `touch {marker}` |\n"
            "| Lookalike | full | env | `mb connect test cloudflare; touch pwned2` |\n"
        ),
        encoding="utf-8",
    )

    section = doctor_mod._dossier_verify_section(tmp_path)
    by_name = {check["name"]: check for check in section["checks"]}

    assert by_name["Cloudflare"]["state"] == "warn"
    assert "not_connected" in by_name["Cloudflare"]["summary"]
    assert by_name["Sneaky"]["state"] == "info"
    assert "not auto-executed" in by_name["Sneaky"]["summary"]
    assert by_name["Lookalike"]["state"] == "info"
    assert not marker.exists()
    assert not (tmp_path / "pwned2").exists()


def test_dossier_verify_reports_connected_provider_ok(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    from mb import connect as connect_mod

    repo = tmp_path
    connect_mod.connect_provider("apify", repo=repo, token="apify-fixture-token")
    dossier = repo / "core" / "operations" / "agent-access-dossier.md"
    dossier.parent.mkdir(parents=True)
    dossier.write_text(
        (
            "| Provider | Access level | Storage | Verify |\n"
            "|---|---|---|---|\n"
            "| Apify | research actors | keychain | `mb connect test apify` |\n"
        ),
        encoding="utf-8",
    )

    section = doctor_mod._dossier_verify_section(repo)

    apify = section["checks"][0]
    assert apify["name"] == "Apify"
    assert "mb connect test apify" in apify["summary"]
    assert apify["state"] in {"ok", "warn"}


def test_doctor_guard_refuses_writes_outside_business_folder(tmp_path: Path) -> None:
    (tmp_path / "stray-notes.md").write_text("# not a business\n", encoding="utf-8")

    plan = doctor_mod.repair_plan(tmp_path)
    assert plan["guard"] == "not_business_folder"
    assert plan["actions"] == []
    assert "mb onboard" in plan["summary"]
    # No phantom validation of stray markdown
    assert len(plan["sections"]) == 1

    applied = doctor_mod.repair_apply(tmp_path)
    assert applied["guard"] == "not_business_folder"
    assert applied["applied_actions"] == []
    # Nothing scaffolded into the arbitrary cwd
    assert not (tmp_path / ".claude").exists()
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".gitignore").exists()


def test_doctor_guard_passes_business_folders(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    plan = doctor_mod.repair_plan(repo)
    assert plan.get("guard") is None
    assert len(plan["sections"]) > 1
