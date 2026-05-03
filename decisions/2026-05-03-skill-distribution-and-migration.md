---
type: decision
date: 2026-05-03
status: proposed
topic: Skill distribution and runtime migration model
linked_issues:
  - https://github.com/noontide-co/mainbranch/issues/236
  - https://github.com/noontide-co/mainbranch/issues/234
  - https://github.com/noontide-co/mainbranch/issues/237
  - https://github.com/noontide-co/mainbranch/issues/238
participants: [Devon, Codex]
tags: [v0-2, skills, runtime-adapters, claude-code, migration, decision]
---

# Skill Distribution and Migration Model

## Decision

Main Branch should ship the **migration and shadow-detection repair path first**,
keep the current project-local Claude Code wiring as the short-term supported
adapter, and design an official Claude Code plugin package as the likely durable
distribution target.

The current `additionalDirectories` plus project-local bridge links are not a
dead end. Claude Code officially loads skills from added directories, and
project-local `.claude/skills/` folders are a documented discovery source. But
global `~/.claude/skills/<name>` entries take precedence over project skills, so
old global Main Branch symlinks can silently shadow the active business repo.
That is a migration problem before it is an architecture problem.

Do not return to global skill symlinks. Do not copy bundled skills into business
repos as the primary update model. Do not claim Codex, Cursor, OpenClaw, Hermes,
Paperclip-adjacent orchestration, or local runtime support until each has an
adapter and smoke evidence.

The plugin path is load-bearing for one reason in particular: **bundled
Main Branch skill names are generic and almost guaranteed to collide with
other authors' skills**. Plugin namespacing
(`<plugin-name>:<skill-name>`) is the only documented mechanism that
escapes Claude Code's personal-overrides-project precedence; it protects
Main Branch users from third-party skill authors and protects third-party
authors from Main Branch. See "Bundled Skill Name Collision Surface"
below.

## Recommendation

1. **v0.2 immediate:** implement stale global Claude Code skill detection and a
   noob-safe migration command. `mb doctor`, `mb start`, and `mb onboard` should
   warn or block before a stale global `/start` can win silently.
2. **v0.2 short term:** keep `mb skill link --repo .` as the Claude Code repair
   primitive. It should continue to write `.claude/settings.local.json` with the
   active engine root and create gitignored local bridge links.
3. **v0.2/v0.3 design target:** prototype a Claude Code plugin or marketplace
   package for Main Branch skills. Adopt it only after it preserves beginner
   `/start` ergonomics, supports local or project scope cleanly, updates through
   a documented path, and passes runtime smoke from a fresh business repo plus a
   migrated old-user repo. The plugin spike must explicitly answer the
   bundled-skill-name collision question: do users invoke `/mb:start` or do we
   prove a plain-`/start` alias works under the plugin namespace? Lock that
   answer before promoting plugin packaging to default.
4. **Runtime-general future:** define runtime adapters as separate tested
   contracts. The portable workflow source can stay runtime-neutral, but each
   runtime needs its own discovery, install, update, and smoke contract.

## Evidence

### Bundled Skill Name Collision Surface

The bundled Main Branch skills today live in `.claude/skills/` and ship in
the wheel at `mb/_engine/.claude/skills/`. The current names are:

```
ads     end     help    organic pull    setup   site
skill-brief-draft       skill-concept   skill-review
start   think   vsl     wiki
```

Most of these are aggressively generic English verbs and nouns. They are
almost certain to be claimed by other skill authors over time, and several
already conflict with extremely common patterns:

- `start`, `end`, `setup`, `pull`, `help` are session and lifecycle words
  that any onboarding, deployment, git-helper, or chat-bookend skill would
  reasonably claim;
- `site`, `ads`, `wiki`, `vsl`, `organic` are content-domain words that
  marketing, ops, and CMS-adjacent skill authors would reasonably claim;
- `think` collides with both Claude Code's documented `<thinking>` workflow
  language and any number of reasoning or research skills already published
  in the wider ecosystem.

Per the [Claude Code skills doc][skills-docs], any user-installed
`~/.claude/skills/start` (whether created by another tool, another version
of Main Branch, or hand-written) silently overrides the project-local
`.claude/skills/start` we wire from the business repo. This is documented
behavior, not a bug. Issue [#234][issue-234] addresses the Main-Branch-vs-
Main-Branch shadow case, but the collision surface is broader: a user can
install any personal or project skill named `start` and lose Main Branch's
`/start` without warning.

The same doc states: *"Plugin skills use a `plugin-name:skill-name`
namespace, so they cannot conflict with other levels."* That is the only
collision-proof mechanism Anthropic documents. Renaming bundled skills to
something less generic (for example `mb-start`, `mb-end`) would reduce the
collision surface inside the current symlink wiring, but it would not solve
it: any third-party personal or project skill can still choose the same name if
no namespace is enforced. Plugin packaging encodes the publisher in the
namespace by default.

This is the strongest single argument for treating the Claude Code plugin
shape as the durable destination rather than as a nice-to-have. The
migration order in this decision is still symlink-first, plugin-next,
because the issue explicitly disallows rewriting wiring in this PR — but
the destination should not drift.

[skills-docs]: https://code.claude.com/docs/en/skills
[issue-234]: https://github.com/noontide-co/mainbranch/issues/234

### Current Main Branch Behavior

`mb` currently packages the Claude Code skill source inside the Python package
or source checkout and wires business repos through `mb.engine`:

- `mb/mb/engine.py` locates the active engine root, preferring packaged data
  over source checkout paths.
- `_write_settings()` writes `.claude/settings.local.json` with
  `permissions.additionalDirectories` pointing at the active engine root.
- `link_skills()` creates `.claude/skills/<name>` symlinks, or copies if
  symlinks fail, and gitignores the generated local wiring.
- `link_status()` requires both the active engine root in
  `additionalDirectories` and a project-local `.claude/skills/start/SKILL.md`.
- `mb start`, `mb doctor`, `mb status`, and `mb onboard` all rely on
  `link_status()` and tell users to run `mb skill link --repo .` when wiring is
  missing.

This proves the current adapter is deterministic, scriptable, and repairable,
but it does not prove Claude Code will choose the intended skill when a personal
skill with the same name exists.

### Claude Code

Claude Code documents four skill locations: enterprise, personal
`~/.claude/skills`, project `.claude/skills`, and plugin skills. It also states
the precedence problem directly: enterprise overrides personal, personal
overrides project, and plugin skills use a plugin namespace so they cannot
conflict with the other levels.

Claude Code also documents that `--add-dir` primarily grants file access, but
skills are an exception: a `.claude/skills/` directory inside an added directory
is loaded automatically. Other `.claude/` configuration from added directories
is not loaded by default.

For reusable distribution, Claude Code now has a plugin system. Plugins can
bundle skills, agents, hooks, MCP servers, LSP servers, commands, executables,
and settings. Marketplaces provide discovery and version management. Plugin
install supports user, project, and local scopes; project scope writes to
`.claude/settings.json`, while local scope writes to `.claude/settings.local.json`.
Claude Code copies installed plugin directories into a cache, so plugin files
must be self-contained or refer to paths through plugin variables.

Sources:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code plugin discovery and marketplaces](https://code.claude.com/docs/en/discover-plugins)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code settings scopes](https://code.claude.com/docs/en/settings)

### Codex

Codex has converged on a similar split:

- `AGENTS.md` is the repo instruction contract. Codex builds an instruction chain
  from global and project files, with closer files overriding broader guidance.
- Agent skills are the authoring format for repeatable workflows. Codex reads
  repo skills from `.agents/skills` along the current directory to repo-root
  path, user skills from `$HOME/.agents/skills`, admin skills from
  `/etc/codex/skills`, and system skills bundled with Codex.
- Codex explicitly says direct skill folders are for local authoring and
  repo-scoped workflows; reusable distribution should use plugins.

Sources:

- [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Codex Agent Skills](https://developers.openai.com/codex/skills)
- [Codex plugins](https://developers.openai.com/codex/plugins)

### Other OSS Agent Tooling

Other serious tools show the same pattern with different file names:

- Cursor uses versioned project rules in `.cursor/rules`, global user rules,
  and `AGENTS.md` as a simple root-level alternative. Its legacy `.cursorrules`
  file remains supported but is deprecated.
- Cline uses project `.clinerules/`, global rules, skills, workflows, hooks, and
  `.clineignore`. It also recognizes `.cursorrules`, `.windsurfrules`, and
  `AGENTS.md` for cross-tool compatibility. Its docs recommend project storage
  for codebase-specific customization and global storage for personal
  preferences.
- Aider does not have a comparable skill package system. It recommends loading a
  small `CONVENTIONS.md` via `/read` or `--read`, and can always-load read-only
  convention files through `.aider.conf.yml`.

Sources:

- [Cursor rules](https://docs.cursor.com/en/context)
- [Cline customization overview](https://docs.cline.bot/customization/overview)
- [Cline rules](https://docs.cline.bot/customization/cline-rules)
- [Aider conventions](https://aider.chat/docs/usage/conventions.html)
- [Aider config](https://aider.chat/docs/config/aider_conf.html)

## Tradeoffs

### Project-Local Symlinks

Pros:

- Deterministic for `mb`; easy to create, inspect, test, and repair.
- Keeps business repos pointing at the active installed package or source
  checkout without committing generated runtime wiring.
- Works for pipx and clone installs with one `mb skill link --repo .` command.

Cons:

- Still loses to personal/global skills with the same name.
- Symlinks can be broken by moved installs, source checkout changes, Windows
  constraints, or filesystems without symlink support.
- Bridge links are Claude Code adapter details, not a portable Main Branch
  workflow format.

### Global Symlinks

Pros:

- One setup step can affect every repo.
- Convenient for a single technical maintainer.

Cons:

- Wrong scope for a business repo product: personal/global state can override
  repo-local truth.
- Stale links survive package updates and repo moves.
- Shadow failures are silent and beginner-hostile.

Global symlinks should be treated as legacy state to detect and migrate away
from, not a supported install target.

### Copied Skill Folders

Pros:

- No symlink support required.
- Easy to inspect from the business repo.

Cons:

- Copies become stale immediately unless every update refreshes them.
- Business repos would carry generated adapter artifacts rather than business
  truth.
- It blurs user-edited skills and packaged Main Branch skills.

Copy fallback is acceptable when symlink creation fails, but copied folders
should be detected as generated adapter state and refreshed or replaced by
`mb`.

### `additionalDirectories`

Pros:

- Officially supported for loading skills from an added directory.
- Lets installed package data remain the source of truth.
- Keeps generated business-repo state small.

Cons:

- It is primarily an access mechanism, not full configuration discovery.
- It does not load other `.claude/` configuration from the engine directory.
- It does not solve personal-skill precedence by itself.

Keep it short term because it is official and already tested, but pair it with
shadow detection and plan to replace the bridge with plugin packaging if the
plugin path proves better.

### Official Plugin Packaging

Pros:

- Current Claude Code and Codex docs both identify plugins as the reusable
  distribution unit for skills.
- **Namespacing is the only documented mechanism that prevents collisions
  with personal/global skills shipped by other authors.** Given how generic
  Main Branch's bundled skill names are (`start`, `end`, `setup`, `pull`,
  `help`, etc.), this stops being a nice-to-have and becomes the
  load-bearing reason to move.
- Plugin scopes make user, project, and local installs explicit.
- Marketplaces and plugin updates provide a real distribution story.

Cons:

- Plugin install/update is a runtime-specific operation that may require Claude
  Code version checks, trust prompts, marketplace setup, and runtime smoke.
- Plugin cache semantics require the package to be self-contained.
- Main Branch must verify beginner `/start` ergonomics. If namespacing changes
  invocation from `/start` to a qualified plugin command, that is a product
  cost, not an implementation detail.

Plugin packaging should be the target, not an untested rewrite.

## Noob-Safe Migration

The migration must be boring, reversible, and explicit.

`mb` should detect:

- global `~/.claude/skills/<bundled-skill>` entries for every bundled Main
  Branch skill name;
- whether each entry is a symlink, directory copy, or unexpected file;
- whether a symlink resolves to the active engine root, a different Main Branch
  engine root, a missing path, or an unrelated user-created skill;
- whether project-local `.claude/settings.local.json` points at the active
  engine root;
- whether project-local `.claude/skills/start/SKILL.md` exists;
- whether copied project-local generated skill folders are stale relative to the
  active bundled skill set;
- Claude Code version or feature availability when plugin migration is later
  added.

`mb` should repair:

- generated project-local bridge links through `mb skill link --repo .`;
- stale global Main Branch symlinks by moving them to a timestamped backup
  directory only after explicit confirmation or `--apply`;
- stale generated project-local copied folders by replacing them only when `mb`
  can prove they are generated Main Branch adapter state;
- missing `.claude/settings.local.json` or missing `additionalDirectories`
  entries by rewriting the local settings file;
- post-update state by running the same detection after `mb update`.

`mb` should not repair:

- unrelated user-authored `~/.claude/skills/<name>` directories automatically;
- any global skill without a backup;
- anything requiring runtime/plugin trust prompts without telling the user what
  Claude Code will ask them to trust.

Suggested command split:

- `mb doctor`: detect shadows, mark stale global `/start` as a hard runtime
  handoff problem, and print exact next commands.
- `mb start`: block handoff when stale global `/start` is likely to win.
- `mb onboard`: run the same preflight before declaring setup complete.
- `mb skill link --repo .`: repair project-local wiring and report global
  shadows without modifying global state.
- `mb migrate runtime --check`: dry-run migration plan for runtime adapter
  state.
- `mb migrate runtime --apply`: perform reversible moves/backups for generated
  Main Branch runtime state only.

## Runtime Adapter Contract

Main Branch should not make the Claude Code adapter shape the product shape.
Each runtime should have an adapter manifest or equivalent code contract with:

- support level: supported, experimental, or roadmap;
- discovery sources and precedence;
- install/update command;
- local vs project vs global state locations;
- generated files and gitignore rules;
- shadow or stale-state detection;
- exact launch instructions for `mb start`;
- JSON status shape for `mb doctor` and `mb status`;
- required runtime smoke.

Initial adapter claims:

- Claude Code: supported today, with current project-local wiring and future
  plugin investigation.
- Codex: roadmap until `.agents/skills`, plugins, and `AGENTS.md` behavior are
  implemented and smoked against a business repo.
- Cursor: roadmap; likely maps to `AGENTS.md` plus `.cursor/rules`, but Main
  Branch should not claim workflow parity without testing.
- OpenClaw, Hermes, Paperclip-adjacent orchestration, and local runtimes:
  roadmap only. Paperclip-like systems should consume stable repo and JSON
  contracts rather than become the CLI's runtime model.

## Kill Criteria

Kill global symlink support if any release ships a migration path that can
detect, back up, and remove stale Main Branch global skill links safely.

Kill copied project-local skill folders as a normal path if package/install
smoke proves symlinks or plugin installs work across the supported OS matrix.
Keep copy fallback only for systems where symlinks are unavailable.

Kill the current `additionalDirectories` bridge as the primary Claude Code path
only when plugin packaging proves all of this:

- fresh `mb onboard` to Claude Code `/start` works;
- an old-user repo with stale global skills migrates cleanly;
- `mb update` or documented Claude plugin update keeps skills current;
- beginner-facing invocation remains acceptable;
- `mb doctor`, `mb start`, and `mb onboard` can detect and repair broken plugin
  state;
- package/install smoke and Claude Code runtime smoke are recorded.

Kill the plugin path, or defer it, if:

- plugin namespacing makes `/start` confusing for beginners without a clean
  alias;
- project or local scope cannot be automated or explained safely;
- marketplace setup adds more first-run friction than the current bridge;
- plugin caching breaks skill references, helper scripts, or packaged data;
- Claude Code plugin APIs change faster than Main Branch can validate.

## Follow-Up Work

Concrete follow-ups should be separate from this decision:

1. Implement [#234](https://github.com/noontide-co/mainbranch/issues/234):
   stale global Claude Code skill shadow detection and safe
   migration.
2. Add [#237](https://github.com/noontide-co/mainbranch/issues/237): a Claude
   Code plugin packaging spike with fresh-repo and migrated-repo runtime smoke.
3. Define [#238](https://github.com/noontide-co/mainbranch/issues/238): the
   first runtime adapter contract document or JSON shape before adding Codex,
   Cursor, OpenClaw, Hermes, Paperclip-adjacent orchestration, or local runtime
   behavior.
4. Update compatibility docs only after adapter smoke changes what is supported.
