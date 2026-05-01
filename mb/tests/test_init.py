"""``mb init`` scaffolds the canonical six folders + CLAUDE.md."""

from __future__ import annotations

import json
from pathlib import Path

from mb.init import DATA_FOLDERS, run


def test_init_scaffolds_folders(tmp_path: Path) -> None:
    target = tmp_path / "acme"
    result = run(path=str(target), name="Acme Brewing")
    assert result["status"] == "ok"
    for folder in DATA_FOLDERS:
        assert (target / folder).is_dir(), f"missing {folder}"
    assert (target / "reference" / "core" / ".gitkeep").exists()
    assert (target / "reference" / "offers" / ".gitkeep").exists()
    assert (target / "reference" / "proof" / "angles").is_dir()
    assert (target / "reference" / "domain").is_dir()
    assert (target / "reference" / "visual-identity").is_dir()
    assert (target / "CLAUDE.md").exists()
    assert (target / ".github" / "CODEOWNERS").exists()
    assert (target / ".gitignore").exists()
    assert (target / ".claude" / "settings.local.json").exists()
    assert (target / ".claude" / "skills" / "start" / "SKILL.md").exists()

    settings = json.loads((target / ".claude" / "settings.local.json").read_text())
    dirs = settings["permissions"]["additionalDirectories"]
    assert dirs
    assert (Path(dirs[0]) / ".claude" / "skills" / "start" / "SKILL.md").exists()

    gitignore = (target / ".gitignore").read_text()
    assert ".claude/settings.local.json" in gitignore
    assert ".claude/skills/start" in gitignore
    assert "Acme Brewing" in (target / "CLAUDE.md").read_text()


def test_init_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "acme"
    first = run(path=str(target), name="Acme")
    second = run(path=str(target), name="Acme")
    assert first["status"] == "ok"
    assert second["status"] == "already-initialized"


def test_init_requires_name(tmp_path: Path, monkeypatch) -> None:
    # Force input() to raise EOFError, simulating no TTY.
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError()))
    target = tmp_path / "noname"
    result = run(path=str(target), name="")
    assert result["status"] == "error"
