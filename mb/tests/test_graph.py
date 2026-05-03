"""``mb graph`` index and DOT emission."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb.cli import app
from mb.graph import build_dot, build_index

runner = CliRunner()


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


def test_build_index_includes_frontmatter_links_wikilinks_and_entities(tmp_path: Path) -> None:
    decisions = tmp_path / "decisions"
    research = tmp_path / "research"
    decisions.mkdir()
    research.mkdir()
    (research / "audience.md").write_text(
        "---\ntitle: Audience Research\npeople:\n  - Devon Meadows\n---\n"
        "Mentions #company/noontide-co and [[growth-decision]].\n",
        encoding="utf-8",
    )
    (decisions / "growth-decision.md").write_text(
        "---\ntitle: Growth Decision\nstatus: accepted\n"
        "linked_research:\n  - research/audience.md\n"
        "tags:\n  - offer:Main Branch\n  - channel:GitHub\n---\n"
        "Track #metric/activation-rate against #competitor/status-quo.\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))
    node_ids = {node["id"] for node in index["nodes"]}
    edge_types = {edge["type"] for edge in index["edges"]}

    assert "file:research/audience.md" in node_ids
    assert "file:decisions/growth-decision.md" in node_ids
    assert "person:devon-meadows" in node_ids
    assert "company:noontide-co" in node_ids
    assert "offer:main-branch" in node_ids
    assert "channel:github" in node_ids
    assert "metric:activation-rate" in node_ids
    assert "competitor:status-quo" in node_ids
    assert any(
        node["id"] == "competitor:status-quo" and node["label"] == "status quo"
        for node in index["nodes"]
    )
    assert "linked_research" in edge_types
    assert "wikilink" in edge_types
    assert "mentions" in edge_types
    assert index["summary"]["entities"]["person"] == 1


def test_graph_json_cli_emits_machine_readable_index(tmp_path: Path) -> None:
    research = tmp_path / "research"
    research.mkdir()
    (research / "audience.md").write_text(
        "---\ntitle: Audience Research\ncompanies:\n  - Acme\n---\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["graph", str(tmp_path), "--json"])

    assert result.exit_code == 0
    index = json.loads(result.stdout)
    assert index["version"] == 1
    assert index["summary"]["files"] == 1
    assert any(node["id"] == "company:acme" for node in index["nodes"])


def test_graph_json_rejects_open_flag(tmp_path: Path) -> None:
    result = runner.invoke(app, ["graph", str(tmp_path), "--json", "--open"])

    assert result.exit_code != 0
    assert "cannot be combined" in result.output


def test_existing_repo_paths_are_not_marked_external_by_root_heuristic(tmp_path: Path) -> None:
    decisions = tmp_path / "decisions"
    nested = tmp_path / "tools" / "research"
    decisions.mkdir()
    nested.mkdir(parents=True)
    (nested / "notes.md").write_text("---\ntitle: Tool Notes\n---\n", encoding="utf-8")
    (decisions / "decision.md").write_text(
        "---\ntitle: Decision\nstatus: accepted\n"
        "linked_research:\n  - tools/research/notes.md\n---\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))

    assert any(node["id"] == "file:tools/research/notes.md" for node in index["nodes"])
    assert not any(node["id"] == "external:tools-research-notes-md" for node in index["nodes"])
    assert any(
        edge["source"] == "file:decisions/decision.md"
        and edge["target"] == "file:tools/research/notes.md"
        and edge["type"] == "linked_research"
        for edge in index["edges"]
    )


def test_duplicate_entity_mentions_are_deduped(tmp_path: Path) -> None:
    research = tmp_path / "research"
    research.mkdir()
    (research / "audience.md").write_text(
        "---\ntitle: Audience\n---\n#channel/github appears twice: #channel/github\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))
    channel_edges = [
        edge
        for edge in index["edges"]
        if edge["source"] == "file:research/audience.md"
        and edge["target"] == "channel:github"
        and edge["type"] == "mentions"
    ]

    assert len(channel_edges) == 1
