"""Shared workflow source validation and renderer drift tests."""

from __future__ import annotations

from pathlib import Path

from mb import codex as codex_mod
from mb.workflows import (
    codex_shell_policy_errors,
    load_workflow,
    public_private_boundary_errors,
    render_claude_shell,
    render_codex_shell,
    shell_drift_errors,
    validate_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / "workflows" / "mb-start-money-path" / "workflow.md"
THINK_WORKFLOW = REPO_ROOT / "workflows" / "mb-think" / "workflow.md"
FIXTURES = REPO_ROOT / "mb" / "tests" / "fixtures" / "workflows"
AGENTS_TEMPLATE = REPO_ROOT / "mb" / "mb" / "_data" / "templates" / "AGENTS.md.tmpl"
WORKFLOW_PATHS = [
    WORKFLOW,
    THINK_WORKFLOW,
]


def test_start_money_path_workflow_source_validates() -> None:
    assert validate_workflow(WORKFLOW) == []


def test_all_workflow_sources_validate() -> None:
    for path in WORKFLOW_PATHS:
        assert validate_workflow(path) == []


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


def test_workflow_validation_flags_missing_required_approval_gate(tmp_path: Path) -> None:
    broken = tmp_path / "workflow.md"
    broken.write_text(
        THINK_WORKFLOW.read_text(encoding="utf-8").replace("  - checkpoint\n", "", 1),
        encoding="utf-8",
    )

    errors = validate_workflow(broken)

    assert any("approval_gates missing minimum gates" in error for error in errors)
    assert any("checkpoint" in error for error in errors)


def test_generated_start_money_path_claude_and_codex_snapshots_match_fixtures() -> None:
    workflow = load_workflow(WORKFLOW)

    assert render_claude_shell(workflow) == (FIXTURES / "mb-start-money-path.claude.md").read_text(
        encoding="utf-8"
    )
    assert render_codex_shell(workflow) == (FIXTURES / "mb-start-money-path.codex.md").read_text(
        encoding="utf-8"
    )


def test_generated_think_claude_and_codex_snapshots_match_fixtures() -> None:
    workflow = load_workflow(THINK_WORKFLOW)

    assert render_claude_shell(workflow) == (FIXTURES / "mb-think.claude.md").read_text(
        encoding="utf-8"
    )
    assert render_codex_shell(workflow) == (FIXTURES / "mb-think.codex.md").read_text(
        encoding="utf-8"
    )


def test_supported_shells_preserve_required_commands_and_json_facts() -> None:
    for path in WORKFLOW_PATHS:
        workflow = load_workflow(path)
        shells = [
            render_claude_shell(workflow),
            render_codex_shell(workflow),
        ]

        for shell in shells:
            assert shell_drift_errors(workflow, shell) == []


def test_codex_agents_think_route_preserves_shared_workflow_contract() -> None:
    workflow = load_workflow(THINK_WORKFLOW)
    text = AGENTS_TEMPLATE.read_text(encoding="utf-8")

    assert "Engine source workflow: `workflows/mb-think/workflow.md`" in text
    assert "does not need to contain that engine source file" in text
    assert "`AGENTS.md` section as the Codex shell" in text
    for command in workflow.required_mb_commands:
        assert f"- `{command}`" in text
    for fact in workflow.json_facts:
        assert f"- `{fact}`" in text
    for gate in workflow.approval_gates:
        assert f"`{gate}`" in text
    for boundary in workflow.public_private_boundaries:
        assert f"`{boundary}`" in text


def test_codex_contract_markers_match_think_workflow_source() -> None:
    workflow = load_workflow(THINK_WORKFLOW)

    assert codex_mod.CODEX_THINK_SOURCE_WORKFLOW == "workflows/mb-think/workflow.md"
    assert tuple(workflow.required_mb_commands) == codex_mod.CODEX_THINK_REQUIRED_MB_COMMANDS
    assert tuple(workflow.json_facts) == codex_mod.CODEX_THINK_REQUIRED_JSON_FACTS
    assert tuple(workflow.approval_gates) == codex_mod.CODEX_THINK_APPROVAL_GATES
    assert (
        tuple(workflow.public_private_boundaries) == codex_mod.CODEX_THINK_PUBLIC_PRIVATE_BOUNDARIES
    )


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


def test_think_drift_detection_flags_missing_required_workflow_rules() -> None:
    workflow = load_workflow(THINK_WORKFLOW)
    shell = render_codex_shell(workflow)
    drifted = shell.replace("Research Depth Recommendation", "research note")
    drifted = drifted.replace("Research depth recommendation", "research note")
    drifted = drifted.replace("parallel research files", "source notes")
    drifted = drifted.replace("Public/private boundaries", "boundaries")
    drifted = drifted.replace("public/private handling", "handling")

    errors = shell_drift_errors(workflow, drifted)

    assert "shell missing required workflow rule: research-depth ladder" in errors
    assert "shell missing required workflow rule: parallel research file pattern" in errors
    assert "shell missing required workflow rule: public/private boundary" in errors


def test_think_runtime_shells_surface_stale_source_cleanup_route() -> None:
    workflow = load_workflow(THINK_WORKFLOW)

    for shell in (render_claude_shell(workflow), render_codex_shell(workflow)):
        assert "stale source, claim, proof, or angle cleanup" in shell
        assert "find downstream usage" in shell
        assert "record and codify the decision" in shell


def test_think_codex_shell_does_not_claim_slash_command_or_skill_parity() -> None:
    workflow = load_workflow(THINK_WORKFLOW)
    shell = render_codex_shell(workflow)

    assert codex_shell_policy_errors(workflow, shell) == []
    assert "Run `/mb-think`" not in shell
    assert "Claude Code skills work in Codex" not in shell
    assert "not need to contain `workflows/mb-think/workflow.md`" in shell
    assert "as the Codex shell for natural-language thinking tasks" in shell


def test_think_codex_policy_flags_forbidden_support_language() -> None:
    workflow = load_workflow(THINK_WORKFLOW)
    shell = render_codex_shell(workflow) + "\nRun `/mb-think`.\nClaude Code skills work in Codex.\n"

    errors = codex_shell_policy_errors(workflow, shell)

    assert "Codex shell contains forbidden support phrase: Run `/mb-think`" in errors
    assert (
        "Codex shell contains forbidden support phrase: Claude Code skills work in Codex" in errors
    )


def test_think_runtime_shells_stay_thin_and_currently_named() -> None:
    workflow = load_workflow(THINK_WORKFLOW)
    shells = [
        render_claude_shell(workflow),
        render_codex_shell(workflow),
    ]

    for shell in shells:
        assert len(shell.splitlines()) < 90
        assert "workflow corpus" not in shell.lower()
        assert "shared workflow source" not in shell.lower()


def test_workflow_source_and_snapshots_stay_public_safe() -> None:
    texts = [path.read_text(encoding="utf-8") for path in WORKFLOW_PATHS] + [
        fixture.read_text(encoding="utf-8") for fixture in sorted(FIXTURES.glob("*.md"))
    ]

    errors = [error for text in texts for error in public_private_boundary_errors(text)]

    assert errors == []
