"""Tests for read-only link suggestions."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import suggest
from mb.cli import app

runner = CliRunner()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _actions_by_path(report: dict[str, object]) -> dict[str, dict[str, object]]:
    suggestions = report["suggestions"]
    assert isinstance(suggestions, list)
    by_path: dict[str, dict[str, object]] = {}
    for suggestion in suggestions:
        assert isinstance(suggestion, dict)
        target = suggestion["target"]
        assert isinstance(target, dict)
        path = target.get("path")
        if isinstance(path, str):
            by_path[path] = suggestion
    return by_path


def test_suggest_links_returns_ranked_json_without_writing(tmp_path: Path) -> None:
    source = tmp_path / "decisions" / "2026-05-11-google-ads-first.md"
    _write(
        tmp_path / "research" / "google-ads-intent.md",
        "---\ntitle: Google Ads Intent Research\n---\n"
        "Search intent from founders comparing launch systems.\n"
        "Track #channel/google-ads.\n",
    )
    _write(
        tmp_path / "reports" / "google-ads-weekly.md",
        "---\ntype: report\ntitle: Google Ads Weekly Report\n---\n"
        "Weekly Google Ads spend and conversion notes.\n",
    )
    _write(
        source,
        "---\n"
        "title: Google Ads First Decision\n"
        "status: accepted\n"
        "linked_research: []\n"
        "---\n"
        "# Google Ads First Decision\n\n"
        "We chose Google Ads first because the Google Ads Intent Research and "
        "Google Ads Weekly Report showed enough demand.\n",
    )
    before = source.read_text(encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/2026-05-11-google-ads-first.md",
            "--repo",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert source.read_text(encoding="utf-8") == before
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["safe_to_apply"] is False
    assert report["summary"]["writes"] == 0
    by_path = _actions_by_path(report)
    research = by_path["research/google-ads-intent.md"]
    assert research["action"] == "add_typed_frontmatter_link"
    research_target = research["target"]
    assert isinstance(research_target, dict)
    assert research_target["field"] == "linked_research"
    assert by_path["reports/google-ads-weekly.md"]["action"] == "link_report_or_data_metadata"
    assert any(
        suggestion["action"] == "add_entity_tag"
        and suggestion["target"] == {"tag": "#channel/google-ads"}
        for suggestion in report["suggestions"]
    )


def test_suggest_links_can_include_ignored_candidates(tmp_path: Path) -> None:
    _write(
        tmp_path / "decisions" / "pricing.md",
        "---\ntitle: Pricing\nstatus: accepted\n---\n# Pricing\n\nUse annual plans.\n",
    )
    _write(
        tmp_path / "research" / "unrelated.md",
        "---\ntitle: Churn Interview\n---\n# Churn Interview\n\nSupport notes.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/pricing.md",
            "--repo",
            str(tmp_path),
            "--include-ignored",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["suggestions"][0]["action"] == "ignore"
    assert report["summary"]["ignored_candidates"] == 1


def test_suggest_links_skips_targets_already_in_frontmatter(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "google-ads-intent.md",
        "---\ntitle: Google Ads Intent Research\n---\n"
        "Search intent from founders comparing launch systems.\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-11-google-ads-first.md",
        "---\n"
        "title: Google Ads First Decision\n"
        "status: accepted\n"
        "linked_research:\n"
        "  - research/google-ads-intent.md\n"
        "---\n"
        "# Google Ads First Decision\n\n"
        "We weighed paid acquisition against organic for the new quarter.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/2026-05-11-google-ads-first.md",
            "--repo",
            str(tmp_path),
            "--include-ignored",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    research = by_path["research/google-ads-intent.md"]
    assert research["action"] == "ignore"
    reasons = research["reasons"]
    assert isinstance(reasons, list)
    assert "already connected" in reasons[0]


def test_suggest_links_skips_targets_already_inline_linked(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "google-ads-intent.md",
        "---\ntitle: Google Ads Intent Research\n---\n"
        "Search intent from founders comparing launch systems.\n",
    )
    _write(
        tmp_path / "docs" / "ads-overview.md",
        "---\ntitle: Ads Overview\n---\n"
        "# Ads Overview\n\n"
        "See [Google Ads Intent Research](../research/google-ads-intent.md) for "
        "the demand signal we used.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "docs/ads-overview.md",
            "--repo",
            str(tmp_path),
            "--include-ignored",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    research = by_path["research/google-ads-intent.md"]
    assert research["action"] == "ignore"
    reasons = research["reasons"]
    assert isinstance(reasons, list)
    assert "already connected" in reasons[0]


def test_suggest_links_skips_report_already_linked(tmp_path: Path) -> None:
    _write(
        tmp_path / "reports" / "google-ads-weekly.md",
        "---\ntype: report\ntitle: Google Ads Weekly Report\n---\n"
        "Weekly Google Ads spend and conversion notes.\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-11-google-ads-first.md",
        "---\n"
        "title: Google Ads First Decision\n"
        "status: accepted\n"
        "---\n"
        "# Google Ads First Decision\n\n"
        "We chose Google Ads first; see "
        "[Google Ads Weekly Report](../reports/google-ads-weekly.md) "
        "for the spend and conversion trend.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/2026-05-11-google-ads-first.md",
            "--repo",
            str(tmp_path),
            "--include-ignored",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    report_entry = by_path["reports/google-ads-weekly.md"]
    assert report_entry["action"] == "ignore"
    reasons = report_entry["reasons"]
    assert isinstance(reasons, list)
    assert "already connected" in reasons[0]


def test_suggest_links_rejects_non_markdown_source(tmp_path: Path) -> None:
    _write(tmp_path / "notes.txt", "plain text\n")

    result = runner.invoke(
        app,
        ["suggest", "links", "notes.txt", "--repo", str(tmp_path), "--json"],
    )

    assert result.exit_code == 2
    assert "is not a Markdown file" in result.stderr


def test_suggest_links_does_not_misclassify_outcome_substring(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "voice-outcome-mapping.md",
        "---\ntitle: Voice Outcome Mapping\n---\nMapping launch voice to expected outcomes.\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-11-voice-pass.md",
        "---\n"
        "title: Voice Pass Decision\n"
        "status: accepted\n"
        "---\n"
        "# Voice Pass Decision\n\n"
        "We will incorporate the Voice Outcome Mapping research before the launch.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/2026-05-11-voice-pass.md",
            "--repo",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    research = by_path["research/voice-outcome-mapping.md"]
    target = research["target"]
    assert isinstance(target, dict)
    assert target.get("field") == "linked_research"


def test_suggest_links_skips_targets_already_wikilinked(tmp_path: Path) -> None:
    _write(
        tmp_path / "research" / "google-ads-intent.md",
        "---\ntitle: Google Ads Intent Research\n---\n"
        "Search intent from founders comparing launch systems.\n",
    )
    _write(
        tmp_path / "docs" / "ads-overview.md",
        "---\ntitle: Ads Overview\n---\n"
        "# Ads Overview\n\n"
        "See [[google-ads-intent]] for the demand signal we used.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "docs/ads-overview.md",
            "--repo",
            str(tmp_path),
            "--include-ignored",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    research = by_path["research/google-ads-intent.md"]
    assert research["action"] == "ignore"
    reasons = research["reasons"]
    assert isinstance(reasons, list)
    assert "already connected" in reasons[0]


def test_suggest_links_render_human_prints_target_and_reasons(
    tmp_path: Path, capsys: object
) -> None:
    report = {
        "source": "decisions/sample.md",
        "suggestions": [
            {
                "action": "add_typed_frontmatter_link",
                "action_label": "add typed frontmatter link",
                "score": 90,
                "target": {
                    "path": "research/example.md",
                    "title": "Example Research",
                    "field": "linked_research",
                },
                "reasons": ["The source directly names Example Research."],
                "evidence": {},
            }
        ],
        "matrix": {"doc": "docs/business-connections.md", "actions": []},
    }

    suggest.render_human(report)

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "mb suggest links" in captured.out
    assert "decisions/sample.md" in captured.out
    assert "research/example.md" in captured.out
    assert "linked_research" in captured.out
    assert "The source directly names Example Research." in captured.out
    assert "docs/business-connections.md" in captured.out


def test_suggest_links_recognizes_data_source_registry(tmp_path: Path) -> None:
    _write(
        tmp_path / "data" / "google-ads" / "source.md",
        "---\n"
        "type: data_source\n"
        "provider: google-ads\n"
        "owner: growth\n"
        "privacy: team_private\n"
        "cadence: daily\n"
        "freshness: 2026-05-10\n"
        "---\n"
        "# Google Ads source\n"
        "Local SQLite for Google Ads spend, impressions, clicks.\n",
    )
    _write(
        tmp_path / "decisions" / "2026-05-11-google-ads-first.md",
        "---\n"
        "title: Google Ads First Decision\n"
        "status: accepted\n"
        "---\n"
        "# Google Ads First Decision\n\n"
        "We will run a Google Ads test; see data/google-ads/source.md for the "
        "local Google Ads numbers we will trust.\n",
    )

    result = runner.invoke(
        app,
        [
            "suggest",
            "links",
            "decisions/2026-05-11-google-ads-first.md",
            "--repo",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    by_path = _actions_by_path(report)
    source = by_path["data/google-ads/source.md"]
    assert source["action"] == "link_report_or_data_metadata"
    target = source["target"]
    assert isinstance(target, dict)
    assert target.get("field") == "linked_data_sources"
    reasons = source["reasons"]
    assert isinstance(reasons, list)
    assert any("data-source registry record" in reason for reason in reasons)
