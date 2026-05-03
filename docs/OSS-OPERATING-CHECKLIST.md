# Main Branch OSS Operating Checklist

Use this checklist during cold start, implementation, and review when a change
could affect Main Branch's public product shape, release discipline, runtime
claims, contributor workflow, or public/private boundary.

This is not a generic open-source checklist. It captures the operating rules
that keep Main Branch usable as public infrastructure while it evolves quickly.

## 1. Public / Private Boundary

- [ ] Every committed sentence is safe for a stranger to read forever.
- [ ] No secrets, tokens, credentials, raw account data, customer data, member
  data, or private operating details are committed.
- [ ] Examples and fixtures are sanitized and generic.
- [ ] Private local preferences, agent-runner notes, launch plans, partner
  strategy, and machine-specific paths stay in private repos or `.context/`,
  not in durable public docs.
- [ ] If a note only makes sense to one maintainer, rewrite it generically or
  keep it private.

## 2. Product Boundary

- [ ] `mb` remains the deterministic, inspectable, scriptable control plane.
- [ ] Agent-runtime skills remain the judgment-heavy execution layer.
- [ ] `mb` owns repo shape, validation, migration, status, updates, graphing,
  integration metadata, and runtime wiring.
- [ ] Skills own synthesis, writing, decision support, review, and session
  routing.
- [ ] New CLI verbs are one-shot, exit-coded, scriptable, and designed for
  future JSON output where useful.
- [ ] `mb` does not become a chat client, model host, scheduler, dashboard
  daemon, vector store, or artifact generator without a new accepted decision.

## 3. Beginner Reality

- [ ] First-run, update, migration, and repair flows end with exact next
  commands, not vague advice.
- [ ] Beginner-facing failures explain what broke, why it matters, and which
  command to run next.
- [ ] Power users can skip guided copy and use quiet/scriptable primitives.
- [ ] TTY behavior, non-TTY behavior, exit codes, and `--json` behavior stay
  deliberate where the CLI exposes them.
- [ ] GitHub language is translated into business terms when the user loop needs
  it: issues are tasks, PRs are proposals or review conversations, and merge
  history is shipped work.

## 4. State Model

- [ ] Canonical business truth stays in the business repo and git history:
  reference files, research, decisions, plans, campaign artifacts, durable
  summaries, and proposal changes.
- [ ] `.mb/` is used only for explicit Main Branch operational state such as
  schema markers, repo-safe connection metadata, backups, indexes, or caches.
- [ ] Each `.mb/` addition has a clear tracked-vs-gitignored rule and a repair
  path through `mb doctor`, `mb status`, `mb migrate`, or documented commands.
- [ ] `.mb/` schema changes round-trip through `mb migrate` and `mb doctor`
  without losing existing user state, and ship a documented manual fallback for
  users who cannot run the migration.
- [ ] Secrets stay outside git in the OS keychain, runtime-specific local
  config, environment variables, 1Password, or another documented secret store.
- [ ] Rebuildable indexes and local caches do not become the source of truth.
- [ ] Live process state is explicit and optional; users should know when they
  have started a dashboard, server, watcher, bridge, or background process.

## 5. Runtime Claims

- [ ] Claude Code is described as first-class today.
- [ ] Codex, Cursor, OpenClaw, Hermes, Paperclip-adjacent orchestration, and
  local runtimes are described only as roadmap or compatibility targets unless
  an adapter and smoke evidence exist.
- [ ] Compatibility docs distinguish supported, experimental, and roadmap
  surfaces.
- [ ] No PR claims runtime support based only on product intent or local hopes.
- [ ] Runtime smoke evidence is included when discovery, invocation, skill
  packaging, or first-run handoff changes.

## 6. Skill-to-CLI Contract

- [ ] Skills lean on deterministic `mb` commands for repo health, migration,
  update, validation, graph, connection, and skill-link checks.
- [ ] Skills do not duplicate shell probes or prose-only checks that belong in
  `mb`.
- [ ] A skill workflow that needs stable machine-readable data has an `mb`
  command or documented JSON contract to call.
- [ ] Skill prose stays self-contained, public-safe, and free of sibling-skill
  path assumptions.
- [ ] Mechanical tests do not replace runtime/manual validation when skill
  discovery or LLM-facing workflow instructions change.

## 7. Release Readiness

- [ ] `scripts/check.sh` passes from the repo root before pushing, unless the
  PR explicitly documents why a docs-only validation exception is appropriate.
- [ ] CLI behavior changes include focused tests for commands, exit codes,
  `--json`, and TTY/non-TTY behavior where relevant.
- [ ] Packaging, entrypoint, bundled-data, skill-discovery, update, or install
  changes include wheel/install smoke evidence.
- [ ] First-run, repo-shape, migration, `mb onboard`, `mb status`, `mb start`,
  or validation changes include fixture business-repo smoke evidence.
- [ ] Runtime discovery, invocation, or skill behavior changes include runtime
  smoke evidence, or the PR states exactly why it could not be run.
- [ ] Bundled `templates/` and the fixture business-repo flow stay in sync with
  `.mb/` schema, skill-discovery, and onboarding changes.
- [ ] `CHANGELOG.md` is updated for user-visible CLI, skill, packaging,
  compatibility, workflow, or release-process changes, using the Keep a
  Changelog categories already in that file (Added, Changed, Deprecated,
  Removed, Fixed, Security).
- [ ] Schema, config-file, or CLI-output breaking changes follow Semantic
  Versioning, bump the appropriate version, and ship with a `mb migrate` path
  or an explicit manual migration step in the changelog.
- [ ] Deprecated CLI surfaces, schemas, JSON contracts, or runtime adapters are
  marked with the deprecation date, the release that will remove them, and a
  migration command or fallback so users are not stranded.

## 8. Issue / PR Discipline

- [ ] GitHub issues are the public durable task thread.
- [ ] Pull requests are proposals and review conversations.
- [ ] Git history tells the evolution story with concern-organized commits.
- [ ] Linear is a visual, planning, release, or private/internal layer; it does
  not replace GitHub as the public coordination primitive.
- [ ] Use `Closes #N` only when the PR fully satisfies the GitHub issue, and
  keep `Closes #N` / `Refs #N` in the PR body rather than commit subjects so
  the close action stays scoped to the merge.
- [ ] Use `Refs #N` for partial slices, setup work, or related context.
- [ ] Public blockers, scope changes, readiness notes, and validation gaps are
  recorded on GitHub where future contributors can find them.
- [ ] Branch history is not rewritten or force-pushed after the first push;
  follow-up fixes land as new commits unless the maintainer explicitly asks
  for a rebase.
- [ ] Suspected security issues follow `SECURITY.md` private channels rather
  than public issues, PR comments, or release notes.
- [ ] Private/local workflow details stay out of GitHub and public docs.

## Review Verdict

Before approval or handoff, answer these plainly:

- Does this preserve Main Branch as public OSS infrastructure?
- Does it keep `mb`, skills, GitHub, Linear, git, and runtime responsibilities
  in the right places?
- Does a new or non-expert user get exact next commands when something fails?
- Does the validation evidence match the surface that changed?
- Is anything here private, overclaimed, or likely to mislead a future agent?

Private local preferences should point to this checklist instead of duplicating
public operating rules. Keep local workflow details private and keep durable
product truth in this repository.
