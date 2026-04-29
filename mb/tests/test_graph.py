"""``mb graph`` DOT emission."""

from __future__ import annotations

from pathlib import Path

from mb.graph import build_dot


def test_empty_repo_emits_valid_dot(tmp_path: Path) -> None:
    out = build_dot(path=str(tmp_path))
    assert out.startswith("digraph mb {")
    assert out.rstrip().endswith("}")


def test_links_become_edges(tmp_path: Path) -> None:
    decisions = tmp_path / "decisions"
    research = tmp_path / "research"
    decisions.mkdir()
    research.mkdir()
    (research / "2026-04-29-foo.md").write_text(
        "---\ndate: 2026-04-29\ntopic: foo\nsource: claude-code\n---\n",
    )
    (decisions / "2026-04-29-bar.md").write_text(
        "---\ndate: 2026-04-29\nstatus: accepted\n"
        "linked_research:\n  - research/2026-04-29-foo.md\n---\n",
    )
    out = build_dot(path=str(tmp_path))
    assert "linked_research" in out
    assert "->" in out
