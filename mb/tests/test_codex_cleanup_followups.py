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
