"""Follow-ups to the Codex content-proof cleanup (#1067, #1072 item 3).

An unreadable file is kept and reported, never a traceback. Both applies prove
a file again right before removing it. Walks stop at a linked folder above a
Main Branch path. JSON that repeats a key is not proven. `mb update` passes on
the global files doctor keeps. Repair prose names the business repo.
"""

from __future__ import annotations

import json
import os
import shlex
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import codex as codex_mod
from mb import durable as durable_mod
from mb import update as update_mod
from mb.cli import app

runner = CliRunner()

RELEASED = Path(__file__).parent / "fixtures" / "codex_released"
POLICY = "# Team policy\nOur Main Branch workflow requires two reviewers.\n"
APPENDED = "\n## Team policy\nA person wrote this: require two reviewers.\n"
NOT_UTF8 = b"# mb-start\n\xff\xfe a person's file in another encoding\n"


@pytest.fixture
def roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "home" / "codex"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "home" / "skills"))
    monkeypatch.setattr(codex_mod, "_which", lambda name: "")
    return codex_mod.global_plugin_source_root(), codex_mod.global_skill_source_root()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "biz"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# Fixture\n", encoding="utf-8")
    (target / ".mb").mkdir()
    return target


def _released_files(tag: str, family: str) -> dict[str, bytes]:
    source = RELEASED / tag / family
    return {
        path.relative_to(source).as_posix(): path.read_bytes()
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }


def _place(root: Path, files: dict[str, bytes]) -> list[Path]:
    placed = []
    for relative, data in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        placed.append(path)
    return placed


def _doctor(repo: Path, *args: str) -> dict[str, Any]:
    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), *args, "--json"])
    assert result.exception is None or isinstance(result.exception, SystemExit), result.exception
    payload: dict[str, Any] = json.loads(result.stdout)
    payload["exit_code"] = result.exit_code
    return payload


def _operator(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in payload["operator_actions"]}


# --- 1. An unreadable file is kept and reported -------------------------------


def test_a_non_utf8_global_mb_start_command_is_kept_and_doctor_completes(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    command = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-start.md"
    command.write_bytes(NOT_UTF8)
    manifest = plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH

    status = codex_mod.plugin_status(repo)
    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    assert any("mb-start.md" in item for item in status["read_errors"])
    entry = _operator(plan)["codex-global-kept"]
    assert str(command) in entry["changes"]
    assert str(command) in entry["on_apply"]["keeps"]
    assert str(command) not in entry["on_apply"]["removes"]
    assert applied["exit_code"] == 0
    assert command.read_bytes() == NOT_UTF8
    assert not manifest.exists()


def test_a_non_utf8_global_skill_file_is_kept_not_overwritten(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    codex_mod.write_global_skill_source()
    skill = codex_mod.global_skill_file_path(codex_mod.CODEX_GLOBAL_SKILL_NAME)
    skill.write_bytes(NOT_UTF8)

    status = codex_mod.global_skill_status(repo)
    plan = _doctor(repo, "--plan", "--only", "codex")
    _doctor(repo, "--apply", "--only", "codex")

    assert status["read_error"]
    assert str(skill) in status["kept"]
    assert str(skill) in _operator(plan)["codex-global-kept"]["changes"]
    assert not any(item["path"] == str(skill) for item in codex_mod.global_skill_operations())
    assert skill.read_bytes() == NOT_UTF8


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="needs POSIX modes, not root")
def test_a_global_command_that_cannot_be_read_is_kept(repo: Path, roots: tuple[Path, Path]) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    command = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-start.md"
    command.chmod(0)
    try:
        status = codex_mod.plugin_status(repo)
        plan = _doctor(repo, "--plan", "--only", "codex")
        applied = _doctor(repo, "--apply", "--only", "codex")
    finally:
        command.chmod(0o644)

    assert any("mb-start.md" in item for item in status["read_errors"])
    assert str(command) in _operator(plan)["codex-global-kept"]["changes"]
    assert applied["exit_code"] == 0
    assert command.is_file()


# --- 2. Re-prove before unlink ------------------------------------------------


def test_the_global_apply_keeps_a_file_changed_after_the_plan(
    roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    plugin_root, _skills_root = roots
    placed = _place(plugin_root, _released_files("0.3.35", "plugin"))
    command = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-start.md"
    planned = codex_mod.global_skill_operations()
    assert any(item["path"] == str(command) for item in planned)
    command.write_text(command.read_text(encoding="utf-8") + APPENDED, encoding="utf-8")
    monkeypatch.setattr(codex_mod, "global_skill_operations", lambda: planned)

    result = codex_mod.write_global_skill_source()

    assert command.read_text(encoding="utf-8").endswith(APPENDED)
    assert str(command) in result["kept"]
    assert str(command) not in result["changed_paths"]
    assert not any(path.exists() for path in placed if path != command)


def test_remove_owned_entry_proves_the_file_again(tmp_path: Path) -> None:
    root = tmp_path / "old"
    [released] = _place(
        root,
        {
            "commands/mb-start.md": (
                RELEASED / "0.3.35/plugin/.agents/plugins/main-branch/commands/mb-start.md"
            ).read_bytes()
        },
    )
    operations, kept = codex_mod._owned_tree_cleanup(
        root, codex_mod._is_mainbranch_transitional_file
    )
    assert [item["path"] for item in operations] == [str(released)] and kept == []
    released.write_text(POLICY, encoding="utf-8")

    assert codex_mod._remove_owned_entry(operations[0]) is False
    assert released.read_text(encoding="utf-8") == POLICY


def test_the_repo_apply_reports_a_file_changed_after_the_plan(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    released = _released_files("0.3.30", "repo")
    _place(repo, released)
    mine = repo / ".agents/plugins/marketplace.json"
    (repo / ".agents/skills/main-branch-owner-loop/references/note.md").write_text(
        POLICY, encoding="utf-8"
    )
    plan = codex_mod.agents_md_plan(repo)
    assert any(item.get("rel") == ".agents/plugins/marketplace.json" for item in plan["operations"])
    mine.write_text('{"name": "mine"}\n', encoding="utf-8")
    monkeypatch.setattr(codex_mod, "agents_md_plan", lambda *args, **kwargs: plan)

    result = codex_mod.write_agents_md(repo)

    assert mine.read_text(encoding="utf-8") == '{"name": "mine"}\n'
    assert ".agents/plugins/marketplace.json" in result["kept"]


def _swap_for_link(folder: Path, outside: Path) -> list[Path]:
    """Move `folder` to `outside` and leave a link to it in its place; return its files."""

    outside.parent.mkdir(parents=True, exist_ok=True)
    folder.rename(outside)
    folder.symlink_to(outside, target_is_directory=True)
    return sorted(path for path in outside.rglob("*") if path.is_file())


def test_the_global_apply_keeps_files_whose_folder_became_a_link_after_the_plan(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plugin_root, _skills_root = roots
    _place(plugin_root, _released_files("0.3.35", "plugin"))
    commands = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH
    planned = codex_mod.global_skill_operations()
    assert any(item["path"].startswith(str(commands) + os.sep) for item in planned)
    moved = _swap_for_link(commands, tmp_path / "my-commands")
    monkeypatch.setattr(codex_mod, "global_skill_operations", lambda: planned)

    result = codex_mod.write_global_skill_source()

    assert moved and all(path.is_file() for path in moved)
    assert commands.is_symlink()
    assert str(commands / "mb-start.md") in result["kept"]
    assert not (plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH).exists()


def test_the_repo_apply_keeps_files_whose_agents_folder_became_a_link_after_the_plan(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _place(repo, _released_files("0.3.30", "repo"))
    plan = codex_mod.agents_md_plan(repo)
    removals = [item["rel"] for item in plan["operations"] if item["op"] != "write"]
    assert removals
    moved = _swap_for_link(repo / ".agents", tmp_path / "shared-agents")
    monkeypatch.setattr(codex_mod, "agents_md_plan", lambda *args, **kwargs: plan)

    result = codex_mod.write_agents_md(repo)

    assert moved and all(path.is_file() for path in moved)
    assert (repo / ".agents").is_symlink()
    assert sorted(result["kept"]) == sorted(removals)
    assert not any(path.startswith("removed:") for path in result["changed_paths"])


# --- 3. Walks stop at a linked folder ----------------------------------------


@pytest.mark.parametrize("linked", [".agents", ".agents/plugins"])
def test_a_linked_repo_agents_folder_is_not_walked(
    repo: Path, roots: tuple[Path, Path], tmp_path: Path, linked: str
) -> None:
    outside = tmp_path / "shared-agents"
    files = {
        relative.removeprefix(linked + "/"): data
        for relative, data in _released_files("0.3.30", "repo").items()
        if relative.startswith(linked + "/")
    }
    placed = _place(outside, files)
    link = repo / linked
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside, target_is_directory=True)

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    entry = _operator(plan)["codex-agents-md"]
    assert entry["on_apply"]["keeps"] == [linked]
    assert entry["on_apply"]["removes"] == []
    assert "is a link" in entry["reason"]
    assert applied["exit_code"] == 0
    assert link.is_symlink()
    assert all(path.is_file() for path in placed)


@pytest.mark.parametrize("via", ["override", "xdg"])
def test_a_linked_global_plugin_root_is_not_walked(
    repo: Path,
    roots: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    via: str,
) -> None:
    outside = tmp_path / "synced" / "codex"
    placed = _place(outside, _released_files("0.3.35", "plugin"))
    if via == "override":
        link = tmp_path / "plugin-root-link"
        link.symlink_to(outside, target_is_directory=True)
        monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(link))
    else:
        monkeypatch.delenv("MAINBRANCH_CODEX_PLUGIN_ROOT")
        data_home = tmp_path / "xdg"
        data_home.mkdir()
        monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
        link = data_home / "mainbranch"
        link.symlink_to(outside.parent, target_is_directory=True)

    cleanup = codex_mod.global_skill_cleanup()
    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    assert cleanup == {"removals": {}, "kept": [str(link)]}
    entry = _operator(plan)["codex-global-kept"]
    assert entry["changes"] == [str(link)]
    assert "is a link" in entry["reason"]
    assert applied["exit_code"] == 0
    assert link.is_symlink()
    assert all(path.is_file() for path in placed)


def test_write_global_plugin_source_never_walks_a_linked_agents_folder(
    roots: tuple[Path, Path], tmp_path: Path
) -> None:
    plugin_root, _skills_root = roots
    outside = tmp_path / "my-agents"
    placed = _place(
        outside,
        {
            relative.removeprefix(".agents/"): data
            for relative, data in _released_files("0.3.33", "plugin").items()
        },
    )
    plugin_root.mkdir(parents=True)
    (plugin_root / ".agents").symlink_to(outside, target_is_directory=True)

    result = codex_mod.write_global_plugin_source()

    assert result["changed_paths"] == []
    assert result["kept"] == [str(plugin_root / ".agents")]
    assert all(path.is_file() for path in placed)
    assert sorted(p.name for p in (outside / "plugins").iterdir()) == [
        "main-branch-owner-loop",
        "marketplace.json",
    ]


# --- 4. Duplicate JSON keys ---------------------------------------------------

MANIFEST = RELEASED / "0.3.35/plugin/.agents/plugins/main-branch/.codex-plugin/plugin.json"
MARKETPLACE = RELEASED / "0.3.35/plugin/.agents/plugins/marketplace.json"


def _duplicate_first_key(text: str, nested: bool) -> str:
    """Repeat a key with another value ahead of the real one, at the top or one level down."""

    payload = json.loads(text)
    if nested:
        key = next(k for k, v in payload.items() if isinstance(v, dict))
        inner = next(iter(payload[key]))
        anchor = f'"{key}": {{'
        assert anchor in text
        return text.replace(anchor, f'{anchor}\n    "{inner}": "MY-OWN",', 1)
    first = next(iter(payload))
    return text.replace("{", f'{{\n  "{first}": "MY-OWN",', 1)


@pytest.mark.parametrize("nested", [False, True], ids=["top", "nested"])
@pytest.mark.parametrize("source", [MANIFEST, MARKETPLACE], ids=["plugin", "marketplace"])
def test_json_with_a_repeated_key_is_not_proven(tmp_path: Path, source: Path, nested: bool) -> None:
    original = source.read_text(encoding="utf-8")
    doubled = _duplicate_first_key(original, nested)
    assert json.loads(doubled) == json.loads(original)  # last-wins hides the first value
    relative = source.relative_to(RELEASED / "0.3.35" / "plugin")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)

    path.write_text(original, encoding="utf-8")
    assert codex_mod._is_mainbranch_transitional_file(path)
    path.write_text(doubled, encoding="utf-8")
    assert codex_mod.normalised_generated_digest(path.name, doubled.encode()) is None
    assert not codex_mod._is_mainbranch_transitional_file(path)


def test_a_marketplace_json_with_a_repeated_name_is_kept_by_doctor(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    plugin_root, _skills_root = roots
    placed = _place(plugin_root, _released_files("0.3.35", "plugin"))
    marketplace = plugin_root / codex_mod.CODEX_MARKETPLACE_RELATIVE_PATH
    doubled = _duplicate_first_key(MARKETPLACE.read_text(encoding="utf-8"), nested=False)
    marketplace.write_text(doubled, encoding="utf-8")

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    assert _operator(plan)["codex-global-kept"]["changes"] == [str(marketplace)]
    assert applied["exit_code"] == 0
    assert marketplace.read_text(encoding="utf-8") == doubled
    assert not any(path.exists() for path in placed if path != marketplace)


# --- 5. `mb update` passes on the global files doctor keeps -------------------


@pytest.mark.parametrize("check", [False, True], ids=["run", "check"])
def test_update_reports_global_files_doctor_keeps(
    repo: Path,
    roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    check: bool,
) -> None:
    plugin_root, _skills_root = roots
    mine = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-team-policy.md"
    mine.parent.mkdir(parents=True)
    mine.write_text(POLICY, encoding="utf-8")
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)
    doctor_entry = _operator(_doctor(repo, "--plan", "--only", "codex"))["codex-global-kept"]

    result = update_mod.run(repo=repo, check=check, refresh_surfaces=False, interactive=False)
    update_mod.render_human(result)
    printed = capsys.readouterr().out

    entries = [item for item in result["operator_actions"] if item.get("id") == "codex-global-kept"]
    assert len(entries) == 1
    entry = entries[0]
    for key in ("command", "changes", "reason", "manual_step", "on_apply", "note"):
        assert entry[key] == doctor_entry[key], key
    assert (
        entry["command"] == f"mb doctor repair --repo {shlex.quote(str(repo))} --apply --only codex"
    )
    assert entry["note"] in result["warnings"]
    assert str(mine) in printed
    assert f"for you to run: {entry['command']}" in printed
    assert mine.read_text(encoding="utf-8") == POLICY


# --- 6. Repair prose names the business repo (#1072 item 3) -------------------


def test_repair_prose_names_the_repo_when_it_is_not_the_current_folder(
    tmp_path: Path, roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "my biz"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        f"# Mine\n{codex_mod.AGENTS_MANAGED_BEGIN}\nguidance\n", encoding="utf-8"
    )
    mine = repo / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-team-policy.md"
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    flag = f"--repo {shlex.quote(str(repo))}"
    command = f"mb doctor repair {flag} --apply --only codex"
    text = f"Run `mb doctor repair {flag} --plan --only codex`, review, then `{command}`."

    refused = codex_mod.agents_md_plan(repo)
    (repo / "AGENTS.md").unlink()
    mine.parent.mkdir(parents=True)
    mine.write_text(POLICY, encoding="utf-8")
    kept_plan = codex_mod.agents_md_plan(repo)
    kept_action = codex_mod.agents_md_operator_action(kept_plan, repo=repo)
    refused_action = codex_mod.agents_md_operator_action(refused, repo=repo)

    assert f"mb doctor repair {flag} --plan --only codex" in refused["refused"][0]["manual_step"]
    assert refused_action is not None and refused_action["command"] == command
    assert kept_action is not None and kept_action["command"] == command
    assert f"`{command}` (or `--all-agents`)" in kept_action["manual_step"]
    for status in (
        codex_mod.global_skill_status(repo),
        codex_mod.plugin_status(repo),
        codex_mod.instructions_status(repo),
        codex_mod.skill_status(repo),
    ):
        assert status["repair_command"] == command
        assert status["repair"] in ("", text)
    assert codex_mod.instructions_status(repo)["repair"] == text


def test_repair_prose_is_bare_in_the_repo_itself(
    repo: Path, roots: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(repo)

    assert codex_mod.repair_command(repo) == codex_mod.CODEX_REPAIR_COMMAND
    assert codex_mod.repair_text(repo) == codex_mod.CODEX_REPAIR_TEXT
    assert codex_mod.instructions_status(repo)["repair"] == codex_mod.CODEX_REPAIR_TEXT
    assert codex_mod.repair_command(None) == codex_mod.CODEX_REPAIR_COMMAND


# --- 7. Linked skill folder, link agreement, directory at SKILL.md (#1078) ----


def test_a_linked_global_skill_folder_is_kept_and_never_written_through(
    repo: Path, roots: tuple[Path, Path], tmp_path: Path
) -> None:
    _plugin_root, skills_root = roots
    mine = tmp_path / "my-skill"
    mine.mkdir()
    (mine / "SKILL.md").write_text("# my own skill\n", encoding="utf-8")
    link = skills_root / codex_mod.CODEX_GLOBAL_SKILL_NAME
    skills_root.mkdir(parents=True)
    link.symlink_to(mine, target_is_directory=True)

    result = codex_mod.write_global_skill_source()
    entry = _operator(_doctor(repo, "--plan", "--only", "codex"))["codex-global-kept"]

    assert (mine / "SKILL.md").read_text(encoding="utf-8") == "# my own skill\n"
    assert link.is_symlink()
    assert str(link) in result["kept"]
    assert str(link) in entry["changes"]
    assert "is a link" in entry["reason"]


@pytest.mark.parametrize(
    "relative",
    [
        f"{codex_mod.CODEX_PLUGIN_DIR_RELATIVE_PATH}/skills",
        codex_mod.CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH,
    ],
    ids=["plugin-skills", "legacy-plugin"],
)
def test_a_link_the_plan_keeps_is_kept_by_the_apply(
    roots: tuple[Path, Path], tmp_path: Path, relative: str
) -> None:
    plugin_root, _skills_root = roots
    mine = tmp_path / "my-folder"
    mine.mkdir()
    (mine / "note.md").write_text("mine\n", encoding="utf-8")
    link = plugin_root / relative
    link.parent.mkdir(parents=True)
    link.symlink_to(mine, target_is_directory=True)

    planned = codex_mod.global_skill_cleanup()
    result = codex_mod.write_global_plugin_source()

    assert str(link) in planned["kept"]
    assert link.is_symlink()
    assert str(link) in result["kept"]
    assert (mine / "note.md").is_file()


def test_a_directory_where_the_global_skill_file_belongs_is_kept_and_not_safe_to_apply(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    _plugin_root, skills_root = roots
    codex_mod.write_global_skill_source()
    skill = skills_root / codex_mod.CODEX_GLOBAL_SKILL_NAME / "SKILL.md"
    skill.unlink()
    skill.mkdir()
    (skill / "mine.md").write_text("mine\n", encoding="utf-8")

    plan = _doctor(repo, "--plan", "--only", "codex")
    entry = _operator(plan)["codex-global-kept"]
    action = next(item for item in plan["actions"] if item["id"] == "codex-global-skill")
    applied = codex_mod.write_global_skill_source()

    assert codex_mod.global_skill_operations() == []
    assert str(skill) in entry["changes"]
    assert "folder" in entry["reason"]
    assert action["safe_to_apply"] is False
    assert str(skill) in applied["kept"]
    assert (skill / "mine.md").is_file()


def test_the_global_apply_keeps_files_when_a_link_appears_above_the_plugin_root(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("MAINBRANCH_CODEX_PLUGIN_ROOT")
    data_home = tmp_path / "xdg"
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    plugin_root = codex_mod.global_plugin_source_root()
    _place(plugin_root, _released_files("0.3.35", "plugin"))
    planned = codex_mod.global_skill_operations()
    assert any(item["op"] == "delete" for item in planned)
    outside = tmp_path / "synced"
    (data_home / "mainbranch").rename(outside)
    (data_home / "mainbranch").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(codex_mod, "global_skill_operations", lambda: planned)

    result = codex_mod.write_global_skill_source()

    assert all(path.is_file() for path in outside.rglob("*") if not path.is_dir())
    assert len([path for path in outside.rglob("*") if path.is_file()]) == 10
    assert str(data_home / "mainbranch") in result["kept"]


# --- 8. `mb update` prints each kept note once ---------------------------------


def test_update_human_output_prints_the_kept_note_once(
    repo: Path,
    roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plugin_root, _skills_root = roots
    mine = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-team-policy.md"
    mine.parent.mkdir(parents=True)
    mine.write_text(POLICY, encoding="utf-8")
    (repo / "AGENTS.md").write_text(
        f"# Mine\n{codex_mod.AGENTS_MANAGED_BEGIN}\nguidance\n", encoding="utf-8"
    )
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)

    result = update_mod.run(repo=repo, check=True, refresh_surfaces=False, interactive=False)
    update_mod.render_human(result)
    printed = capsys.readouterr().out

    notes = {
        item["id"]: item["note"]
        for item in result["operator_actions"]
        if item.get("id") in {"codex-global-kept", "codex-agents-md"}
    }
    assert set(notes) == {"codex-global-kept", "codex-agents-md"}
    assert notes["codex-global-kept"] in result["warnings"]  # JSON is unchanged
    for note in notes.values():
        assert printed.count(note) == 1


# --- #1087: links at SKILL.md and the last plugin removal loop ---------------


@pytest.mark.parametrize("target_kind", ["folder", "dangling"])
def test_a_global_skill_file_link_is_kept_in_both_plan_and_apply(
    repo: Path, roots: tuple[Path, Path], tmp_path: Path, target_kind: str
) -> None:
    codex_mod.write_global_skill_source()
    skill = codex_mod.global_skill_file_path("main-branch")
    skill.unlink()
    outside = tmp_path / "my-folder"
    if target_kind == "folder":
        outside.mkdir()
        (outside / "note.md").write_text(POLICY, encoding="utf-8")
    skill.symlink_to(outside, target_is_directory=True)

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")
    direct = codex_mod.write_global_skill_source()

    assert skill.is_symlink()
    assert skill.readlink() == outside
    entry = _operator(plan)["codex-global-kept"]
    assert entry["on_apply"] == {"writes": [], "removes": [], "keeps": [str(skill)]}
    assert "is a link" in entry["reason"]
    action = next(item for item in plan["actions"] if item["id"] == "codex-global-skill")
    assert action["safe_to_apply"] is False
    assert _operator(applied)["codex-global-kept"]["on_apply"] == entry["on_apply"]
    assert applied["exit_code"] == 0
    assert direct["changed_paths"] == []
    assert direct["kept"] == [str(skill)]
    if target_kind == "folder":
        assert (outside / "note.md").read_text(encoding="utf-8") == POLICY
    else:
        assert not outside.exists()


def test_plugin_commands_recheck_the_parent_link_before_each_removal(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("MAINBRANCH_CODEX_PLUGIN_ROOT")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    root = codex_mod.global_plugin_source_root()
    codex_mod.write_global_plugin_source()
    # Model two retired commands with real released content proof, not a mocked proof.
    retired = {"mb-start", "mb-think"}
    commands = codex_mod.render_codex_slash_commands()
    monkeypatch.setattr(
        codex_mod,
        "render_codex_slash_commands",
        lambda: {rel: text for rel, text in commands.items() if Path(rel).stem not in retired},
    )
    monkeypatch.setattr(
        codex_mod,
        "CODEX_SLASH_COMMAND_NAMES",
        tuple(name for name in codex_mod.CODEX_SLASH_COMMAND_NAMES if name not in retired),
    )
    _place(root, _released_files("0.3.35", "plugin"))
    first = root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-start.md"
    second = first.with_name("mb-think.md")
    original = second.read_bytes()
    assert codex_mod._is_mainbranch_transitional_file(first)
    assert codex_mod._is_mainbranch_transitional_file(second)
    real_unlink = codex_mod._unlink_if_proven
    outside = tmp_path / "synced"

    def remove_then_link(path: Path, base: Path | None = None) -> bool:
        removed = real_unlink(path, base)
        if path == first:
            assert removed
            root.parent.rename(outside)
            root.parent.symlink_to(outside, target_is_directory=True)
        return removed

    monkeypatch.setattr(codex_mod, "_unlink_if_proven", remove_then_link)
    result = codex_mod.write_global_plugin_source()

    assert root.parent.is_symlink()
    assert second.read_bytes() == original
    assert str(first) in result["changed_paths"]
    assert str(second) not in result["changed_paths"]
    assert str(root.parent) in result["kept"]


@pytest.mark.parametrize("with_removals", [False, True])
def test_global_kept_manual_step_names_the_writes_in_the_apply(
    repo: Path, roots: tuple[Path, Path], with_removals: bool
) -> None:
    plugin_root, _ = roots
    codex_mod.write_global_skill_source()
    missing = codex_mod.global_skill_file_path("mb-start")
    missing.unlink()
    mine = plugin_root / "notes.md"
    mine.parent.mkdir(parents=True)
    mine.write_text(POLICY, encoding="utf-8")
    if with_removals:
        _place(plugin_root, _released_files("0.3.35", "plugin"))
    entry = _operator(_doctor(repo, "--plan", "--only", "codex"))["codex-global-kept"]

    assert entry["on_apply"]["writes"] == [str(missing)]
    assert f"writes these skill files: {missing}" in entry["manual_step"]
    for path in entry["on_apply"]["removes"]:
        assert path in entry["manual_step"]
    assert "it keeps the files above" in entry["manual_step"]


# --- #1087 item 2: a link appears above the plugin root mid-run -------------


def _tree(folder: Path) -> dict[str, bytes | None]:
    """Every entry under `folder`, with file bytes; folders map to None."""

    return {
        path.relative_to(folder).as_posix(): (path.read_bytes() if path.is_file() else None)
        for path in sorted(folder.rglob("*"))
    }


@pytest.mark.parametrize("swap_after", ["write", "removal"])
def test_plugin_source_stops_at_a_parent_link_that_appears_mid_run(
    roots: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, swap_after: str
) -> None:
    monkeypatch.delenv("MAINBRANCH_CODEX_PLUGIN_ROOT")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    root = codex_mod.global_plugin_source_root()
    _place(root, _released_files("0.3.33", "plugin"))
    outside = tmp_path / "synced"
    behind: dict[str, dict[str, bytes | None]] = {}
    done: list[str] = []

    def swap() -> None:
        root.parent.rename(outside)
        root.parent.symlink_to(outside, target_is_directory=True)
        behind["at_swap"] = _tree(outside)

    real_write = durable_mod.atomic_write_text
    real_remove = codex_mod._remove_owned_entry

    def write_then_link(path: Path, text: str) -> None:
        real_write(path, text)
        done.append(str(path))
        if swap_after == "write" and len(done) == 1:
            swap()

    def remove_then_link(item: dict[str, Any]) -> bool:
        removed = real_remove(item)
        if swap_after == "removal" and removed and not behind:
            done.append(str(item["path"]))
            swap()
        return removed

    monkeypatch.setattr(codex_mod, "atomic_write_text", write_then_link)
    monkeypatch.setattr(codex_mod, "_remove_owned_entry", remove_then_link)
    result = codex_mod.write_global_plugin_source()

    assert root.parent.is_symlink()
    assert _tree(outside) == behind["at_swap"]  # nothing behind the link was touched
    assert str(root.parent) in result["kept"]
    # The result names only what changed before the link appeared.
    if swap_after == "write":
        assert result["changed_paths"] == done[:1]
    else:
        legacy = str(root / codex_mod.CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH) + os.sep
        assert [path for path in result["changed_paths"] if path.startswith(legacy)] == done[-1:]
    assert len(result["changed_paths"]) == len(set(result["changed_paths"]))


# --- #1087 item 6: a linked skill folder that already holds the current skill -


@pytest.fixture
def linked_current(roots: tuple[Path, Path], tmp_path: Path) -> tuple[Path, Path]:
    """`main-branch` is a link to a folder of a person's that holds the current skill."""

    codex_mod.write_global_skill_source()
    link = codex_mod.global_skill_file_path(codex_mod.CODEX_GLOBAL_SKILL_NAME).parent
    mine = tmp_path / "my-skills" / "main-branch"
    mine.parent.mkdir()
    link.rename(mine)
    link.symlink_to(mine, target_is_directory=True)
    return link, mine


def test_a_current_linked_skill_folder_gets_an_informational_note_not_a_kept_step(
    repo: Path, linked_current: tuple[Path, Path]
) -> None:
    link, mine = linked_current
    before = _tree(mine)

    status = codex_mod.global_skill_status(repo)
    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")
    direct = codex_mod.write_global_skill_source()

    assert status["ok"] is True
    assert str(link) not in status["kept"]
    assert status["linked"] == [str(link)]
    assert "Nothing to do" in status["note"] and status["note"] in status["summary"]
    for payload in (plan, applied):
        assert "codex-global-kept" not in _operator(payload)
        assert not any(item["id"] == "codex-global-skill" for item in payload["actions"])
        checks = [
            check
            for section in payload["sections"]
            for check in section.get("checks", [])
            if check.get("name") == "codex-global-skill"
        ]
        assert [check["note"] for check in checks] == [status["note"]]
        assert checks[0]["state"] == "ok"
    assert applied["exit_code"] == 0
    assert codex_mod.global_skill_operations() == []
    assert direct["kept"] == [] and direct["changed_paths"] == []
    assert direct["linked"] == [str(link)] and direct["note"] == status["note"]
    assert link.is_symlink()
    assert _tree(mine) == before


@pytest.mark.parametrize("check", [False, True], ids=["run", "check"])
def test_update_shows_the_linked_folder_note_once_as_information(
    repo: Path,
    linked_current: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    check: bool,
) -> None:
    link, mine = linked_current
    before = _tree(mine)
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)

    result = update_mod.run(repo=repo, check=check, refresh_surfaces=False, interactive=False)
    update_mod.render_human(result)
    printed = capsys.readouterr().out

    note = result["codex_adapter"]["global_skill"]["note"]
    assert result["codex_adapter"]["global_skill"]["linked"] == [str(link)]
    assert not any(item.get("id") == "codex-global-kept" for item in result["operator_actions"])
    assert not any(str(link) in warning for warning in result["warnings"])
    assert printed.count(note) == 1
    assert f"note: {note}" in printed
    assert _tree(mine) == before


def test_a_stale_linked_skill_folder_still_gets_the_kept_step(
    repo: Path, linked_current: tuple[Path, Path]
) -> None:
    link, mine = linked_current
    (mine / "SKILL.md").write_text(POLICY, encoding="utf-8")

    status = codex_mod.global_skill_status(repo)
    entry = _operator(_doctor(repo, "--plan", "--only", "codex"))["codex-global-kept"]

    assert "linked" not in status and "note" not in status
    assert str(link) in status["kept"]
    assert str(link) in entry["changes"]
    assert "delete the rest yourself" in entry["manual_step"]
    assert (mine / "SKILL.md").read_text(encoding="utf-8") == POLICY
