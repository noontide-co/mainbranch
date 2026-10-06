"""Codex cleanup deletes only content proven to be Main Branch's (0.6.4 release gate).

A file at an old Codex path, repo-local or global, is Main Branch's only when
its content, normalised for what varies per install, equals a version a
released `mb` wrote there (`mb.codex_known_files`) or what this `mb` renders.
A person's look-alike or a generated file with additions stays and is reported
for a person to decide. The fixtures in `fixtures/codex_released` are files
exactly as released versions wrote them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import codex as codex_mod
from mb.cli import app
from mb.codex_known_files import KNOWN_FILE_DIGESTS, RELEASES_REPLAYED

runner = CliRunner()

RELEASED = Path(__file__).parent / "fixtures" / "codex_released"
ROOT = Path(__file__).resolve().parents[2]
POLICY = "# Team policy\nOur Main Branch workflow requires two reviewers.\n"
APPENDED = "\n## Team policy\nA person wrote this: require two reviewers.\n"


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


def _generated_command(name: str = "mb-start") -> tuple[str, str]:
    relative = f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md"
    return relative, codex_mod.render_codex_slash_commands()[relative]


def _doctor(repo: Path, *args: str) -> dict[str, Any]:
    result = runner.invoke(app, ["doctor", "repair", "--repo", str(repo), *args, "--json"])
    payload: dict[str, Any] = json.loads(result.stdout)
    payload["exit_code"] = result.exit_code
    return payload


# --- The two reproduced cases, repo-local ------------------------------------


def test_a_persons_mb_command_mentioning_main_branch_is_kept_in_the_repo(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    mine = repo / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-team-policy.md"
    mine.parent.mkdir(parents=True)
    mine.write_text(POLICY, encoding="utf-8")

    plan = codex_mod.agents_md_plan(repo)
    action = codex_mod.agents_md_operator_action(plan)
    codex_mod.write_agents_md(repo)

    assert codex_mod._is_mainbranch_transitional_file(mine) is False
    assert plan["kept"] == [f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/mb-team-policy.md"]
    assert action is not None
    assert "mb-team-policy.md" in action["reason"]
    assert mine.read_text(encoding="utf-8") == POLICY


def test_doctor_apply_keeps_a_generated_repo_command_with_a_persons_addition(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    relative, generated = _generated_command()
    edited = repo / relative
    edited.parent.mkdir(parents=True)
    edited.write_text(generated + APPENDED, encoding="utf-8")
    plain_relative, plain_text = _generated_command("mb-status")
    plain = repo / plain_relative
    plain.write_text(plain_text, encoding="utf-8")

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    actions = {item["id"]: item for item in plan["actions"]}
    operator = {item["id"]: item for item in plan["operator_actions"]}
    assert actions["codex-agents-md"]["safe_to_apply"] is False
    assert relative in actions["codex-agents-md"]["kept"]
    assert operator["codex-agents-md"]["on_apply"]["keeps"] == [relative]
    assert operator["codex-agents-md"]["on_apply"]["removes"] == [plain_relative]
    assert applied["exit_code"] == 0
    assert edited.read_text(encoding="utf-8") == generated + APPENDED
    assert not plain.exists()  # the unchanged Main Branch file is proven and goes


# --- The two reproduced cases, global ----------------------------------------


def test_a_persons_mb_command_in_the_old_global_plugin_root_is_kept(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    mine = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / "mb-team-policy.md"
    mine.write_text(POLICY, encoding="utf-8")

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    operator = {item["id"]: item for item in plan["operator_actions"]}
    entry = operator["codex-global-kept"]
    assert entry["changes"] == [str(mine)]
    assert str(mine) in entry["reason"]
    assert str(mine) in entry["on_apply"]["keeps"]
    assert str(mine) not in entry["on_apply"]["removes"]
    manifest = plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH
    assert str(manifest) in entry["on_apply"]["removes"]
    action = {item["id"]: item for item in plan["actions"]}["codex-global-skill"]
    assert action["safe_to_apply"] is False
    assert action["on_apply"] == entry["on_apply"]
    assert applied["exit_code"] == 0
    assert mine.read_text(encoding="utf-8") == POLICY
    assert not manifest.exists()


def test_a_generated_global_command_with_a_persons_addition_is_kept(
    roots: tuple[Path, Path],
) -> None:
    plugin_root, _skills_root = roots
    codex_mod.write_global_plugin_source()
    relative, generated = _generated_command()
    edited = plugin_root / relative
    edited.write_text(generated + APPENDED, encoding="utf-8")

    result = codex_mod.write_global_skill_source()

    assert edited.read_text(encoding="utf-8") == generated + APPENDED
    assert result["kept"] == [str(edited)]
    assert not (plugin_root / codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH).exists()
    action = codex_mod.global_skill_operator_action(result["status"])
    assert action is not None
    assert action["id"] == "codex-global-kept"
    assert action["on_apply"]["removes"] == []


# --- Every released file is still recognised ---------------------------------


def test_the_frozen_set_covers_every_release_that_wrote_old_codex_files() -> None:
    assert RELEASES_REPLAYED[0] == "oe-v0.3.14"
    assert "oe-v0.6.3" in RELEASES_REPLAYED
    assert {
        "commands/mb-start.md",
        "commands/mb-checkpoint.md",
        ".codex-plugin/plugin.json",
        "plugins/marketplace.json",
        "main-branch-owner-loop/SKILL.md",
        "references/workflow-inventory.md",
        "ship-bet/SKILL.md",
        "weekly-review/SKILL.md",
        "google-ads-search-launch/SKILL.md",
    } <= set(KNOWN_FILE_DIGESTS)
    for digests in KNOWN_FILE_DIGESTS.values():
        assert digests
        assert all(len(digest) == 64 for digest in digests)


@pytest.mark.parametrize("tag", sorted(path.name for path in RELEASED.iterdir()))
def test_every_sampled_released_file_is_proven(tag: str, tmp_path: Path) -> None:
    for family in (RELEASED / tag).iterdir():
        for path in _place(tmp_path / family.name, _released_files(tag, family.name)):
            assert codex_mod._is_mainbranch_transitional_file(path), path


@pytest.mark.parametrize(
    ("tag", "where"),
    [("0.3.33", "plugin"), ("0.3.35", "plugin"), ("0.3.36", "skills")],
)
def test_released_global_files_are_removed_and_nothing_is_kept(
    roots: tuple[Path, Path], tag: str, where: str
) -> None:
    plugin_root, skills_root = roots
    placed = _place(plugin_root if where == "plugin" else skills_root, _released_files(tag, where))

    result = codex_mod.write_global_skill_source()

    assert result["kept"] == []
    assert not any(path.exists() for path in placed)
    assert not plugin_root.exists()
    for name in codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES:
        assert not (skills_root / name).exists()
    assert result["status"]["ok"] is True


def test_a_released_legacy_global_skill_is_removed(roots: tuple[Path, Path]) -> None:
    _plugin_root, skills_root = roots
    legacy = skills_root / codex_mod.CODEX_LEGACY_GLOBAL_SKILL_NAME / "SKILL.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(
        (RELEASED / "0.3.30/repo/.agents/skills/main-branch-owner-loop/SKILL.md").read_bytes()
    )

    result = codex_mod.write_global_skill_source()

    assert not legacy.parent.exists()
    assert result["kept"] == []


def test_released_repo_local_files_are_removed_whole(repo: Path) -> None:
    placed = _place(repo, _released_files("0.3.30", "repo"))

    plan = codex_mod.agents_md_plan(repo)
    codex_mod.write_agents_md(repo)

    assert plan["kept"] == []
    assert not any(path.exists() for path in placed)
    assert not (repo / ".agents").exists()


def test_a_note_in_the_version_slot_is_kept_and_reported(
    repo: Path, roots: tuple[Path, Path]
) -> None:
    plugin_root, _skills_root = roots
    released = (RELEASED / SAMPLE).read_bytes().replace(b"`0.3.30`", SLOT_NOTE, 1)
    relative = ".agents/plugins/main-branch-owner-loop/commands/mb-start.md"
    in_repo = repo / relative
    in_repo.parent.mkdir(parents=True)
    in_repo.write_bytes(released)
    global_files = _released_files("0.3.33", "plugin")
    global_files[relative] = global_files[relative].replace(b"`0.3.33`", SLOT_NOTE, 1)
    placed = _place(plugin_root, global_files)
    in_home = plugin_root / relative

    plan = _doctor(repo, "--plan", "--only", "codex")
    applied = _doctor(repo, "--apply", "--only", "codex")

    operator = {item["id"]: item for item in plan["operator_actions"]}
    assert operator["codex-agents-md"]["on_apply"]["keeps"] == [relative]
    assert str(in_home) in operator["codex-global-kept"]["changes"]
    assert applied["exit_code"] == 0
    assert in_repo.read_bytes() == released
    assert SLOT_NOTE in in_home.read_bytes()
    assert not any(path.exists() for path in placed if path != in_home)


# --- The content comparison ---------------------------------------------------

SAMPLE = "0.3.30/repo/.agents/plugins/main-branch-owner-loop/commands/mb-start.md"
SLOT_NOTE = b"`0.3.30 - TEAM NOTE: we pin our fork, ask the owner before upgrading`"


def _proven(tmp_path: Path, relative: str, data: bytes) -> bool:
    path = tmp_path / "probe" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return codex_mod._is_mainbranch_transitional_file(path)


def test_the_embedded_version_and_line_endings_are_normalised(tmp_path: Path) -> None:
    data = (RELEASED / SAMPLE).read_bytes()
    assert b"`0.3.30`" in data

    assert _proven(tmp_path, "commands/mb-start.md", data)
    assert _proven(tmp_path, "commands/mb-start.md", data.replace(b"`0.3.30`", b"`0.4.1`"))
    assert _proven(tmp_path, "commands/mb-start.md", data.replace(b"\n", b"\r\n"))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data + b"\n",
        lambda data: data + APPENDED.encode(),
        lambda data: data.replace(b"Main Branch", b"Main  Branch", 1),
        lambda data: data[:-2] + data[-1:],
        lambda data: data.replace(b"`0.3.30`", b"0.3.30", 1),
        lambda data: data.replace(b"`0.3.30`", SLOT_NOTE, 1),
        lambda data: b"\xff" + data,
    ],
    ids=[
        "newline",
        "appended",
        "one-space",
        "one-byte-gone",
        "version-unquoted",
        "text-in-version-slot",
        "not-utf8",
    ],
)
def test_any_other_change_to_a_released_file_is_not_proven(tmp_path: Path, mutate: Any) -> None:
    data = (RELEASED / SAMPLE).read_bytes()

    assert not _proven(tmp_path, "commands/mb-start.md", mutate(data))


def test_released_content_is_proven_only_under_its_own_name(tmp_path: Path) -> None:
    data = (RELEASED / SAMPLE).read_bytes()

    assert not _proven(tmp_path, "commands/mb-team-policy.md", data)
    assert not _proven(tmp_path, "commands/mb-status.md", data)


def test_json_is_compared_as_data(tmp_path: Path) -> None:
    source = RELEASED / "0.3.35/plugin/.agents/plugins/main-branch/.codex-plugin/plugin.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    reordered = json.dumps(dict(reversed(list(payload.items()))), indent=4).encode()
    added = json.dumps({**payload, "mine": True}, indent=2).encode()
    changed = json.dumps({**payload, "name": "my-plugin"}, indent=2).encode()

    assert _proven(tmp_path, ".codex-plugin/plugin.json", source.read_bytes())
    assert _proven(tmp_path, ".codex-plugin/plugin.json", reordered)
    assert not _proven(tmp_path, ".codex-plugin/plugin.json", added)
    assert not _proven(tmp_path, ".codex-plugin/plugin.json", changed)
    assert not _proven(tmp_path, ".codex-plugin/plugin.json", b"{not json")


def test_a_symlink_to_a_released_file_is_never_proven(tmp_path: Path) -> None:
    target = tmp_path / "elsewhere" / "commands" / "mb-start.md"
    target.parent.mkdir(parents=True)
    target.write_bytes((RELEASED / SAMPLE).read_bytes())
    link = tmp_path / "commands" / "mb-start.md"
    link.parent.mkdir()
    link.symlink_to(target)

    assert codex_mod._is_mainbranch_transitional_file(target)
    assert not codex_mod._is_mainbranch_transitional_file(link)


# --- Folders and symlinks ----------------------------------------------------


def test_a_planned_folder_removal_keeps_a_file_added_after_the_plan(repo: Path) -> None:
    _place(repo, _released_files("0.3.30", "repo"))
    plan = codex_mod.agents_md_plan(repo)
    late = repo / ".agents/skills/main-branch-owner-loop/references/late-note.md"
    late.write_text(POLICY, encoding="utf-8")

    for item in plan["operations"]:
        if item["op"] != "write":
            codex_mod._apply_transitional_operation(item, repo)

    assert late.read_text(encoding="utf-8") == POLICY
    assert not (repo / ".agents/skills/main-branch-owner-loop/SKILL.md").exists()
    assert not (repo / ".agents/plugins/main-branch-owner-loop").exists()
    assert not (repo / ".agents/plugins/marketplace.json").exists()


def test_write_global_plugin_source_never_walks_a_symlinked_commands_folder(
    roots: tuple[Path, Path], tmp_path: Path
) -> None:
    plugin_root, _skills_root = roots
    outside = tmp_path / "my-commands"
    outside.mkdir()
    released = outside / "mb-checkpoint.md"
    released.write_bytes(
        (
            RELEASED / "0.3.33/plugin/.agents/plugins/main-branch-owner-loop/commands"
            "/mb-checkpoint.md"
        ).read_bytes()
    )
    mine = outside / "mb-start.md"
    mine.write_text(POLICY, encoding="utf-8")
    commands = plugin_root / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH
    commands.parent.mkdir(parents=True)
    commands.symlink_to(outside, target_is_directory=True)

    result = codex_mod.write_global_plugin_source()

    assert commands.is_symlink()
    assert released.is_file()
    assert mine.read_text(encoding="utf-8") == POLICY
    assert str(commands) in result["kept"]
    assert sorted(path.name for path in outside.iterdir()) == ["mb-checkpoint.md", "mb-start.md"]


# --- The frozen set is reproducible ------------------------------------------


def _has_release_tags() -> bool:
    if not (ROOT / ".git").exists():
        return False
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "tag", "-l", RELEASES_REPLAYED[-1]],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() == RELEASES_REPLAYED[-1]


@pytest.mark.skipif(
    not _has_release_tags(),
    reason="needs the release tags; CI checkouts are shallow and carry none",
)
def test_the_regenerate_script_reproduces_the_committed_set() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "codex_known_files.py")],
        capture_output=True,
        text=True,
        check=False,
        env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": os.environ.get("PATH", "")},
        timeout=420,
    )

    assert proc.returncode == 0, proc.stderr[-2000:]
    assert "is current" in proc.stdout
