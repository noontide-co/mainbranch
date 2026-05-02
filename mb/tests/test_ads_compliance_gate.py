from pathlib import Path

from mb.ads_compliance_gate import main

FIXTURES = Path(__file__).parent / "fixtures" / "ads"


def test_ads_compliance_gate_dry_run_prints_diff_without_modifying_source(
    tmp_path: Path, capsys
) -> None:
    source = tmp_path / "unsafe-batch.md"
    source.write_text((FIXTURES / "unsafe-batch.md").read_text(encoding="utf-8"), encoding="utf-8")
    original = source.read_text(encoding="utf-8")

    result = main([str(source), str(FIXTURES / "compliance-findings.json")])

    output = capsys.readouterr().out
    assert result == 0
    assert "Mode: dry-run" in output
    assert "Dry run complete: source copy was not modified." in output
    assert "-If you're tired of dead-end marketing" in output
    assert "+For coaches rebuilding a marketing system" in output
    assert "this helps clarify your funnel plan" not in output
    assert source.read_text(encoding="utf-8") == original


def test_ads_compliance_gate_requires_approval_before_writing_source(tmp_path: Path) -> None:
    source = tmp_path / "unsafe-batch.md"
    review_log = tmp_path / "review-log.md"
    source.write_text((FIXTURES / "unsafe-batch.md").read_text(encoding="utf-8"), encoding="utf-8")

    result = main(
        [
            str(source),
            str(FIXTURES / "compliance-findings.json"),
            "--approve",
            "--review-log",
            str(review_log),
        ]
    )

    updated = source.read_text(encoding="utf-8")
    assert result == 0
    assert "For coaches rebuilding a marketing system" in updated
    assert "A clearer growth system for coaches" in updated
    assert "If you're tired of dead-end marketing" not in updated
    assert "Guaranteed growth for coaches" not in updated
    assert "this fixes your funnel in 30 days" in updated
    assert review_log.exists()
    assert "Ads Compliance Proposed Changes" in review_log.read_text(encoding="utf-8")


def test_ads_compliance_gate_skips_ambiguous_repeated_evidence(tmp_path: Path, capsys) -> None:
    source = tmp_path / "repeated-batch.md"
    source.write_text(
        "## Ad 1\nRepeated claim.\n\n## Ad 2\nRepeated claim.\n",
        encoding="utf-8",
    )
    findings = tmp_path / "findings.json"
    findings.write_text(
        """
{
  "findings": [
    {
      "severity": "P2",
      "item_ref": "Ad 1",
      "issue": "Ambiguous repeated evidence.",
      "evidence": "Repeated claim.",
      "rule": "Copy quality",
      "fix": "Specific replacement."
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )
    original = source.read_text(encoding="utf-8")

    result = main([str(source), str(findings), "--approve"])

    output = capsys.readouterr().out
    assert result == 0
    assert "Skipped findings: 1" in output
    assert "refusing ambiguous rewrite" in output
    assert "No source copy changes are proposed." in output
    assert source.read_text(encoding="utf-8") == original


def test_ads_compliance_gate_matches_against_original_text_to_avoid_compounding(
    tmp_path: Path,
) -> None:
    source = tmp_path / "compound-batch.md"
    source.write_text("Risky phrase.\n", encoding="utf-8")
    findings = tmp_path / "findings.json"
    findings.write_text(
        """
{
  "findings": [
    {
      "severity": "P2",
      "item_ref": "Ad 1",
      "issue": "First fix.",
      "evidence": "Risky phrase.",
      "rule": "Meta personal attributes",
      "fix": "Safer phrase."
    },
    {
      "severity": "P2",
      "item_ref": "Ad 1",
      "issue": "Would compound if matched sequentially.",
      "evidence": "Safer phrase.",
      "rule": "Copy quality",
      "fix": "Final phrase."
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    result = main([str(source), str(findings), "--approve"])

    assert result == 0
    assert source.read_text(encoding="utf-8") == "Safer phrase.\n"
