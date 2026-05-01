"""``mb resolve`` layered lookup."""

from __future__ import annotations

from pathlib import Path

from mb.resolve import run


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
