"""``mb validate`` frontmatter shape checks."""

from __future__ import annotations

import json
import re
from pathlib import Path

from typer.testing import CliRunner

from mb import relationships
from mb.cli import app
from mb.validate import run

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[2]


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
    _write(
        tmp_path / "bets" / "2026-04-29-launch.md",
        (
            "---\n"
            "status: open\n"
            "opened: 2026-04-29\n"
            "deadline: 2026-05-13\n"
            "appetite: 2 weeks\n"
            "hypothesis: If we launch, qualified calls will increase.\n"
            "metric: qualified calls\n"
            "target: 10 qualified calls\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n"
            "# Launch bet\n"
        ),
    )
    report = run(path=str(tmp_path))
    assert report["ok"] is True
    assert all(f["ok"] for f in report["files"])


def test_validate_accepts_canonical_bet_linked_pushes_without_legacy_campaigns(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "bets" / "2026-05-08-launch.md",
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-08\n"
            "deadline: 2026-05-22\n"
            "appetite: 2 weeks\n"
            "hypothesis: If we ship the push, qualified calls will increase.\n"
            "metric: qualified calls\n"
            "target: 10 qualified calls\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_pushes: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n"
            "# Launch bet\n"
        ),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True
    bet = next(file for file in report["files"] if file["schema"] == "bets")
    assert bet["errors"] == []


def test_validate_keeps_legacy_bet_campaign_links_readable(tmp_path: Path) -> None:
    _write(
        tmp_path / "bets" / "2026-05-08-legacy.md",
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-08\n"
            "deadline: 2026-05-22\n"
            "appetite: 2 weeks\n"
            "hypothesis: If the legacy campaign lands, calls will increase.\n"
            "metric: qualified calls\n"
            "target: 10 qualified calls\n"
            "result: ''\n"
            "linked_decisions: []\n"
            "linked_research: []\n"
            "linked_campaigns: []\n"
            "linked_outcomes: []\n"
            "public: false\n"
            "channels: []\n"
            "tags: []\n"
            "---\n"
            "# Legacy bet\n"
        ),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True
    bet = next(file for file in report["files"] if file["schema"] == "bets")
    assert bet["errors"] == []
    assert any("linked_campaigns" in warning for warning in bet["warnings"])


def test_validate_ignores_folder_readme_docs(tmp_path: Path) -> None:
    _write(tmp_path / "research" / "README.md", "# Research\n\nFolder docs without frontmatter.\n")
    _write(tmp_path / "decisions" / "README.md", "# Decisions\n\nFolder docs.\n")
    _write(tmp_path / "bets" / "README.md", "# Bets\n\nFolder docs.\n")
    _write(tmp_path / "log" / "README.md", "# Log\n\nFolder docs.\n")
    _write(tmp_path / "documents" / "README.md", "# Documents\n\nFolder docs.\n")
    _write(
        tmp_path / "pushes" / "2026-05-08-launch" / "playbooks" / "README.md",
        "# Playbooks\n\nFolder docs.\n",
    )
    _write(
        tmp_path / "research" / "2026-05-08-topic-source.md",
        "---\ndate: 2026-05-08\ntopic: topic\nsource: source\n---\n# Research\n",
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True
    paths = {file["path"] for file in report["files"]}
    assert "research/README.md" not in paths
    assert "decisions/README.md" not in paths
    assert "bets/README.md" not in paths
    assert "log/README.md" not in paths
    assert "documents/README.md" not in paths
    assert "pushes/2026-05-08-launch/playbooks/README.md" not in paths


def test_keyword_gate_documented_frontmatter_validates(tmp_path: Path) -> None:
    guide = REPO_ROOT / ".claude" / "skills" / "mb-think" / "references" / "keyword-gate.md"
    text = guide.read_text(encoding="utf-8")
    match = re.search(r"Frontmatter:\n\n```yaml\n(?P<frontmatter>---\n.*?\n---)\n```", text, re.S)
    assert match is not None

    frontmatter = (
        match.group("frontmatter")
        .replace("YYYY-MM-DD", "2026-05-08")
        .replace("offer-slug", "workshop")
        .replace("core/offers/<offer>/offer.md", "core/offers/workshop/offer.md")
    )
    _write(
        tmp_path / "research" / "2026-05-08-keyword-gate-workshop.md",
        f"{frontmatter}\n\n# Keyword Gate\n",
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True
    assert all(file["ok"] for file in report["files"])


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


def test_validate_explains_legacy_frontmatter_debt_after_migration(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-legacy.md",
        "---\ndate: 2026-04-29\nstatus: pending\n---\n# legacy\n",
    )
    (tmp_path / ".mb").mkdir()
    (tmp_path / ".mb" / "schema_version").write_text("0.2\n", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["legacy_repair"]["code"] == "legacy-frontmatter-schema-debt"
    assert "not as evidence that the path migration failed" in payload["legacy_repair"]["message"]


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
    assert report["cross_refs"]["registry"]["version"] == "0.1"
    assert report["summary"]["warnings"] == 0


def test_source_scoped_offer_relationship_requires_source_path() -> None:
    assert relationships.relationship_for_field("offer") is None
    assert (
        relationships.relationship_for_field("offer", source_path="pushes/2026-05-07-demo/push.md")
        is not None
    )


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
    assert finding["code"] == "missing-target"
    assert finding["path"] == "decisions/2026-04-29-broken.md"
    assert finding["field"] == "linked_decisions"
    assert finding["target"] == "decisions/missing.md"


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
    assert report["files"][0]["ok"] is False


def test_cross_refs_skip_explicit_cross_repo_refs(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-04-29-cross-repo.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_research:\n"
            "  - noontide-projects/research/2026-04-29-note.md\n"
            "linked_decisions:\n"
            "  - repo:noontide-projects/decisions/2026-04-29-choice.md\n"
            "---\n"
            "# cross repo\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_skip_bundled_package_data(tmp_path: Path) -> None:
    _write(
        tmp_path / "mb" / "_data" / "fixtures" / "decisions" / "fixture.md",
        (
            "---\n"
            "date: 2026-04-29\n"
            "status: accepted\n"
            "linked_research: research/missing.md\n"
            "---\n"
            "# fixture\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_warn_on_missing_wikilink_target(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[missing-note]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-wikilink-target"
    assert finding["field"] == "wikilink"
    assert finding["target"] == "missing-note"


def test_cross_refs_warn_on_ambiguous_wikilink_target(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "note.md",
        "---\ndate: 2026-05-04\ntopic: one\nsource: manual\n---\n# Note\n",
    )
    _write(
        tmp_path / "documents" / "note.md",
        "---\ntitle: Other note\n---\n# Other\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[note]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "ambiguous-wikilink"
    assert finding["target"] == "note"


def test_cross_refs_accept_resolved_wikilink_target_without_extension(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "audience.md",
        "---\ndate: 2026-05-04\ntopic: audience\nsource: manual\n---\n# Audience\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[research/audience|audience]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_accept_resolved_wikilink_target_with_heading_anchor(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "audience.md",
        "---\ndate: 2026-05-04\ntopic: audience\nsource: manual\n---\n# Details\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[research/audience#details]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_do_not_stem_fallback_for_path_like_wikilinks(tmp_path: Path) -> None:
    _write(
        tmp_path / "documents" / "audience.md",
        "---\ntitle: Audience\n---\n# Audience\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[research/audience]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-wikilink-target"
    assert finding["target"] == "research/audience"


def test_cross_refs_warn_when_wikilink_resolves_only_to_directory(tmp_path: Path) -> None:
    (tmp_path / "campaigns" / "spring-launch").mkdir(parents=True)
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[campaigns/spring-launch]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-wikilink-target"
    assert finding["target"] == "campaigns/spring-launch"


def test_cross_refs_warn_when_wikilink_resolves_only_to_non_markdown_file(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "documents" / "diagram.png", "fake image\n")
    _write(
        tmp_path / "decisions" / "2026-05-04-link.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\nSee [[documents/diagram.png]].\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-wikilink-target"
    assert finding["target"] == "documents/diagram.png"


def test_cross_refs_ignore_wikilink_like_syntax_inside_fenced_code(tmp_path: Path) -> None:
    _write(
        tmp_path / "documents" / "netlify.md",
        '---\ntitle: Netlify\n---\n```toml\n[[redirects]]\nfrom = "/"\n```\n',
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_ignore_wikilink_like_syntax_inside_inline_code(tmp_path: Path) -> None:
    _write(
        tmp_path / "documents" / "obsidian.md",
        "---\ntitle: Obsidian\n---\nUse `[[example]]` only when the target exists.\n",
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_resolve_standard_markdown_links_and_skip_safe_non_refs(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "research" / "audience.md",
        "---\ndate: 2026-05-07\ntopic: audience\nsource: manual\n---\n# Audience\n",
    )
    _write(
        tmp_path / "docs" / "brief.md",
        "---\ntitle: Brief\n---\n"
        "See [Audience](../research/audience.md), [root](research/audience.md), "
        "and [external](https://en.wikipedia.org/wiki/Foo_(bar)).\n"
        "![Chart](../research/chart.png)\n"
        "Use `[Missing](../research/missing.md)` as an example.\n"
        "```md\n[Missing](../research/missing.md)\n```\n",
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_warn_on_missing_standard_markdown_link_target(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "brief.md",
        "---\ntitle: Brief\n---\nSee [Missing](../research/missing.md).\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-markdown-link-target"
    assert finding["field"] == "markdown_link"
    assert finding["target"] == "../research/missing.md"


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


def test_cross_refs_warn_when_bet_link_lacks_reverse_link(tmp_path: Path) -> None:
    _write(
        tmp_path / "bets" / "2026-05-04-demo.md",
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-04\n"
            "deadline: 2026-05-11\n"
            "appetite: 1 week\n"
            "hypothesis: If demo prospects see the workflow, calls increase.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "result: ''\n"
            "linked_decisions:\n"
            "  - decisions/2026-05-04-demo.md\n"
            "linked_research: []\n"
            "linked_pushes: []\n"
            "linked_outcomes: []\n"
            "public: true\n"
            "channels:\n"
            "  - site\n"
            "tags:\n"
            "  - channel:site\n"
            "---\n"
            "# Demo bet\n"
        ),
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-demo.md",
        "---\ndate: 2026-05-04\nstatus: accepted\n---\n# Demo\n",
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-bet-backlink"
    assert finding["field"] == "linked_decisions"
    assert "linked_bets: bets/2026-05-04-demo.md" in finding["message"]


def test_cross_refs_pass_when_bet_links_are_bidirectional(tmp_path: Path) -> None:
    _write(
        tmp_path / "bets" / "2026-05-04-demo.md",
        (
            "---\n"
            "status: open\n"
            "opened: 2026-05-04\n"
            "deadline: 2026-05-11\n"
            "appetite: 1 week\n"
            "hypothesis: If demo prospects see the workflow, calls increase.\n"
            "metric: calls\n"
            "target: 5 calls\n"
            "result: ''\n"
            "linked_decisions:\n"
            "  - decisions/2026-05-04-demo.md\n"
            "linked_research: []\n"
            "linked_pushes: []\n"
            "linked_outcomes: []\n"
            "public: true\n"
            "channels:\n"
            "  - site\n"
            "tags: []\n"
            "---\n"
            "# Demo bet\n"
        ),
    )
    _write(
        tmp_path / "decisions" / "2026-05-04-demo.md",
        (
            "---\n"
            "date: 2026-05-04\n"
            "status: accepted\n"
            "linked_bets:\n"
            "  - bets/2026-05-04-demo.md\n"
            "---\n"
            "# Demo\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


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
    assert payload["files"][0]["ok"] is False


def _campaign(status: str) -> str:
    return f"---\nslug: workshop-waitlist\nstatus: {status}\n---\n# Workshop waitlist\n"


def test_validate_accepts_campaign_lifecycle_statuses(tmp_path: Path) -> None:
    for status in ("draft", "planned", "active", "paused", "completed", "canceled", "archived"):
        path = tmp_path / "campaigns" / f"2026-05-{status}-push" / "campaign.md"
        _write(path, _campaign(status))

    report = run(path=str(tmp_path))

    assert report["ok"] is True, report
    campaign_files = [f for f in report["files"] if "campaigns/" in f["path"]]
    assert len(campaign_files) == 7
    assert all(f["ok"] for f in campaign_files)


def test_validate_rejects_offer_only_status_on_campaign(tmp_path: Path) -> None:
    # `running` and `scaling` are valid offer statuses but invalid for campaigns;
    # the merged decision tells operators to use `active`.
    _write(
        tmp_path / "campaigns" / "2026-05-bad" / "campaign.md",
        _campaign("scaling"),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [f for f in report["files"] if not f["ok"]]
    assert any("status" in e for f in bad for e in f["errors"])


def test_validate_flags_unknown_campaign_status(tmp_path: Path) -> None:
    _write(
        tmp_path / "campaigns" / "2026-05-typo" / "campaign.md",
        _campaign("live"),  # operator-vocab synonym; not yet wired
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [f for f in report["files"] if not f["ok"]]
    assert any("status" in e for f in bad for e in f["errors"])


def _push(
    status: str,
    slug: str = "workshop-waitlist",
    *,
    kind: str = "launch",
    health: str = "on-track",
) -> str:
    return (
        "---\n"
        "type: push\n"
        f"slug: {slug}\n"
        f"kind: {kind}\n"
        f"status: {status}\n"
        f"health: {health}\n"
        "goal:\n"
        "  metric: qualified calls\n"
        "  target: 10 qualified calls\n"
        "  by: 2026-05-20\n"
        "owner: Devon\n"
        "audience: founders testing Main Branch\n"
        "offer: core/offers/workshop/offer.md\n"
        "promise: Own the launch memory in git.\n"
        "---\n"
        f"# {slug}\n"
    )


def _playbook(
    status: str = "draft",
    *,
    provider: str = "manual",
    provider_boundary: str = "plan-only",
    push: str = "../push.md",
) -> str:
    return (
        "---\n"
        "type: playbook\n"
        f"status: {status}\n"
        f"push: {push}\n"
        "platform: instagram\n"
        f"provider: {provider}\n"
        f"provider_boundary: {provider_boundary}\n"
        "trigger:\n"
        "  kind: comment_keyword\n"
        "  keyword: TEMPLATE\n"
        "resource:\n"
        "  kind: url\n"
        "  value: https://example.com/resource\n"
        "copy:\n"
        "  public_cta: Comment TEMPLATE for the resource.\n"
        "  reply: Thanks. The resource is linked in the post.\n"
        "approval:\n"
        "  required: true\n"
        "  status: needed\n"
        "  approved_by:\n"
        "  approved_at:\n"
        "state:\n"
        "  provider_refs: []\n"
        "  activated_at:\n"
        "  retired_at:\n"
        "validation:\n"
        "  dry_run: not-run\n"
        "  smoke_evidence: []\n"
        "  notes: Draft only; no provider mutation.\n"
        "linked_outcomes: []\n"
        "---\n"
        "# Comment keyword playbook\n"
    )


def test_validate_accepts_push_lifecycle_statuses(tmp_path: Path) -> None:
    for status in ("draft", "planned", "active", "paused", "completed", "canceled", "archived"):
        path = tmp_path / "pushes" / f"2026-05-06-{status}-push" / "push.md"
        _write(path, _push(status, slug=f"{status}-push"))

    report = run(path=str(tmp_path))

    assert report["ok"] is True, report
    push_files = [f for f in report["files"] if "pushes/" in f["path"]]
    assert len(push_files) == 7
    assert all(f["ok"] for f in push_files)


def test_validate_requires_canonical_push_schema(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-incomplete" / "push.md",
        "---\nslug: incomplete\nstatus: active\n---\n# incomplete\n",
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert "missing key: type" in bad["errors"]
    assert "missing key: kind" in bad["errors"]
    assert "missing key: goal" in bad["errors"]
    assert "missing key: owner" in bad["errors"]
    assert "missing key: audience" in bad["errors"]
    assert "missing key: offer" in bad["errors"]
    assert "missing key: promise" in bad["errors"]


def test_validate_requires_canonical_push_folder_shape(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "workshop-waitlist" / "push.md",
        _push("active"),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert "push folder must match YYYY-MM-DD-slug" in bad["errors"]


def test_validate_rejects_invalid_push_shape_fields(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-invalid" / "push.md",
        (
            "---\n"
            "type: campaign\n"
            "slug: invalid\n"
            "kind: sprint\n"
            "status: active\n"
            "health: spicy\n"
            "goal: 40 calls\n"
            "owner: ''\n"
            "audience: founders\n"
            "offer: core/offers/workshop/offer.md\n"
            "promise: " + ("x" * 141) + "\n"
            "---\n"
            "# invalid\n"
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert report["ok"] is False
    assert "type must be 'push'" in bad["errors"]
    assert any("kind=" in error for error in bad["errors"])
    assert any("health=" in error for error in bad["errors"])
    assert "goal must be a mapping with metric, target, and by" in bad["errors"]
    assert "owner must be a non-empty string" in bad["errors"]
    assert "promise must be 140 characters or fewer" in bad["errors"]


def test_validate_rejects_incomplete_structured_push_goal(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-bad-goal" / "push.md",
        (
            "---\n"
            "type: push\n"
            "slug: bad-goal\n"
            "kind: launch\n"
            "status: active\n"
            "health: on-track\n"
            "goal:\n"
            "  metric: qualified calls\n"
            "  target: ''\n"
            "  by: soon\n"
            "owner: Devon\n"
            "audience: founders\n"
            "offer: core/offers/workshop/offer.md\n"
            "promise: Own the launch memory in git.\n"
            "---\n"
            "# bad goal\n"
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert "goal.target must be a non-empty string" in bad["errors"]
    assert "goal.by must be YYYY-MM-DD" in bad["errors"]


def test_validate_rejects_unknown_push_status(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-typo" / "push.md",
        _push("live", slug="typo"),  # operator-vocab synonym; not engine canonical
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False


def test_validate_rejects_unknown_push_kind_even_when_vocabulary_renames_it(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "core" / "vocabulary.md",
        (
            "---\n"
            "type: vocabulary\n"
            "status: active\n"
            "terms:\n"
            "  kinds:\n"
            "    sprint: sprint\n"
            "---\n"
            "# Vocabulary\n"
        ),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-sprint" / "push.md",
        _push("active", slug="sprint", kind="sprint"),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert any("kind=" in error for error in bad["errors"])


def test_validate_accepts_push_playbook_schema(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True, report
    playbook = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][
        0
    ]
    assert playbook["schema"] == "push-playbooks"
    assert playbook["ok"] is True


def test_validate_accepts_sanitized_push_playbook_fixture() -> None:
    fixture_root = Path(__file__).parent / "fixtures"

    report = run(path=str(fixture_root))

    assert report["ok"] is True, report
    assert any(
        file["path"] == "pushes/2026-05-06-resource-delivery/playbooks/valid-resource-delivery.md"
        and file["schema"] == "push-playbooks"
        and file["ok"]
        for file in report["files"]
    )
    assert any(
        file["path"] == "pushes/2026-05-08-google-ads-launch/playbooks/google-ads-launch-plan.md"
        and file["schema"] == "push-playbooks"
        and file["ok"]
        for file in report["files"]
    )


def test_validate_requires_push_playbook_shape(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "incomplete.md",
        "---\ntype: playbook\nstatus: draft\n---\n# Incomplete\n",
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is False
    bad = [file for file in report["files"] if file["path"].endswith("playbooks/incomplete.md")][0]
    assert "missing key: push" in bad["errors"]
    assert "missing key: provider_boundary" in bad["errors"]
    assert "missing key: resource" in bad["errors"]
    assert "missing key: approval" in bad["errors"]
    assert "missing key: linked_outcomes" in bad["errors"]


def test_validate_rejects_playbook_missing_linked_push(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert "push target does not exist" in bad["errors"]


def test_validate_rejects_playbook_wrong_push_link(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(push="pushes/2026-05-06-other/push.md"),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert "push must link to the containing push.md" in bad["errors"]


def test_validate_rejects_unknown_playbook_status(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(status="live"),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert any("status=" in error for error in bad["errors"])


def test_validate_rejects_playbook_supported_provider_claim_without_adapter(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(provider="postiz", provider_boundary="accepted-adapter"),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert any("tested Main Branch provider adapter" in error for error in bad["errors"])


def test_validate_rejects_playbook_secret_frontmatter_value(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook().replace(
            "  notes: Draft only; no provider mutation.\n",
            "  notes: ghp_123456789012345678901234567890123456\n",
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert any("validation.notes" in error for error in bad["errors"])


def test_validate_rejects_playbook_secret_frontmatter(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook().replace(
            "  provider_refs: []\n",
            "  access_token: ghp_123456789012345678901234567890123456\n",
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("playbooks/resource.md")][0]
    assert report["ok"] is False
    assert any("state.access_token" in error for error in bad["errors"])


def test_cross_refs_resolve_linked_pushes_field(tmp_path: Path) -> None:
    """linked_pushes is recognized as a graph link field and must resolve."""
    _write(
        tmp_path / "core" / "offers" / "workshop" / "offer.md",
        "---\nslug: workshop\nstatus: running\n---\n# Workshop\n",
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "decisions" / "2026-05-06-with-link.md",
        (
            "---\n"
            "date: 2026-05-06\n"
            "status: accepted\n"
            "linked_pushes:\n"
            "  - pushes/2026-05-06-target/push.md\n"
            "---\n"
            "# decision\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_validate_push_offer_relationship(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "offers" / "workshop" / "offer.md",
        "---\nslug: workshop\nstatus: running\n---\n# Workshop\n",
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )

    report = run(path=str(tmp_path), cross_refs=True, strict=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 0


def test_cross_refs_warn_on_missing_push_offer_relationship(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-target"
    assert finding["field"] == "offer"
    assert finding["target"] == "core/offers/workshop/offer.md"


def test_validate_accepts_provider_refs_mapping_shape(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target").replace(
            "---\n# target\n",
            "provider_refs:\n  meta_ads:\n    campaign_id: '123'\n---\n# target\n",
        ),
    )

    report = run(path=str(tmp_path))

    assert report["ok"] is True


def test_validate_rejects_provider_refs_scalar_shape(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target").replace(
            "---\n# target\n",
            "provider_refs: meta_ads:123\n---\n# target\n",
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert report["ok"] is False
    assert "provider_refs must be a mapping of provider names to non-secret refs" in bad["errors"]


def test_validate_rejects_provider_refs_list_with_empty_ref_name(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target").replace(
            "---\n# target\n",
            "provider_refs:\n  meta_ads:\n    - \"\": '123'\n---\n# target\n",
        ),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["path"].endswith("push.md")][0]
    assert report["ok"] is False
    assert "provider_refs.meta_ads ref names must be non-empty strings" in bad["errors"]


def _repo_topology(extra_repo_fields: str = "") -> str:
    return (
        "---\n"
        "type: repo_topology\n"
        "status: active\n"
        "schema: mb.repo_topology.v0\n"
        "home: github:example-co/example\n"
        'business_display_name: "Example Business"\n'
        "repos:\n"
        "  - slug: example\n"
        '    display_name: "Example Business"\n'
        "    role: business\n"
        "    lifecycle: active\n"
        "    github_owner: example-co\n"
        "    repo_name: example\n"
        "    remote: github:example-co/example\n"
        "    visibility: team_private\n"
        "    relationship: hub_for\n"
        "  - slug: workshop-site\n"
        '    display_name: "Workshop site"\n'
        "    role: site\n"
        "    lifecycle: active\n"
        "    relationship: execution_vehicle_for\n"
        "    parent: example\n"
        "    github_owner: example-co\n"
        "    repo_name: workshop-site\n"
        "    remote: https://github.com/example-co/workshop-site.git\n"
        "    visibility: public\n"
        "    domain: workshop.example.com\n"
        "    linked_offers:\n"
        "      - core/offers/workshop/offer.md\n"
        "    linked_pushes:\n"
        "      - pushes/2026-05-06-target/push.md\n"
        "    linked_playbook_runs:\n"
        "      - pushes/2026-05-06-target/playbooks/resource.md\n"
        f"{extra_repo_fields}"
        "  - slug: finance\n"
        '    display_name: "Finance source"\n'
        "    role: finance\n"
        "    lifecycle: active\n"
        "    visibility: restricted\n"
        "    relationship: reports_to\n"
        "    parent: example\n"
        "    purpose: Private bookkeeping source; hub stores approved summaries only.\n"
        "---\n"
        "# Repo Topology\n"
    )


def test_validate_accepts_repo_topology_schema_and_links(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "offers" / "workshop" / "offer.md",
        "---\nslug: workshop\nstatus: running\n---\n# Workshop\n",
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "push.md",
        _push("active", slug="target"),
    )
    _write(
        tmp_path / "pushes" / "2026-05-06-target" / "playbooks" / "resource.md",
        _playbook(),
    )
    _write(tmp_path / "core" / "operations" / "repo-topology.md", _repo_topology())

    report = run(path=str(tmp_path), strict=True)

    assert report["ok"] is True, report
    topology = [
        file for file in report["files"] if file["path"] == "core/operations/repo-topology.md"
    ][0]
    assert topology["schema"] == "repo-topology"
    assert topology["warnings"] == []


def test_validate_rejects_unknown_repo_topology_values(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "operations" / "repo-topology.md",
        _repo_topology()
        .replace("role: site", "role: website")
        .replace("lifecycle: active", "lifecycle: graduated", 1)
        .replace("visibility: public", "visibility: secret"),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["schema"] == "repo-topology"][0]
    assert report["ok"] is False
    assert any("role='website'" in error for error in bad["errors"])
    lifecycle_errors = [error for error in bad["errors"] if ".lifecycle" in error]
    assert lifecycle_errors == [
        "repos[0].lifecycle must not be 'graduated'; use a relationship instead"
    ]
    assert any("visibility='secret'" in error for error in bad["errors"])


def test_validate_repo_topology_status_uses_topology_lifecycle(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "operations" / "repo-topology.md",
        _repo_topology().replace("status: active", "status: running"),
    )

    report = run(path=str(tmp_path))

    bad = [file for file in report["files"] if file["schema"] == "repo-topology"][0]
    assert report["ok"] is False
    assert any("topology status='running'" in error for error in bad["errors"])


def test_validate_repo_topology_warns_on_sensitive_boundary_metadata(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "operations" / "repo-topology.md",
        _repo_topology(
            "    raw_ledger_path: /Users/alex/private/books.ledger\n"
            "    provider_cache: raw exports live here\n"
        ),
    )

    report = run(path=str(tmp_path), strict=False)

    topology = [file for file in report["files"] if file["schema"] == "repo-topology"][0]
    assert report["ok"] is True
    assert any("raw_ledger_path" in warning for warning in topology["warnings"])
    assert any("local absolute path" in warning for warning in topology["warnings"])
    assert any("provider_cache" in warning for warning in topology["warnings"])

    strict_report = run(path=str(tmp_path), strict=True)
    assert strict_report["ok"] is False


def test_validate_repo_topology_warns_on_missing_safe_links(tmp_path: Path) -> None:
    _write(tmp_path / "core" / "operations" / "repo-topology.md", _repo_topology())

    report = run(path=str(tmp_path))

    topology = [file for file in report["files"] if file["schema"] == "repo-topology"][0]
    assert report["ok"] is True
    assert any("linked_offers" in warning for warning in topology["warnings"])
    assert any("linked_playbook_runs" in warning for warning in topology["warnings"])


def test_cross_refs_warn_on_missing_linked_pushes_target(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "2026-05-06-broken.md",
        (
            "---\n"
            "date: 2026-05-06\n"
            "status: accepted\n"
            "linked_pushes:\n"
            "  - pushes/2026-05-06-missing/push.md\n"
            "---\n"
            "# broken\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    assert report["ok"] is True
    assert report["summary"]["warnings"] == 1
    finding = report["cross_refs"]["warnings"][0]
    assert finding["code"] == "missing-target"
    assert finding["field"] == "linked_pushes"


def test_cross_refs_flag_campaign_status_transition_regressions(tmp_path: Path) -> None:
    # A newer campaign supersedes an older one but reports a status earlier
    # in the campaign lifecycle. The status-transition checker should flag it
    # against CAMPAIGN_STATUS_ORDER, not the offer order.
    _write(
        tmp_path / "campaigns" / "2026-05-old-push" / "campaign.md",
        (
            "---\n"
            "slug: old-push\n"
            "status: completed\n"  # order = 3
            "---\n"
            "# old push\n"
        ),
    )
    _write(
        tmp_path / "campaigns" / "2026-05-new-push" / "campaign.md",
        (
            "---\n"
            "slug: new-push\n"
            "status: draft\n"  # order = 0 — backward
            "supersedes: campaigns/2026-05-old-push/campaign.md\n"
            "---\n"
            "# new push\n"
        ),
    )

    report = run(path=str(tmp_path), cross_refs=True)

    transition_warnings = [
        w for w in report["cross_refs"]["warnings"] if w["code"] == "status-transition"
    ]
    assert len(transition_warnings) == 1
    assert "move backward" in transition_warnings[0]["message"]
