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


def test_doctor_spine_section_grades_declared_position(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    from mb import connect as connect_mod
    from mb import doctor as doctor_mod

    repo = tmp_path / "biz"
    repo.mkdir()

    undeclared = doctor_mod._spine_section(repo)
    assert undeclared["state"] == "info"
    assert "mb spine declare" in undeclared["summary"]

    connect_mod.connect_provider("shopify", repo=repo, token="shp-fixture", custom=True)
    spine_mod.declare(
        repo,
        store="shopify",
        lenses=["klaviyo:email"],
        gaps=["person-level web journey"],
        revisit="first unanswerable engagement question",
    )
    section = doctor_mod._spine_section(repo)
    by_name = {check["name"]: check for check in section["checks"]}

    assert by_name["declaration"]["state"] == "ok"
    assert by_name["agent-queryability"]["state"] == "ok"
    assert by_name["timeline-completeness"]["state"] == "info"
    assert "owned event log" in by_name["timeline-completeness"]["summary"]
    assert by_name["revisit-trigger"]["state"] == "ok"


def test_doctor_spine_section_intentional_none_is_ok(tmp_path: Path) -> None:
    from mb import doctor as doctor_mod

    spine_mod.declare(tmp_path, store="none", intentional_none=True, revisit="public launch")

    section = doctor_mod._spine_section(tmp_path)

    assert section["state"] == "ok"
    assert "on purpose" in section["summary"]
    assert "public launch" in section["summary"]


def test_doctor_spine_section_unconnected_store_warns(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    from mb import doctor as doctor_mod

    spine_mod.declare(tmp_path, store="cloudflare")

    section = doctor_mod._spine_section(tmp_path)
    by_name = {check["name"]: check for check in section["checks"]}

    assert by_name["agent-queryability"]["state"] == "warn"
    assert "not agent-queryable" in by_name["agent-queryability"]["summary"]


def test_spine_init_owned_scaffolds_schema(tmp_path: Path) -> None:
    result = runner.invoke(app, ["spine", "init", "--owned", "--repo", str(tmp_path), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "spine/schema.sql" in payload["written"]

    schema = (tmp_path / "spine" / "schema.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS contact" in schema
    assert "CREATE TABLE IF NOT EXISTS event" in schema
    assert "provider_message_id" in schema
    assert "delivery_state" in schema

    readme = (tmp_path / "spine" / "README.md").read_text(encoding="utf-8")
    assert "acceptance is not delivery" in readme.lower() or "delivery-truth" in readme
    assert "mb spine declare --force" in readme
    for banned in ("roofer", "booked", "noontide", "bor-data"):
        assert banned not in schema.lower()
        assert banned not in readme.lower()


def test_spine_init_requires_owned_flag(tmp_path: Path) -> None:
    result = runner.invoke(app, ["spine", "init", "--repo", str(tmp_path)])

    assert result.exit_code == 2
    assert "TRIGGERED" in result.stderr


def test_spine_init_owned_schema_is_valid_sqlite(tmp_path: Path) -> None:
    import sqlite3

    spine_mod.init_owned(tmp_path)
    conn = sqlite3.connect(":memory:")
    conn.executescript((tmp_path / "spine" / "schema.sql").read_text(encoding="utf-8"))
    conn.execute("INSERT INTO contact (email, status) VALUES ('a@example.com', 'lead')")
    conn.execute(
        "INSERT INTO event (contact_id, type, ts, provider_message_id, delivery_state) "
        "VALUES (1, 'email_sent', '2026-06-12T00:00:00Z', 'msg_1', 'accepted')"
    )
    row = conn.execute(
        "SELECT delivery_state FROM event WHERE provider_message_id = 'msg_1'"
    ).fetchone()
    assert row == ("accepted",)
