"""Claude Code skill wiring and personal-shadow repair."""

from __future__ import annotations

import json
from pathlib import Path

from mb import engine as engine_mod


def _write_skill(root: Path, name: str) -> Path:
    skill = root / ".claude" / "skills" / name
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill.\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill


def test_personal_legacy_mainbranch_symlink_is_reported_and_backed_up(
    tmp_path: Path, monkeypatch
) -> None:
    old_engine = tmp_path / "old-engine"
    (old_engine / "mb" / "mb").mkdir(parents=True)
    (old_engine / "mb" / "mb" / "__init__.py").write_text('__version__ = "0.1.0"\n')
    old_start = _write_skill(old_engine, "start")
    personal = tmp_path / "home" / ".claude" / "skills"
    personal.mkdir(parents=True)
    (personal / "start").symlink_to(old_start, target_is_directory=True)
    repo = tmp_path / "biz"
    _write_skill(repo, "mb-start")

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])

    dry = engine_mod.inspect_personal_skill_conflicts(repo, personal_skills_dir=personal)

    assert dry["ok"] is True
    assert dry["summary"]["legacy_globals"] == 1
    assert dry["summary"]["repairable"] == 1
    assert dry["findings"][0]["classification"] == "stale-mainbranch-link"
    assert (personal / "start").is_symlink()

    applied = engine_mod.inspect_personal_skill_conflicts(
        repo,
        apply=True,
        personal_skills_dir=personal,
    )

    assert applied["summary"]["repaired"] == 1
    assert not (personal / "start").exists()
    assert Path(applied["findings"][0]["backup_path"]).is_symlink()


def test_personal_legacy_broken_symlink_is_reported_and_backed_up(
    tmp_path: Path, monkeypatch
) -> None:
    personal = tmp_path / "home" / ".claude" / "skills"
    personal.mkdir(parents=True)
    (personal / "start").symlink_to(tmp_path / "missing-engine" / "start")
    repo = tmp_path / "biz"
    _write_skill(repo, "mb-start")

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])

    dry = engine_mod.inspect_personal_skill_conflicts(repo, personal_skills_dir=personal)

    assert dry["ok"] is True
    assert dry["summary"]["legacy_globals"] == 1
    assert dry["summary"]["repairable"] == 1
    assert dry["findings"][0]["classification"] == "broken-symlink"
    assert (personal / "start").is_symlink()

    applied = engine_mod.inspect_personal_skill_conflicts(
        repo,
        apply=True,
        personal_skills_dir=personal,
    )

    assert applied["summary"]["repaired"] == 1
    assert not (personal / "start").exists()
    assert not (personal / "start").is_symlink()
    assert Path(applied["findings"][0]["backup_path"]).is_symlink()


def test_personal_third_party_active_shadow_is_reported_but_not_repaired(
    tmp_path: Path, monkeypatch
) -> None:
    personal = tmp_path / "home" / ".claude" / "skills"
    _write_skill(personal.parent.parent, "mb-start")
    repo = tmp_path / "biz"
    _write_skill(repo, "mb-start")

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])

    result = engine_mod.inspect_personal_skill_conflicts(
        repo,
        apply=True,
        personal_skills_dir=personal,
    )

    assert result["ok"] is False
    assert result["summary"]["active_shadows"] == 1
    assert result["summary"]["repairable"] == 0
    assert result["findings"][0]["classification"] == "not-mainbranch-link"
    assert (personal / "mb-start" / "SKILL.md").exists()


def test_link_skills_auto_repairs_broken_legacy_personal_symlink(
    tmp_path: Path, monkeypatch
) -> None:
    personal = tmp_path / "home" / ".claude" / "skills"
    personal.mkdir(parents=True)
    (personal / "start").symlink_to(tmp_path / "missing-engine" / "start")
    repo = tmp_path / "biz"

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])
    monkeypatch.setattr(engine_mod, "_personal_skills_dir", lambda: personal)

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    assert result["shadow_report"]["summary"]["repaired"] == 1
    assert result["shadow_report"]["findings"][0]["classification"] == "broken-symlink"
    assert not (personal / "start").exists()
    assert not (personal / "start").is_symlink()
    assert (repo / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()


def test_bundled_skills_ignores_directories_without_skill_md(tmp_path: Path, monkeypatch) -> None:
    engine = tmp_path / "engine"
    _write_skill(engine, "mb-start")
    leftover = engine / ".claude" / "skills" / "start"
    leftover.mkdir(parents=True)
    (leftover / ".DS_Store").write_bytes(b"")
    (engine / ".claude" / "skills" / "setup").mkdir()

    monkeypatch.setattr(engine_mod, "skills_dir", lambda root=None: engine / ".claude" / "skills")

    assert engine_mod.bundled_skills() == ["mb-start"]


def test_link_skills_does_not_relink_engine_leftover_without_skill_md(
    tmp_path: Path, monkeypatch
) -> None:
    """A removed legacy project symlink stays removed even when the engine root
    still carries a leftover same-named directory with no SKILL.md (rename
    residue). Regression for link_skills re-creating `.claude/skills/start`."""
    repo = tmp_path / "biz"
    engine = tmp_path / "engine"
    _write_skill(engine, "mb-start")
    leftover = engine / ".claude" / "skills" / "start"
    leftover.mkdir(parents=True)
    (leftover / ".DS_Store").write_bytes(b"")
    legacy = repo / ".claude" / "skills" / "start"
    legacy.parent.mkdir(parents=True)
    legacy.symlink_to(leftover, target_is_directory=True)

    monkeypatch.setattr(engine_mod, "engine_root", lambda: engine)
    monkeypatch.setattr(engine_mod, "skills_dir", lambda root=None: engine / ".claude" / "skills")

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    assert ".claude/skills/start" in result["removed_legacy"]
    assert not legacy.exists()
    assert not legacy.is_symlink()
    assert (repo / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()
    gitignore = (repo / ".gitignore").read_text(encoding="utf-8")
    assert ".claude/skills/start" not in gitignore.splitlines()


def test_link_skills_removes_legacy_project_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    old_engine = tmp_path / "old-engine"
    old_start = _write_skill(old_engine, "start")
    legacy = repo / ".claude" / "skills" / "start"
    legacy.parent.mkdir(parents=True)
    legacy.symlink_to(old_start, target_is_directory=True)

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    assert ".claude/skills/start" in result["removed_legacy"]
    assert not legacy.exists()
    assert (repo / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()


def test_link_skills_removes_retired_project_symlinks_and_gitignore_entries(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "biz"
    old_engine = tmp_path / "old-engine"
    old_vsl = _write_skill(old_engine, "mb-vsl")
    old_pull = _write_skill(old_engine, "mb-pull")
    skills = repo / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / "mb-vsl").symlink_to(old_vsl, target_is_directory=True)
    (skills / "mb-pull").symlink_to(old_pull, target_is_directory=True)
    (repo / ".gitignore").write_text(
        "\n".join(
            [
                engine_mod.GITIGNORE_HEADER,
                ".claude/settings.local.json",
                ".claude/skills/mb-start",
                ".claude/skills/mb-vsl",
                ".claude/skills/mb-pull",
                "",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    assert ".claude/skills/mb-vsl" in result["removed_legacy"]
    assert ".claude/skills/mb-pull" in result["removed_legacy"]
    assert not (skills / "mb-vsl").exists()
    assert not (skills / "mb-pull").exists()
    gitignore = (repo / ".gitignore").read_text(encoding="utf-8")
    assert ".claude/skills/mb-start" in gitignore
    assert ".claude/skills/mb-vsl" not in gitignore
    assert ".claude/skills/mb-pull" not in gitignore


def test_link_skills_ignores_claude_code_worktrees(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "biz"

    monkeypatch.setattr(engine_mod, "bundled_skills", lambda: ["mb-start"])

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    gitignore = (repo / ".gitignore").read_text(encoding="utf-8")
    assert ".claude/settings.local.json" in gitignore
    assert ".claude/worktrees/" in gitignore
    assert ".claude/skills/mb-start" in gitignore


def test_link_skills_removes_stale_mainbranch_engine_paths(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    stale_engine = tmp_path / "old-mainbranch"
    other_dir = tmp_path / "other-tools"
    unrelated_missing = tmp_path / "vip-clients"
    _write_skill(stale_engine, "start")
    (stale_engine / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    other_dir.mkdir()
    settings = repo / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps(
            {
                "permissions": {
                    "additionalDirectories": [
                        str(stale_engine),
                        str(tmp_path / "mb-vip"),
                        str(unrelated_missing),
                        str(other_dir),
                    ]
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = engine_mod.link_skills(repo)

    assert result["ok"] is True
    assert str(stale_engine) in result["removed_stale_engine_paths"]
    assert str(tmp_path / "mb-vip") in result["removed_stale_engine_paths"]
    repaired = json.loads(settings.read_text(encoding="utf-8"))
    dirs = repaired["permissions"]["additionalDirectories"]
    assert dirs[0] == result["engine_root"]
    assert str(stale_engine) not in dirs
    assert str(tmp_path / "mb-vip") not in dirs
    assert str(unrelated_missing) in dirs
    assert str(other_dir) in dirs


def test_mb_install_diagnostics_reports_multiple_versions(tmp_path: Path, monkeypatch) -> None:
    bin_a = tmp_path / "a"
    bin_b = tmp_path / "b"
    bin_a.mkdir()
    bin_b.mkdir()
    mb_a = bin_a / "mb"
    mb_b = bin_b / "mb"
    mb_a.write_text("#!/bin/sh\necho 'mb 0.3.22'\n", encoding="utf-8")
    mb_b.write_text("#!/bin/sh\necho 'mb 0.3.18'\n", encoding="utf-8")
    mb_a.chmod(0o755)
    mb_b.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_a}:{bin_b}")
    versions = {
        str(mb_a): "0.3.22",
        str(mb_b): "0.3.18",
    }
    monkeypatch.setattr(
        engine_mod,
        "_mb_binary_version",
        lambda path: {
            "ok": True,
            "version": versions[path],
            "output": f"mb {versions[path]}",
            "error": "",
        },
    )

    result = engine_mod.mb_install_diagnostics()

    assert result["active_path"] == str(mb_a)
    assert result["multiple_installs"] is True
    assert result["multiple_versions"] is True
    assert [item["version"] for item in result["installs"]] == ["0.3.22", "0.3.18"]
    assert result["repair_command"] == "mb skill link --repo ."


def test_login_shell_mb_diagnostics_reports_stale_runtime_mb(tmp_path: Path, monkeypatch) -> None:
    active_bin = tmp_path / "active"
    stale_bin = tmp_path / "stale"
    active_bin.mkdir()
    stale_bin.mkdir()
    active_mb = active_bin / "mb"
    stale_mb = stale_bin / "mb"
    active_mb.write_text("#!/bin/sh\necho 'mb 0.3.29'\n", encoding="utf-8")
    stale_mb.write_text("#!/bin/sh\necho 'mb 0.3.18'\n", encoding="utf-8")
    active_mb.chmod(0o755)
    stale_mb.chmod(0o755)
    shell = tmp_path / "login-shell"
    shell.write_text(
        f'#!/bin/sh\nPATH={stale_bin}:$PATH exec /bin/sh -c "$2"\n',
        encoding="utf-8",
    )
    shell.chmod(0o755)
    monkeypatch.setenv("PATH", str(active_bin))

    result = engine_mod.login_shell_mb_diagnostics(str(shell))

    assert result["ok"] is False
    assert result["mismatch"] is True
    assert result["path"] == str(stale_mb)
    assert result["version"] == "0.3.18"
    assert result["active_path"] == str(active_mb)
    assert "different mb" in result["summary"]


def test_login_shell_mb_diagnostics_ignores_login_shell_banner(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    mb = bin_dir / "mb"
    mb.write_text("#!/bin/sh\necho 'mb 0.3.29'\n", encoding="utf-8")
    mb.chmod(0o755)
    shell = tmp_path / "login-shell"
    shell.write_text(
        f'#!/bin/sh\necho welcome-banner\nPATH={bin_dir}:$PATH exec /bin/sh -c "$2"\n',
        encoding="utf-8",
    )
    shell.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))
    monkeypatch.setattr(engine_mod, "__version__", "0.3.29")

    result = engine_mod.login_shell_mb_diagnostics(str(shell))

    assert result["ok"] is True
    assert result["mismatch"] is False
    assert result["path"] == str(mb)
    assert result["version"] == "0.3.29"


def test_link_status_explains_stale_engine_path_from_other_install(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "biz"
    stale_engine = tmp_path / "mb-vip"
    _write_skill(stale_engine, "start")
    (stale_engine / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    settings = repo / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps({"permissions": {"additionalDirectories": [str(stale_engine)]}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        engine_mod,
        "mb_install_diagnostics",
        lambda: {
            "active_path": "/tmp/new/mb",
            "current_version": "0.3.22",
            "multiple_installs": True,
            "multiple_versions": True,
            "installs": [
                {"path": "/tmp/new/mb", "version": "0.3.22"},
                {"path": "/tmp/old/mb", "version": "0.3.18"},
            ],
            "repair_command": "mb skill link --repo .",
        },
    )

    result = engine_mod.link_status(repo)

    assert result["ok"] is False
    assert str(stale_engine) in result["stale_engine_paths"]
    assert result["stale_from_other_install"] is True
    assert result["current_mb"]["path"] == "/tmp/new/mb"
    assert result["repair_command"] == "mb skill link --repo ."
