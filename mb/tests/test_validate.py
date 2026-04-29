"""``mb validate`` frontmatter shape checks."""

from __future__ import annotations

from pathlib import Path

from mb.validate import run


def _write(p: Path, body: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def test_validate_passes_well_formed(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-ok.md",
        "---\ndate: 2026-04-29\nstatus: accepted\n---\n# ok\n",
    )
    _write(
        tmp_path / "research" / "2026-04-29-topic-claude-code.md",
        "---\ndate: 2026-04-29\ntopic: tau\nsource: claude-code\n---\n# r\n",
    )
    report = run(path=str(tmp_path))
    assert report["ok"] is True
    assert all(f["ok"] for f in report["files"])


def test_validate_flags_missing_status(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-broken.md",
        "---\ndate: 2026-04-29\n---\n# missing status\n",
    )
    report = run(path=str(tmp_path))
    assert report["ok"] is False
    bad = [f for f in report["files"] if not f["ok"]]
    assert any("status" in e for f in bad for e in f["errors"])


def test_validate_flags_bad_status_enum(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-typo.md",
        "---\ndate: 2026-04-29\nstatus: pending\n---\n# typo\n",
    )
    report = run(path=str(tmp_path))
    assert report["ok"] is False


def test_validate_handles_no_frontmatter(tmp_path: Path) -> None:
    _write(tmp_path / "decisions" / "2026-04-29-naked.md", "no frontmatter here\n")
    report = run(path=str(tmp_path))
    assert report["ok"] is False
