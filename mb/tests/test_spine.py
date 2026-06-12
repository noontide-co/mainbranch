"""``mb spine declare`` / ``mb spine show`` — the declared spine position."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from mb import spine as spine_mod
from mb.cli import app

runner = CliRunner()


def test_spine_declare_writes_committed_fact(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "spine",
            "declare",
            "--store",
            "shopify",
            "--repo",
            str(tmp_path),
            "--lens",
            "seguno:email",
            "--lens",
            "loox:reviews",
            "--gap",
            "person-level web journey",
            "--revisit",
            "first unanswerable engagement question",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["declaration"]["store"] == "shopify"

    fact = tmp_path / "core" / "operations" / "spine.md"
    text = fact.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text[3 : text.index("\n---", 3)])
    assert frontmatter["type"] == "spine"
    assert frontmatter["store"] == "shopify"
    assert frontmatter["lenses"] == [
        {"store": "seguno", "domain": "email"},
        {"store": "loox", "domain": "reviews"},
    ]
    assert frontmatter["known_gaps"] == ["person-level web journey"]
    assert "fan-out lens" in text


def test_spine_show_roundtrip(tmp_path: Path) -> None:
    spine_mod.declare(tmp_path, store="stripe", revisit="cross-channel attribution")

    shown = runner.invoke(app, ["spine", "show", "--repo", str(tmp_path), "--json"])

    assert shown.exit_code == 0
    payload = json.loads(shown.stdout)
    assert payload["declared"] is True
    assert payload["declaration"]["store"] == "stripe"
    assert payload["declaration"]["revisit_trigger"] == "cross-channel attribution"


def test_spine_none_requires_intentional(tmp_path: Path) -> None:
    refused = runner.invoke(app, ["spine", "declare", "--store", "none", "--repo", str(tmp_path)])
    assert refused.exit_code == 2
    assert "--intentional" in refused.stderr

    declared = runner.invoke(
        app,
        ["spine", "declare", "--store", "none", "--intentional", "--repo", str(tmp_path)],
    )
    assert declared.exit_code == 0
    text = (tmp_path / "core" / "operations" / "spine.md").read_text(encoding="utf-8")
    assert "none, on purpose" in text
    assert "stance, not a gap" in text


def test_spine_declare_refuses_overwrite_without_force(tmp_path: Path) -> None:
    spine_mod.declare(tmp_path, store="shopify")

    refused = runner.invoke(
        app, ["spine", "declare", "--store", "hubspot", "--repo", str(tmp_path)]
    )
    assert refused.exit_code == 1

    forced = runner.invoke(
        app,
        ["spine", "declare", "--store", "hubspot", "--force", "--repo", str(tmp_path)],
    )
    assert forced.exit_code == 0
    assert spine_mod.show(tmp_path)["declaration"]["store"] == "hubspot"


def test_spine_show_undeclared_points_at_declare(tmp_path: Path) -> None:
    result = runner.invoke(app, ["spine", "show", "--repo", str(tmp_path)])

    assert result.exit_code == 1
    assert "mb spine declare" in result.stdout
