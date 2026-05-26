"""Shared workflow source validation and renderer drift tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import codex as codex_mod
from mb.cli import app
from mb.workflows import (
    codex_shell_policy_errors,
    load_workflow,
    public_private_boundary_errors,
    render_claude_shell,
    render_codex_shell,
    shell_drift_errors,
    validate_workflow,
)

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / "workflows" / "mb-start-money-path" / "workflow.md"
START_STATUS_WORKFLOW = REPO_ROOT / "workflows" / "mb-start-status" / "workflow.md"
SETUP_WORKFLOW = REPO_ROOT / "workflows" / "mb-setup" / "workflow.md"
MAINTENANCE_REPAIR_WORKFLOW = REPO_ROOT / "workflows" / "mb-maintenance-repair" / "workflow.md"
THINK_WORKFLOW = REPO_ROOT / "workflows" / "mb-think" / "workflow.md"
END_WORKFLOW = REPO_ROOT / "workflows" / "mb-end" / "workflow.md"
SHIPPED_END_SKILL = REPO_ROOT / ".claude" / "skills" / "mb-end" / "SKILL.md"
FIXTURES = REPO_ROOT / "mb" / "tests" / "fixtures" / "workflows"
AGENTS_TEMPLATE = REPO_ROOT / "mb" / "mb" / "_data" / "templates" / "AGENTS.md.tmpl"
WORKFLOW_PATHS = [
    WORKFLOW,
    START_STATUS_WORKFLOW,
    SETUP_WORKFLOW,
    MAINTENANCE_REPAIR_WORKFLOW,
    THINK_WORKFLOW,
    END_WORKFLOW,
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


def test_generated_daily_claude_and_codex_snapshots_match_fixtures() -> None:
    for path in (START_STATUS_WORKFLOW, SETUP_WORKFLOW, MAINTENANCE_REPAIR_WORKFLOW):
        workflow = load_workflow(path)
        fixture_stem = path.parent.name

        assert render_claude_shell(workflow) == (FIXTURES / f"{fixture_stem}.claude.md").read_text(
            encoding="utf-8"
        )
        assert render_codex_shell(workflow) == (FIXTURES / f"{fixture_stem}.codex.md").read_text(
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


def test_generated_end_claude_and_codex_snapshots_match_fixtures() -> None:
    workflow = load_workflow(END_WORKFLOW)

    assert render_claude_shell(workflow) == (FIXTURES / "mb-end.claude.md").read_text(
        encoding="utf-8"
    )
    assert render_codex_shell(workflow) == (FIXTURES / "mb-end.codex.md").read_text(
        encoding="utf-8"
    )


def test_shipped_claude_end_skill_preserves_shared_workflow_contract() -> None:
    workflow = load_workflow(END_WORKFLOW)
    skill_text = SHIPPED_END_SKILL.read_text(encoding="utf-8")

    assert shell_drift_errors(workflow, skill_text) == []
    assert "workflows/mb-end/workflow.md" in skill_text


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


def test_codex_contract_markers_match_end_workflow_source() -> None:
    workflow = load_workflow(END_WORKFLOW)

    assert codex_mod.CODEX_END_SOURCE_WORKFLOW == "workflows/mb-end/workflow.md"
    assert tuple(workflow.required_mb_commands) == codex_mod.CODEX_END_REQUIRED_MB_COMMANDS
    assert tuple(workflow.json_facts) == codex_mod.CODEX_END_REQUIRED_JSON_FACTS
    assert tuple(workflow.approval_gates) == codex_mod.CODEX_END_APPROVAL_GATES
    assert (
        tuple(workflow.public_private_boundaries) == codex_mod.CODEX_END_PUBLIC_PRIVATE_BOUNDARIES
    )


def test_codex_command_surface_and_inventory_render() -> None:
    commands = codex_mod.render_codex_slash_commands()
    inventory = codex_mod.render_workflow_inventory_md()
    manifest = codex_mod.render_codex_plugin_manifest()
    marketplace = codex_mod.render_codex_marketplace_json()
    inventory_json = codex_mod.workflow_inventory(runtime="codex")

    assert set(commands) == set(codex_mod.CODEX_SLASH_COMMAND_RELATIVE_PATHS)
    assert (
        "description: Start Main Branch."
        in commands[f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/mb-start.md"]
    )
    assert (
        "mb status --json --peek"
        in commands[f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/mb-start.md"]
    )
    assert (
        "codex_runtime_mb_mismatch"
        in commands[f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/mb-start.md"]
    )
    assert (
        "Ask before durable writes"
        in commands[f"{codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/mb-start.md"]
    )
    assert "main-branch-owner-loop" not in "\n".join(commands.values())
    assert "Main Branch" in manifest
    assert '"skills": "./skills/"' not in manifest
    assert "main-branch-owner-loop" not in manifest
    assert '"path": "./.agents/plugins/main-branch"' in marketplace
    assert "global Main Branch skill bundle is installed" in inventory
    assert "codex plugin list --marketplace main-branch" not in inventory
    assert ".claude/skills/mb-start/SKILL.md" in inventory
    assert ".claude/skills/mb-skill-review/SKILL.md" in inventory
    assert "Source-of-truth meanings" in inventory
    assert (
        "shared workflow source -> Claude Code shell -> Codex shell -> inventory/tests" in inventory
    )
    assert "temporary_source_skill_mirror" in inventory
    assert "plugin" not in inventory_json
    assert inventory_json["global_skill"]["install_hint"] == "mb doctor repair --apply --only codex"
    assert "mb-start" in inventory_json["global_skill"]["routes"]
    assert "`main-branch mb-start`" in inventory
    assert "pending_shared_source_migration" in inventory
    assert "intentionally_unsupported" in inventory
    assert "Copied Claude" not in "\n".join(commands.values())


def test_codex_global_plugin_source_generates_slash_commands_and_removes_visible_skill(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    old_skill = (
        codex_mod.global_plugin_source_root()
        / codex_mod.CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH
        / "skills"
        / "main-branch-owner-loop"
        / "SKILL.md"
    )
    old_skill.parent.mkdir(parents=True, exist_ok=True)
    old_skill.write_text("# stale\n", encoding="utf-8")

    result = codex_mod.write_global_plugin_source()

    assert result["ok"] is True
    assert not old_skill.exists()
    assert codex_mod.CODEX_PLUGIN_MANIFEST_RELATIVE_PATH in result["relative_paths"]
    assert codex_mod.CODEX_PLUGIN_SKILL_RELATIVE_PATH not in result["relative_paths"]
    for relative in codex_mod.CODEX_SLASH_COMMAND_RELATIVE_PATHS:
        path = codex_mod.global_plugin_source_root() / relative
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "deterministic `mb` facts" in text
        assert "Ask before durable writes" in text
    assert "description: Start Main Branch." in (
        codex_mod.global_plugin_source_root()
        / codex_mod.CODEX_PLUGIN_COMMANDS_RELATIVE_PATH
        / "mb-start.md"
    ).read_text(encoding="utf-8")


def test_codex_plugin_status_marks_missing_or_stale_commands_not_ready(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    codex_mod.write_global_plugin_source()
    command = (
        codex_mod.global_plugin_source_root() / codex_mod.CODEX_SLASH_COMMAND_RELATIVE_PATHS[0]
    )
    command.write_text("# stale\n", encoding="utf-8")

    status = codex_mod.plugin_status(tmp_path / "business")

    assert status["ok"] is False
    assert status["current"] is False
    assert codex_mod.CODEX_SLASH_COMMAND_RELATIVE_PATHS[0] in status["stale"]
    assert status["command_files_current"] is False
    assert status["slash_commands_generated"] is False
    assert status["slash_commands_ready"] is False
    assert status["repair"] == codex_mod.CODEX_REPAIR_TEXT


def test_codex_global_skill_upgrade_removes_retired_playbook_skills(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "codex-skills"))
    codex_mod.write_global_skill_source()
    for name in codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES:
        assert name not in codex_mod.CODEX_GLOBAL_SKILL_NAMES
        assert name not in codex_mod.CODEX_GLOBAL_SKILL_DESCRIPTIONS
        assert name not in codex_mod.CODEX_GLOBAL_SKILL_FACTS
        assert name not in codex_mod.CODEX_GLOBAL_SKILL_SUPPORT
        stale_skill = codex_mod.global_skill_source_root() / name / "SKILL.md"
        stale_skill.parent.mkdir(parents=True, exist_ok=True)
        stale_skill.write_text(
            "\n".join(codex_mod.CODEX_RETIRED_GLOBAL_SKILL_MARKERS[name]) + "\n",
            encoding="utf-8",
        )

    before = codex_mod.global_skill_status(tmp_path / "business")

    assert before["ok"] is False
    for name in codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES:
        assert name in before["stale"]

    result = codex_mod.write_global_skill_source()

    assert result["ok"] is True
    assert result["status"]["ok"] is True
    for name in codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES:
        assert not (codex_mod.global_skill_source_root() / name).exists()
        assert str(codex_mod.global_skill_source_root() / name) in result["changed_paths"]


def test_codex_global_skill_upgrade_preserves_manual_same_name_playbook_skill(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "codex-skills"))
    codex_mod.write_global_skill_source()
    manual_skills = []
    for name in ("ship-bet", "weekly-review"):
        manual_skill = codex_mod.global_skill_source_root() / name / "SKILL.md"
        manual_skill.parent.mkdir(parents=True, exist_ok=True)
        manual_skill.write_text(
            f"# {name}\n\nPersonal {name} skill, not generated by Main Branch.\n",
            encoding="utf-8",
        )
        manual_skills.append(manual_skill)

    before = codex_mod.global_skill_status(tmp_path / "business")
    result = codex_mod.write_global_skill_source()

    for manual_skill in manual_skills:
        assert manual_skill.parent.name not in before["stale"]
        assert manual_skill.exists()
        assert "not generated by Main Branch" in manual_skill.read_text(encoding="utf-8")
        assert str(manual_skill.parent) not in result["changed_paths"]


def test_removed_provisional_playbooks_are_cleanup_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MAINBRANCH_CODEX_PLUGIN_ROOT", str(tmp_path / "codex-global"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(tmp_path / "codex-skills"))
    removed = {"ship-bet", "weekly-review"}
    inventory = codex_mod.workflow_inventory(runtime="codex")
    inventory_ids = {item["id"] for item in inventory["items"]}

    assert removed.isdisjoint(codex_mod.CLAUDE_PLAYBOOK_SOURCE_NAMES)
    assert {"ship-bet-playbook", "weekly-review-playbook"}.isdisjoint(inventory_ids)
    assert removed.isdisjoint(inventory["global_skill"]["routes"])
    assert removed.isdisjoint(codex_mod.CODEX_GLOBAL_SKILL_NAMES)
    assert removed.isdisjoint(codex_mod.CODEX_GLOBAL_SKILL_DESCRIPTIONS)
    assert removed.isdisjoint(codex_mod.CODEX_GLOBAL_SKILL_FACTS)
    assert removed.isdisjoint(codex_mod.CODEX_GLOBAL_SKILL_SUPPORT)
    assert removed.issubset(codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES)
    assert removed.issubset(codex_mod.CODEX_RETIRED_GLOBAL_SKILL_MARKERS)

    status = codex_mod.global_skill_status(tmp_path / "business")
    assert removed.isdisjoint(status["required_skills"])


def test_codex_workflow_inventory_command_lists_supported_and_pending_surfaces() -> None:
    result = runner.invoke(app, ["workflow", "list", "--runtime", "codex", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["support_level"] == "supported_global_main_branch_skill"
    statuses = set(data["statuses"])
    assert {
        "supported",
        "read_only_planning",
        "pending_shared_source_migration",
        "blocked_by_provider_gates",
        "internal_composable",
        "generated_shell_pending",
        "intentionally_unsupported",
    }.issubset(statuses)
    by_id = {item["id"]: item for item in data["items"]}
    assert by_id["think-codify"]["codex_status"] == "supported"
    assert by_id["think-codify"]["source_status"] == "shared_workflow_source"
    assert by_id["think-codify"]["source_of_truth"]["status"] == "shared_workflow_source"
    assert (
        by_id["think-codify"]["source_of_truth"]["shared_source"]
        == "workflows/mb-think/workflow.md"
    )
    assert {
        "intent",
        "required_mb_commands",
        "required_json_facts",
        "approval_gates",
        "read_boundaries",
        "write_boundaries",
        "core_flow",
        "public_private_boundaries",
    }.issubset(set(by_id["think-codify"]["source_of_truth"]["contract_checks"]))
    assert by_id["think-codify"]["codex_entrypoints"] == ["main-branch mb-think"]
    assert by_id["daily-start-status"]["codex_entrypoints"] == [
        "main-branch mb-start",
        "main-branch mb-status",
    ]
    assert by_id["daily-start-status"]["source_status"] == "shared_workflow_source"
    assert (
        by_id["daily-start-status"]["source_of_truth"]["shared_source"]
        == "workflows/mb-start-status/workflow.md"
    )
    assert by_id["daily-setup"]["source_status"] == "shared_workflow_source"
    assert (
        by_id["daily-setup"]["source_of_truth"]["shared_source"] == "workflows/mb-setup/workflow.md"
    )
    assert by_id["daily-maintenance-repair"]["source_status"] == "shared_workflow_source"
    assert (
        by_id["daily-maintenance-repair"]["source_of_truth"]["shared_source"]
        == "workflows/mb-maintenance-repair/workflow.md"
    )
    assert by_id["daily-maintenance-repair"]["codex_entrypoints"] == [
        "main-branch mb-update",
        "main-branch mb-doctor",
    ]
    assert by_id["end-checkpoint-save"]["source_status"] == "shared_workflow_source"
    assert (
        by_id["end-checkpoint-save"]["source_of_truth"]["shared_source"]
        == "workflows/mb-end/workflow.md"
    )
    assert (
        "save_state_language" in by_id["end-checkpoint-save"]["source_of_truth"]["contract_checks"]
    )
    assert by_id["daily-start-status"]["claude_skill_sources"] == [
        ".claude/skills/mb-start/SKILL.md",
        ".claude/skills/mb-status/SKILL.md",
    ]
    assert by_id["daily-setup"]["claude_skill_sources"] == [
        ".claude/skills/mb-setup/SKILL.md",
    ]
    assert by_id["daily-maintenance-repair"]["claude_skill_sources"] == [
        ".claude/skills/mb-update/SKILL.md",
    ]
    assert by_id["ads"]["codex_status"] == "read_only_planning"
    assert by_id["ads"]["source_status"] == "blocked_by_provider_gates"
    assert by_id["ads"]["source_of_truth"]["next_required_issue"] == "#750"
    assert by_id["ads"]["source_of_truth"]["follow_up_issue"].endswith("/issues/750")
    assert by_id["bets"]["source_of_truth"]["next_required_issue"] == "#751"
    assert by_id["organic-content"]["source_of_truth"]["next_required_issue"] == "#752"
    assert by_id["site"]["source_of_truth"]["next_required_issue"] == "#749"
    assert by_id["google-ads-search-launch-playbook"]["surface_type"] == "playbook"
    assert by_id["google-ads-search-launch-playbook"]["playbook_status"] == "draft_manual"
    assert by_id["google-ads-search-launch-playbook"]["codex_entrypoints"] == []
    assert by_id["google-ads-search-launch-playbook"]["codex_status"] == (
        "blocked_by_provider_gates"
    )
    assert by_id["wiki"]["codex_status"] == "intentionally_unsupported"
    assert by_id["wiki"]["source_status"] == "intentionally_unsupported"
    assert data["architecture"] == {
        "canonical_flow": (
            "shared workflow source -> Claude Code shell -> Codex shell -> inventory/tests"
        ),
        "shared_source_root": "workflows/<workflow>/workflow.md",
        "runtime_shells": {
            "claude_code": ".claude/skills/<name>/SKILL.md",
            "codex_cli": "global main-branch skills plus AGENTS.md guidance",
        },
        "status_field": "items[].source_of_truth.status",
    }
    assert {
        "shared_workflow_source",
        "temporary_source_skill_mirror",
        "pending_shared_source_migration",
        "blocked_by_provider_gates",
        "internal_composable",
        "intentionally_unsupported",
    }.issubset(set(data["source_statuses"]))
    assert {
        "shared_source",
        "claude_skill",
        "playbook",
        "codex_global_skill",
        "read_only_planning",
        "pending_shared_source_migration",
        "blocked_by_provider_gates",
        "internal_composable",
    }.issubset(set(data["surface_kinds"]))
    assert {"shared_source", "claude_skill", "codex_global_skill"}.issubset(
        set(by_id["think-codify"]["surface_kinds"])
    )
    assert {
        "codex_global_skill",
        "read_only_planning",
        "blocked_by_provider_gates",
    }.issubset(set(by_id["ads"]["surface_kinds"]))
    assert {"playbook", "blocked_by_provider_gates"}.issubset(
        set(by_id["google-ads-search-launch-playbook"]["surface_kinds"])
    )
    assert "plugin" not in data
    assert data["global_skill"]["path"] == codex_mod.CODEX_GLOBAL_SKILL_RELATIVE_PATH
    assert "mb-start" in data["global_skill"]["routes"]
    assert "google-ads-search-launch" not in data["global_skill"]["routes"]
    assert "ship-bet" not in data["global_skill"]["routes"]
    assert "weekly-review" not in data["global_skill"]["routes"]


def test_codex_workflow_inventory_human_output_shows_status_labels() -> None:
    result = runner.invoke(app, ["workflow", "list", "--runtime", "codex"])

    assert result.exit_code == 0
    assert "status: supported" in result.stdout
    assert "status: read_only_planning" in result.stdout
    assert "status: blocked_by_provider_gates" in result.stdout
    assert "Google Ads search launch playbook" in result.stdout
    assert "Ship bet playbook" not in result.stdout
    assert "Weekly review playbook" not in result.stdout


def test_codex_workflow_inventory_source_status_contract_is_explicit() -> None:
    inventory = codex_mod.workflow_inventory(runtime="codex")
    items = inventory["items"]

    for item in items:
        source = item["source_of_truth"]
        assert source["status"] == item["source_status"]
        assert source["description"]
        assert source["surface_type"] in {"workflow", "skill", "playbook"}
        assert isinstance(source["claude_sources"], list)
        assert isinstance(source["codex_sources"], list)
        assert isinstance(source["contract_checks"], list)
        assert isinstance(source["surface_kinds"], list)
        if item["source_status"] in {
            "pending_shared_source_migration",
            "blocked_by_provider_gates",
        }:
            assert source["status_reason"]
            assert source["next_required_issue"]
            assert source["follow_up_issue"]
        if item["codex_status"] == "supported":
            assert item["source_status"] in {
                "shared_workflow_source",
                "temporary_source_skill_mirror",
            }
            assert source["contract_checks"]
        if item["source_status"] == "shared_workflow_source":
            assert source["shared_source"] in {
                path.relative_to(REPO_ROOT).as_posix() for path in WORKFLOW_PATHS
            }
            assert "required_mb_commands" in source["contract_checks"]
            assert "approval_gates" in source["contract_checks"]
            assert "write_boundaries" in source["contract_checks"]
            assert "core_flow" in source["contract_checks"]
        else:
            assert not source["shared_source"]


def test_codex_workflow_inventory_static_metadata_is_complete() -> None:
    assert set(codex_mod.CODEX_GLOBAL_SKILL_DESCRIPTIONS) == set(codex_mod.CODEX_GLOBAL_SKILL_NAMES)
    assert set(codex_mod.CODEX_GLOBAL_SKILL_FACTS) == set(codex_mod.CODEX_GLOBAL_SKILL_NAMES)
    assert set(codex_mod.CODEX_GLOBAL_SKILL_SUPPORT) == set(codex_mod.CODEX_GLOBAL_SKILL_NAMES)
    assert set(codex_mod.CODEX_RETIRED_GLOBAL_SKILL_MARKERS) == set(
        codex_mod.CODEX_RETIRED_GLOBAL_SKILL_NAMES
    )

    for item in codex_mod.CODEX_WORKFLOW_INVENTORY:
        codex_status = item["codex_status"]
        source_status = item["source_status"]
        assert codex_status in codex_mod.CODEX_WORKFLOW_STATUS_VOCABULARY
        assert source_status in codex_mod.CODEX_SOURCE_STATUS_VOCABULARY
        assert source_status in codex_mod.CODEX_SOURCE_STATUS_DESCRIPTIONS

        for entrypoint in item.get("codex_entrypoints", ()):
            route_name = str(entrypoint).split()[-1]
            assert route_name in codex_mod.CODEX_GLOBAL_SKILL_NAMES
            assert route_name in codex_mod.CODEX_GLOBAL_SKILL_SUPPORT

        if source_status in {
            "pending_shared_source_migration",
            "blocked_by_provider_gates",
            "internal_composable",
        }:
            assert item.get("status_reason")
            assert item.get("next_required_issue")
            assert item.get("follow_up_issue")


def test_codex_global_skills_hide_legacy_plugin_and_fake_slash_claims() -> None:
    texts = [
        codex_mod.render_codex_global_skill_md(name) for name in codex_mod.CODEX_GLOBAL_SKILL_NAMES
    ]
    combined = "\n".join(texts)

    assert "main-branch-owner-loop" not in combined
    assert "plugin readiness" not in combined.lower()
    assert "slash" not in combined.lower()
    assert "slash commands are available" not in combined.lower()
    assert "slash-command parity" not in combined.lower()
    assert "Claude Code command surfaces are available" in combined


def test_codex_shared_global_skills_are_rendered_from_workflow_sources() -> None:
    for path, name in (
        (START_STATUS_WORKFLOW, "mb-start"),
        (START_STATUS_WORKFLOW, "mb-status"),
        (SETUP_WORKFLOW, "mb-setup"),
        (MAINTENANCE_REPAIR_WORKFLOW, "mb-update"),
        (MAINTENANCE_REPAIR_WORKFLOW, "mb-doctor"),
        (THINK_WORKFLOW, "mb-think"),
        (END_WORKFLOW, "mb-end"),
    ):
        workflow = load_workflow(path)
        text = codex_mod.render_codex_global_skill_md(name)

        assert "Follow the generated Codex shell below" in text
        assert f"Source workflow: `{path.relative_to(REPO_ROOT).as_posix()}`" in text
        assert render_codex_shell(workflow).strip() in text
        assert shell_drift_errors(workflow, text) == []
        assert codex_shell_policy_errors(workflow, text) == []
        assert "main-branch-owner-loop" not in text
        assert "plugin" not in text.lower()
        assert "slash" not in text.lower()


def test_codex_workflow_inventory_accounts_for_every_bundled_claude_skill() -> None:
    result = runner.invoke(app, ["workflow", "list", "--runtime", "codex", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    expected = {
        str(path.relative_to(REPO_ROOT))
        for path in sorted((REPO_ROOT / ".claude" / "skills").glob("mb-*/SKILL.md"))
    }
    top_level_sources = set(data["claude_skill_sources"])
    item_sources = {
        source for item in data["items"] for source in item.get("claude_skill_sources", [])
    }

    assert top_level_sources == expected
    assert item_sources == expected


def test_codex_workflow_inventory_accounts_for_every_bundled_claude_playbook() -> None:
    result = runner.invoke(app, ["workflow", "list", "--runtime", "codex", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    expected = {
        str(path.relative_to(REPO_ROOT))
        for path in sorted((REPO_ROOT / ".claude" / "playbooks").glob("*/SKILL.md"))
    }
    top_level_sources = set(data["claude_playbook_sources"])
    item_sources = {
        source for item in data["items"] for source in item.get("claude_playbook_sources", [])
    }

    assert top_level_sources == expected
    assert item_sources == expected
    assert {
        f".claude/playbooks/{name}/SKILL.md" for name in codex_mod.CLAUDE_PLAYBOOK_SOURCE_NAMES
    } == expected


def test_codex_workflow_inventory_json_unsupported_runtime_uses_error_envelope() -> None:
    result = runner.invoke(app, ["workflow", "list", "--runtime", "claude", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["result_status"] == "error"
    assert payload["mb_command"] == "mb workflow list"
    assert payload["result_schema"]["name"] == "mainbranch.workflow.inventory.result"
    assert payload["errors"] == [
        {
            "code": "unsupported_runtime",
            "message": "mb workflow list: only --runtime codex is available today",
        }
    ]
    assert result.stderr == ""


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


def test_end_runtime_shells_surface_closeout_save_state_contract() -> None:
    workflow = load_workflow(END_WORKFLOW)

    for shell in (render_claude_shell(workflow), render_codex_shell(workflow)):
        normalized = " ".join(shell.split())
        assert "status scan" in normalized
        assert "checkpoint plan" in normalized
        assert "session summary" in normalized
        assert "final thought" in normalized
        assert "crystallize" in normalized
        assert "approval-gated save" in normalized
        assert "drafted" in normalized
        assert "saved locally" in normalized
        assert "ready to send up" in normalized
        assert "sent for review" in normalized
        assert "landed in main" in normalized
        assert "blocked by unrelated cleanup" in normalized
        assert "warm close" in normalized


def test_end_codex_shell_does_not_claim_slash_command_or_skill_parity() -> None:
    workflow = load_workflow(END_WORKFLOW)
    shell = render_codex_shell(workflow)

    assert codex_shell_policy_errors(workflow, shell) == []
    assert "Run `/mb-end`" not in shell
    assert "Claude Code skills work in Codex" not in shell
    assert "not need to contain `workflows/mb-end/workflow.md`" in shell
    assert "as the Codex shell for natural-language closeout tasks" in shell


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
