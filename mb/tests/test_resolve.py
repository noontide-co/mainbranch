"""``mb resolve`` layered lookup."""

from __future__ import annotations

from pathlib import Path

from mb import engine as engine_mod
from mb.engine import engine_root
from mb.resolve import bundled_skills, run, skill_path


def test_resolve_local_override(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / "core").mkdir(parents=True)
    (repo / "core" / "voice.md").write_text("# Voice\n")
    out = run(key="voice", repo=str(repo))
    assert out["resolved"] is True
    assert out["tier"] == "local"
    assert out["is_stub"] is False


def test_resolve_unknown_key_returns_unresolved_or_stub(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    out = run(key="nonexistent-9f3a", repo=str(repo))
    # Either unresolved or a stub. Both are valid; nothing crashes.
    assert "resolved" in out


def test_skill_path_uses_engine_root() -> None:
    root = engine_root()
    assert root is not None
    path = skill_path("start")
    assert path is not None
    assert path == root / ".claude" / "skills" / "start"
    assert "think" in bundled_skills()


def test_install_mode_does_not_treat_empty_pipx_home_as_prefix(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "tmp.with.dot" / "site-packages" / "mb" / "_engine"
    monkeypatch.delenv("PIPX_HOME", raising=False)
    monkeypatch.setattr(engine_mod, "packaged_engine_root", lambda: root)
    monkeypatch.setattr(engine_mod, "source_engine_root", lambda: None)

    assert engine_mod.install_mode() == "wheel"
