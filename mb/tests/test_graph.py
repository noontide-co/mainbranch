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


def test_bet_links_become_edges(tmp_path: Path) -> None:
    bets = tmp_path / "bets"
    decisions = tmp_path / "decisions"
    bets.mkdir()
    decisions.mkdir()
    (bets / "2026-05-04-demo.md").write_text(
        "---\n"
        "status: open\n"
        "opened: 2026-05-04\n"
        "deadline: 2026-05-11\n"
        "appetite: 1 week\n"
        "hypothesis: Demo creates qualified calls.\n"
        "metric: calls\n"
        "target: 5 calls\n"
        "result: ''\n"
        "linked_decisions:\n  - decisions/2026-05-04-demo.md\n"
        "linked_research: []\n"
        "linked_campaigns: []\n"
        "linked_outcomes: []\n"
        "public: true\n"
        "channels: []\n"
        "tags: []\n"
        "---\n",
        encoding="utf-8",
    )
    (decisions / "2026-05-04-demo.md").write_text(
        "---\ndate: 2026-05-04\nstatus: accepted\nlinked_bets:\n  - bets/2026-05-04-demo.md\n---\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))
    edge_types = {edge["type"] for edge in index["edges"]}

    assert "linked_decisions" in edge_types
    assert "linked_bets" in edge_types


def test_graph_exposes_push_offer_and_provider_refs_without_raw_values(tmp_path: Path) -> None:
    pushes = tmp_path / "pushes" / "2026-05-06-workshop"
    decisions = tmp_path / "decisions"
    offer = tmp_path / "core" / "offers" / "workshop"
    pushes.mkdir(parents=True)
    decisions.mkdir()
    offer.mkdir(parents=True)
    (offer / "offer.md").write_text(
        "---\nslug: workshop\nstatus: running\n---\n# Workshop offer\n",
        encoding="utf-8",
    )
    (pushes / "push.md").write_text(
        "---\n"
        "type: push\n"
        "slug: workshop\n"
        "kind: launch\n"
        "status: active\n"
        "health: on-track\n"
        "goal:\n"
        "  metric: qualified calls\n"
        "  target: 10 qualified calls\n"
        "  by: 2026-05-20\n"
        "owner: Devon\n"
        "audience: founders\n"
        "offer: core/offers/workshop/offer.md\n"
        "promise: Own the launch memory in git.\n"
        "linked_decisions:\n"
        "  - decisions/2026-05-06-workshop.md\n"
        "provider_refs:\n"
        "  meta_ads:\n"
        "    campaign_id: '123'\n"
        "metrics_sources:\n"
        "  - .mb/sidecars/meta-ads/workshop.sqlite\n"
        "---\n"
        "# Workshop\n",
        encoding="utf-8",
    )
    (decisions / "2026-05-06-workshop.md").write_text(
        "---\ndate: 2026-05-06\nstatus: accepted\n---\n# Workshop decision\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))

    assert index["push_count"] == 1
    assert index["summary"]["push_count"] == 1
    assert index["canonical_push_count"] == 1
    assert index["summary"]["canonical_push_count"] == 1
    assert index["pushes"][0]["path"] == "pushes/2026-05-06-workshop/push.md"
    assert index["pushes"][0]["kind"] == "launch"
    assert index["push_compatibility"]["legacy_campaign_keys_deprecated"] is True
    edge_targets = {edge["target"] for edge in index["edges"]}
    assert "file:decisions/2026-05-06-workshop.md" in edge_targets
    assert "file:core/offers/workshop/offer.md" in edge_targets
    assert any(
        edge["source"] == "file:pushes/2026-05-06-workshop/push.md"
        and edge["target"] == "file:core/offers/workshop/offer.md"
        and edge["type"] == "offer"
        and edge["rel_type"] == "offer"
        for edge in index["edges"]
    )
    assert any(
        edge["source"] == "file:pushes/2026-05-06-workshop/push.md"
        and edge["target"] == "provider:meta-ads"
        and edge["type"] == "provider_refs"
        and edge["rel_type"] == "provider"
        for edge in index["edges"]
    )
    assert not any("123" in target for target in edge_targets)
    assert not any("sidecars" in target for target in edge_targets)
    assert not any("123" in json.dumps(node) for node in index["nodes"])


def test_graph_keeps_legacy_campaign_facts_during_compatibility(tmp_path: Path) -> None:
    campaign = tmp_path / "campaigns" / "2026-05-workshop"
    campaign.mkdir(parents=True)
    (campaign / "campaign.md").write_text(
        "---\ntype: campaign\nslug: workshop\nstatus: active\n---\n# Workshop\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))

    assert index["push_count"] == 1
    assert index["summary"]["push_count"] == 1
    assert index["campaign_count"] == 1
    assert index["summary"]["legacy_campaign_count"] == 1
    assert index["campaigns"][0]["legacy"] is True
    assert index["deprecated_campaign_keys"] is True


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


def test_build_index_normalizes_relationship_registry_fields(tmp_path: Path) -> None:
    bets = tmp_path / "bets"
    campaigns = tmp_path / "campaigns" / "spring"
    bets.mkdir()
    campaigns.mkdir(parents=True)
    (campaigns / "campaign.md").write_text(
        "---\nslug: spring\nstatus: active\n---\n# Spring\n",
        encoding="utf-8",
    )
    (bets / "spring.md").write_text(
        "---\n"
        "status: open\n"
        "opened: 2026-05-04\n"
        "deadline: 2026-05-11\n"
        "appetite: 1 week\n"
        "hypothesis: Spring push creates calls.\n"
        "metric: calls\n"
        "target: 5 calls\n"
        "result: ''\n"
        "linked_decision: decisions/spring.md\n"
        "linked_research: []\n"
        "linked_campaigns:\n"
        "  - campaigns/spring/campaign.md\n"
        "linked_outcomes: []\n"
        "public: true\n"
        "channels: []\n"
        "tags: []\n"
        "---\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))

    assert index["registry"]["version"] == "0.1"
    assert any(
        edge["type"] == "linked_decision"
        and edge["rel_type"] == "decision"
        and edge["original_field"] == "linked_decision"
        for edge in index["edges"]
    )
    assert any(
        edge["type"] == "linked_campaigns"
        and edge["rel_type"] == "push"
        and edge["original_field"] == "linked_campaigns"
        for edge in index["edges"]
    )


def test_build_index_parses_safe_markdown_links(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    research = tmp_path / "research"
    docs.mkdir()
    research.mkdir()
    (research / "audience.md").write_text(
        "---\ndate: 2026-05-07\ntopic: audience\nsource: manual\n---\n# Audience\n",
        encoding="utf-8",
    )
    (docs / "brief.md").write_text(
        "---\ntitle: Brief\n---\n"
        "See [Audience](../research/audience.md) and "
        "[external](https://en.wikipedia.org/wiki/Foo_(bar)).\n"
        "![Chart](../research/chart.png)\n"
        "Use `[Missing](../research/missing.md)` as an example.\n"
        "```md\n[Missing](../research/missing.md)\n```\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))

    assert any(
        edge["source"] == "file:docs/brief.md"
        and edge["target"] == "file:research/audience.md"
        and edge["type"] == "markdown_link"
        and edge["rel_type"] == "reference"
        for edge in index["edges"]
    )
    assert any(
        node["id"] == "external:https-en-wikipedia-org-wiki-foo-bar"
        and node["metadata"]["ref"] == "https://en.wikipedia.org/wiki/Foo_(bar)"
        for node in index["nodes"]
    )
    assert not any("chart" in edge["target"] for edge in index["edges"])
    assert not any("missing" in edge["target"] for edge in index["edges"])


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
    assert index["version"] == 2
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


# ---------------------------------------------------------------------------
# Topology integration (MAIN-289)
# ---------------------------------------------------------------------------


_TOPOLOGY_REGISTRY_BODY = """---
type: repo_topology
status: active
schema: mb.repo_topology.v0
home: github:example-co/example
business_display_name: Example Business
repos:
  - slug: example
    display_name: Example Business
    role: business
    lifecycle: active
    github_owner: example-co
    repo_name: example
    remote: github:example-co/example
    visibility: team_private
    relationship: hub_for
  - slug: workshop-site
    display_name: Workshop site
    role: site
    lifecycle: active
    relationship: execution_vehicle_for
    parent: example
    github_owner: example-co
    repo_name: workshop-site
    remote: github:example-co/workshop-site
    visibility: public
    linked_offers:
      - core/offers/workshop/offer.md
    linked_playbook_runs:
      - pushes/2026-05-20-workshop-launch/playbooks/launch.md
  - slug: finance
    display_name: Finance source
    role: finance
    lifecycle: active
    relationship: reports_to
    parent: example
    visibility: restricted
---
# Topology
"""


def _write_topology_registry(repo: Path, body: str = _TOPOLOGY_REGISTRY_BODY) -> Path:
    operations = repo / "core" / "operations"
    operations.mkdir(parents=True, exist_ok=True)
    registry = operations / "repo-topology.md"
    registry.write_text(body, encoding="utf-8")
    return registry


def test_graph_index_version_is_two(tmp_path: Path) -> None:
    index = build_index(path=str(tmp_path))
    assert index["version"] == 2


def test_graph_includes_repo_nodes_from_topology(tmp_path: Path) -> None:
    _write_topology_registry(tmp_path)

    index = build_index(path=str(tmp_path))
    nodes_by_id = {node["id"]: node for node in index["nodes"]}

    for slug in ("example", "workshop-site", "finance"):
        node = nodes_by_id.get(f"repo:{slug}")
        assert node is not None, f"missing repo node for {slug}"
        assert node["type"] == "repo"

    assert nodes_by_id["repo:example"]["metadata"]["role"] == "business"
    assert nodes_by_id["repo:example"]["metadata"]["visibility"] == "team_private"
    assert nodes_by_id["repo:workshop-site"]["metadata"]["role"] == "site"
    assert nodes_by_id["repo:workshop-site"]["metadata"]["visibility"] == "public"
    assert nodes_by_id["repo:finance"]["metadata"]["role"] == "finance"
    assert nodes_by_id["repo:finance"]["metadata"]["visibility"] == "restricted"

    assert index["summary"]["repos"] == 3


def test_graph_emits_deterministic_topology_edges(tmp_path: Path) -> None:
    _write_topology_registry(tmp_path)
    offer_path = tmp_path / "core" / "offers" / "workshop" / "offer.md"
    offer_path.parent.mkdir(parents=True, exist_ok=True)
    offer_path.write_text(
        "---\ntitle: Workshop offer\n---\n",
        encoding="utf-8",
    )
    playbook_path = tmp_path / "pushes" / "2026-05-20-workshop-launch" / "playbooks" / "launch.md"
    playbook_path.parent.mkdir(parents=True, exist_ok=True)
    playbook_path.write_text(
        "---\ntitle: Launch playbook\n---\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))
    triples = {(edge["source"], edge["target"], edge["type"]) for edge in index["edges"]}

    assert (
        "repo:workshop-site",
        "repo:example",
        "execution_vehicle_for",
    ) in triples
    assert ("repo:finance", "repo:example", "reports_to") in triples
    assert ("repo:example", "repo:workshop-site", "hub_for") in triples
    assert ("repo:example", "repo:finance", "hub_for") in triples
    assert (
        "repo:workshop-site",
        "file:core/offers/workshop/offer.md",
        "linked_offers",
    ) in triples
    assert (
        "repo:workshop-site",
        "file:pushes/2026-05-20-workshop-launch/playbooks/launch.md",
        "linked_playbook_run",
    ) in triples

    assert index["summary"]["repo_relationships"] >= 6


def test_graph_resolves_missing_playbook_run_target(tmp_path: Path) -> None:
    _write_topology_registry(tmp_path)
    offer_path = tmp_path / "core" / "offers" / "workshop" / "offer.md"
    offer_path.parent.mkdir(parents=True, exist_ok=True)
    offer_path.write_text(
        "---\ntitle: Workshop offer\n---\n",
        encoding="utf-8",
    )

    index = build_index(path=str(tmp_path))
    missing_edges = [
        edge
        for edge in index["edges"]
        if edge["source"] == "repo:workshop-site"
        and edge["type"] == "linked_playbook_run"
        and str(edge["target"]).startswith("missing:")
    ]
    assert len(missing_edges) == 1


def test_graph_skips_linked_playbooks_blueprint_field(tmp_path: Path) -> None:
    body = """---
type: repo_topology
status: active
schema: mb.repo_topology.v0
home: github:example-co/example
business_display_name: Example Business
repos:
  - slug: example
    display_name: Example Business
    role: business
    lifecycle: active
    github_owner: example-co
    repo_name: example
    remote: github:example-co/example
    visibility: team_private
    relationship: hub_for
    linked_playbooks:
      - core/playbooks/launch-checklist.md
---
# Topology
"""
    _write_topology_registry(tmp_path, body)

    index = build_index(path=str(tmp_path))
    node_ids = {node["id"] for node in index["nodes"]}
    edge_types = {edge["type"] for edge in index["edges"]}

    assert not any(node_id.startswith("engine_playbook:") for node_id in node_ids)
    assert "linked_playbook" not in edge_types
