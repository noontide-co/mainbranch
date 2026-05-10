"""Business repo migration drift lint."""

from __future__ import annotations

import json
from pathlib import Path

from mb import migration_lint


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_migration_lint_reports_shape_and_frontmatter_drift_privately(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "reference" / "core" / "offer.md", "# Private offer body\n")
    _write(
        tmp_path / "campaigns" / "spring" / "campaign.md",
        "---\nslug: spring\nstatus: active\n---\n# Private campaign body\n",
    )
    _write(tmp_path / "ops" / "handoff.md", "# Private ops body\n")
    _write(tmp_path / "outputs" / "old-vsl.md", "# Private generated work\n")
    _write(
        tmp_path / "pushes" / "spring" / "push.md",
        (
            "---\n"
            "type: push\n"
            "slug: spring\n"
            "kind: launch\n"
            "status: active\n"
            "health: unknown\n"
            "---\n"
            "# Private push body\n"
        ),
    )
    _write(
        tmp_path / "pushes" / "2026-05-08-launch" / "run.md",
        "---\ntype: playbook\n---\n# Private playbook body\n",
    )
    _write(
        tmp_path / "bets" / "2026-05-08-legacy.md",
        ("---\nstatus: open\nlinked_campaigns: []\n---\n# Private bet body\n"),
    )

    report = migration_lint.run(tmp_path)

    codes = {finding["code"] for finding in report["findings"]}
    assert "legacy-reference-active-content" in codes
    assert "legacy-campaigns-active-content" in codes
    assert "legacy-top-level-ops" in codes
    assert "legacy-top-level-outputs" in codes
    assert "push-record-wrong-shape" in codes
    assert "playbook-run-wrong-path" in codes
    assert "bet-legacy-campaign-links-only" in codes
    assert all(finding["content_included"] is False for finding in report["findings"])
    assert "Private" not in json.dumps(report)
    outputs = next(
        finding for finding in report["findings"] if finding["code"] == "legacy-top-level-outputs"
    )
    assert "documents/archive/<name>/" in outputs["message"]
    assert "do not bulk-promote" in outputs["message"]


def test_migration_lint_reports_stale_generated_guidance_without_file_body(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "CLAUDE.md",
        (
            "# Business\n\n"
            "- `reference/` - active business memory\n"
            "- `campaigns/` - active coordinated work\n\n"
            "Private customer detail.\n"
        ),
    )

    report = migration_lint.run(tmp_path)

    codes = {finding["code"] for finding in report["findings"]}
    assert "stale-claude-reference-guidance" in codes
    assert "stale-claude-campaigns-guidance" in codes
    assert "Private customer detail" not in json.dumps(report)


def test_migration_lint_does_not_flag_negated_reference_write_guidance(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "CLAUDE.md",
        (
            "# Business\n\n"
            "Do not write to reference/core; it is a compatibility path. "
            "New truth belongs in core/.\n"
        ),
    )

    report = migration_lint.run(tmp_path)

    codes = {finding["code"] for finding in report["findings"]}
    assert "stale-claude-reference-core-guidance" not in codes


def test_migration_lint_reports_stale_claude_settings_engine_path(
    tmp_path: Path,
) -> None:
    stale_engine = tmp_path / "mb-vip"
    _write(
        tmp_path / ".claude" / "settings.local.json",
        json.dumps({"permissions": {"additionalDirectories": [str(stale_engine)]}}),
    )

    report = migration_lint.run(tmp_path)

    codes = {finding["code"] for finding in report["findings"]}
    assert "stale-claude-settings-engine-path" in codes


def test_migration_lint_reuses_push_frontmatter_reads(tmp_path: Path, monkeypatch) -> None:
    wrong_push = tmp_path / "pushes" / "spring" / "push.md"
    wrong_playbook = tmp_path / "pushes" / "2026-05-08-launch" / "run.md"
    _write(
        wrong_push,
        "---\ntype: push\nslug: spring\n---\n# Private push body\n",
    )
    _write(
        wrong_playbook,
        "---\ntype: playbook\n---\n# Private playbook body\n",
    )
    original = migration_lint._read_frontmatter
    calls: dict[Path, int] = {}

    def counted(path: Path) -> dict[str, object]:
        calls[path] = calls.get(path, 0) + 1
        return original(path)

    monkeypatch.setattr(migration_lint, "_read_frontmatter", counted)

    report = migration_lint.run(tmp_path)

    codes = {finding["code"] for finding in report["findings"]}
    assert "push-record-wrong-shape" in codes
    assert "playbook-run-wrong-path" in codes
    assert calls[wrong_push] == 1
    assert calls[wrong_playbook] == 1
