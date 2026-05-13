"""Shared workflow source validation and renderer drift tests."""

from __future__ import annotations

from pathlib import Path

from mb.workflows import (
    load_workflow,
    public_private_boundary_errors,
    render_claude_shell,
    render_codex_shell,
    shell_drift_errors,
    validate_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / "workflows" / "mb-start-money-path" / "workflow.md"
FIXTURES = REPO_ROOT / "mb" / "tests" / "fixtures" / "workflows"


def test_start_money_path_workflow_source_validates() -> None:
    assert validate_workflow(WORKFLOW) == []


def test_workflow_validation_flags_missing_required_section(tmp_path: Path) -> None:
    broken = tmp_path / "workflow.md"
    broken.write_text(
        WORKFLOW.read_text(encoding="utf-8").replace("## Approval Gates", "## Approval Gatez"),
        encoding="utf-8",
    )

    errors = validate_workflow(broken)

    assert "missing workflow section: Approval Gates" in errors


def test_workflow_validation_flags_missing_required_json_fact(tmp_path: Path) -> None:
    broken = tmp_path / "workflow.md"
    broken.write_text(
        WORKFLOW.read_text(encoding="utf-8").replace("  - money_path.objects.proof.quality\n", ""),
        encoding="utf-8",
    )

    errors = validate_workflow(broken)

    assert any("json_facts missing minimum paths" in error for error in errors)
    assert any("money_path.objects.proof.quality" in error for error in errors)


def test_generated_claude_and_codex_snapshots_match_fixtures() -> None:
    workflow = load_workflow(WORKFLOW)

    assert render_claude_shell(workflow) == (FIXTURES / "mb-start-money-path.claude.md").read_text(
        encoding="utf-8"
    )
    assert render_codex_shell(workflow) == (FIXTURES / "mb-start-money-path.codex.md").read_text(
        encoding="utf-8"
    )


def test_supported_shells_preserve_required_commands_and_json_facts() -> None:
    workflow = load_workflow(WORKFLOW)
    shells = [
        render_claude_shell(workflow),
        render_codex_shell(workflow),
    ]

    for shell in shells:
        assert shell_drift_errors(workflow, shell) == []


def test_drift_detection_flags_omitted_required_command_or_fact() -> None:
    workflow = load_workflow(WORKFLOW)
    shell = render_codex_shell(workflow)
    drifted = shell.replace("mb status --json --peek", "mb status")
    drifted = drifted.replace("money_path.objects.proof.quality", "proof_quality")

    errors = shell_drift_errors(workflow, drifted)

    assert "shell missing required mb command: mb status --json --peek" in errors
    assert "shell missing required JSON fact path: money_path.objects.proof.quality" in errors


def test_drift_detection_requires_exact_bulleted_fact_paths() -> None:
    workflow = load_workflow(WORKFLOW)
    shell = render_codex_shell(workflow)
    drifted = shell.replace("- `money_path`\n", "")
    drifted = drifted.replace("- `ranked_actions`\n", "")

    errors = shell_drift_errors(workflow, drifted)

    assert "shell missing required JSON fact path: money_path" in errors
    assert "shell missing required JSON fact path: ranked_actions" in errors


def test_workflow_source_and_snapshots_stay_public_safe() -> None:
    texts = [
        WORKFLOW.read_text(encoding="utf-8"),
        (FIXTURES / "mb-start-money-path.claude.md").read_text(encoding="utf-8"),
        (FIXTURES / "mb-start-money-path.codex.md").read_text(encoding="utf-8"),
    ]

    errors = [error for text in texts for error in public_private_boundary_errors(text)]

    assert errors == []
