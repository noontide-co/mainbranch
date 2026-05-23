"""Codex owner-loop adapter helpers.

Codex owner-loop support starts with repo instructions, the global plugin
surface, and deterministic ``mb`` facts. This module intentionally does not
invoke Codex or manage model conversation.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

from mb import __version__
from mb import engine as engine_mod

AGENTS_TEMPLATE = "AGENTS.md.tmpl"
AGENTS_RELATIVE_PATH = "AGENTS.md"
CODEX_SKILL_DIR_RELATIVE_PATH = ".agents/skills/main-branch-owner-loop"
CODEX_SKILL_RELATIVE_PATH = f"{CODEX_SKILL_DIR_RELATIVE_PATH}/SKILL.md"
CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH = (
    f"{CODEX_SKILL_DIR_RELATIVE_PATH}/references/workflow-inventory.md"
)
CODEX_MARKETPLACE_RELATIVE_PATH = ".agents/plugins/marketplace.json"
CODEX_MARKETPLACE_NAME = "main-branch"
CODEX_PLUGIN_NAME = "main-branch-owner-loop"
CODEX_PLUGIN_SELECTOR = f"{CODEX_PLUGIN_NAME}@{CODEX_MARKETPLACE_NAME}"
CODEX_PLUGIN_INSTALL_COMMAND = f"codex plugin add {CODEX_PLUGIN_SELECTOR}"
CODEX_PLUGIN_DIR_RELATIVE_PATH = f".agents/plugins/{CODEX_PLUGIN_NAME}"
CODEX_PLUGIN_LEGACY_COMMANDS_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/commands"
CODEX_PLUGIN_MANIFEST_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/.codex-plugin/plugin.json"
CODEX_PLUGIN_SKILL_RELATIVE_PATH = (
    f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/skills/main-branch-owner-loop/SKILL.md"
)
CODEX_SUPPORT_LEVEL = "supported_generated_guidance"
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
    "checks before owner-loop advice, repair planning, or writes."
)
REQUIRED_FACT_COMMANDS = (
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan",
)
OWNER_LOOP_COMMANDS = (
    "mb --version",
    "mb status --json --peek",
    "mb start --json",
    "mb doctor repair --plan --json",
    "mb update --check --json",
    "mb validate --json",
    "mb checkpoint --plan --json",
    "mb workflow list --runtime codex --json",
)
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
REQUIRED_LIFECYCLE_GUIDANCE = (
    "## Codex Lifecycle Workflow Index",
    "## Codex Status Workflow",
    "## Codex Think Route",
    f"Engine source workflow: `{CODEX_THINK_SOURCE_WORKFLOW}`",
    "does not need to contain that engine source file",
    "Shared source required `mb` commands",
    "runtime/login-shell PATH",
    "`runtime.codex_cli.status` is `runtime_mismatch`",
    "`codex_runtime_mb_mismatch`",
    "Shared source required JSON fact paths",
    "Shared source gates",
    "Shared public/private boundaries",
    "Use the global Main Branch Codex plugin",
    "do not claim these workflows are ported to",
    "generated Codex guidance",
    "/plugins",
)
REQUIRED_LIFECYCLE_GUIDANCE_MARKERS = (
    *REQUIRED_LIFECYCLE_GUIDANCE,
    *(f"- `{command}`" for command in CODEX_THINK_REQUIRED_MB_COMMANDS),
    *(f"- `{fact}`" for fact in CODEX_THINK_REQUIRED_JSON_FACTS),
    *(f"`{gate}`" for gate in CODEX_THINK_APPROVAL_GATES),
    *(f"`{boundary}`" for boundary in CODEX_THINK_PUBLIC_PRIVATE_BOUNDARIES),
)
CODEX_SKILL_REQUIRED_MARKERS = (
    "Main Branch owner loop for Codex",
    "mb workflow list --runtime codex --json",
    "runtime/login-shell PATH",
    "codex_runtime_mb_mismatch",
    "start/status/setup/update/doctor",
    "think/codify",
    "end/checkpoint/save",
    "Ask before durable writes",
)
CODEX_PLUGIN_REQUIRED_MARKERS = (
    "Main Branch",
    "skills",
    "main-branch-owner-loop",
    "mb facts",
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
CODEX_WORKFLOW_STATUS_VOCABULARY = (
    "supported",
    "pending_shared_source_migration",
    "generated_shell_pending",
    "intentionally_unsupported",
)

CODEX_WORKFLOW_INVENTORY: tuple[dict[str, Any], ...] = (
    {
        "id": "owner-loop-start-status",
        "label": "Start, status, and what changed",
        "claude_surface": "/mb-start, /mb-status",
        "claude_skill_sources": ("mb-start", "mb-status"),
        "codex_status": "supported",
        "codex_surface": ("Generated Codex guidance plus mb status/start facts"),
        "codex_entrypoints": ("Codex Start Workflow", "Codex Status Workflow"),
        "commands": ("mb status --json --peek", "mb start --json"),
        "notes": (
            "Codex starts from deterministic status/start facts, translates them "
            "into business language, and routes one next owner-loop move."
        ),
    },
    {
        "id": "owner-loop-setup-repair-update",
        "label": "Setup, update, doctor, and repair planning",
        "claude_surface": "/mb-setup, /mb-update, /mb-start repair routing",
        "claude_skill_sources": ("mb-setup", "mb-update"),
        "codex_status": "supported",
        "codex_surface": ("Generated Codex guidance plus mb setup/update/doctor fact commands"),
        "codex_entrypoints": ("Setup/update/doctor guidance",),
        "commands": (
            "mb --version",
            "mb doctor repair --plan --json",
            "mb update --check --json",
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
        "codex_surface": ("Generated Codex guidance plus AGENTS.md#codex-think-route"),
        "codex_entrypoints": ("Codex Think Route",),
        "shared_source": CODEX_THINK_SOURCE_WORKFLOW,
        "commands": CODEX_THINK_REQUIRED_MB_COMMANDS,
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
        "codex_surface": ("Generated Codex guidance plus mb checkpoint/validate facts"),
        "codex_entrypoints": ("End/checkpoint guidance",),
        "commands": ("mb checkpoint --plan --json", "mb validate --json"),
        "notes": (
            "Codex can plan a closeout and propose checkpoint subjects. Creating "
            "a checkpoint or editing files requires explicit approval."
        ),
    },
    {
        "id": "workflow-discovery",
        "label": "Workflow discovery and support inventory",
        "claude_surface": "/mb-help and docs",
        "claude_skill_sources": ("mb-help",),
        "codex_status": "supported",
        "codex_surface": ("Generated Codex guidance plus workflow inventory facts"),
        "codex_entrypoints": ("Workflow inventory guidance",),
        "commands": ("mb workflow list --runtime codex --json",),
        "notes": "Codex users can inspect supported, pending, and unsupported workflow surfaces.",
    },
    {
        "id": "bets",
        "label": "Bet lifecycle",
        "claude_surface": "/mb-bet",
        "claude_skill_sources": ("mb-bet",),
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only facts and business-file planning only",
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
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "commands": ("mb status --json --peek", "mb connect doctor --json"),
        "notes": "No provider mutation, spend, upload, or publishing is supported in Codex.",
    },
    {
        "id": "organic-content",
        "label": "Organic content and newsletter planning",
        "claude_surface": "/mb-organic and related playbooks",
        "claude_skill_sources": ("mb-organic",),
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
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
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning and site readiness facts only",
        "commands": ("mb status --json --peek", "mb site check --json"),
        "notes": "Codex must not claim site build, deploy, domain, or publishing parity.",
    },
    {
        "id": "wiki",
        "label": "Wiki and personal atomic notes",
        "claude_surface": "/mb-wiki",
        "claude_skill_sources": ("mb-wiki",),
        "codex_status": "intentionally_unsupported",
        "codex_surface": "None",
        "commands": (),
        "notes": "Specialty workflow outside the owner-loop support target.",
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
        "codex_surface": "None",
        "commands": (),
        "notes": "Engine-contributor workflow, not a business owner-loop runtime surface.",
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


def codex_marketplace_add_command() -> str:
    return f"codex plugin marketplace add {shlex.quote(str(global_plugin_source_root()))}"


_DEFAULT_AGENTS = """\
# {{BUSINESS_NAME}}

Main Branch business repo instructions for Codex.

## Codex Operating Contract

Main Branch CLI facts are the source of truth for repo health, setup, runtime
wiring, updates, graph/status signals, provider readiness, and repair paths.
When the operator asks to start, begin, get oriented, triage the day, or decide
what to do next, use this Codex-native start workflow or the generated Codex
guidance. Do not pretend Claude Code skills work in Codex.

Start in this repo. Before setup, routing, migration, update, or repair advice,
run the runtime preflight and read-only checks that fit the situation:

```bash
command -v mb
mb --version
mb status --json --peek
mb start --json
mb doctor repair --plan
```

This guidance was generated by Main Branch `{{MAINBRANCH_VERSION}}`. If
`mb --version` reports an older or different version, stop before status or
repair commands and tell the operator to put the current Main Branch install
earlier on the runtime/login-shell PATH.

After `mb status --json --peek` or `mb start --json`, stop if
`runtime.codex_cli.status` is `runtime_mismatch` or any `drift.items[].id`
equals `codex_runtime_mb_mismatch`. Treat that as a runtime `mb` mismatch: tell
the operator to fix the runtime/login-shell PATH and rerun read-only checks
before owner-loop advice, repair planning, or writes.

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

This tracked `AGENTS.md` file is the repo-level Codex bootstrap. The generated
Main Branch Codex plugin is installed globally once per user and supplies
generated Codex guidance over deterministic `mb` facts. Business repos keep this
lightweight `AGENTS.md` guidance instead of tracked repo-local plugin copies.
`mb doctor repair --only codex` refreshes this file and installs or repairs the
global plugin when Codex CLI is available.

Use the global Main Branch Codex plugin for the proven owner loop only. Do not
create repo-local Codex plugin manifests, copied Claude skill trees, or
symlinked Claude skills unless a future `mb` command or issue says that surface
is supported for this repo.

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

Use `/plugins` to inspect or install the global Main Branch plugin.

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
    mapping = {
        "BUSINESS_NAME": name.strip() or business_name(target),
        "GH_USERNAME": gh_username.strip() or _repo_owner(target),
        "MAINBRANCH_VERSION": __version__,
    }
    return _render(template, mapping)


def _commands_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    commands = item.get("commands") or ()
    if not isinstance(commands, tuple):
        return tuple(str(command) for command in commands)
    return tuple(str(command) for command in commands)


def _claude_skill_sources_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    sources = item.get("claude_skill_sources") or ()
    names = sources if isinstance(sources, tuple) else tuple(str(source) for source in sources)
    return tuple(f".claude/skills/{name}/SKILL.md" for name in names)


def workflow_inventory(*, runtime: str = "codex") -> dict[str, Any]:
    """Return the public-safe Main Branch workflow support inventory."""

    items = []
    for item in CODEX_WORKFLOW_INVENTORY:
        copied = dict(item)
        copied["commands"] = list(_commands_for_inventory_item(item))
        copied["claude_skill_sources"] = list(_claude_skill_sources_for_inventory_item(item))
        copied["codex_entrypoints"] = [
            str(entrypoint) for entrypoint in item.get("codex_entrypoints", ())
        ]
        items.append(copied)
    statuses = sorted(
        {*CODEX_WORKFLOW_STATUS_VOCABULARY}
        | {str(item["codex_status"]) for item in CODEX_WORKFLOW_INVENTORY}
    )
    return {
        "ok": True,
        "runtime": runtime,
        "support_level": CODEX_SUPPORT_LEVEL,
        "entrypoint": CODEX_SKILL_RELATIVE_PATH,
        "repo_guidance": AGENTS_RELATIVE_PATH,
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "claude_skill_sources": [
            f".claude/skills/{name}/SKILL.md" for name in CLAUDE_SKILL_SOURCE_NAMES
        ],
        "plugin": {
            "name": CODEX_PLUGIN_NAME,
            "marketplace_name": CODEX_MARKETPLACE_NAME,
            "plugin_selector": CODEX_PLUGIN_SELECTOR,
            "marketplace_path": CODEX_MARKETPLACE_RELATIVE_PATH,
            "manifest_path": CODEX_PLUGIN_MANIFEST_RELATIVE_PATH,
            "skill_path": CODEX_PLUGIN_SKILL_RELATIVE_PATH,
            "slash_commands_ready": False,
            "install_hint": (
                f"Run `{codex_marketplace_add_command()}`, then `{CODEX_PLUGIN_INSTALL_COMMAND}`."
            ),
        },
        "statuses": statuses,
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
            f"`{source}`" for source in _claude_skill_sources_for_inventory_item(item)
        )
        row_template = (
            "| {label} | `{status}` | {claude} | {sources} | {codex} | {entrypoints} | {commands} |"
        )
        rows.append(
            row_template.format(
                label=item["label"],
                status=item["codex_status"],
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
        "Main Branch workflow surfaces to the Codex daily-loop support boundary.\n\n"
        "Status meanings:\n\n"
        "- `supported`: Codex can use this surface for the owner loop from "
        "deterministic `mb` facts and generated guidance.\n"
        "- `pending_shared_source_migration`: Codex may plan from read-only facts, "
        "but a runtime shell should wait for a shared workflow source.\n"
        "- `generated_shell_pending`: a shared source exists, but a generated Codex "
        "shell still needs implementation and smoke evidence.\n"
        "- `intentionally_unsupported`: outside the current Codex daily-loop target.\n\n"
        "Codex plugin files are installed globally by `mb doctor repair --only codex`; "
        "business repos keep only lightweight `AGENTS.md` guidance. Use `/plugins` "
        "or `codex plugin list --marketplace main-branch` to inspect the global "
        "Main Branch Codex plugin. Each row names its bundled Claude skill "
        "source(s); every bundled Claude `mb-*` skill must be accounted for here "
        "until the shared workflow generator owns both runtime shells.\n\n"
        "| Workflow | Codex status | Claude Code surface | Claude source | Codex surface | "
        "Codex route | Fact commands |\n"
        "|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        "Codex must ask before durable writes, checkpoints, repairs, updates, "
        "migrations, provider mutation, publishing, spend, customer contact, or "
        "public issue/proposal submission.\n"
    )


def render_codex_skill_md() -> str:
    """Render the Codex guidance packaged as a skill."""

    command_lines = "\n".join(f"- `{command}`" for command in OWNER_LOOP_COMMANDS)
    description = (
        "Use when the operator asks Codex to run the Main Branch daily owner loop "
        "from a business repo: start/status/setup/update/doctor, think/codify, "
        "end/checkpoint/save, validate, or workflow discovery. Starts from "
        "deterministic mb facts and asks before durable writes, provider mutations, "
        "publishing, spend, customer contact, or checkpoints."
    )
    return f"""---
name: main-branch-owner-loop
description: >-
  {description}
---

# Main Branch daily loop for Codex

Run the Main Branch daily owner loop from a business repo. This is generated
Codex guidance packaged in the global Main Branch plugin; `AGENTS.md` remains
the repo-level bootstrap.

## Start Here

Before advice, run read-only facts that fit the request:

{command_lines}

Run `command -v mb` and `mb --version` as a standalone runtime preflight before
substantive `mb` commands. This guidance was generated by Main Branch
`{__version__}`. If the runtime reports an older or different version, stop and
tell the operator to put the current Main Branch install earlier on the
runtime/login-shell PATH before continuing.

{CODEX_RUNTIME_MISMATCH_STOP_TEXT}

Use `mb status --json --peek` as the first daily read. Use `mb start --json`
when runtime handoff or adapter readiness matters. Use
`mb workflow list --runtime codex --json` when the operator asks what Codex can
do.

## Supported Daily Loop

- start/status/setup/update/doctor: inspect facts and plans, then ask before
  applying repairs, migrations, setup writes, or updates.
- think/codify: follow the `mb-think` shared workflow route in `AGENTS.md`.
- end/checkpoint/save: run `mb checkpoint --plan --json`, propose a
  business-readable checkpoint, and ask before saving it.
- validate: run `mb validate --json` and explain repo health in business
  language before technical details.
- workflow discovery: read `references/workflow-inventory.md` or run
  `mb workflow list --runtime codex --json`.

## Approval Gates

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations, raw
private-source reads, or public issue/proposal submission.

Do not claim Claude Code slash-skill parity in Codex. Do not claim ads, site,
organic, provider mutation, wiki, or skill-authoring parity unless the
inventory marks that surface `supported`.
"""


def render_codex_plugin_manifest() -> str:
    """Render the global Codex plugin manifest."""

    payload = {
        "name": CODEX_PLUGIN_NAME,
        "version": "0.1.0",
        "description": (
            "Main Branch daily-loop guidance for Codex. Uses deterministic mb facts "
            "and generated business-repo guidance."
        ),
        "author": {"name": "Noontide"},
        "homepage": "https://github.com/noontide-co/mainbranch",
        "repository": "https://github.com/noontide-co/mainbranch",
        "license": "MIT",
        "keywords": ["main-branch", "mainbranch", "owner-loop", "business-memory"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Main Branch",
            "shortDescription": "Start, inspect, decide, and checkpoint from mb facts",
            "longDescription": (
                "Adds Codex-native guidance for Main Branch business repos. The plugin "
                "routes through generated guidance and direct mb facts; it does not add "
                "provider mutation, publishing, spend, customer contact, ads/site "
                "production, or all-skill parity."
            ),
            "developerName": "Noontide",
            "category": "Productivity",
            "capabilities": ["Interactive", "Read", "Write"],
            "websiteURL": "https://github.com/noontide-co/mainbranch",
            "defaultPrompt": [
                "Start this Main Branch business day from mb facts",
                "Show what Main Branch workflows Codex supports",
                "Plan a Main Branch checkpoint before saving work",
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


def render_codex_plugin_skill_md() -> str:
    """Render the plugin-packaged Codex guidance.

    Keep this equal to the generated project-local skill so drift tests catch
    accidental second-source behavior.
    """

    return render_codex_skill_md()


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


def executable_status() -> dict[str, Any]:
    path = _which("codex")
    return {
        "found": bool(path),
        "path": path,
        "executable": "codex",
        "repair": "" if path else "Install Codex CLI before using the Codex owner-loop adapter.",
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
    skill_ready = bool(plugin_installed and plugin_enabled)
    return {
        "marketplace_registered": marketplace_registered,
        "marketplace_stale": marketplace_stale,
        "marketplace_path": str(expected_marketplace_path),
        "registered_marketplace_path": actual_marketplace_path,
        "global_plugin_installed": plugin_installed,
        "plugin_available": plugin_available,
        "plugin_installed": plugin_installed,
        "plugin_enabled": plugin_enabled,
        "skill_ready": skill_ready,
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
            "skill_ready": False,
            "slash_commands_ready": False,
            "install_command": install_command,
            "register_command": register_command,
            "repair": "Install Codex CLI before using the Codex owner-loop adapter.",
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
    state = "ok"
    summary = "Codex plugin is installed and enabled; generated Codex guidance is available."
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


def plugin_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    marketplace = marketplace_path(target)
    manifest = plugin_manifest_path(target)
    skill = plugin_skill_path(target)
    expected_marketplace = render_codex_marketplace_json()
    expected_manifest = render_codex_plugin_manifest()
    expected_skill = render_codex_plugin_skill_md()

    paths = {
        CODEX_MARKETPLACE_RELATIVE_PATH: marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: manifest,
        CODEX_PLUGIN_SKILL_RELATIVE_PATH: skill,
    }
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    stale: list[str] = []
    read_errors: list[str] = []

    expected_by_path = {
        CODEX_MARKETPLACE_RELATIVE_PATH: expected_marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: expected_manifest,
        CODEX_PLUGIN_SKILL_RELATIVE_PATH: expected_skill,
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
    legacy_commands = global_plugin_source_root() / CODEX_PLUGIN_LEGACY_COMMANDS_RELATIVE_PATH
    if legacy_commands.exists():
        stale.append(CODEX_PLUGIN_LEGACY_COMMANDS_RELATIVE_PATH)

    ok = not missing and not stale and not read_errors and not missing_markers
    return {
        "ok": ok,
        "exists": not missing,
        "current": not stale and not missing_markers,
        "marketplace_path": CODEX_MARKETPLACE_RELATIVE_PATH,
        "manifest_path": CODEX_PLUGIN_MANIFEST_RELATIVE_PATH,
        "skill_path": CODEX_PLUGIN_SKILL_RELATIVE_PATH,
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
    skill = plugin_skill_path(root)
    expected_marketplace = render_codex_marketplace_json()
    expected_manifest = render_codex_plugin_manifest()
    expected_skill = render_codex_plugin_skill_md()
    writes = {
        CODEX_MARKETPLACE_RELATIVE_PATH: (marketplace, expected_marketplace),
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: (manifest, expected_manifest),
        CODEX_PLUGIN_SKILL_RELATIVE_PATH: (skill, expected_skill),
    }
    changed_paths: list[str] = []
    for _relative, (path, text) in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing != text:
            path.write_text(text, encoding="utf-8")
            changed_paths.append(str(path))
    old_commands = root / CODEX_PLUGIN_LEGACY_COMMANDS_RELATIVE_PATH
    if _remove_generated_tree(old_commands):
        changed_paths.append(str(old_commands))
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
        CODEX_MARKETPLACE_RELATIVE_PATH,
        CODEX_SKILL_DIR_RELATIVE_PATH,
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
    plugin = plugin_status(repo)
    return {
        "ok": True,
        "exists": False,
        "current": True,
        "path": CODEX_SKILL_RELATIVE_PATH,
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "missing_markers": [],
        "plugin": plugin,
        "read_error": "",
        "repair": "",
        "repair_command": CODEX_REPAIR_COMMAND,
        "deprecated": True,
        "summary": (
            "Repo-local Codex guidance files are no longer required; the Main Branch "
            "Codex plugin is installed globally."
        ),
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
    slash_ok = "Do not pretend Claude Code skills work in Codex." in text
    missing_lifecycle_guidance = [
        marker for marker in REQUIRED_LIFECYCLE_GUIDANCE_MARKERS if marker not in text
    ]
    lifecycle_discovery_ok = bool(exists and not missing_lifecycle_guidance)
    fact_grounding_ok = bool(
        exists and not missing_commands and approval_ok and slash_ok and lifecycle_discovery_ok
    )
    skill = skill_status(target)
    repo_local_plugin_paths = [
        relative
        for relative in (
            CODEX_SKILL_DIR_RELATIVE_PATH,
            CODEX_MARKETPLACE_RELATIVE_PATH,
            CODEX_PLUGIN_DIR_RELATIVE_PATH,
        )
        if (target / relative).exists()
    ]
    template_match = bool(exists and text == expected)
    current = bool(fact_grounding_ok and not repo_local_plugin_paths)
    return {
        "ok": current,
        "exists": exists,
        "current": current,
        "template_match": template_match,
        "fact_grounding_ok": fact_grounding_ok,
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
    plugin_install = plugin_install_status(repo, adapter_files_ok=bool(instructions["ok"]))
    plugin_ok = bool(plugin_install.get("ok"))
    slash_commands_ready = bool(plugin_install.get("slash_commands_ready"))
    generated_guidance_ready = bool(plugin_ok and plugin_install.get("skill_ready"))
    command_surface_ok = generated_guidance_ready
    ok = bool(static_ok and runtime_ok and generated_guidance_ready)
    if ok:
        status = "ready"
    elif not executable["found"] or not instructions["ok"]:
        status = "needs_setup"
    elif runtime.get("mismatch"):
        status = "runtime_mismatch"
    elif runtime_ok and not plugin_ok:
        status = str(plugin_install.get("state") or "plugin_not_installed")
    else:
        status = "runtime_unverified"
    return {
        "ok": ok,
        "status": status,
        "support_level": CODEX_SUPPORT_LEVEL,
        "static_ok": static_ok,
        "runtime_ok": runtime_ok,
        "plugin_ok": plugin_ok,
        "generated_guidance_ready": generated_guidance_ready,
        "command_surface_ok": command_surface_ok,
        "slash_commands_ready": slash_commands_ready,
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
            else str(plugin_install.get("repair") or "")
            if static_ok and runtime_ok and not plugin_ok
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
    plugin_install = readiness_report.get("plugin_install") or {}
    if not plugin_install.get("ok"):
        if plugin_install.get("state") == "plugin_not_installed":
            return "plugin not installed"
        if plugin_install.get("state") == "marketplace_not_registered":
            return "marketplace missing"
        return "plugin not ready"
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
