"""``mb similar-bets`` deterministic repo-memory lookup."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import similar_bets
from mb.cli import app

runner = CliRunner()


def _write_repo(repo: Path) -> None:
    (repo / "bets").mkdir(parents=True)
    (repo / "decisions").mkdir()
    (repo / "research").mkdir()
    (repo / "core" / "offers" / "ads-lab").mkdir(parents=True)
    (repo / "core" / "offers" / "ops-audit").mkdir(parents=True)
    (repo / "decisions" / "github-agency.md").write_text(
        "---\ntitle: GitHub Agency Decision\nstatus: accepted\n---\n"
        "# GitHub Agency Decision\n\nUse GitHub tasks for agency delivery.\n",
        encoding="utf-8",
    )
    (repo / "research" / "calls.md").write_text(
        "---\ntitle: Qualified Calls Research\n---\n"
        "# Qualified Calls Research\n\nOperators respond to proof-led audits.\n",
        encoding="utf-8",
    )
    (repo / "bets" / "2026-05-04-github-audit.md").write_text(
        "---\n"
        "status: closed\n"
        "opened: 2026-05-04\n"
        "deadline: 2026-05-11\n"
        "appetite: 1 week\n"
        "hypothesis: GitHub audit offer books qualified agency calls.\n"
        "metric: qualified calls booked\n"
        "target: 5 qualified calls\n"
        "result: Hit 6 qualified calls and graduated into an agency workflow.\n"
        "linked_decisions:\n"
        "  - decisions/github-agency.md\n"
        "linked_research:\n"
        "  - research/calls.md\n"
        "linked_campaigns: []\n"
        "linked_outcomes: []\n"
        "public: true\n"
        "channels:\n"
        "  - github\n"
        "tags:\n"
        "  - agency\n"
        "---\n"
        "# GitHub Audit Bet\n\nThe proof-led audit worked for agency prospects.\n",
        encoding="utf-8",
    )
    (repo / "core" / "offers" / "ads-lab" / "offer.md").write_text(
        "---\n"
        "title: Ads Lab\n"
        "status: died\n"
        "metric: monthly recurring revenue\n"
        "result: Killed after missing qualified call targets.\n"
        "tags:\n"
        "  - agency\n"
        "---\n"
        "# Ads Lab\n\nA dead agency offer with a post-mortem about call quality.\n",
        encoding="utf-8",
    )
    (repo / "core" / "offers" / "ops-audit" / "offer.md").write_text(
        "---\n"
        "title: Ops Audit\n"
        "status: running\n"
        "metric: qualified calls\n"
        "tags:\n"
        "  - agency\n"
        "---\n"
        "# Ops Audit\n\nA running agency offer.\n",
        encoding="utf-8",
    )


def test_similar_bets_json_prefers_bets_and_includes_offer_context(tmp_path: Path) -> None:
    _write_repo(tmp_path)

    result = runner.invoke(
        app,
        [
            "similar-bets",
            "agency github qualified calls",
            "--repo",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema"]["name"] == "mainbranch.similar_bets"
    assert payload["summary"]["records_scanned"] == 3
    assert payload["summary"]["bets"] == 1
    assert payload["summary"]["offers"] == 2
    assert payload["summary"]["graduated"] == 1
    assert payload["summary"]["killed"] == 1
    assert payload["matches"][0]["source_type"] == "bet"
    assert payload["matches"][0]["outcome_bucket"] == "graduated"
    assert "decisions/github-agency.md" in payload["matches"][0]["linked_files"]
    assert payload["matches"][0]["similarity"]["graph_overlap"]
    assert payload["schema"]["status_inputs"]["offers"] == [
        "died",
        "graduated",
        "killed",
        "proposed",
        "running",
        "scaling",
    ]
    assert any(
        match["path"] == "core/offers/ops-audit/offer.md" and match["outcome_bucket"] == "active"
        for match in payload["matches"]
    )


def test_similar_bets_human_output_names_evidence(tmp_path: Path, capsys) -> None:
    _write_repo(tmp_path)

    report = similar_bets.run(str(tmp_path), "qualified calls", limit=1)
    similar_bets.render_human(report)

    output = capsys.readouterr().out
    assert "mb similar-bets" in output
    assert "qualified calls" in output
    assert "evidence: target: 5 qualified calls" in output
