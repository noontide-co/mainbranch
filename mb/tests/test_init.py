"""``mb init`` scaffolds the canonical business folders + CLAUDE.md."""

from __future__ import annotations

import json
from pathlib import Path

from mb.init import _DEFAULT_CLAUDE, DATA_FOLDERS, _read_template, run


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def _assert_claude_md_cli_first_contract(text: str) -> None:
    assert "## Claude operating contract" in text
    assert "Main Branch CLI facts are the source of truth" in text
    assert "run `claude`" in text
    assert "`/mb-start` inside Claude Code" in text
    assert "mb start --launch" in text
    assert "mb --version" in text
    assert "mb status --json --peek" in text
    assert "mb start --json" in text
    assert "mb doctor repair --plan" in text
    assert "Do not replace those facts with ad hoc shell inspection" in text
    assert "Read-only commands can be run without asking first" in text
    assert "require explicit operator approval before applying" in text
    assert "mb skill repair --repo ." in text
    assert "mb skill link --repo .          # writes project-local Claude skill wiring" in text
    assert "mb skill repair --repo . --apply" in text
    assert "mb doctor repair --apply" in text
    assert "If `/mb-start` is not discoverable" in text
    assert "restart Claude Code from this repo and try" in text
    assert "business-owner language" in text
    assert "bets, goals, offers, pushes" in text
    assert "playbooks, outcomes" in text
    assert "Claude Desktop" not in text
    for unsupported_runtime in ("Codex", "Cursor", "OpenClaw", "Hermes"):
        assert unsupported_runtime not in text


def test_default_claude_operating_contract_matches_template() -> None:
    template = _read_template("CLAUDE.md.tmpl")
    template_contract = _section(template, "## Claude operating contract", "## Folders")
    fallback_contract = _section(_DEFAULT_CLAUDE, "## Claude operating contract", "## Folders")

    assert fallback_contract == template_contract
    _assert_claude_md_cli_first_contract(_DEFAULT_CLAUDE)


def test_init_scaffolds_folders(tmp_path: Path) -> None:
    target = tmp_path / "acme"
    result = run(path=str(target), name="Acme Brewing")
    assert result["status"] == "ok"
    for folder in DATA_FOLDERS:
        assert (target / folder).is_dir(), f"missing {folder}"
    assert not (target / "reference").exists()
    assert (target / "core" / "proof").is_dir()
    assert (target / "core" / "brand").is_dir()
    assert (target / "core" / "strategy").is_dir()
    assert (target / "core" / "operations").is_dir()
    assert (target / "bets").is_dir()
    # Canonical primitive is `pushes/`; legacy `campaigns/` is not scaffolded.
    assert (target / "pushes").is_dir()
    assert not (target / "campaigns").exists()
    # Operator vocabulary is an optional file scaffolded by init.
    assert (target / "core" / "vocabulary.md").exists()
    vocab = (target / "core" / "vocabulary.md").read_text(encoding="utf-8")
    assert "type: vocabulary" in vocab
    assert "terms:" in vocab
    assert "singular: push" in vocab
    assert (target / "CLAUDE.md").exists()
    assert (target / ".github" / "CODEOWNERS").exists()
    assert (target / ".gitignore").exists()
    assert (target / ".mb" / "schema_version").read_text(encoding="utf-8") == "0.2\n"
    assert (target / ".claude" / "settings.local.json").exists()
    assert (target / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()
    assert (target / ".git" / "hooks" / "commit-msg").exists()
    hook = (target / ".git" / "hooks" / "commit-msg").read_text(encoding="utf-8")
    assert "MB_BIN=" in hook
    assert '"$MB_CHECKPOINT" checkpoint --validate -' in hook
    assert result["checkpoint_hook"]["state"] == "installed"

    settings = json.loads((target / ".claude" / "settings.local.json").read_text())
    dirs = settings["permissions"]["additionalDirectories"]
    assert dirs
    assert (Path(dirs[0]) / ".claude" / "skills" / "mb-start" / "SKILL.md").exists()

    gitignore = (target / ".gitignore").read_text()
    assert ".claude/settings.local.json" in gitignore
    assert ".claude/worktrees/" in gitignore
    assert ".claude/skills/mb-start" in gitignore
    assert ".mb/backups/" in gitignore
    assert ".mb/connect.yaml" in gitignore
    assert ".mb/onboarding.json" in gitignore
    assert ".mb/issue-drafts/" in gitignore
    claude_md = (target / "CLAUDE.md").read_text()
    assert "Acme Brewing" in claude_md
    assert "## Connected accounts" in claude_md
    assert "Stripe account IDs" in claude_md
    assert "Google Ads customer IDs" in claude_md
    assert "MCP server names" in claude_md
    assert "MCP tokens" in claude_md
    assert "Never commit API keys" in claude_md
    assert "`bets/`" in claude_md
    # CLAUDE.md teaches the canonical push primitive and the optional
    # vocabulary file; legacy campaigns/ appears only as compatibility.
    assert "`pushes/`" in claude_md
    assert "core/vocabulary.md" in claude_md
    assert "legacy `campaigns/`" in claude_md
    _assert_claude_md_cli_first_contract(claude_md)


def test_init_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "acme"
    first = run(path=str(target), name="Acme")
    second = run(path=str(target), name="Acme")
    assert first["status"] == "ok"
    assert second["status"] == "already-initialized"
    assert second["checkpoint_hook"]["state"] == "installed"


def test_init_requires_name(tmp_path: Path, monkeypatch) -> None:
    # Force input() to raise EOFError, simulating no TTY.
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError()))
    target = tmp_path / "noname"
    result = run(path=str(target), name="")
    assert result["status"] == "error"
