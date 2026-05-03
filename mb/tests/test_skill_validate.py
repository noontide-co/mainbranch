"""``mb skill validate`` structural checks for bundled skills."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mb import engine as engine_mod
from mb import skill_validate as skill_validate_mod
from mb.cli import app

runner = CliRunner()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _skill(
    root: Path,
    name: str,
    body: str = "See [details](references/details.md).\n",
    frontmatter: str | None = None,
) -> Path:
    skill_root = root / ".claude" / "skills" / name
    if frontmatter is None:
        frontmatter = f"---\nname: {name}\ndescription: Test skill.\n---\n"
    _write(skill_root / "SKILL.md", frontmatter + "\n# Test\n\n" + body)
    _write(skill_root / "references" / "details.md", "# Details\n")
    return skill_root


def _patch_engine(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    skills_root = root / ".claude" / "skills"

    def skill_path(name: str) -> Path | None:
        candidate = skills_root / name
        return candidate if candidate.is_dir() else None

    def bundled_skills() -> list[str]:
        return sorted(path.name for path in skills_root.iterdir() if path.is_dir())

    monkeypatch.setattr(engine_mod, "skill_path", skill_path)
    monkeypatch.setattr(engine_mod, "bundled_skills", bundled_skills)


def test_skill_validate_passes_frontmatter_references_and_line_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _skill(tmp_path, "alpha")
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run("alpha")

    assert report is not None
    assert report["ok"] is True
    assert report["summary"]["line_count"] < skill_validate_mod.MAX_SKILL_LINES


def test_skill_validate_flags_missing_description(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _skill(tmp_path, "alpha", frontmatter="---\nname: alpha\n---\n")
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run("alpha")

    assert report is not None
    assert report["ok"] is False
    assert "missing key: description" in report["files"][0]["errors"]


def test_skill_validate_flags_missing_local_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skill_root = _skill(tmp_path, "alpha", body="See [missing](references/missing.md).\n")
    (skill_root / "references" / "details.md").unlink()
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run("alpha")

    assert report is not None
    assert report["ok"] is False
    assert any("references/missing.md" in error for error in report["files"][0]["errors"])


def test_skill_validate_flags_parent_directory_references(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _skill(tmp_path, "alpha", body="See [other](../beta/SKILL.md).\n")
    _skill(tmp_path, "beta")
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run("alpha")

    assert report is not None
    assert report["ok"] is False
    assert any("outside the skill directory" in error for error in report["files"][0]["errors"])


def test_skill_validate_flags_line_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = "\n".join(f"line {i}" for i in range(skill_validate_mod.MAX_SKILL_LINES + 1))
    _skill(tmp_path, "alpha", body=body)
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run("alpha")

    assert report is not None
    assert report["ok"] is False
    assert any("limit is 500" in error for error in report["files"][0]["errors"])


def test_skill_validate_all_envelope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _skill(tmp_path, "alpha")
    _skill(tmp_path, "beta", body="See [missing](references/missing.md).\n")
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run_all()

    assert report["ok"] is False
    assert report["mode"] == "all"
    assert report["summary"]["skills"] == 2
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 1


def test_skill_validate_all_fails_when_no_bundled_skills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    _patch_engine(monkeypatch, tmp_path)

    report = skill_validate_mod.run_all()

    assert report["ok"] is False
    assert report["summary"]["skills"] == 0
    assert report["summary"]["errors"] == 1
    assert report["errors"] == ["no bundled skills found"]


def test_skill_validate_cli_json_and_exit_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _skill(tmp_path, "alpha")
    _skill(tmp_path, "beta", body="See [missing](references/missing.md).\n")
    _patch_engine(monkeypatch, tmp_path)

    result = runner.invoke(app, ["skill", "validate", "alpha", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"]["passed"] == 1

    result = runner.invoke(app, ["skill", "validate", "beta", "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False

    result = runner.invoke(app, ["skill", "validate", "missing", "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["errors"] == ["skill not found: missing"]

    result = runner.invoke(app, ["skill", "validate", "--all", "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["mode"] == "all"
    assert payload["summary"]["failed"] == 1
