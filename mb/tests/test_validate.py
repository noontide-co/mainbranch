"""``mb validate`` frontmatter shape checks."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb.cli import app
from mb.validate import run

runner = CliRunner()


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


def test_cross_refs_pass_when_targets_exist(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-ok.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_research:\n"
            "  - research/2026-04-29-topic-source.md\n"
            "---\n"
            "# ok\n"
        ),
    )
    _write(
        tmp_path / "research" / "2026-04-29-topic-source.md",
        "---\ndate: 2026-04-29\ntopic: topic\nsource: source\n---\n# r\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["cross_refs"]["enabled"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_warn_on_missing_targets_without_strict(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-broken.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_decisions:\n"
            "  - decisions/missing.md\n"
            "---\n"
            "# broken\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding == {
        "code": "missing-target",
        "path": "decisions/2026-04-29-broken.md",
        "field": "linked_decisions",
        "target": "decisions/missing.md",
        "message": "linked_decisions target 'decisions/missing.md' does not exist",
    }


def test_cross_refs_strict_fails_on_warnings(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-broken.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_research: research/missing.md\n"
            "---\n"
            "# broken\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is False
    assert report["summary"] == {"errors": 0, "warnings": 1}


def test_cross_refs_flag_status_transition_regressions(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-28-old.md",
        "---\ndate: 2026-04-28\nstatus: running\n---\n# old\n",
    )
    _write(
        tmp_path / "decisions" / "2026-04-29-new.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: proposed\n"
            "supersedes: decisions/2026-04-28-old.md\n"
            "---\n"
            "# new\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    assert report["cross_refs"]["warnings"][0]["code"] == "status-transition"
    assert "move backward" in report["cross_refs"]["warnings"][0]["message"]


def test_cross_refs_flag_orphan_offer_dirs(tmp_path: Path) -> None:
    (tmp_path / "core" / "offers" / "alpha").mkdir(parents=True)

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 1
    assert report["cross_refs"]["orphan_offers"] == [
        {
            "code": "orphan-offer",
            "path": "core/offers/alpha",
            "field": "core/offers",
            "target": "offer.md",
            "message": "core/offers/alpha/ is missing offer.md",
        }
    ]


def test_validate_cli_cross_refs_default_warns_strict_fails(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-broken.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_research: research/missing.md\n"
            "---\n"
            "# broken\n"
        ),
    )

    result = runner.invoke(app, ["validate", str(tmp_path), "--cross-refs", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"]["warnings"] == 1

    result = runner.invoke(
        app,
        ["validate", str(tmp_path), "--cross-refs", "--strict", "--json"],
    )
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
