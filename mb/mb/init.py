"""``mb init`` — non-interactive scaffold for a Main Branch business repo.

Per master decision, v0.1 asks ONE question (business name). Path-config
flexibility is locked; folder names are canonical. Re-running on
an existing repo returns ``status=already-initialized`` (idempotent).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

from mb import checkpoint as checkpoint_mod
from mb import codex as codex_mod
from mb.engine import link_skills
from mb.migrate import LATEST_SCHEMA_VERSION, SCHEMA_MARKER

# The canonical business folders. Keep these stable unless a schema migration lands.
DATA_FOLDERS = [
    "core",
    "core/offers",
    "core/proof",
    "core/brand",
    "core/marketing",
    "core/marketing/channels",
    "core/marketing/accounts",
    "core/people",
    "core/strategy",
    "core/operations",
    "core/finance",
    "research",
    "decisions",
    "bets",
    "log",
    "pushes",
    "documents",
]

DEFAULT_GITIGNORE = """\
# Main Branch defaults
.env
.env.*
*.journal
*.hledger
*.ledger
*.beancount
.DS_Store
__pycache__/
.mypy_cache/
.ruff_cache/
.pytest_cache/
node_modules/
.venv/
.claude/worktrees/
.mb/private/
.mb/backups/
.mb/connect.yaml
.mb/onboarding.json
.mb/last-status-seen.json
.mb/issue-drafts/
"""


def _gh_username() -> str:
    """Best-effort gh-cli username probe. Returns empty string on miss."""
    try:
        out = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return ""


def _read_template(name: str) -> str:
    """Read a bundled template by relative path under ``_data/templates/``."""
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(name)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        # Fallback to repo-relative path during dev (-e install).
        here = Path(__file__).resolve().parent / "_data" / "templates" / name
        if here.exists():
            return here.read_text(encoding="utf-8")
        return ""


def _render(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, val in mapping.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def run(path: str, name: str) -> dict[str, Any]:
    """Scaffold ``path`` as a Main Branch business repo.

    Returns a dict with ``status`` ∈ {ok, already-initialized, error},
    ``path`` (absolute), and ``created`` (list of relative paths created).
    """
    target = Path(path).resolve()
    target.mkdir(parents=True, exist_ok=True)

    if (target / "CLAUDE.md").exists():
        link_result = link_skills(target)
        return {
            "status": "already-initialized",
            "path": str(target),
            "created": link_result["created"],
            "skill_link": link_result,
            "checkpoint_hook": checkpoint_mod.hook_status(target),
        }

    business_name = name.strip() or os.environ.get("MB_BUSINESS_NAME", "").strip()
    if not business_name:
        try:
            business_name = input("business name: ").strip()
        except (EOFError, KeyboardInterrupt):
            return {"status": "error", "path": str(target), "error": "no business name"}
    if not business_name:
        return {"status": "error", "path": str(target), "error": "empty business name"}

    gh_user = _gh_username() or "your-gh-username"

    created: list[str] = []
    for sub in DATA_FOLDERS:
        d = target / sub
        d.mkdir(parents=True, exist_ok=True)
        # .gitkeep so empty folders survive git
        keep = d / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
            created.append(f"{sub}/.gitkeep")

    marker = target / SCHEMA_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(LATEST_SCHEMA_VERSION + "\n", encoding="utf-8")
    created.append(SCHEMA_MARKER)

    mapping = {
        "BUSINESS_NAME": business_name,
        "GH_USERNAME": gh_user,
    }

    claude_tmpl = _read_template("CLAUDE.md.tmpl") or _DEFAULT_CLAUDE
    (target / "CLAUDE.md").write_text(_render(claude_tmpl, mapping), encoding="utf-8")
    created.append("CLAUDE.md")

    agents_result = codex_mod.write_agents_md(
        target,
        name=business_name,
        gh_username=gh_user,
    )
    if agents_result["changed"]:
        created.append("AGENTS.md")

    vocabulary_tmpl = _read_template("core_vocabulary.md.tmpl")
    if vocabulary_tmpl:
        vocabulary_path = target / "core" / "vocabulary.md"
        vocabulary_path.parent.mkdir(parents=True, exist_ok=True)
        if not vocabulary_path.exists():
            vocabulary_path.write_text(_render(vocabulary_tmpl, mapping), encoding="utf-8")
            created.append("core/vocabulary.md")

    codeowners_tmpl = _read_template("CODEOWNERS.tmpl") or f"* @{gh_user}\n"
    github_dir = target / ".github"
    github_dir.mkdir(exist_ok=True)
    (github_dir / "CODEOWNERS").write_text(_render(codeowners_tmpl, mapping), encoding="utf-8")
    created.append(".github/CODEOWNERS")

    gitignore_tmpl = _read_template(".gitignore.tmpl") or DEFAULT_GITIGNORE
    (target / ".gitignore").write_text(_render(gitignore_tmpl, mapping), encoding="utf-8")
    created.append(".gitignore")

    link_result = link_skills(target)
    created.extend(path for path in link_result["created"] if path not in created)

    if shutil.which("git") and not (target / ".git").exists():
        try:
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=target,
                check=True,
                timeout=10,
            )
            created.append(".git/")
        except subprocess.SubprocessError:
            # git init failure is not fatal for scaffolding
            pass

    checkpoint_hook = (
        checkpoint_mod.install_commit_hook(target)
        if (target / ".git").exists()
        else checkpoint_mod.hook_status(target)
    )
    if checkpoint_hook.get("changed"):
        created.append(".git/hooks/commit-msg")

    return {
        "status": "ok",
        "path": str(target),
        "created": created,
        "business_name": business_name,
        "skill_link": link_result,
        "checkpoint_hook": checkpoint_hook,
    }


# Embedded fallback CLAUDE.md so ``mb init`` works even without bundled
# templates resolving (early dev installs, source checkouts).
_DEFAULT_CLAUDE = """\
# {{BUSINESS_NAME}}

Your business as files. Claude reads these; you edit them; git remembers them.

## Claude operating contract

Main Branch CLI facts are the source of truth for repo health, setup, runtime
wiring, updates, graph/status signals, provider readiness, and repair paths.
The normal runtime path is: open a terminal in this repo, run `claude`, then
type `/mb-start` inside Claude Code. From the terminal, `mb start --json`
checks the handoff and `mb start --launch` can open Claude Code when available.
Before giving setup, routing, migration, update, or repair advice, run the
read-only checks that fit the situation from this business repo:

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
refresh local runtime wiring, move personal skill shadows, update packages,
migrate business files, create checkpoints, publish, spend money, email, or
mutate provider accounts require explicit operator approval before applying.
Plan first, then apply only after approval:

```bash
mb doctor repair --plan
mb skill repair --repo .
mb skill link --repo .          # writes project-local Claude skill wiring
mb skill repair --repo . --apply
mb doctor repair --apply
mb update
```

If `/mb-start` is not discoverable or Claude Code reports `Unknown command:
/mb-start`, do not improvise from memory. From this business repo, check
`mb --version`, run `mb start --json` and `mb status --json --peek`, inspect
repair options with `mb doctor repair --plan`, then ask before running any
write/apply command such as `mb skill link --repo .`, `mb skill repair --repo .
--apply`, `mb doctor repair --apply`, or `mb update`. After repairing skill
wiring, tell the operator to restart Claude Code from this repo and try
`/mb-start` again.

If `mb status --json --peek` reports `update.severity` as `recommended` or
`required`, make that the only recommendation before business routing. Name the
installed/latest versions when present. For recommended updates, say the update
brings recent routing, repair, and skill improvements when release highlights
are unavailable, then ask whether to update now. Do not show ranked actions
until after the operator updates or explicitly chooses to continue. For required
updates, route to the cited
`mb update` command before business work. After an approved update, rerun the
status briefing.

Do the technical work in technical commands, then translate the result back into
business-owner language. Speak first in terms of bets, goals, offers, pushes,
playbooks, outcomes, decisions, next actions, and saved checkpoints. Treat git,
branches, pull requests, provider refs, and local wiring as the hidden memory
layer unless the operator asks for the plumbing.

## Folders

- `core/` — the business brain: offer, audience, voice, soul, proof, brand,
  strategy, operations, finance
- `core/offers/` — per-offer specifics when this is a multi-offer repo
- `core/proof/` — testimonials, typicality, and reusable proof
- `core/brand/` — visual identity, voice guardrails, and brand systems
- `core/marketing/` — optional content distribution, channel, and account strategy
- `core/people/` — optional founder/person voice source material, beliefs, stories, and proof
- `core/strategy/` — strategic context that should remain evergreen
- `core/operations/` — operating context such as fulfillment, classroom, funnel, or membership notes
- `core/finance/` — approved finance summaries, policies, and safe provider refs
- `research/` — dated notes from when you went looking
- `decisions/` — dated choices, with rationale
- `bets/` — operating bets with appetite, metric, target, and outcome
- `log/` — running activity log
- `pushes/` — coordinated pushes (launches, drops, challenges, promos, etc.)
- `documents/` — anything that doesn't belong above

If your repo was created before the push primitive decision, you may also have
a legacy `campaigns/` folder. `mb` continues to read it; new coordinated work
should land in `pushes/`. Run `mb doctor` to see whether your repo is on the
canonical shape and `mb migrate campaigns --plan` to preview a safe move.

## Hub and child repos

This repo is the hub for business strategy, bets, decisions, offers, pushes,
logs, approved summaries, and routing. Child repos hold role-specific execution
work when a site, offer, product, client, finance, legal, ops, integration
sidecar, experiment, or archive surface needs its own lifecycle or access
boundary.

Use the hub for strategy, durable business truth, and checkpoint context. Switch
to a child repo when editing that child repo's code, site, product files, client
deliverables, sidecar code, or ops files. When you are in a child repo, read
`.mainbranch/repo.json` if it exists; existing site repos may still use
`.mainbranch/source.json` as a compatibility link. Return to this hub for
business routing, decisions, and cross-repo topology questions.

The hub topology registry, when present, lives at
`core/operations/repo-topology.md`. It should use safe handles such as display
names, roles, lifecycle, GitHub owner/repo, linked offers/pushes/bets/decisions,
and private-boundary notes. Do not commit local absolute paths, secrets, raw
provider caches, raw finance/legal/customer data, or permission claims in hub
or child repo descriptors.

## Business primitive routing

When deciding where an idea belongs, use business meaning first:

- Offer: what the business sells or may sell repeatedly.
- Bet: a time-boxed wager with appetite, target, evidence, and verdict.
- Push: coordinated work that ships something to an audience.
- Reusable playbook: an engine recipe for running a repeatable operating
  workflow. Treat its defaults as attributed method, not universal law.
- Push playbook: this push's approval, provider-boundary, check, manual-step,
  evidence, fork, and outcome record.
- Proof: evidence that a claim is true.
- Decision: rationale for changing durable truth.

Reusable playbooks can encode official platform rules, Main Branch guidance,
and author opinion. Push playbooks record which defaults were used or forked
for this run and why. See `docs/playbooks.md` in the Main Branch engine for
the full model.

In a single-offer repo, `core/offer.md` is the durable offer truth. In a
multi-offer repo, `core/offer.md` is the portfolio thesis and
`core/offers/<slug>/offer.md` holds per-offer truth. Company-wide proof belongs
in `core/proof/`; offer-specific proof belongs in `core/offers/<slug>/proof/`.
Use standard proof files such as `testimonials.md`, `typicality.md`, and
`angles/` inside those proof folders. Make proof status-detectable with
structured testimonial fields such as `public`, `permissioned_public`,
`approved_for_public`, `safe_to_share`, `offer`, `linked_offer`, and
`linked_offers`. Use `typicality.md` for average-case outcomes, caveats,
common failure context, and time-to-outcome when available.
Content strategy starts at `core/content-strategy.md`. Keep it as the simple
business-level strategy and index: what the business wants to be known for, who
the content is for, pillars, content jobs, non-publishing rules, and links to
the rest of the model. When the operator needs more detail, use
`core/marketing/distribution-strategy.md`,
`core/marketing/channels/<channel>.md`,
`core/marketing/accounts/<platform>-<account>.md`, and
`core/people/<person>.md`. Weekly content planning should read those files by
reference, then write concrete execution to `pushes/` and results to `log/`.
`mb status --json --peek` also emits `money_path`, a read-only map of whether
customer progress, offer, proof, CTA, channel, push, playbook, page readiness,
and outcome feedback are legible and connected. Use MoneyPath from
`mb status --json --peek` for routing when the path needs to be legible,
supported, connected, and instrumented. Treat proof-quality fields as factual
signals for badges or gaps, not persuasion scores; do not claim proof or offers
are good, bad, high-converting, or likely to convert.
A live idea can be both a bet and an offer candidate: open the bet first, then
create or update the offer only when the operator wants durable sellable truth.

Do not rename, delete, merge, split, or move offer folders until an accepted
decision, approved migration plan, or explicit operator instruction exists.
Paused, dead, superseded, or graduated offers should remain inspectable until
the operator decides what happens to them.

## Optional: operator vocabulary

`core/vocabulary.md` is an optional file where the business names what it
calls coordinated pushes. A coach might call them *drops*; a creator might
call them *launches*; a community might call them *challenges*. The file
shape:

    ---
    type: vocabulary
    status: active
    terms:
      push:
        singular: drop
        plural: drops
      statuses:
        active: live
        completed: shipped
    ---

    Optional prose explanation goes here.

Vocabulary changes how skills and `mb status` speak in conversation. It does
not rename folders, frontmatter types, link fields, JSON keys, validator
rules, or commands. Engine internals stay canonical.

## Conventions

- Decisions, research, bets, and offers carry a small block of metadata at the top
  (frontmatter). Run `mb validate` to check it.
- Status field: proposed | running | scaling | killed | graduated | died.
- One owner per file (CODEOWNERS pattern).

## Connected accounts

Treat this repo as the boundary for connected business tools. When you switch
business repos, switch the accounts, tokens, and MCP servers that can act on
that business.

Keep non-secret IDs in repo files when they help agents choose the right
account: Stripe account/product/price IDs in `core/offers/<offer>/stripe.md`,
Google Ads customer and campaign IDs (provider's term for their object) in
`pushes/<push>/push.md` `provider_refs:`, ad pixel IDs beside the site or
push files they belong to, and MCP server names/scopes in local setup notes.

Never commit API keys, OAuth refresh tokens, service-account JSON, webhook
secrets, MCP tokens, or bearer tokens. Put secrets in a runtime local config,
OS keychain, 1Password, `.env`, or `.claude/settings.local.json`; those files
should stay gitignored. If a tool can spend money, publish, email, or mutate a
customer account, verify it is tethered to this repo before using it.

## Helpful commands

```
mb doctor                  # see if anything is off in this repo
mb validate                # check the metadata on your files
mb graph --open            # see what links to what
```

Visit https://mainbranch.io for the full system docs.

Owner: @{{GH_USERNAME}}
"""
