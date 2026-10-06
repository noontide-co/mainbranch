"""Codex cleanup removes only what Main Branch wrote, and says what it does (#1056).

The global Codex folders under the person's home lose only files `mb` wrote,
one by one, and a folder goes only once it is empty. `mb init` reports a
refused AGENTS.md write the way doctor and update do. The doctor plan names
exactly what an explicit apply does, and a dangling symlink at a transitional
repo path is removed as a link.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mb import codex as codex_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()

NOTE = "## Our team rules\n\nShip on Fridays only after the owner says yes.\n"
MINE = "Notes I wrote myself.\n"


@pytest.fixture
def roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    plugin_root = tmp_path / "home" / ".local" / "share" / "mainbranch" / "codex"
    skills_root = tmp_path / "home" / ".codex" / "skills"
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(plugin_root))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(skills_root))
    return codex_mod.global_plugin_source_root(), codex_mod.global_skill_source_root()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "biz"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# Acme\n", encoding="utf-8")
    return target


def _current_block(repo: Path) -> str:
    rendered = codex_mod.render_agents_md(repo, name="Acme", gh_username="acme-owner")
    return codex_mod._managed_agents_block(rendered)


RELEASED = Path(__file__).parent / "fixtures" / "codex_released"


def _released(relative: str) -> str:
    """A file exactly as a released `mb` wrote it (see fixtures/codex_released)."""

    return (RELEASED / relative).read_text(encoding="utf-8")


def _old_plugin_skill() -> str:
    return _released("0.3.30/repo/.agents/skills/main-branch-owner-loop/SKILL.md")


# --- Item 3: the global plugin source and skill folders ----------------------


def test_global_refresh_keeps_a_persons_file_in_the_old_plugin_root(
    roots: tuple[Path, Path],
) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    mine = plugin_root / "my-notes.md"
    mine.write_text(MINE, encoding="utf-8")
    manifest = plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH
    assert manifest.is_file()

    before = codex_mod.global_skill_status(Path.cwd())
    result = codex_mod.write_global_skill_source()

    assert str(plugin_root) in before["stale"]
    assert mine.read_text(encoding="utf-8") == MINE
    assert not manifest.exists()
    assert not (plugin_root / codex_mod.CODEX_MARKETPLACE_RELATIVE_PATH).exists()
    assert not (plugin_root / ".agents").exists()
    assert result["kept"] == [str(mine)]
    assert result["status"]["ok"] is True
    assert result["status"]["kept"] == [str(mine)]


def test_global_refresh_leaves_an_override_root_that_holds_no_main_branch_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unrelated = tmp_path / "projects"
    (unrelated / "src").mkdir(parents=True)
    (unrelated / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (unrelated / "plugin.json").write_text('{"name": "mine"}\n', encoding="utf-8")
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(unrelated))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))

    assert codex_mod.global_skill_cleanup()["removals"] == {}
    result = codex_mod.write_global_skill_source()

    assert (unrelated / "src" / "app.py").is_file()
    assert (unrelated / "plugin.json").is_file()
    assert str(unrelated) not in result["changed_paths"]
    assert result["status"]["ok"] is True


def test_global_refresh_removes_only_the_mb_file_in_the_legacy_skill_folder(
    roots: tuple[Path, Path],
) -> None:
    _plugin_root, skills_root = roots
    legacy = skills_root / codex_mod.CODEX_LEGACY_GLOBAL_SKILL_NAME
    (legacy / "references").mkdir(parents=True)
    (legacy / "SKILL.md").write_text(_old_plugin_skill(), encoding="utf-8")
    mine = legacy / "references" / "mine.md"
    mine.write_text(MINE, encoding="utf-8")

    result = codex_mod.write_global_skill_source()

    assert not (legacy / "SKILL.md").exists()
    assert mine.read_text(encoding="utf-8") == MINE
    assert result["kept"] == [str(mine)]
    assert result["status"]["ok"] is True


def test_global_refresh_keeps_extra_files_in_a_retired_skill_folder(
    roots: tuple[Path, Path],
) -> None:
    _plugin_root, skills_root = roots
    folder = skills_root / "weekly-review"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        _released("0.3.36/skills/weekly-review/SKILL.md"), encoding="utf-8"
    )
    (folder / "my-checklist.md").write_text(MINE, encoding="utf-8")

    operations = codex_mod.global_skill_operations()
    result = codex_mod.write_global_skill_source()

    assert {"op": "delete", "path": str(folder / "SKILL.md")} in [
        {"op": item["op"], "path": item["path"]} for item in operations
    ]
    assert all(item["op"] in {"write", "delete"} for item in operations)
    assert not (folder / "SKILL.md").exists()
    assert (folder / "my-checklist.md").read_text(encoding="utf-8") == MINE
    assert str(folder / "my-checklist.md") in result["kept"]


def test_global_refresh_keeps_a_persons_linked_skill_at_a_retired_name(
    roots: tuple[Path, Path], tmp_path: Path
) -> None:
    _plugin_root, skills_root = roots
    mine = tmp_path / "my-skills" / "weekly-review"
    mine.mkdir(parents=True)
    (mine / "SKILL.md").write_text("---\nname: weekly-review\n---\n\nMine.\n", encoding="utf-8")
    skills_root.mkdir(parents=True)
    link = skills_root / "weekly-review"
    link.symlink_to(mine, target_is_directory=True)

    result = codex_mod.write_global_skill_source()

    assert link.is_symlink()
    assert (mine / "SKILL.md").is_file()
    assert str(link) not in result["changed_paths"]
    assert result["status"]["ok"] is True


def test_global_refresh_never_follows_a_symlink_inside_the_plugin_root(
    roots: tuple[Path, Path], tmp_path: Path
) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "SKILL.md").write_text(_old_plugin_skill(), encoding="utf-8")
    link = plugin_root / "linked"
    link.symlink_to(outside, target_is_directory=True)

    result = codex_mod.write_global_skill_source()

    assert (outside / "SKILL.md").is_file()
    assert link.is_symlink()
    assert str(link) in result["kept"]


def test_write_global_plugin_source_keeps_unknown_files_it_did_not_write(
    roots: tuple[Path, Path],
) -> None:
    plugin_root, _skills_root = roots
    commands = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH
    commands.mkdir(parents=True)
    mine = commands / "my-command.md"
    mine.write_text(MINE, encoding="utf-8")
    retired = commands / "mb-checkpoint.md"
    retired.write_text(
        _released("0.3.33/plugin/.agents/plugins/main-branch-owner-loop/commands/mb-checkpoint.md"),
        encoding="utf-8",
    )
    old_plugin = plugin_root / codex_mod.CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH
    old_skill = old_plugin / "skills" / "main-branch-owner-loop" / "SKILL.md"
    old_skill.parent.mkdir(parents=True)
    old_skill.write_text(_old_plugin_skill(), encoding="utf-8")
    old_mine = old_plugin / "notes.md"
    old_mine.write_text(MINE, encoding="utf-8")

    result = codex_mod.write_global_plugin_source()

    assert mine.read_text(encoding="utf-8") == MINE
    assert not retired.exists()
    assert not old_skill.exists()
    assert not (old_plugin / "skills").exists()
    assert old_mine.read_text(encoding="utf-8") == MINE
    assert sorted(result["kept"]) == sorted([str(mine), str(old_mine)])


def test_clean_global_install_and_refresh_are_unchanged(roots: tuple[Path, Path]) -> None:
    plugin_root, skills_root = roots
    codex_mod.write_global_plugin_source()

    first = codex_mod.write_global_skill_source()
    second = codex_mod.write_global_skill_source()

    assert first["changed"] is True
    assert not plugin_root.exists()
    assert first["kept"] == []
    assert second["changed"] is False
    assert second["status"]["ok"] is True
    for name in codex_mod.CODEX_GLOBAL_SKILL_NAMES:
        assert (skills_root / name / "SKILL.md").is_file()


def test_doctor_plan_reports_kept_global_files(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plugin_root, _skills_root = roots
    monkeypatch.setattr(codex_mod, "_which", lambda name: "")
    codex_mod.write_global_plugin_source()
    mine = plugin_root / "my-notes.md"
    mine.write_text(MINE, encoding="utf-8")
    target = tmp_path / "biz-plan"
    init_run(path=str(target), name="Acme")

    result = runner.invoke(
        app, ["doctor", "repair", "--repo", str(target), "--plan", "--only", "codex", "--json"]
    )

    payload = json.loads(result.stdout)
    actions = {item["id"]: item for item in payload["actions"]}
    action = actions["codex-global-skill"]
    assert action["kept"] == [str(mine)]
    assert {"op": "delete", "path": str(mine)} not in action["operations"]
    assert {
        "op": "delete",
        "path": str(plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH),
    } in action["operations"]


# --- Item 1: `mb init` reports a refused AGENTS.md write ---------------------


def _damaged_agents_md(target: Path) -> str:
    block = _current_block(target).replace(codex_mod.AGENTS_MANAGED_END + "\n", "")
    return block + "\n" + NOTE


def test_init_reports_a_refused_agents_md_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))
    target = tmp_path / "biz-init"
    target.mkdir()
    before = _damaged_agents_md(target)
    (target / "AGENTS.md").write_text(before, encoding="utf-8")

    result = init_run(path=str(target), name="Acme", owner_github="acme-owner")

    assert result["status"] == "ok"
    assert (target / "AGENTS.md").read_text(encoding="utf-8") == before
    assert "AGENTS.md" not in result["created"]
    refusal = result["codex_agents_md"]["refused"][0]
    assert refusal["code"] == "missing_end_marker"
    assert result["codex_agents_md"]["ok"] is False
    [action] = result["operator_actions"]
    assert action["id"] == "codex-agents-md"
    assert action["command"] == codex_mod.CODEX_REPAIR_COMMAND
    assert action["reason"] == refusal["reason"]
    assert action["manual_step"] == refusal["manual_step"]
    assert result["warnings"] == [action["note"]]
    # The same entry doctor lists for this repo.
    plan = codex_mod.agents_md_plan(target, name="Acme", gh_username="acme-owner")
    doctor_entry = codex_mod.agents_md_operator_action(plan)
    assert doctor_entry is not None
    assert (doctor_entry["reason"], doctor_entry["manual_step"]) == (
        action["reason"],
        action["manual_step"],
    )


def test_init_cli_warns_on_a_refused_agents_md_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))
    target = tmp_path / "biz-cli"
    target.mkdir()
    (target / "AGENTS.md").write_text(_damaged_agents_md(target), encoding="utf-8")

    result = runner.invoke(app, ["init", str(target), "--name", "Acme"])

    assert result.exit_code == 0
    assert "warning:" in result.stderr
    assert codex_mod.AGENTS_MANAGED_END in result.stderr
    assert codex_mod.CODEX_REPAIR_COMMAND in result.stderr


def test_fresh_init_has_no_codex_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))
    target = tmp_path / "biz-fresh"

    result = init_run(path=str(target), name="Acme")

    assert result["status"] == "ok"
    assert "AGENTS.md" in result["created"]
    assert result["codex_agents_md"] == {"ok": True, "refused": [], "kept": []}
    assert result["warnings"] == []
    assert result["operator_actions"] == []


# --- Item 2: the plan names exactly what an apply does ------------------------


def _kept_case(repo: Path) -> tuple[Path, Path]:
    (repo / "AGENTS.md").write_text("# Acme\n\nOld notes, no facts.\n", encoding="utf-8")
    folder = repo / ".agents" / "skills" / "main-branch"
    folder.mkdir(parents=True)
    mine = folder / "my-notes.md"
    mine.write_text(MINE, encoding="utf-8")
    skill = folder / "SKILL.md"
    skill.write_text(codex_mod.render_codex_global_skill_md("main-branch"), encoding="utf-8")
    return mine, skill


@pytest.mark.parametrize("scope", [["--only", "codex"], ["--all-agents"]])
def test_unsafe_codex_plan_states_exactly_what_the_apply_does(
    repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    scope: list[str],
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "plugin"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))
    monkeypatch.setattr(codex_mod, "_which", lambda name: "")
    mine, skill = _kept_case(repo)
    agents_before = (repo / "AGENTS.md").read_text(encoding="utf-8")

    plan = json.loads(
        runner.invoke(
            app, ["doctor", "repair", "--repo", str(repo), "--plan", *scope, "--json"]
        ).stdout
    )
    action = {item["id"]: item for item in plan["actions"]}["codex-agents-md"]
    operator = {item.get("id"): item for item in plan["operator_actions"]}["codex-agents-md"]

    assert action["safe_to_apply"] is False
    expected = {
        "writes": ["AGENTS.md"],
        "removes": [".agents/skills/main-branch/SKILL.md"],
        "keeps": [".agents/skills/main-branch/my-notes.md"],
    }
    assert action["on_apply"] == expected
    assert operator["on_apply"] == expected
    assert ".agents/skills/main-branch/SKILL.md" in operator["manual_step"]
    assert "then run" not in operator["manual_step"]

    applied = json.loads(
        runner.invoke(
            app, ["doctor", "repair", "--repo", str(repo), "--apply", *scope, "--json"]
        ).stdout
    )
    result = {item["id"]: item for item in applied["applied_actions"]}["codex-agents-md"]

    assert sorted(result["result"]["changed_paths"]) == sorted(
        ["AGENTS.md", "removed:.agents/skills/main-branch/SKILL.md"]
    )
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") != agents_before
    assert not skill.exists()
    assert mine.read_text(encoding="utf-8") == MINE


def test_refused_codex_plan_says_an_apply_changes_nothing(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "plugin"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "skills"))
    monkeypatch.setattr(codex_mod, "_which", lambda name: "")
    # Guidance from an older template, so a repair is due, and no end marker.
    before = _damaged_agents_md(repo).replace(codex_mod.guidance_template_hash(), "0" * 16)
    (repo / "AGENTS.md").write_text(before, encoding="utf-8")

    plan = json.loads(
        runner.invoke(
            app, ["doctor", "repair", "--repo", str(repo), "--plan", "--only", "codex", "--json"]
        ).stdout
    )
    action = {item["id"]: item for item in plan["actions"]}["codex-agents-md"]
    runner.invoke(
        app, ["doctor", "repair", "--repo", str(repo), "--apply", "--only", "codex", "--json"]
    )

    assert action["on_apply"] == {"writes": [], "removes": [], "keeps": []}
    assert action["operations"] == []
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == before


# --- Item 4: a dangling symlink at a transitional path -----------------------


def test_a_dangling_symlink_at_a_transitional_path_is_removed_as_a_link(
    repo: Path, tmp_path: Path
) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    link = repo / ".agents" / "skills" / "main-branch"
    link.parent.mkdir(parents=True)
    link.symlink_to(tmp_path / "gone", target_is_directory=True)

    status = codex_mod.instructions_status(repo)
    plan = codex_mod.agents_md_plan(repo)
    codex_mod.write_agents_md(repo)

    assert ".agents/skills/main-branch" in status["repo_local_plugin_paths"]
    assert [(item["op"], item["rel"]) for item in plan["operations"]] == [
        ("delete_tree", ".agents/skills/main-branch")
    ]
    assert not os.path.lexists(link)
    assert not (tmp_path / "gone").exists()
    assert codex_mod.instructions_status(repo)["ok"] is True


def test_a_live_symlink_at_a_transitional_path_is_unlinked_and_its_target_kept(
    repo: Path, tmp_path: Path
) -> None:
    (repo / "AGENTS.md").write_text(_current_block(repo), encoding="utf-8")
    elsewhere = tmp_path / "my-skills"
    elsewhere.mkdir()
    (elsewhere / "SKILL.md").write_text(MINE, encoding="utf-8")
    link = repo / ".agents" / "skills" / "main-branch"
    link.parent.mkdir(parents=True)
    link.symlink_to(elsewhere, target_is_directory=True)

    codex_mod.write_agents_md(repo)

    assert not os.path.lexists(link)
    assert (elsewhere / "SKILL.md").read_text(encoding="utf-8") == MINE
