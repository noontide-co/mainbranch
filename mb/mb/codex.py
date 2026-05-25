"""Codex global-skill helpers.

Codex support starts with repo instructions, global Main Branch skills, and
deterministic ``mb`` facts. This module intentionally does not invoke Codex or
manage model conversation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

from mb import __version__
from mb import engine as engine_mod
from mb.workflows import WorkflowSource, load_workflow, render_codex_shell

AGENTS_TEMPLATE = "AGENTS.md.tmpl"
AGENTS_RELATIVE_PATH = "AGENTS.md"
CODEX_GUIDANCE_SCHEMA = 1
CODEX_GUIDANCE_MIN_MB = "0.3.36"
CODEX_SKILL_DIR_RELATIVE_PATH = ".agents/skills/main-branch-owner-loop"
CODEX_SKILL_RELATIVE_PATH = f"{CODEX_SKILL_DIR_RELATIVE_PATH}/SKILL.md"
CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH = AGENTS_RELATIVE_PATH
CODEX_GLOBAL_SKILL_NAME = "main-branch"
CODEX_LEGACY_GLOBAL_SKILL_NAME = "main-branch-owner-loop"
CODEX_GLOBAL_SKILL_RELATIVE_PATH = f"{CODEX_GLOBAL_SKILL_NAME}/SKILL.md"
CODEX_MARKETPLACE_RELATIVE_PATH = ".agents/plugins/marketplace.json"
CODEX_MARKETPLACE_NAME = "main-branch"
CODEX_LEGACY_PLUGIN_NAME = "main-branch-owner-loop"
CODEX_PLUGIN_NAME = "main-branch"
CODEX_PLUGIN_SELECTOR = f"{CODEX_PLUGIN_NAME}@{CODEX_MARKETPLACE_NAME}"
CODEX_LEGACY_PLUGIN_SELECTOR = f"{CODEX_LEGACY_PLUGIN_NAME}@{CODEX_MARKETPLACE_NAME}"
CODEX_PLUGIN_INSTALL_COMMAND = f"codex plugin add {CODEX_PLUGIN_SELECTOR}"
CODEX_PLUGIN_DIR_RELATIVE_PATH = f".agents/plugins/{CODEX_PLUGIN_NAME}"
CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH = f".agents/plugins/{CODEX_LEGACY_PLUGIN_NAME}"
CODEX_PLUGIN_COMMANDS_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/commands"
CODEX_PLUGIN_LEGACY_COMMANDS_RELATIVE_PATH = f"{CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH}/commands"
CODEX_PLUGIN_MANIFEST_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/.codex-plugin/plugin.json"
CODEX_PLUGIN_SKILL_RELATIVE_PATH = (
    f"{CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH}/skills/main-branch-owner-loop/SKILL.md"
)
CODEX_SUPPORT_LEVEL = "supported_global_main_branch_skill"
CODEX_REPAIR_COMMAND = "mb doctor repair --apply --only codex"
CODEX_REPAIR_TEXT = (
    "Run `mb doctor repair --plan --only codex`, review, then "
    "`mb doctor repair --apply --only codex`."
)
CODEX_RUNTIME_MISMATCH_STOP_TEXT = (
    "After `mb status --json --peek` or `mb start --json`, stop if "
    "`runtime.codex_cli.status` is `runtime_mismatch` or any `drift.items[].id` "
    "equals `codex_runtime_mb_mismatch`. Treat that as a runtime `mb` mismatch: "
    "tell the operator to fix the runtime/login-shell PATH and rerun read-only "
    "checks before Main Branch advice, repair planning, or writes."
)
REQUIRED_FACT_COMMANDS = (
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
)
CODEX_SLASH_COMMAND_NAMES = (
    "mb-start",
    "mb-status",
    "mb-setup",
    "mb-update",
    "mb-doctor",
    "mb-think",
    "mb-end",
    "mb-help",
)
CLAUDE_SKILL_SOURCE_NAMES = (
    "mb-start",
    "mb-status",
    "mb-setup",
    "mb-update",
    "mb-think",
    "mb-end",
    "mb-help",
    "mb-bet",
    "mb-ads",
    "mb-organic",
    "mb-site",
    "mb-wiki",
    "mb-skill-concept",
    "mb-skill-brief-draft",
    "mb-skill-review",
)
CLAUDE_PLAYBOOK_SOURCE_NAMES = (
    "google-ads-search-launch",
    "ship-bet",
    "weekly-review",
)
CODEX_GLOBAL_SKILL_NAMES = (
    CODEX_GLOBAL_SKILL_NAME,
    "mb-doctor",
    "mb-start",
    "mb-status",
    "mb-setup",
    "mb-update",
    "mb-think",
    "mb-end",
    "mb-help",
    "mb-bet",
    "mb-ads",
    "mb-organic",
    "mb-site",
    "mb-wiki",
    "mb-skill-concept",
    "mb-skill-brief-draft",
    "mb-skill-review",
    *CLAUDE_PLAYBOOK_SOURCE_NAMES,
)
CODEX_SLASH_COMMAND_RELATIVE_PATHS = tuple(
    f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md" for name in CODEX_SLASH_COMMAND_NAMES
)
CODEX_SLASH_COMMAND_FACTS: dict[str, tuple[str, ...]] = {
    "mb-start": ("mb status --json --peek", "mb start --json"),
    "mb-status": ("mb status --json --peek",),
    "mb-setup": ("mb --version", "mb onboard --help", "mb status --json --peek"),
    "mb-update": ("mb update --check --json", "mb status --json --peek"),
    "mb-doctor": ("mb doctor repair --plan --json", "mb status --json --peek"),
    "mb-think": (
        "mb status --json --peek",
        "mb start --json",
        "mb doctor repair --plan",
        "mb connect doctor --json",
        "mb checkpoint --plan --json",
    ),
    "mb-end": (
        "mb status --json --peek",
        "mb start --json",
        "mb doctor repair --plan",
        "mb checkpoint --plan --json",
        "mb validate --json",
    ),
    "mb-help": ("mb workflow list --runtime codex --json", "mb status --json --peek"),
}
CODEX_SLASH_COMMAND_DESCRIPTIONS = {
    "mb-start": "Start Main Branch.",
    "mb-status": "Show Main Branch status.",
    "mb-setup": "Set up Main Branch.",
    "mb-update": "Update Main Branch.",
    "mb-doctor": "Repair Main Branch setup.",
    "mb-think": "Think through a Main Branch decision.",
    "mb-end": "End and checkpoint work.",
    "mb-help": "Show Main Branch commands.",
}
CODEX_GLOBAL_SKILL_DESCRIPTIONS = {
    **CODEX_SLASH_COMMAND_DESCRIPTIONS,
    "main-branch": "Route Main Branch work to the right mb-* skill.",
    "mb-bet": "Plan and review Main Branch bets.",
    "mb-ads": "Plan ads and paid creative from Main Branch facts.",
    "mb-organic": "Plan organic content from Main Branch facts.",
    "mb-site": "Plan pages and site readiness from Main Branch facts.",
    "mb-wiki": "Explain wiki support status for Main Branch.",
    "mb-skill-concept": "Plan a Main Branch skill concept.",
    "mb-skill-brief-draft": "Draft a Main Branch skill brief.",
    "mb-skill-review": "Review a Main Branch skill proposal.",
    "google-ads-search-launch": "Plan a Google Ads search launch playbook.",
    "ship-bet": "Plan a ship-bet playbook run.",
    "weekly-review": "Plan a weekly review.",
}
CODEX_GLOBAL_SKILL_FACTS: dict[str, tuple[str, ...]] = {
    **CODEX_SLASH_COMMAND_FACTS,
    "main-branch": REQUIRED_FACT_COMMANDS,
    "mb-bet": ("mb status --json --peek", "mb validate --json"),
    "mb-ads": ("mb status --json --peek", "mb connect doctor --json"),
    "mb-organic": ("mb status --json --peek",),
    "mb-site": ("mb status --json --peek", "mb site check --json"),
    "mb-wiki": ("mb workflow list --runtime codex --json",),
    "mb-skill-concept": ("mb workflow list --runtime codex --json",),
    "mb-skill-brief-draft": ("mb workflow list --runtime codex --json",),
    "mb-skill-review": ("mb workflow list --runtime codex --json",),
    "google-ads-search-launch": ("mb status --json --peek", "mb connect doctor --json"),
    "ship-bet": ("mb status --json --peek", "mb checkpoint --plan --json"),
    "weekly-review": ("mb status --json --peek", "mb validate --json"),
}
CODEX_GLOBAL_SKILL_SUPPORT: dict[str, str] = {
    "main-branch": "supported",
    "mb-start": "supported",
    "mb-status": "supported",
    "mb-setup": "supported",
    "mb-update": "supported",
    "mb-doctor": "supported",
    "mb-think": "supported",
    "mb-end": "supported",
    "mb-help": "supported",
    "mb-bet": "read_only_planning",
    "mb-ads": "read_only_planning",
    "mb-organic": "read_only_planning",
    "mb-site": "read_only_planning",
    "google-ads-search-launch": "read_only_planning",
    "ship-bet": "read_only_planning",
    "weekly-review": "read_only_planning",
    "mb-wiki": "intentionally_unsupported",
    "mb-skill-concept": "intentionally_unsupported",
    "mb-skill-brief-draft": "intentionally_unsupported",
    "mb-skill-review": "intentionally_unsupported",
}
CODEX_THINK_SOURCE_WORKFLOW = "workflows/mb-think/workflow.md"
CODEX_THINK_REQUIRED_MB_COMMANDS = (
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
    "mb connect doctor --json",
    "mb checkpoint --plan --json",
)
CODEX_THINK_REQUIRED_JSON_FACTS = (
    "money_path",
    "money_path.objects.offer",
    "money_path.objects.proof",
    "money_path.objects.proof.quality",
    "money_path.objects.product_ladder",
    "money_path.objects.cta_path",
    "money_path.objects.channel_strategy",
    "money_path.objects.active_push",
    "money_path.objects.outcome_feedback_loop",
    "money_path.ranked_actions",
    "content_strategy",
    "ranked_actions",
    "update",
    "readiness",
    "drift.items",
    "books",
    "runtime.codex",
    "runtime.claude_code",
)
CODEX_THINK_APPROVAL_GATES = (
    "updates_repairs_migrations",
    "file_writes",
    "checkpoint",
    "provider_mutation",
    "publishing_or_spend",
    "customer_contact",
    "private_data",
    "destructive_operations",
    "structured_collection",
    "public_issue_or_proposal",
)
CODEX_THINK_PUBLIC_PRIVATE_BOUNDARIES = (
    "no_secrets",
    "no_raw_provider_exports",
    "no_raw_transcripts",
    "no_customer_member_data",
    "no_private_runtime_settings",
    "no_private_dms_or_gated_communities",
    "no_raw_finance_legal_records",
)
CODEX_END_SOURCE_WORKFLOW = "workflows/mb-end/workflow.md"
CODEX_END_REQUIRED_MB_COMMANDS = (
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
    "mb checkpoint --plan --json",
    "mb validate --json",
)
CODEX_END_REQUIRED_JSON_FACTS = (
    "money_path",
    "money_path.objects.proof.quality",
    "content_strategy",
    "ranked_actions",
    "update",
    "readiness",
    "drift.items",
    "runtime.codex_cli",
    "runtime.claude_code",
    "journal",
    "since_last_check",
    "checkpoint.pending",
    "checkpoint.pending.changed_files",
    "checkpoint.pending.blockers",
    "checkpoint.pending.proposed_subject",
    "summary.changed_files",
    "safety.blocks",
    "proposal.message",
    "validation",
)
CODEX_END_APPROVAL_GATES = (
    "updates_repairs_migrations",
    "file_writes",
    "checkpoint",
    "provider_mutation",
    "publishing_or_spend",
    "customer_contact",
    "private_data",
    "destructive_operations",
    "public_issue_or_proposal",
)
CODEX_END_PUBLIC_PRIVATE_BOUNDARIES = (
    "no_secrets",
    "no_raw_provider_exports",
    "no_raw_transcripts",
    "no_customer_member_data",
    "no_private_runtime_settings",
    "no_raw_finance_legal_records",
)
CODEX_SHARED_WORKFLOW_SKILLS = {
    "mb-think": CODEX_THINK_SOURCE_WORKFLOW,
    "mb-end": CODEX_END_SOURCE_WORKFLOW,
}
REQUIRED_LIFECYCLE_GUIDANCE = (
    "## Codex Lifecycle Workflow Index",
    "## Codex Status Workflow",
    "## Codex Think Route",
    "## Codex End Route",
    f"Engine source workflow: `{CODEX_THINK_SOURCE_WORKFLOW}`",
    f"Engine source workflow: `{CODEX_END_SOURCE_WORKFLOW}`",
    "does not need to contain that engine source file",
    "Shared source required `mb` commands",
    "runtime/login-shell PATH",
    "`runtime.codex_cli.status` is `runtime_mismatch`",
    "`codex_runtime_mb_mismatch`",
    "Shared source required JSON fact paths",
    "Shared source gates",
    "Shared public/private boundaries",
    "Use the global Main Branch skill",
    "do not claim these workflows are ported to",
    "global skill",
    "main-branch",
)
REQUIRED_LIFECYCLE_GUIDANCE_MARKERS = (*REQUIRED_LIFECYCLE_GUIDANCE,)
REQUIRED_LIFECYCLE_SECTION_MARKERS = (
    (
        "## Codex Think Route",
        (
            *(f"- `{command}`" for command in CODEX_THINK_REQUIRED_MB_COMMANDS),
            *(f"- `{fact}`" for fact in CODEX_THINK_REQUIRED_JSON_FACTS),
            *(f"`{gate}`" for gate in CODEX_THINK_APPROVAL_GATES),
            *(f"`{boundary}`" for boundary in CODEX_THINK_PUBLIC_PRIVATE_BOUNDARIES),
        ),
    ),
    (
        "## Codex End Route",
        (
            *(f"- `{command}`" for command in CODEX_END_REQUIRED_MB_COMMANDS),
            *(f"- `{fact}`" for fact in CODEX_END_REQUIRED_JSON_FACTS),
            *(f"`{gate}`" for gate in CODEX_END_APPROVAL_GATES),
            *(f"`{boundary}`" for boundary in CODEX_END_PUBLIC_PRIVATE_BOUNDARIES),
        ),
    ),
)
CODEX_PLUGIN_REQUIRED_MARKERS = (
    "Main Branch",
    "commands",
    "mb-*",
    "business repos",
)
CODEX_WORKFLOW_STATUS_VOCABULARY = (
    "supported",
    "read_only_planning",
    "pending_shared_source_migration",
    "generated_shell_pending",
    "intentionally_unsupported",
)
CODEX_SURFACE_KIND_VOCABULARY = (
    "shared_source",
    "claude_skill",
    "codex_global_skill",
    "read_only_planning",
    "pending_shared_source_migration",
    "intentionally_unsupported",
)
CODEX_SURFACE_KIND_DESCRIPTIONS = {
    "shared_source": "canonical workflow source under workflows/<workflow>/workflow.md",
    "claude_skill": "Claude Code runtime shell under .claude/skills/<name>/SKILL.md",
    "codex_global_skill": "generated Codex global skill shell under the Codex skills root",
    "read_only_planning": (
        "Codex may inspect facts and plan, but must not claim full workflow parity"
    ),
    "pending_shared_source_migration": "workflow substance still needs a shared source migration",
    "intentionally_unsupported": "outside the current Codex daily-loop support target",
}
CODEX_SOURCE_STATUS_VOCABULARY = (
    "shared_workflow_source",
    "temporary_source_skill_mirror",
    "pending_shared_source_migration",
    "intentionally_unsupported",
)
CODEX_SOURCE_STATUS_DESCRIPTIONS = {
    "shared_workflow_source": (
        "portable workflow semantics live in workflows/<name>/workflow.md and "
        "the checked Claude/Codex shells must preserve that contract"
    ),
    "temporary_source_skill_mirror": (
        "Codex mirrors existing Claude skill or CLI guidance until a shared "
        "workflow source owns both runtime shells"
    ),
    "pending_shared_source_migration": (
        "Codex may use read-only facts or planning guidance, but runtime shells "
        "must wait for a shared source migration"
    ),
    "intentionally_unsupported": "outside the current Codex daily-loop target",
}

CODEX_WORKFLOW_INVENTORY: tuple[dict[str, Any], ...] = (
    {
        "id": "daily-start-status",
        "label": "Start, status, and what changed",
        "claude_surface": "/mb-start, /mb-status",
        "claude_skill_sources": ("mb-start", "mb-status"),
        "codex_status": "supported",
        "source_status": "temporary_source_skill_mirror",
        "codex_surface": "main-branch skill routes: mb-start, mb-status",
        "codex_entrypoints": ("main-branch mb-start", "main-branch mb-status"),
        "commands": ("mb status --json --peek", "mb start --json"),
        "contract_checks": (
            "required_mb_commands",
            "runtime_mismatch_gate",
            "read_before_write_boundary",
            "one_next_route_core_flow",
        ),
        "notes": (
            "Codex starts from deterministic status/start facts, translates them "
            "into business language, and routes one next Main Branch move."
        ),
    },
    {
        "id": "daily-setup-repair-update",
        "label": "Setup, update, doctor, and repair planning",
        "claude_surface": "/mb-setup, /mb-update, /mb-start repair routing",
        "claude_skill_sources": ("mb-setup", "mb-update"),
        "codex_status": "supported",
        "source_status": "temporary_source_skill_mirror",
        "codex_surface": "main-branch skill routes: mb-setup, mb-update, mb-doctor",
        "codex_entrypoints": (
            "main-branch mb-setup",
            "main-branch mb-update",
            "main-branch mb-doctor",
        ),
        "commands": (
            "mb --version",
            "mb doctor repair --plan --json",
            "mb update --check --json",
        ),
        "contract_checks": (
            "required_mb_commands",
            "approval_gates",
            "read_before_write_boundary",
            "repair_plan_core_flow",
        ),
        "notes": (
            "Codex may inspect plans and explain next steps. Applying updates, "
            "repairs, migrations, or setup writes requires explicit approval."
        ),
    },
    {
        "id": "think-codify",
        "label": "Think, research, decide, and codify",
        "claude_surface": "/mb-think",
        "claude_skill_sources": ("mb-think",),
        "codex_status": "supported",
        "source_status": "shared_workflow_source",
        "codex_surface": "main-branch skill route: mb-think plus AGENTS.md#codex-think-route",
        "codex_entrypoints": ("main-branch mb-think",),
        "shared_source": CODEX_THINK_SOURCE_WORKFLOW,
        "commands": CODEX_THINK_REQUIRED_MB_COMMANDS,
        "contract_checks": (
            "intent",
            "required_mb_commands",
            "required_json_facts",
            "approval_gates",
            "read_boundaries",
            "write_boundaries",
            "core_flow",
            "public_private_boundaries",
        ),
        "notes": (
            "Codex uses the shared mb-think contract for research depth, source "
            "privacy, decision routing, codification, and approval gates."
        ),
    },
    {
        "id": "end-checkpoint-save",
        "label": "End, checkpoint, and save business memory",
        "claude_surface": "/mb-end, mb checkpoint",
        "claude_skill_sources": ("mb-end",),
        "codex_status": "supported",
        "source_status": "shared_workflow_source",
        "codex_surface": "main-branch skill route: mb-end",
        "codex_entrypoints": ("main-branch mb-end",),
        "shared_source": CODEX_END_SOURCE_WORKFLOW,
        "commands": CODEX_END_REQUIRED_MB_COMMANDS,
        "contract_checks": (
            "intent",
            "required_mb_commands",
            "required_json_facts",
            "approval_gates",
            "read_boundaries",
            "write_boundaries",
            "core_flow",
            "public_private_boundaries",
            "save_state_language",
        ),
        "notes": (
            "Codex uses the shared mb-end contract for status scan, checkpoint "
            "plan, final thought capture, crystallize-lite/deep when available, "
            "owner-facing save states, approval-gated save, and warm close."
        ),
    },
    {
        "id": "workflow-discovery",
        "label": "Workflow discovery and support inventory",
        "claude_surface": "/mb-help and docs",
        "claude_skill_sources": ("mb-help",),
        "codex_status": "supported",
        "source_status": "temporary_source_skill_mirror",
        "codex_surface": "main-branch skill route: mb-help",
        "codex_entrypoints": ("main-branch mb-help",),
        "commands": ("mb workflow list --runtime codex --json",),
        "contract_checks": ("inventory_json_schema", "support_boundary_copy"),
        "notes": "Codex users can inspect supported, pending, and unsupported workflow surfaces.",
    },
    {
        "id": "bets",
        "label": "Bet lifecycle",
        "claude_surface": "/mb-bet",
        "claude_skill_sources": ("mb-bet",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only facts and business-file planning only",
        "codex_entrypoints": ("main-branch mb-bet",),
        "commands": ("mb status --json --peek", "mb validate --json"),
        "notes": (
            "Codex may inspect and discuss bets. A generated Codex shell should "
            "wait for a shared bet workflow source."
        ),
    },
    {
        "id": "ads",
        "label": "Ads and paid creative",
        "claude_surface": "/mb-ads",
        "claude_skill_sources": ("mb-ads",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "codex_entrypoints": ("main-branch mb-ads",),
        "commands": ("mb status --json --peek", "mb connect doctor --json"),
        "notes": "No provider mutation, spend, upload, or publishing is supported in Codex.",
    },
    {
        "id": "organic-content",
        "label": "Organic content and newsletter planning",
        "claude_surface": "/mb-organic and related playbooks",
        "claude_skill_sources": ("mb-organic",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "codex_entrypoints": ("main-branch mb-organic",),
        "commands": ("mb status --json --peek",),
        "notes": (
            "Codex may route content strategy questions through think/codify, "
            "but publishing and newsletter dogfood remain outside this parity slice."
        ),
    },
    {
        "id": "site",
        "label": "Site and page production",
        "claude_surface": "/mb-site",
        "claude_skill_sources": ("mb-site",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning and site readiness facts only",
        "codex_entrypoints": ("main-branch mb-site",),
        "commands": ("mb status --json --peek", "mb site check --json"),
        "notes": "Codex must not claim site build, deploy, domain, or publishing parity.",
    },
    {
        "id": "wiki",
        "label": "Wiki and personal atomic notes",
        "claude_surface": "/mb-wiki",
        "claude_skill_sources": ("mb-wiki",),
        "codex_status": "intentionally_unsupported",
        "source_status": "intentionally_unsupported",
        "codex_surface": "None",
        "commands": (),
        "notes": "Specialty workflow outside the current Codex command target.",
    },
    {
        "id": "google-ads-search-launch-playbook",
        "label": "Google Ads search launch playbook",
        "claude_surface": "google-ads-search-launch playbook",
        "claude_skill_sources": (),
        "claude_playbook_sources": ("google-ads-search-launch",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "codex_entrypoints": ("google-ads-search-launch",),
        "commands": ("mb status --json --peek", "mb connect doctor --json"),
        "notes": (
            "No Google Ads account mutation, spend, upload, or publishing is supported in Codex."
        ),
    },
    {
        "id": "ship-bet-playbook",
        "label": "Ship bet playbook",
        "claude_surface": "ship-bet playbook",
        "claude_skill_sources": (),
        "claude_playbook_sources": ("ship-bet",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "codex_entrypoints": ("ship-bet",),
        "commands": ("mb status --json --peek", "mb checkpoint --plan --json"),
        "notes": (
            "Codex can plan from facts but must ask before changing bet, push, or checkpoint files."
        ),
    },
    {
        "id": "weekly-review-playbook",
        "label": "Weekly review playbook",
        "claude_surface": "weekly-review playbook",
        "claude_skill_sources": (),
        "claude_playbook_sources": ("weekly-review",),
        "codex_status": "read_only_planning",
        "source_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "codex_entrypoints": ("weekly-review",),
        "commands": ("mb status --json --peek", "mb validate --json"),
        "notes": (
            "Codex can summarize review inputs but should not update durable "
            "files without approval."
        ),
    },
    {
        "id": "skill-authoring",
        "label": "Skill concept, draft, and review",
        "claude_surface": "/mb-skill-concept, /mb-skill-brief-draft, /mb-skill-review",
        "claude_skill_sources": (
            "mb-skill-concept",
            "mb-skill-brief-draft",
            "mb-skill-review",
        ),
        "codex_status": "intentionally_unsupported",
        "source_status": "intentionally_unsupported",
        "codex_surface": "None",
        "commands": (),
        "notes": "Engine-contributor workflow, not a business runtime surface.",
    },
)


def global_plugin_source_root() -> Path:
    """Return the user-local source directory for the global Codex plugin."""

    override = os.environ.get("MAINBRANCH_CODEX_PLUGIN_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", "") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", "") or Path.home() / ".local" / "share")
    return (base / "mainbranch" / "codex").expanduser().resolve()


def global_skill_source_root() -> Path:
    """Return the user-local directory where Codex global skills are installed."""

    override = os.environ.get("MAINBRANCH_CODEX_SKILLS_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / ".codex" / "skills").expanduser().resolve()


def global_skill_path() -> Path:
    return global_skill_source_root() / CODEX_GLOBAL_SKILL_RELATIVE_PATH


def global_skill_file_path(name: str) -> Path:
    return global_skill_source_root() / name / "SKILL.md"


def codex_marketplace_add_command() -> str:
    return f"codex plugin marketplace add {shlex.quote(str(global_plugin_source_root()))}"


_DEFAULT_AGENTS = """\
{{CODEX_GUIDANCE_METADATA}}

# {{BUSINESS_NAME}}

Main Branch business repo instructions for Codex.

## Codex Operating Contract

Main Branch CLI facts are the source of truth for repo health, setup, runtime
wiring, updates, graph/status signals, provider readiness, and repair paths.
When the operator asks to start, begin, get oriented, triage the day, or decide
what to do next, use the global Main Branch skill route (`mb-start`,
`mb-status`, or the closest `mb-*` route) or the read-only `mb` fact commands
below. Do not pretend Claude Code slash skills work in Codex.

Start in this repo. Before setup, routing, migration, update, or repair advice,
run the runtime preflight and read-only checks that fit the situation:

```bash
command -v mb
mb --version
mb status --json --peek
mb start --json
mb doctor repair --plan
```

This file is managed by Main Branch. Run
`mb doctor repair --plan --only codex` if setup or runtime guidance looks
stale. If `mb --version` reports an older or different version, stop before
status or repair commands and tell the operator to put the current Main Branch
install earlier on the runtime/login-shell PATH.

After `mb status --json --peek` or `mb start --json`, stop if
`runtime.codex_cli.status` is `runtime_mismatch` or any `drift.items[].id`
equals `codex_runtime_mb_mismatch`. Treat that as a runtime `mb` mismatch: tell
the operator to fix the runtime/login-shell PATH and rerun read-only checks
before Main Branch advice, repair planning, or writes.

Use `mb status --json --peek` as the default daily briefing before routing the
operator. It names readiness, drift, onboarding progress, update state, GitHub
activity, provider signals, recent work, MoneyPath, ranked actions, bets,
pushes, and checkpoint state. Do not replace those facts with ad hoc shell
inspection unless `mb` says a section is unavailable or the command itself is
missing.

Read-only commands can be run without asking first. Commands that write files,
refresh local runtime wiring, update packages, migrate business files, create
checkpoints, publish, spend money, contact customers, email, or mutate provider
accounts require explicit operator approval before applying.

## First-run setup intent

When the operator pastes a setup guide, bootstrap prompt, or business/folder
description into an empty or uninitialized folder, treat it as setup intent,
not as a document to save. Do not ask what file format to save the prompt in. First
check `mb --version`. If `mb` is missing, stop and give the exact install step:
`pipx install mainbranch`. If `mb` is available, inspect the setup path with
`mb onboard --help`, then explain which folder will become the business brain
and ask before running any command that writes files.

If the operator asks for GitHub backup, sync, collaboration, or
`mb onboard --github <owner/repo> --push`, check GitHub CLI before any setup write:
`gh auth status` and `gh api user --jq .login`. Confirm the signed-in account
matches the operator's expected account. GitHub is strongly recommended because
it gives Main Branch a free cloud backup, shared history, task/proposal layer,
and connector-friendly copy of the business brain. Main Branch can start
locally without GitHub; GitHub is needed for sync, collaboration, and the
GitHub-backed onboarding path.

After setup, run `mb status --json --peek` and `mb start --json`. Summarize the
outcome in business language first: folder created, business brain ready,
baseline saved, GitHub backup connected when requested, checkpoint state, and
next safe action. Put commands and git/GitHub details second.

Do the technical work in technical commands, then translate the result back into
business-owner language. Speak first in terms of bets, goals, offers, pushes,
playbooks, outcomes, decisions, next actions, and saved checkpoints. Treat git,
branches, pull requests, provider refs, and local wiring as the hidden memory
layer unless the operator asks for the plumbing.

Default translations for normal owner answers:
- `git is clean`, `repo is clean`, `working tree clean`, or `working tree: clean`
  -> nothing unsaved locally;
- `branch main`, `branch: main`, or `current branch: main` -> current business
  folder or workspace;
- `No GitHub origin remote` or `No origin remote` -> no connected GitHub backup
  or shared task source;
- `PR/issue facts` or `PR and issue facts` -> GitHub task and proposal context.

When finishing first-run setup, lead with the owner outcome before the receipt:
created, saved, synced to GitHub when requested, and ready to open in Claude
Code. Put commands, remotes, branches, validation checks, and local wiring in a
short technical receipt after that outcome.

Use the `vocabulary` block from `mb status --json --peek` when present. If
`core/vocabulary.md` says this business calls pushes drops, launches,
challenges, or promos, use that word in operator-facing prose while preserving
canonical paths, frontmatter, JSON keys, validator rules, and command names.

## Codex Lifecycle Workflow Index

This tracked `AGENTS.md` file is the repo-level Codex bootstrap. The Main
Branch Codex skill bundle is installed globally once per user and routes `mb-*`
workflow names over deterministic `mb` facts. Business repos keep this
lightweight `AGENTS.md` guidance instead of tracked repo-local plugin or skill
copies. `mb doctor repair --only codex` refreshes this file and installs or
repairs the global skills.

Use the global Main Branch skills for Main Branch daily routes only. Do not
create repo-local Codex plugin manifests, copied Claude skill trees, or
symlinked Claude skills unless a future `mb` command or issue says that surface
is supported for this repo.
The global `main-branch` skill is an index; named global skills such as
`mb-start`, `mb-status`, and `mb-think` carry the workflow routes.

Use this index to map natural Codex requests:

- **Start the day / what next / get oriented:** use the Codex Start Workflow
  below. Run `mb status --json --peek` first, then `mb start --json` when
  runtime handoff or adapter-readiness facts matter.
- **Inspect status / what changed / what is stale:** use the Codex Status
  Workflow below.
  Answer from `ranked_actions`, `since_last_check`, `journal`, `money_path`,
  `content_strategy`, `integrations`, `readiness`, and `drift.items`.
- **Think / research / decide / codify:** use the Codex Think Route below. Start
  from `mb` facts, choose a research depth, and ask before writing durable
  business files.
- **Site, ads, organic production, provider mutation, publishing, spend,
  domains, or customer contact:** do not claim these workflows are ported to
  Codex. Use read-only `mb` facts for planning and ask before any action.

Use `mb doctor repair --plan --only codex` to inspect global skill wiring.

## Codex Start Workflow

This is the Codex-native start workflow.

1. Run `mb status --json --peek` from the current working directory. Use the
   repo markers in that JSON to confirm this is the business repo. If the
   status report says this is not a Main Branch repo or the command is missing,
   ask for the business repo path instead of guessing.
2. Use the status JSON as the source of truth for
   readiness, drift, onboarding, update severity, GitHub facts, provider
   readiness, recent work, MoneyPath, ranked actions, bets, pushes,
   vocabulary, and checkpoint state.
3. Run `mb start --json` when you need runtime handoff, repo-boundary, or
   adapter-readiness facts.
4. Stop before more checks if either status or start reports
   `runtime.codex_cli.status` as `runtime_mismatch`, or if `drift.items`
   includes `codex_runtime_mb_mismatch`. Tell the operator to fix the
   runtime/login-shell PATH first.
5. Run `mb doctor repair --plan` before recommending setup or repair. Quote the
   exact repair command from the plan. Ask before any write/apply command.
6. If status says an update is required, route to the cited `mb update` command
   and ask before running it. After an approved update, rerun
   `mb status --json --peek`.
7. Resume onboarding from status facts. In rich repos, read existing `core/`
   files before asking bounded missing-profile questions.
8. Present one clear business route: frame a bet, think through a decision,
   advance a push, draft a playbook, repair the repo, review provider
   readiness, save a checkpoint, or inspect a specific offer.

Use numbered lists for operator choices, with one active choice namespace per
turn. If the operator replies with an ambiguous number, ask what they meant
before acting.

## Codex Status Workflow

This is the Codex-native status workflow.

1. Run `mb status --json --peek`.
2. Treat the JSON as the source of truth for setup, update, drift, GitHub,
   onboarding, integrations, bets, recent work, since-last-check,
   `content_strategy`, `money_path`, vocabulary, checkpoint state, and
   `ranked_actions`.
3. Stop before business routing if `runtime.codex_cli.status` is
   `runtime_mismatch` or `drift.items` includes `codex_runtime_mb_mismatch`.
   Tell the operator to fix the runtime/login-shell PATH and rerun the
   read-only checks first.
4. Lead with the top `ranked_actions` entry when the operator asks what to do
   next. Include the reason and cited signal summaries.
5. For "what changed?" answer from `since_last_check.journal` first, then
   top-level `journal` for recent context.
6. For provider questions, read `integrations` first. Run `mb connect plan` or
   `mb connect doctor --json` only when the operator needs choices or repair
   commands.
7. Use `money_path` for customer progress, offer, proof, CTA, channel, push,
   playbook, page readiness, and outcome feedback questions. Keep language
   evidence-based: legible, supported, connected, instrumented.
8. Use `content_strategy` for content strategy health, layered channel/account
   files, stale platform rules, or disconnected content layers.

Do not mutate the last-check marker unless the operator explicitly says this is
the daily check-in and wants it recorded.

## Codex Think Route

This is Codex-native guidance for the existing `mb-think` shared workflow
source. Treat this section as the natural-language Codex route. It does not
mean all Main Branch skills work in Codex.

Engine source workflow: `workflows/mb-think/workflow.md`. This business repo
does not need to contain that engine source file. Treat this generated
`AGENTS.md` section as the Codex shell for that source unless you are explicitly
working inside the Main Branch engine repo.

Shared source required `mb` commands:

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`
- `mb connect doctor --json`
- `mb checkpoint --plan --json`

Shared source required JSON fact paths:

- `money_path`
- `money_path.objects.offer`
- `money_path.objects.proof`
- `money_path.objects.proof.quality`
- `money_path.objects.product_ladder`
- `money_path.objects.cta_path`
- `money_path.objects.channel_strategy`
- `money_path.objects.active_push`
- `money_path.objects.outcome_feedback_loop`
- `money_path.ranked_actions`
- `content_strategy`
- `ranked_actions`
- `update`
- `readiness`
- `drift.items`
- `books`
- `runtime.codex`
- `runtime.claude_code`

Shared source gates: `updates_repairs_migrations`, `file_writes`,
`checkpoint`, `provider_mutation`, `publishing_or_spend`, `customer_contact`,
`private_data`, `destructive_operations`, `structured_collection`,
`public_issue_or_proposal`.

Shared public/private boundaries: `no_secrets`, `no_raw_provider_exports`,
`no_raw_transcripts`, `no_customer_member_data`,
`no_private_runtime_settings`, `no_private_dms_or_gated_communities`,
`no_raw_finance_legal_records`.

Use it when the operator asks to think through an offer, research a market,
compare providers, make a decision, or codify what was learned.

Before advice, run the read-only facts that fit the situation:

```bash
mb status --json --peek
mb start --json
mb doctor repair --plan
```

If the task touches provider readiness, run `mb connect doctor --json`. Before
recommending a saved checkpoint, run `mb checkpoint --plan --json`. These
commands provide facts and plans; they do not authorize writes.

Choose the smallest honest research depth:

- Level 0: operator memory is enough for a low-risk move.
- Level 1: existing repo context and `mb` facts are enough.
- Level 2: lightweight public or operator-provided research is needed.
- Level 3: multi-source synthesis is needed.
- Level 4: structured approved-source collection is justified.
- Level 5: high-resolution market analysis or field evidence is needed.

Read only the business files needed for the question: `core/`, `research/`,
`decisions/`, `bets/`, `pushes/`, `log/`, and `documents/`. Do not inspect
secrets, raw provider exports, raw transcripts, raw finance/legal records,
customer/member records, private DMs, gated communities, local runtime
settings, or credentials unless the operator gives explicit permission and the
source belongs in the business repo. For transcripts, authenticated community
content, provider recordings, cloud-drive files, exported chats, or mixed
private/business sources, inventory sources and apply manifest-first
allow/skip filters before reading content; commit synthesized findings, not raw
payloads.

Ask before creating, editing, moving, deleting, archiving, codifying, or
checkpointing business files. Ask before publishing, opening a public issue,
submitting a proposal, spending money, mutating provider state, or contacting
customers.

## Codex End Route

This is Codex-native guidance for the existing `mb-end` shared workflow source.
Treat this section as the natural-language Codex route. It does not mean all
Main Branch skills work in Codex.

Engine source workflow: `workflows/mb-end/workflow.md`. This business repo does
not need to contain that engine source file. Treat this generated `AGENTS.md`
section as the Codex shell for that source unless you are explicitly working
inside the Main Branch engine repo.

Shared source required `mb` commands:

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`
- `mb checkpoint --plan --json`
- `mb validate --json`

Shared source required JSON fact paths:

- `money_path`
- `money_path.objects.proof.quality`
- `content_strategy`
- `ranked_actions`
- `update`
- `readiness`
- `drift.items`
- `runtime.codex_cli`
- `runtime.claude_code`
- `journal`
- `since_last_check`
- `checkpoint.pending`
- `checkpoint.pending.changed_files`
- `checkpoint.pending.blockers`
- `checkpoint.pending.proposed_subject`
- `summary.changed_files`
- `safety.blocks`
- `proposal.message`
- `validation`

Shared source gates: `updates_repairs_migrations`, `file_writes`,
`checkpoint`, `provider_mutation`, `publishing_or_spend`, `customer_contact`,
`private_data`, `destructive_operations`, `public_issue_or_proposal`.

Shared public/private boundaries: `no_secrets`, `no_raw_provider_exports`,
`no_raw_transcripts`, `no_customer_member_data`,
`no_private_runtime_settings`, `no_raw_finance_legal_records`.

Use it when the operator is done, pausing, saving progress, checkpointing, or
asking whether the work is saved. Run a status scan first, build the checkpoint
plan, summarize the session, ask once for a final thought, run crystallize-lite
in-thread or use available subagent tooling, name the owner-facing save state,
and ask before saving.

Owner-facing save states are `drafted`, `saved locally`, `ready to send up`,
`sent for review`, `landed in main`, and `blocked by unrelated cleanup`.
Technical branch, proposal, merge, and working-tree details come second unless
the operator asks for plumbing.

## Routing Rules

- If `ranked_actions` has entries, lead with the first action, its reason, and
  the cited signal summaries.
- Use `money_path` when the next move depends on customer progress, offer,
  proof, CTA, channel, push, playbook, page readiness, or outcome feedback.
  Keep the language evidence-based: legible, supported, connected,
  instrumented.
- If readiness is blocked or drift has errors, handle repair before output
  work.
- If onboarding is incomplete, use the `onboarding.summary` and checklist from
  status instead of inventing a setup interview.
- If legacy `campaigns/` records exist, surface the doctor warning and suggest
  `mb migrate campaigns --plan` before creating new coordinated work.
- If the operator asks for publishing, spend, provider mutation, customer
  contact, migration, checkpoint creation, or file writes, plan first and ask
  for explicit approval.
- If the operator brings a live idea and it is unclear where it belongs, route
  by business meaning: offers are what the business may keep selling; bets are
  time-boxed wagers; pushes are coordinated execution; proof is evidence; and
  decisions explain durable changes.

## Business Folders

- `core/` - the business brain: offer, audience, voice, soul, proof, brand,
  strategy, operations, finance.
- `core/offers/` - per-offer specifics when this is a multi-offer repo.
- `core/proof/` - testimonials, typicality, and reusable proof. Use
  structured permission and offer-link fields when proof should be detectable
  by `mb status`.
- `core/content-strategy.md` - business-level content strategy and index.
- `core/marketing/` - optional distribution, channel, and account strategy.
- `core/people/` - optional founder/person voice source material, beliefs,
  stories, and proof.
- `research/` - dated notes from when you went looking.
- `decisions/` - dated choices, with rationale.
- `bets/` - operating bets with appetite, metric, target, and outcome.
- `pushes/` - coordinated pushes such as launches, drops, challenges, promos.
- `log/` - running activity log.
- `documents/` - anything that does not belong above.

Use `core/content-strategy.md` as the default solo-operator content strategy.
When the business needs more layers, read or write
`core/marketing/distribution-strategy.md`,
`core/marketing/channels/<channel>.md`,
`core/marketing/accounts/<platform>-<account>.md`, and
`core/people/<person>.md`. Weekly content planning should reference those files,
then put specific execution in `pushes/` and results in `log/`.

## Connected Accounts

Never commit API keys, OAuth refresh tokens, service-account JSON, webhook
secrets, MCP tokens, or bearer tokens. Keep secrets in the runtime's local
config, an OS keychain, 1Password, `.env`, or another gitignored local file. If
a tool can spend money, publish, email, or mutate a customer account, verify it
is tethered to this repo and ask for approval before using it.

## Repo Owner

`@{{GH_USERNAME}}`
"""


def _read_template(name: str) -> str:
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(name)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        here = Path(__file__).resolve().parent / "_data" / "templates" / name
        if here.exists():
            return here.read_text(encoding="utf-8")
        return ""


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, val in mapping.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _markdown_h1(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    except OSError:
        return ""
    return ""


def _repo_owner(repo: Path) -> str:
    codeowners = repo / ".github" / "CODEOWNERS"
    try:
        for raw_line in codeowners.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            for part in parts[1:]:
                if part.startswith("@"):
                    return part.removeprefix("@")
    except OSError:
        pass
    agents = repo / AGENTS_RELATIVE_PATH
    try:
        lines = agents.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "your-gh-username"
    for line in lines:
        stripped = line.strip().strip("`")
        if stripped.startswith("@") and " " not in stripped:
            return stripped.removeprefix("@")
    return "your-gh-username"


def business_name(repo: str | Path) -> str:
    target = Path(repo).expanduser().resolve()
    for relative in ("CLAUDE.md", "AGENTS.md"):
        name = _markdown_h1(target / relative)
        if name and "instructions" not in name.lower():
            return name
    return target.name or "Business"


def render_agents_md(repo: str | Path, *, name: str = "", gh_username: str = "") -> str:
    target = Path(repo).expanduser().resolve()
    template = _read_template(AGENTS_TEMPLATE) or _DEFAULT_AGENTS
    template_hash = guidance_template_hash(template)
    mapping = {
        "BUSINESS_NAME": name.strip() or business_name(target),
        "GH_USERNAME": gh_username.strip() or _repo_owner(target),
        "MAINBRANCH_VERSION": __version__,
        "CODEX_GUIDANCE_METADATA": guidance_metadata_comment(template_hash=template_hash),
    }
    return _render(template, mapping)


def _metadata_free_template(template: str) -> str:
    return template.replace("{{CODEX_GUIDANCE_METADATA}}\n\n", "").replace(
        "{{CODEX_GUIDANCE_METADATA}}\n", ""
    )


def guidance_template_hash(template: str | None = None) -> str:
    source = (
        template if template is not None else (_read_template(AGENTS_TEMPLATE) or _DEFAULT_AGENTS)
    )
    normalized = _metadata_free_template(source).replace("\r\n", "\n").strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def guidance_metadata_comment(*, template_hash: str | None = None) -> str:
    digest = template_hash or guidance_template_hash()
    return (
        "<!-- mainbranch:codex-guidance "
        f"schema={CODEX_GUIDANCE_SCHEMA} "
        f"template_hash={digest} "
        f"min_mb={CODEX_GUIDANCE_MIN_MB} -->"
    )


def parse_guidance_metadata(text: str) -> dict[str, str]:
    match = re.search(r"<!--\s*mainbranch:codex-guidance\s+([^>]*)-->", text)
    if not match:
        return {}
    pairs: dict[str, str] = {}
    for item in match.group(1).split():
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        pairs[key.strip()] = value.strip().strip('"')
    return pairs


def _markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


def _commands_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    commands = item.get("commands") or ()
    if not isinstance(commands, tuple):
        return tuple(str(command) for command in commands)
    return tuple(str(command) for command in commands)


def _workflow_source_path(relative_path: str) -> Path:
    root = engine_mod.engine_root()
    if root is not None:
        candidate = root / relative_path
        if candidate.is_file():
            return candidate
    return Path(__file__).resolve().parents[2] / relative_path


def _load_shared_workflow_for_skill(name: str) -> WorkflowSource | None:
    relative_path = CODEX_SHARED_WORKFLOW_SKILLS.get(name)
    if relative_path is None:
        return None
    return load_workflow(_workflow_source_path(relative_path))


def _claude_skill_sources_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    sources = item.get("claude_skill_sources") or ()
    names = sources if isinstance(sources, tuple) else tuple(str(source) for source in sources)
    return tuple(f".claude/skills/{name}/SKILL.md" for name in names)


def _claude_playbook_sources_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    sources = item.get("claude_playbook_sources") or ()
    names = sources if isinstance(sources, tuple) else tuple(str(source) for source in sources)
    return tuple(f".claude/playbooks/{name}/SKILL.md" for name in names)


def _source_of_truth_for_inventory_item(item: dict[str, Any]) -> dict[str, Any]:
    status = str(item["source_status"])
    surface_kinds = _surface_kinds_for_inventory_item(item)
    return {
        "status": status,
        "description": CODEX_SOURCE_STATUS_DESCRIPTIONS[status],
        "shared_source": item.get("shared_source"),
        "surface_kinds": surface_kinds,
        "claude_sources": list(
            _claude_skill_sources_for_inventory_item(item)
            + _claude_playbook_sources_for_inventory_item(item)
        ),
        "codex_sources": [str(entrypoint) for entrypoint in item.get("codex_entrypoints", ())],
        "contract_checks": [str(check) for check in item.get("contract_checks", ())],
        "follow_up_issue": item.get("follow_up_issue"),
    }


def _surface_kinds_for_inventory_item(item: dict[str, Any]) -> list[str]:
    kinds: list[str] = []
    if item.get("shared_source"):
        kinds.append("shared_source")
    if item.get("claude_skill_sources") or item.get("claude_playbook_sources"):
        kinds.append("claude_skill")
    if item.get("codex_entrypoints"):
        kinds.append("codex_global_skill")
    codex_status = str(item.get("codex_status", ""))
    source_status = str(item.get("source_status", ""))
    if codex_status == "read_only_planning":
        kinds.append("read_only_planning")
    if source_status == "pending_shared_source_migration":
        kinds.append("pending_shared_source_migration")
    if codex_status == "intentionally_unsupported":
        kinds.append("intentionally_unsupported")
    return kinds


def workflow_inventory(*, runtime: str = "codex") -> dict[str, Any]:
    """Return the public-safe Main Branch workflow support inventory."""

    items = []
    for item in CODEX_WORKFLOW_INVENTORY:
        copied = dict(item)
        copied["commands"] = list(_commands_for_inventory_item(item))
        copied["claude_skill_sources"] = list(_claude_skill_sources_for_inventory_item(item))
        copied["claude_playbook_sources"] = list(_claude_playbook_sources_for_inventory_item(item))
        copied["codex_entrypoints"] = [
            str(entrypoint) for entrypoint in item.get("codex_entrypoints", ())
        ]
        copied["surface_kinds"] = _surface_kinds_for_inventory_item(item)
        copied["source_of_truth"] = _source_of_truth_for_inventory_item(item)
        items.append(copied)
    statuses = sorted(
        {*CODEX_WORKFLOW_STATUS_VOCABULARY}
        | {str(item["codex_status"]) for item in CODEX_WORKFLOW_INVENTORY}
    )
    source_statuses = sorted(
        {*CODEX_SOURCE_STATUS_VOCABULARY}
        | {str(item["source_status"]) for item in CODEX_WORKFLOW_INVENTORY}
    )
    return {
        "ok": True,
        "runtime": runtime,
        "support_level": CODEX_SUPPORT_LEVEL,
        "entrypoint": "main-branch mb-start",
        "repo_guidance": AGENTS_RELATIVE_PATH,
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "architecture": {
            "canonical_flow": (
                "shared workflow source -> Claude Code shell -> Codex shell -> inventory/tests"
            ),
            "shared_source_root": "workflows/<workflow>/workflow.md",
            "runtime_shells": {
                "claude_code": ".claude/skills/<name>/SKILL.md",
                "codex_cli": "global main-branch skills plus AGENTS.md guidance",
            },
            "status_field": "items[].source_of_truth.status",
        },
        "claude_skill_sources": [
            f".claude/skills/{name}/SKILL.md" for name in CLAUDE_SKILL_SOURCE_NAMES
        ],
        "claude_playbook_sources": [
            f".claude/playbooks/{name}/SKILL.md" for name in CLAUDE_PLAYBOOK_SOURCE_NAMES
        ],
        "global_skill": {
            "name": CODEX_GLOBAL_SKILL_NAME,
            "display_name": "Main Branch",
            "path": CODEX_GLOBAL_SKILL_RELATIVE_PATH,
            "routes": list(CODEX_GLOBAL_SKILL_NAMES),
            "support": CODEX_GLOBAL_SKILL_SUPPORT,
            "install_hint": CODEX_REPAIR_COMMAND,
        },
        "statuses": statuses,
        "source_statuses": source_statuses,
        "source_status_descriptions": CODEX_SOURCE_STATUS_DESCRIPTIONS,
        "surface_kinds": list(CODEX_SURFACE_KIND_VOCABULARY),
        "surface_kind_descriptions": CODEX_SURFACE_KIND_DESCRIPTIONS,
        "items": items,
        "safe_to_share": True,
    }


def render_workflow_inventory_md() -> str:
    """Render the project-local Codex workflow inventory reference."""

    rows = []
    for item in CODEX_WORKFLOW_INVENTORY:
        commands = ", ".join(f"`{command}`" for command in _commands_for_inventory_item(item))
        entrypoints = ", ".join(f"`{entry}`" for entry in item.get("codex_entrypoints", ()))
        claude_sources = ", ".join(
            f"`{source}`"
            for source in (
                _claude_skill_sources_for_inventory_item(item)
                + _claude_playbook_sources_for_inventory_item(item)
            )
        )
        row_template = (
            "| {label} | `{status}` | `{source_status}` | {claude} | {sources} | "
            "{codex} | {entrypoints} | {commands} |"
        )
        rows.append(
            row_template.format(
                label=item["label"],
                status=item["codex_status"],
                source_status=item["source_status"],
                claude=item["claude_surface"],
                sources=claude_sources or "None",
                codex=item["codex_surface"],
                entrypoints=entrypoints or "None",
                commands=commands or "None",
            )
        )
    return (
        "# Main Branch Codex Workflow Inventory\n\n"
        "Generated by `mb`. Do not edit by hand in business repos. This file maps "
        "Main Branch workflow surfaces to the Codex global-skill support boundary.\n\n"
        "Status meanings:\n\n"
        "- `supported`: Codex can use this surface through global Main Branch skills "
        "grounded in deterministic `mb` facts.\n"
        "- `read_only_planning`: Codex can inspect facts and help plan, but must "
        "not claim full workflow parity until a shared source migration lands.\n"
        "- `pending_shared_source_migration`: Codex may plan from read-only facts, "
        "but a runtime shell should wait for a shared workflow source.\n"
        "- `generated_shell_pending`: a shared source exists, but a generated Codex "
        "shell still needs implementation and smoke evidence.\n"
        "- `intentionally_unsupported`: outside the current Codex daily-loop target.\n\n"
        "Source-of-truth meanings:\n\n"
        "- `shared_workflow_source`: `workflows/<workflow>/workflow.md` owns "
        "the portable workflow contract and tests check runtime shells against it.\n"
        "- `temporary_source_skill_mirror`: Codex mirrors existing Claude skill "
        "or CLI guidance until a shared source owns both runtime shells.\n"
        "- `pending_shared_source_migration`: Codex may use read-only facts or "
        "planning guidance, but runtime shells wait for a shared source migration.\n"
        "- `intentionally_unsupported`: outside the current Codex daily-loop target.\n\n"
        "Canonical architecture: shared workflow source -> Claude Code shell -> "
        "Codex shell -> inventory/tests. Temporary mirrors are explicit so "
        "reviewers can see which routes still need migration.\n\n"
        "Surface kinds in `mb workflow list --json`: `shared_source`, "
        "`claude_skill`, `codex_global_skill`, `read_only_planning`, "
        "`pending_shared_source_migration`, and `intentionally_unsupported`.\n\n"
        "The global Main Branch skill bundle is installed by "
        "`mb doctor repair --only codex`; business repos keep only lightweight "
        "`AGENTS.md` guidance. After repair, open a fresh Codex thread in the "
        "business repo and ask Main Branch to run one of the `mb-*` routes. "
        "Each row names its bundled Claude skill "
        "source(s); every bundled Claude `mb-*` skill must be accounted for here "
        "until the shared workflow generator owns both runtime shells.\n\n"
        "| Workflow | Codex status | Source of truth | Claude Code surface | Claude source | "
        "Codex surface | Codex route | Fact commands |\n"
        "|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        "Codex must ask before durable writes, checkpoints, repairs, updates, "
        "migrations, provider mutation, publishing, spend, customer contact, or "
        "public issue/proposal submission.\n"
    )


def render_codex_plugin_manifest() -> str:
    """Render the global Codex plugin manifest."""

    payload = {
        "name": CODEX_PLUGIN_NAME,
        "version": "0.1.0",
        "description": (
            "Main Branch /mb commands for Codex. Uses deterministic mb facts "
            "and business-repo guidance."
        ),
        "author": {"name": "Noontide"},
        "homepage": "https://github.com/noontide-co/mainbranch",
        "repository": "https://github.com/noontide-co/mainbranch",
        "license": "MIT",
        "keywords": ["main-branch", "mainbranch", "business-memory"],
        "interface": {
            "displayName": "Main Branch",
            "shortDescription": "Main Branch /mb commands for business repos",
            "longDescription": (
                "Adds Codex `/mb-*` commands for Main Branch business repos. Commands "
                "route through deterministic mb facts and repo guidance; "
                "they do not add provider mutation, publishing, spend, customer "
                "contact, ads/site production, or all-skill parity."
            ),
            "developerName": "Noontide",
            "category": "Productivity",
            "capabilities": ["Interactive", "Read", "Write"],
            "websiteURL": "https://github.com/noontide-co/mainbranch",
            "defaultPrompt": [
                "Use /mb-start to start this Main Branch business day",
                "Use /mb-help to show supported Main Branch Codex commands",
                "Use /mb-end to plan a checkpoint before saving work",
            ],
            "brandColor": "#0F766E",
            "screenshots": [],
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def render_codex_marketplace_json() -> str:
    """Render the global Codex plugin marketplace metadata."""

    payload = {
        "name": CODEX_MARKETPLACE_NAME,
        "interface": {"displayName": "Main Branch"},
        "plugins": [
            {
                "name": CODEX_PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./{CODEX_PLUGIN_DIR_RELATIVE_PATH}",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _slash_command_label(name: str) -> str:
    return f"/{name}"


def render_codex_slash_command_md(name: str) -> str:
    """Render one thin Codex slash-command file for the global plugin."""

    if name not in CODEX_SLASH_COMMAND_NAMES:
        raise ValueError(f"unknown Codex slash command: {name}")
    description = CODEX_SLASH_COMMAND_DESCRIPTIONS[name]
    facts = CODEX_SLASH_COMMAND_FACTS[name]
    fact_lines = "\n".join(f"- `{command}`" for command in facts)
    command = _slash_command_label(name)
    specific = {
        "mb-start": (
            "Summarize the business state, readiness, ranked actions, and one "
            "clear next route. Use `mb start --json` when runtime handoff or "
            "Codex readiness matters."
        ),
        "mb-status": (
            "Answer from status facts: readiness, drift, recent work, "
            "since-last-check, MoneyPath, content strategy, provider signals, "
            "and ranked actions."
        ),
        "mb-setup": (
            "Treat setup prompts as onboarding intent. Explain the target folder "
            "and ask before running any command that writes files."
        ),
        "mb-update": (
            "Report whether an update is required or recommended. Ask before "
            "running update, repair, migration, or package-changing commands."
        ),
        "mb-doctor": (
            "Explain the repair plan in business language first. Quote exact "
            "safe commands and ask before applying any write action."
        ),
        "mb-think": (
            "Use the Codex Think Route in `AGENTS.md`. Choose the smallest honest "
            "research depth, read only needed business files, and ask before "
            "codifying or checkpointing."
        ),
        "mb-end": (
            "Use the shared closeout workflow. Run the status scan and checkpoint "
            "plan, summarize the session, capture a final thought, do "
            "crystallize-lite or an available subagent pass, name the owner-facing "
            "save state, and ask before saving."
        ),
        "mb-help": (
            "Show the supported, pending, and unsupported Codex workflow surfaces. "
            "Do not claim parity for surfaces the inventory does not mark supported."
        ),
    }[name]
    return f"""---
description: {description}
---

# {command}

Use Main Branch from the current repo. This command is a thin Codex route over
deterministic `mb` facts and the repo `AGENTS.md` guidance. Do not duplicate
workflow logic here.

## Preflight

Run first:

- `command -v mb`
- `mb --version`

If `mb` is missing or reports an unexpected version, stop and tell the operator
to fix the runtime/login-shell PATH before continuing.

## Facts

Run the read-only facts that fit this command:

{fact_lines}

Stop before business routing if `runtime.codex_cli.status` is
`runtime_mismatch` or if any drift item is `codex_runtime_mb_mismatch`.

## Route

{specific}

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations, or public
issue/proposal submission.
"""


def render_codex_slash_commands() -> dict[str, str]:
    """Render all generated Codex slash-command files by relative path."""

    return {
        f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md": render_codex_slash_command_md(name)
        for name in CODEX_SLASH_COMMAND_NAMES
    }


def _render_shared_workflow_global_skill_adapter(workflow: WorkflowSource) -> str:
    rendered_shell = render_codex_shell(workflow).strip()
    return (
        "Follow the generated Codex shell below. It is rendered from the canonical "
        "shared workflow source, so workflow substance belongs in that source and "
        "Codex differences stay in this adapter layer.\n\n"
        f"{rendered_shell}"
    )


def render_codex_global_skill_md(name: str = CODEX_GLOBAL_SKILL_NAME) -> str:
    """Render one global Main Branch Codex skill."""

    route_lines = "\n".join(
        f"- `{skill}`: {CODEX_GLOBAL_SKILL_DESCRIPTIONS[skill]} "
        f"({CODEX_GLOBAL_SKILL_SUPPORT[skill]})"
        for skill in CODEX_GLOBAL_SKILL_NAMES
        if skill != CODEX_GLOBAL_SKILL_NAME
    )
    if name not in CODEX_GLOBAL_SKILL_NAMES:
        raise ValueError(f"unknown Codex global skill: {name}")
    description = CODEX_GLOBAL_SKILL_DESCRIPTIONS[name]
    support_level = CODEX_GLOBAL_SKILL_SUPPORT[name]
    workflow = _load_shared_workflow_for_skill(name)
    facts = tuple(workflow.required_mb_commands) if workflow else CODEX_GLOBAL_SKILL_FACTS[name]
    if name == CODEX_GLOBAL_SKILL_NAME:
        argument_hint = (
            "[mb-start|mb-status|mb-setup|mb-update|mb-doctor|mb-think|mb-end|mb-help|other-route]"
        )
        title = "Main Branch"
        route_guidance = (
            "Choose the closest route below, then follow that route's facts and approval boundary."
        )
    else:
        argument_hint = "[target]"
        title = name
        if workflow is not None:
            route_guidance = _render_shared_workflow_global_skill_adapter(workflow)
        else:
            supported_guidance = {
                "mb-start": (
                    "Summarize the business state, readiness, ranked actions, and one "
                    "clear next route. Use `mb start --json` when runtime handoff or "
                    "Codex readiness matters."
                ),
                "mb-status": (
                    "Answer from status facts: readiness, drift, recent work, "
                    "since-last-check, MoneyPath, content strategy, provider signals, "
                    "and ranked actions."
                ),
                "mb-setup": (
                    "Treat setup prompts as onboarding intent. Explain the target folder "
                    "and ask before running any command that writes files."
                ),
                "mb-update": (
                    "Report whether an update is required or recommended. Ask before "
                    "running update, repair, migration, or package-changing commands."
                ),
                "mb-doctor": (
                    "Explain the repair plan in business language first. Quote exact "
                    "safe commands and ask before applying any write action."
                ),
                "mb-think": (
                    "Use the Codex Think Route in `AGENTS.md`. Choose the smallest honest "
                    "research depth, read only needed business files, and ask before "
                    "codifying or checkpointing."
                ),
                "mb-end": (
                    "Use the shared closeout workflow. Run the status scan and checkpoint "
                    "plan, summarize the session, capture a final thought, do "
                    "crystallize-lite or an available subagent pass, name the owner-facing "
                    "save state, and ask before saving."
                ),
                "mb-help": (
                    "Show the supported, pending, and unsupported Codex workflow surfaces. "
                    "Do not claim parity for surfaces the inventory does not mark supported."
                ),
            }
            if name in supported_guidance:
                route_guidance = supported_guidance[name]
            elif support_level == "read_only_planning":
                route_guidance = (
                    "Use this as a read-only planning route in Codex. Ground the answer "
                    "in the facts below, name what Claude Code can do more fully when "
                    "relevant, and ask before writing files or touching providers. This "
                    "route is pending shared source migration and is not full workflow "
                    "parity."
                )
            else:
                route_guidance = (
                    "This workflow is inventoried for completeness but is not a supported "
                    "Codex execution route yet. Explain the support boundary and route "
                    "the operator to Claude Code or another supported Main Branch path."
                )
    fact_lines = "\n".join(f"- `{command}`" for command in facts)
    return f"""---
name: {name}
description: "{description}"
argument-hint: "{argument_hint}"
user-invocable: true
---

# {title}

Support level: `{support_level}`.

Use this skill when the operator is in a Main Branch business repo and asks to
start the day, inspect status, set up, update, repair, think through a decision,
close a session, get help, or use one of the inventoried Main Branch workflows.

## Routes

{route_lines}

{route_guidance}

Use the route names above as product-facing workflow names. Do not introduce
legacy adapter names, installation internals, or command-surface vocabulary in
operator-facing answers.

## Grounding

Start in the current repo. Run the read-only facts that fit the route before
advice:

{fact_lines}

Run `command -v mb` and `mb --version` first when setup, update, repair, or
runtime readiness is uncertain. If `mb` is missing or reports an unexpected
version, stop and tell the operator to fix the runtime/login-shell PATH before
continuing.

Use `mb status --json --peek` as the default daily briefing source. It names
readiness, drift, onboarding progress, update state, GitHub activity, provider
signals, recent work, MoneyPath, ranked actions, bets, pushes, and checkpoint
state. Use `mb start --json` when runtime handoff or repo-boundary facts matter.

Stop before business routing if `runtime.codex_cli.status` is `runtime_mismatch`
or if any drift item is `codex_runtime_mb_mismatch`.

## Approval

Read-only fact commands can run without asking. Ask before durable writes,
checkpoints, updates, repairs, migrations, provider mutation, publishing, spend,
customer contact, destructive operations, or public issue/proposal submission.

## Boundaries

Codex supports the daily Main Branch routes listed here. Do not claim all Claude
Code skills, provider mutation, ads/site production, publishing, spend, customer
contact, or Claude Code command surfaces are available unless `mb workflow list
--runtime codex --json` and current runtime evidence say so.
"""


def agents_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / AGENTS_RELATIVE_PATH


def codex_skill_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / CODEX_SKILL_RELATIVE_PATH


def workflow_inventory_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH


def marketplace_path(repo: str | Path) -> Path:
    return global_plugin_source_root() / CODEX_MARKETPLACE_RELATIVE_PATH


def plugin_manifest_path(repo: str | Path) -> Path:
    return global_plugin_source_root() / CODEX_PLUGIN_MANIFEST_RELATIVE_PATH


def plugin_skill_path(repo: str | Path) -> Path:
    return global_plugin_source_root() / CODEX_PLUGIN_SKILL_RELATIVE_PATH


def plugin_commands_dir(repo: str | Path) -> Path:
    return global_plugin_source_root() / CODEX_PLUGIN_COMMANDS_RELATIVE_PATH


def plugin_command_path(repo: str | Path, name: str) -> Path:
    return plugin_commands_dir(repo) / f"{name}.md"


def executable_status() -> dict[str, Any]:
    path = _which("codex")
    return {
        "found": bool(path),
        "path": path,
        "executable": "codex",
        "repair": "" if path else "Install Codex CLI before using Main Branch in Codex.",
    }


def _run_codex_plugin_command(repo: Path, args: list[str]) -> dict[str, Any]:
    codex_path = _which("codex")
    command = [codex_path or "codex", *args]
    if not codex_path:
        return {
            "ok": False,
            "returncode": 127,
            "stdout": "",
            "stderr": "codex not on PATH",
            "command": " ".join(["codex", *args]),
        }
    try:
        proc = subprocess.run(
            command,
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "returncode": 124,
            "stdout": "",
            "stderr": "codex plugin command timed out",
            "command": " ".join(["codex", *args]),
        }
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        return {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": str(exc),
            "command": " ".join(["codex", *args]),
        }
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": " ".join(["codex", *args]),
    }


def _codex_plugin_list(repo: Path) -> dict[str, Any]:
    return _run_codex_plugin_command(
        repo,
        ["plugin", "list", "--marketplace", CODEX_MARKETPLACE_NAME],
    )


def _parse_plugin_install_status(output: str, expected_marketplace_path: Path) -> dict[str, Any]:
    lines = output.splitlines()
    actual_marketplace_path = ""
    for index, line in enumerate(lines):
        if line.strip() == f"Marketplace `{CODEX_MARKETPLACE_NAME}`":
            if index + 1 < len(lines):
                actual_marketplace_path = lines[index + 1].strip()
            break

    marketplace_registered = bool(
        actual_marketplace_path
        and Path(actual_marketplace_path).expanduser().resolve()
        == expected_marketplace_path.expanduser().resolve()
    )
    marketplace_stale = bool(actual_marketplace_path and not marketplace_registered)
    plugin_line = next((line.strip() for line in lines if CODEX_PLUGIN_SELECTOR in line), "")
    plugin_available = bool(plugin_line and marketplace_registered)
    status_text = plugin_line.split(CODEX_PLUGIN_SELECTOR, 1)[1].strip() if plugin_line else ""
    plugin_installed = bool(
        plugin_available and "installed" in status_text and "not installed" not in status_text
    )
    plugin_enabled = bool(plugin_installed and "enabled" in status_text)
    return {
        "marketplace_registered": marketplace_registered,
        "marketplace_stale": marketplace_stale,
        "marketplace_path": str(expected_marketplace_path),
        "registered_marketplace_path": actual_marketplace_path,
        "global_plugin_installed": plugin_installed,
        "plugin_available": plugin_available,
        "plugin_installed": plugin_installed,
        "plugin_enabled": plugin_enabled,
        "skill_available": False,
        "skill_ready": False,
        "slash_commands_ready": False,
        "plugin_line": plugin_line,
    }


def plugin_install_status(repo: str | Path, *, adapter_files_ok: bool = True) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    expected_marketplace_path = marketplace_path(target)
    install_command = CODEX_PLUGIN_INSTALL_COMMAND
    register_command = codex_marketplace_add_command()
    source_status = plugin_status(target)
    source_ok = source_status["ok"]
    if not _which("codex"):
        return {
            "checked": False,
            "ok": False,
            "state": "codex_missing",
            "summary": "Codex CLI is not installed, so plugin install state was not checked.",
            "marketplace_name": CODEX_MARKETPLACE_NAME,
            "plugin_selector": CODEX_PLUGIN_SELECTOR,
            "marketplace_registered": False,
            "marketplace_stale": False,
            "global_source_path": str(global_plugin_source_root()),
            "global_source_ok": source_ok,
            "plugin_available": False,
            "global_plugin_installed": False,
            "plugin_installed": False,
            "plugin_enabled": False,
            "command_files_current": bool(source_status.get("command_files_current", False)),
            "command_surface_ok": False,
            "slash_commands_likely_loaded": False,
            "slash_commands_restart_required": False,
            "skill_ready": False,
            "slash_commands_ready": False,
            "install_command": install_command,
            "register_command": register_command,
            "repair": "Install Codex CLI before using Main Branch Codex commands.",
            "safe_to_share": True,
        }
    if not adapter_files_ok:
        return {
            "checked": False,
            "ok": False,
            "state": "waiting_for_adapter_files",
            "summary": (
                "Codex plugin install check waits until repo AGENTS.md guidance is current."
            ),
            "marketplace_name": CODEX_MARKETPLACE_NAME,
            "plugin_selector": CODEX_PLUGIN_SELECTOR,
            "marketplace_registered": False,
            "marketplace_stale": False,
            "global_source_path": str(global_plugin_source_root()),
            "global_source_ok": source_ok,
            "plugin_available": False,
            "global_plugin_installed": False,
            "plugin_installed": False,
            "plugin_enabled": False,
            "command_files_current": bool(source_status.get("command_files_current", False)),
            "command_surface_ok": False,
            "slash_commands_likely_loaded": False,
            "slash_commands_restart_required": False,
            "skill_ready": False,
            "slash_commands_ready": False,
            "install_command": install_command,
            "register_command": register_command,
            "repair": CODEX_REPAIR_TEXT,
            "safe_to_share": True,
        }

    if not source_ok:
        return {
            "checked": True,
            "ok": False,
            "state": "global_plugin_source_missing",
            "summary": ("The global Main Branch Codex plugin source is missing or stale."),
            "marketplace_name": CODEX_MARKETPLACE_NAME,
            "plugin_selector": CODEX_PLUGIN_SELECTOR,
            "marketplace_registered": False,
            "marketplace_stale": False,
            "marketplace_path": str(expected_marketplace_path),
            "registered_marketplace_path": "",
            "global_source_path": str(global_plugin_source_root()),
            "global_source_ok": False,
            "plugin_available": False,
            "global_plugin_installed": False,
            "plugin_installed": False,
            "plugin_enabled": False,
            "slash_commands_ready": False,
            "command_files_current": bool(source_status.get("command_files_current", False)),
            "command_surface_ok": False,
            "slash_commands_likely_loaded": False,
            "slash_commands_restart_required": False,
            "skill_ready": False,
            "plugin_line": "",
            "install_command": install_command,
            "register_command": register_command,
            "repair": "Run `mb doctor repair --apply --only codex` to install the global plugin.",
            "safe_to_share": True,
        }

    result = _codex_plugin_list(target)
    parsed = _parse_plugin_install_status(
        str(result.get("stdout") or ""), expected_marketplace_path
    )
    command_files_current = bool(source_status.get("command_files_current"))
    state = "ok"
    summary = "Main Branch Codex commands are installed and ready after restarting Codex."
    repair = ""
    if not result["ok"]:
        state = "plugin_state_unverified"
        summary = "Codex plugin install state could not be checked."
        repair = f"Run `{register_command}`, then `{install_command}`."
    elif not parsed["marketplace_registered"]:
        state = "marketplace_not_registered"
        summary = (
            "The global Main Branch Codex plugin source is ready, but its Codex "
            "marketplace is not registered."
        )
        if parsed["marketplace_stale"]:
            summary = (
                "A `main-branch` Codex marketplace is registered, but it "
                "points at a different Main Branch plugin source."
            )
        repair = f"Run `{register_command}`, then `{install_command}`."
    elif not parsed["plugin_available"]:
        state = "plugin_not_available"
        summary = (
            "The global Main Branch Codex marketplace is registered, but the plugin is missing."
        )
        repair = f"Run `{register_command}`, then `{install_command}`."
    elif not parsed["plugin_installed"]:
        state = "plugin_not_installed"
        summary = (
            "The global Main Branch Codex plugin source is ready, but the plugin "
            "is not installed in Codex yet."
        )
        repair = f"Run `{install_command}`."
    elif not parsed["plugin_enabled"]:
        state = "plugin_disabled"
        summary = "The Main Branch Codex plugin is installed but not enabled."
        repair = f"Enable `{CODEX_PLUGIN_SELECTOR}` in Codex plugins."
    elif not command_files_current:
        state = "slash_commands_stale"
        summary = "Main Branch Codex command files are missing or stale."
        repair = CODEX_REPAIR_TEXT

    installed_enabled_current = bool(
        state == "ok"
        and command_files_current
        and parsed["plugin_installed"]
        and parsed["plugin_enabled"]
    )
    return {
        "checked": True,
        "ok": state == "ok",
        "state": state,
        "summary": summary,
        "marketplace_name": CODEX_MARKETPLACE_NAME,
        "plugin_selector": CODEX_PLUGIN_SELECTOR,
        **parsed,
        "global_source_path": str(global_plugin_source_root()),
        "global_source_ok": source_ok,
        "command_files": list(CODEX_SLASH_COMMAND_RELATIVE_PATHS),
        "command_files_current": command_files_current,
        "slash_commands_generated": command_files_current,
        "command_surface_ok": installed_enabled_current,
        "slash_commands_ready": installed_enabled_current,
        "slash_commands_likely_loaded": False,
        "slash_commands_restart_required": installed_enabled_current,
        "install_command": install_command,
        "register_command": register_command,
        "repair": repair,
        "command": result.get("command", ""),
        "returncode": result.get("returncode"),
        "error": str(result.get("stderr") or "").strip(),
        "safe_to_share": True,
    }


def install_plugin(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    source = write_global_plugin_source()
    steps = [
        _run_codex_plugin_command(target, ["plugin", "remove", CODEX_LEGACY_PLUGIN_SELECTOR]),
        _run_codex_plugin_command(
            target,
            ["plugin", "marketplace", "add", str(global_plugin_source_root())],
        ),
        _run_codex_plugin_command(target, ["plugin", "add", CODEX_PLUGIN_SELECTOR]),
    ]
    final = plugin_install_status(target)
    return {
        "ok": bool(final.get("ok")),
        "source": source,
        "steps": steps,
        "status": final,
        "safe_to_share": True,
    }


def global_skill_status(repo: str | Path) -> dict[str, Any]:
    """Return status for the global Main Branch Codex skill bundle."""

    expected_by_name = {
        name: render_codex_global_skill_md(name) for name in CODEX_GLOBAL_SKILL_NAMES
    }
    path_by_name = {name: global_skill_file_path(name) for name in CODEX_GLOBAL_SKILL_NAMES}
    missing = [f"{name}/SKILL.md" for name, path in path_by_name.items() if not path.is_file()]
    read_error = ""
    stale: list[str] = []
    missing_markers: list[str] = []
    skill_reports: dict[str, dict[str, Any]] = {}
    for skill_name, path in path_by_name.items():
        exists = path.is_file()
        text = ""
        skill_read_error = ""
        try:
            text = path.read_text(encoding="utf-8") if exists else ""
        except OSError as exc:
            skill_read_error = str(exc)
            read_error = skill_read_error
        markers = (
            f"name: {skill_name}",
            "user-invocable: true",
            "mb status --json --peek",
        )
        route_missing = [marker for marker in markers if marker not in text]
        if route_missing:
            missing_markers.extend(f"{skill_name}: {marker}" for marker in route_missing)
        if exists and not skill_read_error and text != expected_by_name[skill_name]:
            stale.append(f"{skill_name}/SKILL.md")
        skill_reports[skill_name] = {
            "ok": bool(
                exists
                and not route_missing
                and not skill_read_error
                and text == expected_by_name[skill_name]
            ),
            "exists": exists,
            "current": bool(exists and text == expected_by_name[skill_name]),
            "path": f"{skill_name}/SKILL.md",
            "absolute_path": str(path),
            "missing_markers": route_missing,
            "read_error": skill_read_error,
        }
    legacy_skill = global_skill_source_root() / CODEX_LEGACY_GLOBAL_SKILL_NAME
    if legacy_skill.exists():
        stale.append(CODEX_LEGACY_GLOBAL_SKILL_NAME)
    legacy_plugin = global_plugin_source_root()
    if legacy_plugin.exists():
        stale.append(str(legacy_plugin))
    ok = bool(not missing and not stale and not read_error and not missing_markers)
    return {
        "checked": True,
        "ok": ok,
        "state": "ok" if ok else "global_skill_missing_or_stale",
        "summary": (
            "The global Main Branch Codex skill bundle is installed and current."
            if ok
            else (
                "The global Main Branch Codex skill bundle is missing, stale, "
                "or has old plugin artifacts."
            )
        ),
        "name": CODEX_GLOBAL_SKILL_NAME,
        "display_name": "Main Branch",
        "path": CODEX_GLOBAL_SKILL_RELATIVE_PATH,
        "absolute_path": str(global_skill_path()),
        "skills_root": str(global_skill_source_root()),
        "exists": not missing,
        "current": bool(not stale and not missing_markers),
        "skills": skill_reports,
        "required_skills": list(CODEX_GLOBAL_SKILL_NAMES),
        "stale": stale,
        "missing": missing,
        "missing_markers": missing_markers,
        "read_error": read_error,
        "routes": list(CODEX_SLASH_COMMAND_NAMES),
        "repair": "" if ok else CODEX_REPAIR_TEXT,
        "repair_command": CODEX_REPAIR_COMMAND,
        "safe_to_share": True,
    }


def write_global_skill_source() -> dict[str, Any]:
    """Write the global Main Branch Codex skill bundle and remove old surfaces."""

    changed_paths: list[str] = []
    for name in CODEX_GLOBAL_SKILL_NAMES:
        path = global_skill_file_path(name)
        expected = render_codex_global_skill_md(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing != expected:
            path.write_text(expected, encoding="utf-8")
            changed_paths.append(str(path))

    legacy_skill = global_skill_source_root() / CODEX_LEGACY_GLOBAL_SKILL_NAME
    if _remove_generated_tree(legacy_skill):
        changed_paths.append(str(legacy_skill))

    plugin_root = global_plugin_source_root()
    if _remove_generated_tree(plugin_root):
        changed_paths.append(str(plugin_root))

    return {
        "ok": True,
        "path": str(global_skill_source_root()),
        "skills_root": str(global_skill_source_root()),
        "changed": bool(changed_paths),
        "changed_paths": changed_paths,
        "relative_paths": [f"{name}/SKILL.md" for name in CODEX_GLOBAL_SKILL_NAMES],
        "status": global_skill_status(Path.cwd()),
        "safe_to_share": True,
    }


def install_global_skill(repo: str | Path) -> dict[str, Any]:
    """Install or refresh the primary global Codex skill."""

    source = write_global_skill_source()
    final = global_skill_status(repo)
    return {
        "ok": bool(final.get("ok")),
        "source": source,
        "steps": [],
        "status": final,
        "safe_to_share": True,
    }


def plugin_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    marketplace = marketplace_path(target)
    manifest = plugin_manifest_path(target)
    expected_marketplace = render_codex_marketplace_json()
    expected_manifest = render_codex_plugin_manifest()
    expected_commands = render_codex_slash_commands()

    paths = {
        CODEX_MARKETPLACE_RELATIVE_PATH: marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: manifest,
        **{
            relative: global_plugin_source_root() / relative
            for relative in CODEX_SLASH_COMMAND_RELATIVE_PATHS
        },
    }
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    stale: list[str] = []
    read_errors: list[str] = []

    expected_by_path = {
        CODEX_MARKETPLACE_RELATIVE_PATH: expected_marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: expected_manifest,
        **expected_commands,
    }
    missing_markers: list[str] = []
    for relative, path in paths.items():
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            read_errors.append(f"{relative}: {exc}")
            continue
        if text != expected_by_path[relative]:
            stale.append(relative)
        if relative == CODEX_PLUGIN_MANIFEST_RELATIVE_PATH:
            missing_markers.extend(
                marker for marker in CODEX_PLUGIN_REQUIRED_MARKERS if marker not in text
            )
    legacy_plugin = global_plugin_source_root() / CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH
    if legacy_plugin.exists():
        stale.append(CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH)
    visible_skill_dir = global_plugin_source_root() / CODEX_PLUGIN_DIR_RELATIVE_PATH / "skills"
    if visible_skill_dir.exists():
        stale.append(f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/skills")
    command_files_current = not any(
        relative in missing or relative in stale for relative in CODEX_SLASH_COMMAND_RELATIVE_PATHS
    )

    ok = not missing and not stale and not read_errors and not missing_markers
    return {
        "ok": ok,
        "exists": not missing,
        "current": not stale and not missing_markers,
        "marketplace_path": CODEX_MARKETPLACE_RELATIVE_PATH,
        "manifest_path": CODEX_PLUGIN_MANIFEST_RELATIVE_PATH,
        "skill_path": "",
        "commands_path": CODEX_PLUGIN_COMMANDS_RELATIVE_PATH,
        "command_files": list(CODEX_SLASH_COMMAND_RELATIVE_PATHS),
        "command_files_current": command_files_current,
        "slash_commands_generated": command_files_current,
        "command_surface_ok": command_files_current,
        "slash_commands_ready": False,
        "missing": missing,
        "stale": stale,
        "missing_markers": missing_markers,
        "read_errors": read_errors,
        "repair": "" if ok else CODEX_REPAIR_TEXT,
        "repair_command": CODEX_REPAIR_COMMAND,
        "safe_to_share": True,
    }


def write_global_plugin_source() -> dict[str, Any]:
    """Write the global Main Branch Codex plugin source outside business repos."""

    root = global_plugin_source_root()
    marketplace = marketplace_path(root)
    manifest = plugin_manifest_path(root)
    expected_marketplace = render_codex_marketplace_json()
    expected_manifest = render_codex_plugin_manifest()
    expected_commands = render_codex_slash_commands()
    writes = {
        CODEX_MARKETPLACE_RELATIVE_PATH: (marketplace, expected_marketplace),
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: (manifest, expected_manifest),
        **{relative: (root / relative, text) for relative, text in expected_commands.items()},
    }
    changed_paths: list[str] = []
    for _relative, (path, text) in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing != text:
            path.write_text(text, encoding="utf-8")
            changed_paths.append(str(path))
    old_skill = root / CODEX_PLUGIN_DIR_RELATIVE_PATH / "skills"
    if _remove_generated_tree(old_skill):
        changed_paths.append(str(old_skill))
    old_plugin = root / CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH
    if _remove_generated_tree(old_plugin):
        changed_paths.append(str(old_plugin))
    commands_dir = root / CODEX_PLUGIN_COMMANDS_RELATIVE_PATH
    expected_names = {f"{name}.md" for name in CODEX_SLASH_COMMAND_NAMES}
    if commands_dir.is_dir():
        for path in commands_dir.iterdir():
            if path.is_file() and path.name not in expected_names:
                path.unlink()
                changed_paths.append(str(path))
    return {
        "ok": True,
        "path": str(root),
        "changed": bool(changed_paths),
        "changed_paths": changed_paths,
        "relative_paths": list(writes),
        "safe_to_share": True,
    }


def _remove_generated_tree(path: Path) -> bool:
    if path.is_dir():
        shutil.rmtree(path)
        return True
    if path.is_file():
        path.unlink()
        return True
    return False


def remove_repo_local_codex_plugin_files(repo: str | Path) -> list[str]:
    """Remove generated repo-local Codex plugin files from the transitional model."""

    target = Path(repo).expanduser().resolve()
    removed: list[str] = []
    for relative in (
        CODEX_PLUGIN_DIR_RELATIVE_PATH,
        CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH,
        CODEX_MARKETPLACE_RELATIVE_PATH,
        CODEX_SKILL_DIR_RELATIVE_PATH,
        ".agents/skills/main-branch",
    ):
        path = target / relative
        if _remove_generated_tree(path):
            removed.append(relative)
    for maybe_empty in (
        target / ".agents" / "plugins",
        target / ".agents" / "skills",
        target / ".agents",
    ):
        try:
            if maybe_empty.is_dir() and not any(maybe_empty.iterdir()):
                maybe_empty.rmdir()
        except OSError:
            pass
    return removed


def skill_status(repo: str | Path) -> dict[str, Any]:
    skill = global_skill_status(repo)
    return {
        "ok": bool(skill["ok"]),
        "exists": bool(skill["exists"]),
        "current": bool(skill["current"]),
        "path": skill["path"],
        "absolute_path": skill["absolute_path"],
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "missing_markers": skill["missing_markers"],
        "global_skill": skill,
        "plugin": plugin_status(repo),
        "read_error": skill["read_error"],
        "repair": skill["repair"],
        "repair_command": CODEX_REPAIR_COMMAND,
        "deprecated": False,
        "summary": ("The global Main Branch Codex skill is the supported Codex surface."),
        "safe_to_share": True,
    }


def instructions_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    path = agents_path(target)
    expected = render_agents_md(target)
    exists = path.is_file()
    try:
        text = path.read_text(encoding="utf-8") if exists else ""
    except OSError as exc:
        text = ""
        read_error = str(exc)
    else:
        read_error = ""
    missing_commands = [command for command in REQUIRED_FACT_COMMANDS if command not in text]
    approval_ok = "explicit operator approval" in text
    slash_ok = "Do not pretend Claude Code slash skills work in Codex." in text
    missing_lifecycle_guidance = [
        marker for marker in REQUIRED_LIFECYCLE_GUIDANCE_MARKERS if marker not in text
    ]
    for heading, markers in REQUIRED_LIFECYCLE_SECTION_MARKERS:
        section = _markdown_section(text, heading)
        missing_lifecycle_guidance.extend(marker for marker in markers if marker not in section)
    missing_lifecycle_guidance = list(dict.fromkeys(missing_lifecycle_guidance))
    lifecycle_discovery_ok = bool(exists and not missing_lifecycle_guidance)
    guidance_metadata = parse_guidance_metadata(text) if exists else {}
    expected_template_hash = guidance_template_hash()
    expected_guidance_metadata = guidance_metadata_comment(template_hash=expected_template_hash)
    guidance_schema_ok = guidance_metadata.get("schema") == str(CODEX_GUIDANCE_SCHEMA)
    guidance_template_hash_ok = guidance_metadata.get("template_hash") == expected_template_hash
    guidance_min_mb_ok = guidance_metadata.get("min_mb") == CODEX_GUIDANCE_MIN_MB
    guidance_metadata_ok = bool(
        exists and guidance_schema_ok and guidance_template_hash_ok and guidance_min_mb_ok
    )
    fact_grounding_ok = bool(
        exists and not missing_commands and approval_ok and slash_ok and lifecycle_discovery_ok
    )
    skill = skill_status(target)
    repo_local_plugin_paths = [
        relative
        for relative in (
            CODEX_SKILL_DIR_RELATIVE_PATH,
            ".agents/skills/main-branch",
            CODEX_MARKETPLACE_RELATIVE_PATH,
            CODEX_PLUGIN_DIR_RELATIVE_PATH,
            CODEX_LEGACY_PLUGIN_DIR_RELATIVE_PATH,
        )
        if (target / relative).exists()
    ]
    template_match = bool(exists and text == expected)
    current = bool(fact_grounding_ok and guidance_metadata_ok and not repo_local_plugin_paths)
    return {
        "ok": current,
        "exists": exists,
        "current": current,
        "template_match": template_match,
        "fact_grounding_ok": fact_grounding_ok,
        "guidance_metadata_ok": guidance_metadata_ok,
        "guidance_schema_ok": guidance_schema_ok,
        "guidance_template_hash_ok": guidance_template_hash_ok,
        "guidance_min_mb_ok": guidance_min_mb_ok,
        "guidance_metadata": guidance_metadata,
        "expected_guidance_metadata": expected_guidance_metadata,
        "expected_template_hash": expected_template_hash,
        "guidance_min_mb": CODEX_GUIDANCE_MIN_MB,
        "generated_version_ok": guidance_metadata_ok,
        "expected_version_marker": "",
        "path": AGENTS_RELATIVE_PATH,
        "absolute_path": str(path),
        "missing_fact_commands": missing_commands,
        "missing_lifecycle_guidance": missing_lifecycle_guidance,
        "repo_local_plugin_paths": repo_local_plugin_paths,
        "lifecycle_discovery_ok": lifecycle_discovery_ok,
        "skill": skill,
        "workflow_inventory": workflow_inventory(),
        "approval_boundary_ok": approval_ok,
        "codex_native_ok": slash_ok,
        "repair": "" if current else CODEX_REPAIR_TEXT,
        "repair_command": CODEX_REPAIR_COMMAND,
        "read_error": read_error,
        "safe_to_share": True,
    }


def _login_shell_mb_diagnostics() -> dict[str, Any]:
    return engine_mod.login_shell_mb_diagnostics()


def readiness(repo: str | Path) -> dict[str, Any]:
    executable = executable_status()
    instructions = instructions_status(repo)
    static_ok = bool(executable["found"] and instructions["ok"])
    runtime = _login_shell_mb_diagnostics()
    runtime_ok = bool(runtime.get("ok"))
    global_skill = global_skill_status(repo)
    global_skill_ok = bool(global_skill.get("ok"))
    plugin_install = {
        "checked": False,
        "ok": False,
        "state": "legacy_plugin_not_checked",
        "summary": "Codex plugin commands are legacy/experimental and not part of readiness.",
        "plugin_installed": False,
        "plugin_enabled": False,
        "command_files_current": False,
        "command_surface_ok": False,
        "slash_commands_ready": False,
        "slash_commands_likely_loaded": False,
        "slash_commands_restart_required": False,
        "repair": "",
        "safe_to_share": True,
    }
    plugin_ok = False
    slash_commands_ready = False
    command_surface_ok = global_skill_ok
    generated_guidance_ready = bool(instructions["ok"] and global_skill_ok)
    ok = bool(static_ok and runtime_ok and global_skill_ok)
    if ok:
        status = "ready"
    elif not executable["found"] or not instructions["ok"]:
        status = "needs_setup"
    elif runtime.get("mismatch"):
        status = "runtime_mismatch"
    elif runtime_ok and not global_skill_ok:
        status = str(global_skill.get("state") or "global_skill_missing_or_stale")
    else:
        status = "runtime_unverified"
    return {
        "ok": ok,
        "status": status,
        "support_level": CODEX_SUPPORT_LEVEL,
        "static_ok": static_ok,
        "runtime_ok": runtime_ok,
        "plugin_ok": plugin_ok,
        "global_skill_ok": global_skill_ok,
        "generated_guidance_ready": generated_guidance_ready,
        "command_surface_ok": command_surface_ok,
        "slash_commands_ready": slash_commands_ready,
        "global_skill": global_skill,
        "plugin_install": plugin_install,
        "runtime": runtime,
        "executable": executable,
        "instructions": instructions,
        "skill": instructions["skill"],
        "plugin": instructions["skill"]["plugin"],
        "workflow_inventory": workflow_inventory(),
        "fact_commands": list(REQUIRED_FACT_COMMANDS),
        "repair": ""
        if ok
        else (
            str(runtime.get("repair") or "")
            if static_ok and not runtime_ok
            else str(global_skill.get("repair") or "")
            if static_ok and runtime_ok and not global_skill_ok
            else instructions["repair"] or executable["repair"]
        ),
        "start_command": f"codex -C {shlex.quote(str(Path(repo).expanduser().resolve()))}",
        "smoke_command": (
            "codex exec --json --ephemeral --sandbox read-only "
            "-c 'approval_policy=\"never\"' "
            f"-C {shlex.quote(str(Path(repo).expanduser().resolve()))} "
            "'Start this Main Branch business day. Run only read-only mb checks "
            "and do not edit files.'"
        ),
        "safe_to_share": True,
    }


def human_readiness_label(readiness_report: dict[str, Any]) -> str:
    """Return a short user-facing Codex readiness label."""

    if readiness_report.get("ok"):
        return "ready"
    executable = readiness_report.get("executable") or {}
    if not executable.get("found"):
        return "missing"
    instructions = readiness_report.get("instructions") or {}
    if not instructions.get("ok"):
        return "needs setup"
    runtime = readiness_report.get("runtime") or {}
    if runtime.get("mismatch"):
        return "runtime mismatch"
    if not runtime.get("ok"):
        return "runtime unverified"
    global_skill = readiness_report.get("global_skill") or {}
    if not global_skill.get("ok"):
        return "skill not ready"
    plugin_install = readiness_report.get("plugin_install") or {}
    if not plugin_install.get("ok"):
        return "plugin optional"
    return "not ready"


def write_agents_md(
    repo: str | Path,
    *,
    name: str = "",
    gh_username: str = "",
) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    path = agents_path(target)
    rendered = render_agents_md(target, name=name, gh_username=gh_username)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    changed = existing != rendered
    changed_paths: list[str] = []
    if changed:
        path.write_text(rendered, encoding="utf-8")
        changed_paths.append(AGENTS_RELATIVE_PATH)

    removed_paths = remove_repo_local_codex_plugin_files(target)
    changed_paths.extend(f"removed:{path}" for path in removed_paths)
    return {
        "ok": True,
        "path": AGENTS_RELATIVE_PATH,
        "changed": bool(changed_paths),
        "changed_paths": changed_paths,
        "status": instructions_status(target),
    }
