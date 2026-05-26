from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import file_contracts
from mb import status as status_mod
from mb import validate as validate_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _write_offer(repo: Path, body: str) -> Path:
    path = repo / "core" / "offer.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntype: offer\nstatus: running\n---\n\n" + body, encoding="utf-8")
    return path


GOOD_OFFER = """# Setup Sprint

## Who this is for

Solo operators who lose business context across AI sessions.

## Promise

Turn scattered offer, proof, launch, and decision work into durable memory.

## Mechanism

Main Branch creates a repo-backed workflow that agents read before acting.

## Proof

Public-safe testimonials and typicality notes live under core/proof/.

## Price Or Value

A fixed setup sprint creates the first usable business brain.

## Next Step

Book a fit call before writing launch copy.
"""


def test_offer_contract_valid_file_has_no_findings(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    _write_offer(repo, GOOD_OFFER)

    report = file_contracts.evaluate(repo)

    assert report["ok"] is True
    assert report["summary"]["findings"] == 0
    assert report["contracts"][0]["id"] == "offer"
    assert report["contracts"][0]["recommended_route"] == "mb-think"


def test_offer_contract_missing_sections_reports_owner_route(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    _write_offer(repo, "# Offer\n\nWe help founders organize launch work.\n")

    report = file_contracts.evaluate(repo)
    finding = report["findings"][0]

    assert report["ok"] is False
    assert finding["code"] == "file_contract_missing_section"
    assert finding["recommended_route"] == "mb-think"
    assert "Your offer" in finding["owner_message"]
    assert finding["approval_required"] is True
    assert report["summary"]["routes"] == {"mb-think": report["summary"]["findings"]}


def test_offer_contract_empty_section_is_distinct_from_missing(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    _write_offer(
        repo,
        """# Offer

## Who this is for

Founders.

## Promise

Done.
""",
    )

    report = file_contracts.evaluate(repo)
    codes = {finding["code"] for finding in report["findings"]}

    assert "file_contract_empty_section" in codes
    assert "file_contract_missing_section" in codes


def test_validate_json_includes_file_contract_guided_route(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    _write_offer(repo, "# Offer\n\nA rough offer stub.\n")

    result = runner.invoke(app, ["validate", str(repo), "--json"])
    payload = json.loads(result.stdout)

    assert result.exit_code == 0
    assert payload["file_contracts"]["summary"]["findings"] > 0
    assert payload["file_contracts"]["findings"][0]["recommended_route"] == "mb-think"
    categories = payload["validation_categories"]["by_category"]
    assert categories["file_contract_missing_section"]["recommended_route"] == "mb-think"
    assert payload["summary"]["warnings"] > 0


def test_status_surfaces_file_contract_ranked_route(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", lambda name: "")
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _write_offer(repo, "# Offer\n\nA rough offer stub.\n")

    report = status_mod.run(path=str(repo), update_marker=False)
    action = next(
        item for item in report["ranked_actions"] if item["id"] == "review_file_contract_offer"
    )

    assert report["validation"]["file_contracts"]["summary"]["findings"] > 0
    assert action["command"] == "mb-think"
    assert "offer" in action["title"].lower()
    assert action["signals"][0]["id"] == "validation.file_contracts.findings"


def test_fresh_fixture_surfaces_guided_route_without_writes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", lambda name: "")
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _write_offer(repo, "# Offer\n\nA rough offer stub.\n")
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    validate_report = validate_mod.run(str(repo))
    status_report = status_mod.run(path=str(repo), update_marker=False)
    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    assert validate_report["file_contracts"]["summary"]["findings"] > 0
    assert any(
        action["id"] == "review_file_contract_offer" for action in status_report["ranked_actions"]
    )
    assert after == before
