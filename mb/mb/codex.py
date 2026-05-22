"""Codex owner-loop adapter helpers.

Codex owner-loop support starts with repo instructions, the repo-scoped plugin
surface, and deterministic ``mb`` facts. This module intentionally does not
invoke Codex or manage model conversation.
"""

from __future__ import annotations

import json
import shlex
import shutil
from importlib import resources
from pathlib import Path
from typing import Any

AGENTS_TEMPLATE = "AGENTS.md.tmpl"
AGENTS_RELATIVE_PATH = "AGENTS.md"
CODEX_SKILL_DIR_RELATIVE_PATH = ".agents/skills/main-branch-owner-loop"
CODEX_SKILL_RELATIVE_PATH = f"{CODEX_SKILL_DIR_RELATIVE_PATH}/SKILL.md"
CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH = (
    f"{CODEX_SKILL_DIR_RELATIVE_PATH}/references/workflow-inventory.md"
)
CODEX_MARKETPLACE_RELATIVE_PATH = ".agents/plugins/marketplace.json"
CODEX_PLUGIN_NAME = "main-branch-owner-loop"
CODEX_PLUGIN_DIR_RELATIVE_PATH = f".agents/plugins/{CODEX_PLUGIN_NAME}"
CODEX_PLUGIN_MANIFEST_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/.codex-plugin/plugin.json"
CODEX_PLUGIN_SKILL_RELATIVE_PATH = (
    f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/skills/main-branch-owner-loop/SKILL.md"
)
CODEX_PLUGIN_COMMANDS_RELATIVE_PATH = f"{CODEX_PLUGIN_DIR_RELATIVE_PATH}/commands"
CODEX_COMMAND_NAMES = (
    "mb-start",
    "mb-status",
    "mb-setup",
    "mb-update",
    "mb-doctor",
    "mb-think",
    "mb-end",
    "mb-checkpoint",
    "mb-validate",
    "mb-workflows",
    "mb-help",
)
CODEX_PLUGIN_COMMAND_RELATIVE_PATHS = tuple(
    f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md" for name in CODEX_COMMAND_NAMES
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
    "Shared source required JSON fact paths",
    "Shared source gates",
    "Shared public/private boundaries",
    "Use `.agents/skills/main-branch-owner-loop`",
    "do not claim these workflows are ported to",
    "generated Codex plugin is installed",
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
    "start/status/setup/update/doctor",
    "think/codify",
    "end/checkpoint/save",
    "Ask before durable writes",
)
CODEX_PLUGIN_REQUIRED_MARKERS = (
    "Main Branch Owner Loop",
    "skills",
    "main-branch-owner-loop",
    "mb facts",
)
CODEX_COMMAND_REQUIRED_MARKERS = (
    "Main Branch owner-loop skill",
    "mb status --json --peek",
    "mb start --json",
    "Ask before",
    "provider mutation",
    "publishing",
    "customer contact",
)
CODEX_WORKFLOW_STATUS_VOCABULARY = (
    "supported",
    "pending_shared_source_migration",
    "generated_shell_pending",
    "intentionally_unsupported",
)

CODEX_COMMAND_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "mb-start",
        "title": "Main Branch Start",
        "description": "Start the Main Branch owner loop from direct mb facts.",
        "route": "Start/status/setup/update/doctor",
        "commands": ("mb status --json --peek", "mb start --json", "mb doctor repair --plan"),
        "task": (
            "Orient the operator, name the top business route, and ask before any "
            "repair, update, setup write, file write, checkpoint, provider mutation, "
            "publishing, spend, customer contact, or public issue/proposal submission."
        ),
    },
    {
        "name": "mb-status",
        "title": "Main Branch Status",
        "description": "Summarize current business state and what changed.",
        "route": "Start/status/setup/update/doctor",
        "commands": ("mb status --json --peek", "mb start --json"),
        "task": (
            "Summarize ranked actions, since-last-check changes, readiness, drift, "
            "MoneyPath, content strategy, integrations, bets, pushes, vocabulary, "
            "and checkpoint state from the JSON facts."
        ),
    },
    {
        "name": "mb-setup",
        "title": "Main Branch Setup",
        "description": "Use onboarding facts to continue first-run setup.",
        "route": "Start/status/setup/update/doctor",
        "commands": ("mb --version", "mb status --json --peek", "mb start --json"),
        "task": (
            "Treat setup guides or pasted folder descriptions as setup intent. "
            "Explain which folder becomes the business brain and ask before any "
            "onboarding or GitHub setup write."
        ),
    },
    {
        "name": "mb-update",
        "title": "Main Branch Update",
        "description": "Plan a Main Branch update without applying it first.",
        "route": "Start/status/setup/update/doctor",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb update --check --json",
        ),
        "task": (
            "Report installed/latest version facts, release-note context when present, "
            "and the exact update command. Ask before running update or repair commands."
        ),
    },
    {
        "name": "mb-doctor",
        "title": "Main Branch Doctor",
        "description": "Inspect repairable repo drift before applying fixes.",
        "route": "Start/status/setup/update/doctor",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb doctor repair --plan --json",
        ),
        "task": (
            "Explain repair plan actions in business language. Applying repairs, "
            "migrations, or runtime wiring writes requires explicit approval."
        ),
    },
    {
        "name": "mb-think",
        "title": "Main Branch Think",
        "description": "Route research, decisions, and codification through mb-think.",
        "route": "Think/codify",
        "commands": CODEX_THINK_REQUIRED_MB_COMMANDS,
        "task": (
            "Use the shared mb-think route in AGENTS.md, choose the smallest honest "
            "research depth, preserve source privacy, and ask before codifying files "
            "or opening public issues/proposals."
        ),
    },
    {
        "name": "mb-end",
        "title": "Main Branch End",
        "description": "Close a session with a checkpoint/save plan.",
        "route": "End/checkpoint/save",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb checkpoint --plan --json",
            "mb validate --json",
        ),
        "task": (
            "Summarize what changed, propose next memory updates or checkpoint subjects, "
            "and ask before writing files or saving a checkpoint."
        ),
    },
    {
        "name": "mb-checkpoint",
        "title": "Main Branch Checkpoint",
        "description": "Plan a business-readable saved checkpoint.",
        "route": "End/checkpoint/save",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb checkpoint --plan --json",
            "mb validate --json",
        ),
        "task": (
            "Use checkpoint facts to propose a concise business-readable subject. "
            "Creating the checkpoint requires explicit operator approval."
        ),
    },
    {
        "name": "mb-validate",
        "title": "Main Branch Validate",
        "description": "Validate business repo health from JSON facts.",
        "route": "Validate",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb validate --json",
        ),
        "task": (
            "Explain validation health in business language first, then cite technical "
            "paths or repair commands. Ask before editing files."
        ),
    },
    {
        "name": "mb-workflows",
        "title": "Main Branch Workflows",
        "description": "Show supported, pending, and unsupported Codex surfaces.",
        "route": "Workflow discovery",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb workflow list --runtime codex --json",
        ),
        "task": (
            "List supported owner-loop surfaces, pending shared-source migrations, "
            "and intentionally unsupported workflows without overclaiming parity."
        ),
    },
    {
        "name": "mb-help",
        "title": "Main Branch Help",
        "description": "Answer Main Branch support questions from runtime inventory.",
        "route": "Workflow discovery",
        "commands": (
            "mb status --json --peek",
            "mb start --json",
            "mb workflow list --runtime codex --json",
        ),
        "task": (
            "Answer from the generated owner-loop skill, workflow inventory, and mb "
            "facts. Name unsupported provider/publishing/spend/customer-contact "
            "boundaries plainly."
        ),
    },
)

CODEX_WORKFLOW_INVENTORY: tuple[dict[str, Any], ...] = (
    {
        "id": "owner-loop-start-status",
        "label": "Start, status, and what changed",
        "claude_surface": "/mb-start, /mb-status",
        "codex_status": "supported",
        "codex_surface": "Codex plugin commands /mb-start and /mb-status",
        "codex_entrypoints": ("mb-start", "mb-status"),
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
        "codex_status": "supported",
        "codex_surface": "Codex plugin commands /mb-setup, /mb-update, and /mb-doctor",
        "codex_entrypoints": ("mb-setup", "mb-update", "mb-doctor"),
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
        "codex_status": "supported",
        "codex_surface": "Codex plugin command /mb-think and AGENTS.md#codex-think-route",
        "codex_entrypoints": ("mb-think",),
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
        "codex_status": "supported",
        "codex_surface": "Codex plugin commands /mb-end and /mb-checkpoint",
        "codex_entrypoints": ("mb-end", "mb-checkpoint"),
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
        "codex_status": "supported",
        "codex_surface": "Codex plugin commands /mb-workflows and /mb-help",
        "codex_entrypoints": ("mb-workflows", "mb-help"),
        "commands": ("mb workflow list --runtime codex --json",),
        "notes": "Codex users can inspect supported, pending, and unsupported workflow surfaces.",
    },
    {
        "id": "bets",
        "label": "Bet lifecycle",
        "claude_surface": "/mb-bet",
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
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning only",
        "commands": ("mb status --json --peek", "mb connect doctor --json"),
        "notes": "No provider mutation, spend, upload, or publishing is supported in Codex.",
    },
    {
        "id": "organic-content",
        "label": "Organic content and newsletter planning",
        "claude_surface": "/mb-organic and related playbooks",
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
        "codex_status": "pending_shared_source_migration",
        "codex_surface": "Read-only planning and site readiness facts only",
        "commands": ("mb status --json --peek", "mb site check --json"),
        "notes": "Codex must not claim site build, deploy, domain, or publishing parity.",
    },
    {
        "id": "wiki",
        "label": "Wiki and personal atomic notes",
        "claude_surface": "/mb-wiki",
        "codex_status": "intentionally_unsupported",
        "codex_surface": "None",
        "commands": (),
        "notes": "Specialty workflow outside the owner-loop support target.",
    },
    {
        "id": "skill-authoring",
        "label": "Skill concept, draft, and review",
        "claude_surface": "/mb-skill-concept, /mb-skill-brief-draft, /mb-skill-review",
        "codex_status": "intentionally_unsupported",
        "codex_surface": "None",
        "commands": (),
        "notes": "Engine-contributor workflow, not a business owner-loop runtime surface.",
    },
)


_DEFAULT_AGENTS = """\
# {{BUSINESS_NAME}}

Main Branch business repo instructions for Codex.

## Codex Operating Contract

Main Branch CLI facts are the source of truth for repo health, setup, runtime
wiring, updates, graph/status signals, provider readiness, and repair paths.
When the operator asks to start, begin, get oriented, triage the day, or decide
what to do next, use this Codex-native start workflow or the generated Codex
plugin command surface. Do not pretend Claude Code skills work in Codex.

Start in this repo. Before setup, routing, migration, update, or repair advice,
run the read-only checks that fit the situation:

```bash
mb --version
mb status --json --peek
mb start --json
mb doctor repair --plan
```

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
project-local skill at `.agents/skills/main-branch-owner-loop/SKILL.md` plus
the repo-scoped plugin at `.agents/plugins/main-branch-owner-loop/` are the
Codex-native owner-loop discovery surfaces. They are owned by `mb init`,
`mb onboard`, `mb doctor repair`, and the operator. Keep them compact: route to
lifecycle workflows and `mb` facts, but do not duplicate the full Main Branch
skill tree.

Use `.agents/skills/main-branch-owner-loop` for the proven owner loop only. Do
not create additional Codex plugin manifests, copied Claude skill trees, or
symlinked Claude skills unless a future `mb` command or issue says that surface
is supported for this repo.

Use this index to map natural Codex requests:

- **Start the day / what next / get oriented:** use `/mb-start` when the
  generated Codex plugin is installed, or the Codex Start Workflow below. Run
  `mb status --json --peek` first, then `mb start --json` when runtime handoff
  or adapter-readiness facts matter.
- **Inspect status / what changed / what is stale:** use `/mb-status` when the
  generated Codex plugin is installed, or the Codex Status Workflow below.
  Answer from `ranked_actions`, `since_last_check`, `journal`, `money_path`,
  `content_strategy`, `integrations`, `readiness`, and `drift.items`.
- **Think / research / decide / codify:** use `/mb-think` when the generated
  Codex plugin is installed, or the Codex Think Route below. Start from `mb`
  facts, choose a research depth, and ask before writing durable business files.
- **Site, ads, organic production, provider mutation, publishing, spend,
  domains, or customer contact:** do not claim these workflows are ported to
  Codex. Use read-only `mb` facts for planning and ask before any action.

The generated plugin also exposes `/mb-setup`, `/mb-update`, `/mb-doctor`,
`/mb-end`, `/mb-checkpoint`, `/mb-validate`, `/mb-workflows`, and `/mb-help`
as thin command shims over this owner-loop contract. Use `/plugins` to inspect
or install the Main Branch Owner Loop plugin from this repo.

## Codex Start Workflow

This is the Codex-native port behind `/mb-start`.

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
4. Run `mb doctor repair --plan` before recommending setup or repair. Quote the
   exact repair command from the plan. Ask before any write/apply command.
5. If status says an update is required, route to the cited `mb update` command
   and ask before running it. After an approved update, rerun
   `mb status --json --peek`.
6. Resume onboarding from status facts. In rich repos, read existing `core/`
   files before asking bounded missing-profile questions.
7. Present one clear business route: frame a bet, think through a decision,
   advance a push, draft a playbook, repair the repo, review provider
   readiness, save a checkpoint, or inspect a specific offer.

Use numbered lists for operator choices, with one active choice namespace per
turn. If the operator replies with an ambiguous number, ask what they meant
before acting.

## Codex Status Workflow

This is the Codex-native status route behind `/mb-status`.

1. Run `mb status --json --peek`.
2. Treat the JSON as the source of truth for setup, update, drift, GitHub,
   onboarding, integrations, bets, recent work, since-last-check,
   `content_strategy`, `money_path`, vocabulary, checkpoint state, and
   `ranked_actions`.
3. Lead with the top `ranked_actions` entry when the operator asks what to do
   next. Include the reason and cited signal summaries.
4. For "what changed?" answer from `since_last_check.journal` first, then
   top-level `journal` for recent context.
5. For provider questions, read `integrations` first. Run `mb connect plan` or
   `mb connect doctor --json` only when the operator needs choices or repair
   commands.
6. Use `money_path` for customer progress, offer, proof, CTA, channel, push,
   playbook, page readiness, and outcome feedback questions. Keep language
   evidence-based: legible, supported, connected, instrumented.
7. Use `content_strategy` for content strategy health, layered channel/account
   files, stale platform rules, or disconnected content layers.

Do not mutate the last-check marker unless the operator explicitly says this is
the daily check-in and wants it recorded.

## Codex Think Route

This is Codex-native guidance for the existing `mb-think` shared workflow
source. When the generated Main Branch Owner Loop plugin is installed, this is
the fallback route behind `/mb-think`; without the plugin, treat this section as
the natural-language Codex route. It does not mean all Main Branch skills work
in Codex.

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
    }
    return _render(template, mapping)


def _commands_for_inventory_item(item: dict[str, Any]) -> tuple[str, ...]:
    commands = item.get("commands") or ()
    if not isinstance(commands, tuple):
        return tuple(str(command) for command in commands)
    return tuple(str(command) for command in commands)


def workflow_inventory(*, runtime: str = "codex") -> dict[str, Any]:
    """Return the public-safe Main Branch workflow support inventory."""

    items = []
    for item in CODEX_WORKFLOW_INVENTORY:
        copied = dict(item)
        copied["commands"] = list(_commands_for_inventory_item(item))
        copied["codex_entrypoints"] = [
            f"/{entrypoint}" for entrypoint in item.get("codex_entrypoints", ())
        ]
        items.append(copied)
    statuses = sorted(
        {*CODEX_WORKFLOW_STATUS_VOCABULARY}
        | {str(item["codex_status"]) for item in CODEX_WORKFLOW_INVENTORY}
    )
    return {
        "ok": True,
        "runtime": runtime,
        "support_level": "first_class_owner_loop",
        "entrypoint": CODEX_SKILL_RELATIVE_PATH,
        "repo_guidance": AGENTS_RELATIVE_PATH,
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "plugin": {
            "name": CODEX_PLUGIN_NAME,
            "marketplace_path": CODEX_MARKETPLACE_RELATIVE_PATH,
            "manifest_path": CODEX_PLUGIN_MANIFEST_RELATIVE_PATH,
            "skill_path": CODEX_PLUGIN_SKILL_RELATIVE_PATH,
            "command_paths": list(CODEX_PLUGIN_COMMAND_RELATIVE_PATHS),
            "commands": [f"/{name}" for name in CODEX_COMMAND_NAMES],
            "install_hint": (
                "Run `codex plugin marketplace add .`, open `/plugins`, choose the "
                "repo marketplace, then install Main Branch Owner Loop."
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
        entrypoints = ", ".join(f"`/{entry}`" for entry in item.get("codex_entrypoints", ()))
        rows.append(
            "| {label} | `{status}` | {claude} | {codex} | {entrypoints} | {commands} |".format(
                label=item["label"],
                status=item["codex_status"],
                claude=item["claude_surface"],
                codex=item["codex_surface"],
                entrypoints=entrypoints or "None",
                commands=commands or "None",
            )
        )
    return (
        "# Main Branch Codex Workflow Inventory\n\n"
        "Generated by `mb`. Do not edit by hand in business repos. This file maps "
        "Main Branch workflow surfaces to the Codex owner-loop support boundary.\n\n"
        "Status meanings:\n\n"
        "- `supported`: Codex can use this surface for the owner loop from "
        "deterministic `mb` facts and generated guidance.\n"
        "- `pending_shared_source_migration`: Codex may plan from read-only facts, "
        "but a runtime shell should wait for a shared workflow source.\n"
        "- `generated_shell_pending`: a shared source exists, but a generated Codex "
        "shell still needs implementation and smoke evidence.\n"
        "- `intentionally_unsupported`: outside the current Codex owner-loop target.\n\n"
        "Codex plugin files live under `.agents/plugins/main-branch-owner-loop/` "
        "and are listed by `.agents/plugins/marketplace.json`. Register the repo "
        "first with `codex plugin marketplace add .`, then use `/plugins`.\n\n"
        "| Workflow | Codex status | Claude Code surface | Codex surface | "
        "Codex commands | Fact commands |\n"
        "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        "Codex must ask before durable writes, checkpoints, repairs, updates, "
        "migrations, provider mutation, publishing, spend, customer contact, or "
        "public issue/proposal submission.\n"
    )


def render_codex_skill_md() -> str:
    """Render the project-local Codex skill for the owner loop."""

    command_lines = "\n".join(f"- `{command}`" for command in OWNER_LOOP_COMMANDS)
    description = (
        "Use when the operator asks Codex to run Main Branch daily owner-loop work "
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

# Main Branch owner loop for Codex

Run Main Branch owner-loop work from a business repo. This is a Codex-native
skill generated by `mb`; `AGENTS.md` remains the repo-level bootstrap.

## Start Here

Before advice, run read-only facts that fit the request:

{command_lines}

Use `mb status --json --peek` as the first daily read. Use `mb start --json`
when runtime handoff or adapter readiness matters. Use
`mb workflow list --runtime codex --json` when the operator asks what Codex can
do.

## Supported Owner Loop

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
    """Render the repo-scoped Codex plugin manifest."""

    payload = {
        "name": CODEX_PLUGIN_NAME,
        "version": "0.1.0",
        "description": (
            "Main Branch owner-loop commands for Codex. Uses deterministic mb facts "
            "and generated business-repo guidance."
        ),
        "author": {"name": "Noontide"},
        "homepage": "https://github.com/noontide-co/mainbranch",
        "repository": "https://github.com/noontide-co/mainbranch",
        "license": "MIT",
        "keywords": ["main-branch", "mainbranch", "owner-loop", "business-memory"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Main Branch Owner Loop",
            "shortDescription": "Start, inspect, decide, and checkpoint from mb facts",
            "longDescription": (
                "Adds Codex-native owner-loop commands for Main Branch business repos. "
                "The plugin routes through generated owner-loop guidance and direct "
                "mb facts; it does not add provider mutation, publishing, spend, "
                "customer contact, ads/site production, or all-skill parity."
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
    """Render the repo-scoped Codex plugin marketplace metadata."""

    payload = {
        "name": "main-branch-local",
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


def _command_definition(name: str) -> dict[str, Any]:
    for command in CODEX_COMMAND_DEFINITIONS:
        if command["name"] == name:
            return command
    raise KeyError(name)


def render_codex_command_md(name: str) -> str:
    """Render one thin Codex slash-command shim."""

    command = _command_definition(name)
    facts = "\n".join(f"- `{item}`" for item in command["commands"])
    return f"""---
description: {command["description"]}
---

# /{command["name"]}

Use the Main Branch owner-loop skill and the business repo `AGENTS.md` guidance.
This command is a thin Codex shim, not a separate workflow source.

## Route

{command["route"]}

## Required Facts

Run the direct `mb` facts that fit this request:

{facts}

Do not shell-wrap `mb` JSON through `jq`, temp files, redirects, or Python parsers.

## Task

{command["task"]}

## Boundaries

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations,
raw private-source reads, or public issue/proposal submission.

Do not claim Claude Code skill parity, all-skill parity, ads/site production,
provider mutation support, publishing support, spend support, or customer-contact
support in Codex.
"""


def render_codex_plugin_skill_md() -> str:
    """Render the plugin-packaged owner-loop skill.

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
    return Path(repo).expanduser().resolve() / CODEX_MARKETPLACE_RELATIVE_PATH


def plugin_manifest_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / CODEX_PLUGIN_MANIFEST_RELATIVE_PATH


def plugin_skill_path(repo: str | Path) -> Path:
    return Path(repo).expanduser().resolve() / CODEX_PLUGIN_SKILL_RELATIVE_PATH


def plugin_command_path(repo: str | Path, name: str) -> Path:
    return Path(repo).expanduser().resolve() / CODEX_PLUGIN_COMMANDS_RELATIVE_PATH / f"{name}.md"


def executable_status() -> dict[str, Any]:
    path = _which("codex")
    return {
        "found": bool(path),
        "path": path,
        "executable": "codex",
        "repair": "" if path else "Install Codex CLI before using the Codex owner-loop adapter.",
    }


def plugin_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    marketplace = marketplace_path(target)
    manifest = plugin_manifest_path(target)
    skill = plugin_skill_path(target)
    expected_marketplace = render_codex_marketplace_json()
    expected_manifest = render_codex_plugin_manifest()
    expected_skill = render_codex_plugin_skill_md()
    expected_commands = {name: render_codex_command_md(name) for name in CODEX_COMMAND_NAMES}

    paths = {
        CODEX_MARKETPLACE_RELATIVE_PATH: marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: manifest,
        CODEX_PLUGIN_SKILL_RELATIVE_PATH: skill,
        **{
            f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md": plugin_command_path(target, name)
            for name in CODEX_COMMAND_NAMES
        },
    }
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    stale: list[str] = []
    read_errors: list[str] = []

    expected_by_path = {
        CODEX_MARKETPLACE_RELATIVE_PATH: expected_marketplace,
        CODEX_PLUGIN_MANIFEST_RELATIVE_PATH: expected_manifest,
        CODEX_PLUGIN_SKILL_RELATIVE_PATH: expected_skill,
        **{
            f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{name}.md": expected
            for name, expected in expected_commands.items()
        },
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
        elif relative.startswith(f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/"):
            missing_markers.extend(
                f"{relative}: {marker}"
                for marker in CODEX_COMMAND_REQUIRED_MARKERS
                if marker not in text
            )

    ok = not missing and not stale and not read_errors and not missing_markers
    return {
        "ok": ok,
        "exists": not missing,
        "current": not stale and not missing_markers,
        "marketplace_path": CODEX_MARKETPLACE_RELATIVE_PATH,
        "manifest_path": CODEX_PLUGIN_MANIFEST_RELATIVE_PATH,
        "skill_path": CODEX_PLUGIN_SKILL_RELATIVE_PATH,
        "command_paths": list(CODEX_PLUGIN_COMMAND_RELATIVE_PATHS),
        "commands": [f"/{name}" for name in CODEX_COMMAND_NAMES],
        "missing": missing,
        "stale": stale,
        "missing_markers": missing_markers,
        "read_errors": read_errors,
        "repair": ""
        if ok
        else "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`.",
        "repair_command": "mb doctor repair --apply",
        "safe_to_share": True,
    }


def skill_status(repo: str | Path) -> dict[str, Any]:
    target = Path(repo).expanduser().resolve()
    skill = codex_skill_path(target)
    inventory = workflow_inventory_path(target)
    plugin = plugin_status(target)
    skill_exists = skill.is_file()
    inventory_exists = inventory.is_file()
    expected_skill = render_codex_skill_md()
    expected_inventory = render_workflow_inventory_md()
    try:
        skill_text = skill.read_text(encoding="utf-8") if skill_exists else ""
        inventory_text = inventory.read_text(encoding="utf-8") if inventory_exists else ""
    except OSError as exc:
        return {
            "ok": False,
            "exists": bool(skill_exists and inventory_exists),
            "current": False,
            "path": CODEX_SKILL_RELATIVE_PATH,
            "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
            "missing_markers": list(CODEX_SKILL_REQUIRED_MARKERS),
            "plugin": plugin,
            "read_error": str(exc),
            "repair": "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`.",
            "repair_command": "mb doctor repair --apply",
            "safe_to_share": True,
        }
    missing_markers = [
        marker for marker in CODEX_SKILL_REQUIRED_MARKERS if marker not in skill_text
    ]
    template_match = bool(
        skill_exists
        and inventory_exists
        and skill_text == expected_skill
        and inventory_text == expected_inventory
    )
    ok = bool(
        skill_exists
        and inventory_exists
        and not missing_markers
        and template_match
        and plugin["ok"]
    )
    return {
        "ok": ok,
        "exists": bool(skill_exists and inventory_exists and plugin["exists"]),
        "current": bool(template_match and plugin["current"]),
        "path": CODEX_SKILL_RELATIVE_PATH,
        "inventory_path": CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH,
        "missing_markers": missing_markers,
        "plugin": plugin,
        "read_error": "",
        "repair": ""
        if ok
        else "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`.",
        "repair_command": "mb doctor repair --apply",
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
    template_match = bool(exists and text == expected)
    current = bool(fact_grounding_ok and skill["ok"])
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
        "lifecycle_discovery_ok": lifecycle_discovery_ok,
        "skill": skill,
        "workflow_inventory": workflow_inventory(),
        "approval_boundary_ok": approval_ok,
        "codex_native_ok": slash_ok,
        "repair": ""
        if current
        else "Run `mb doctor repair --plan`, review, then `mb doctor repair --apply`.",
        "repair_command": "mb doctor repair --apply",
        "read_error": read_error,
        "safe_to_share": True,
    }


def readiness(repo: str | Path) -> dict[str, Any]:
    executable = executable_status()
    instructions = instructions_status(repo)
    ok = bool(executable["found"] and instructions["ok"])
    return {
        "ok": ok,
        "status": "ready" if ok else "needs_setup",
        "support_level": "first_class_owner_loop",
        "executable": executable,
        "instructions": instructions,
        "skill": instructions["skill"],
        "plugin": instructions["skill"]["plugin"],
        "workflow_inventory": workflow_inventory(),
        "fact_commands": list(REQUIRED_FACT_COMMANDS),
        "repair": "" if ok else instructions["repair"] or executable["repair"],
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

    skill_path = codex_skill_path(target)
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_skill = render_codex_skill_md()
    existing_skill = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    if existing_skill != rendered_skill:
        skill_path.write_text(rendered_skill, encoding="utf-8")
        changed_paths.append(CODEX_SKILL_RELATIVE_PATH)

    inventory_path = workflow_inventory_path(target)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_inventory = render_workflow_inventory_md()
    existing_inventory = (
        inventory_path.read_text(encoding="utf-8") if inventory_path.exists() else ""
    )
    if existing_inventory != rendered_inventory:
        inventory_path.write_text(rendered_inventory, encoding="utf-8")
        changed_paths.append(CODEX_WORKFLOW_INVENTORY_RELATIVE_PATH)

    marketplace = marketplace_path(target)
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    rendered_marketplace = render_codex_marketplace_json()
    existing_marketplace = marketplace.read_text(encoding="utf-8") if marketplace.exists() else ""
    if existing_marketplace != rendered_marketplace:
        marketplace.write_text(rendered_marketplace, encoding="utf-8")
        changed_paths.append(CODEX_MARKETPLACE_RELATIVE_PATH)

    manifest = plugin_manifest_path(target)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    rendered_manifest = render_codex_plugin_manifest()
    existing_manifest = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    if existing_manifest != rendered_manifest:
        manifest.write_text(rendered_manifest, encoding="utf-8")
        changed_paths.append(CODEX_PLUGIN_MANIFEST_RELATIVE_PATH)

    plugin_skill = plugin_skill_path(target)
    plugin_skill.parent.mkdir(parents=True, exist_ok=True)
    rendered_plugin_skill = render_codex_plugin_skill_md()
    existing_plugin_skill = (
        plugin_skill.read_text(encoding="utf-8") if plugin_skill.exists() else ""
    )
    if existing_plugin_skill != rendered_plugin_skill:
        plugin_skill.write_text(rendered_plugin_skill, encoding="utf-8")
        changed_paths.append(CODEX_PLUGIN_SKILL_RELATIVE_PATH)

    for command_name in CODEX_COMMAND_NAMES:
        command_path = plugin_command_path(target, command_name)
        command_path.parent.mkdir(parents=True, exist_ok=True)
        rendered_command = render_codex_command_md(command_name)
        existing_command = command_path.read_text(encoding="utf-8") if command_path.exists() else ""
        if existing_command != rendered_command:
            command_path.write_text(rendered_command, encoding="utf-8")
            changed_paths.append(f"{CODEX_PLUGIN_COMMANDS_RELATIVE_PATH}/{command_name}.md")
    return {
        "ok": True,
        "path": AGENTS_RELATIVE_PATH,
        "changed": bool(changed_paths),
        "changed_paths": changed_paths,
        "status": instructions_status(target),
    }
