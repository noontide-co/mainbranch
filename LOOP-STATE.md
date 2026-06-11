# LOOP-STATE — the Main Branch development loop

The continuity file for the all-day `/loop` session that builds the engine.
Each iteration reads this first, does the next smallest correct slice, and
updates this file in the same PR. Devon steers by editing the **Steering**
section; the loop never overrides it.

Canon (read on first iteration of a fresh session):
- The architecture lock: `noontide` hub → `decisions/2026-06-11-mb-three-layer-architecture-and-pulse.md`
  (three layers; data flows down only; patterns graduate up only when proven).
- The graduation queue: issues #803–#808 + #812–#820 on noontide-co/mainbranch.

## Steering (Devon edits this; loop obeys)

- Mission: improve and fix Main Branch's current issues. Work the priority
  order below. Small slices, release discipline.
- Check-in cadence: Devon reviews every few hours. Park anything ambiguous
  in **Flagged for Devon** instead of guessing.

### Steering input — transcribed from Devon, 2026-06-11 chat (loop wrote this down verbatim-in-spirit; Devon may edit)

- Bigger frame: we are revamping Main Branch from the learnings of three live
  businesses — Booked Out Roofers, Awake Happy, The Morning Paper. Each runs
  its own loop session; they feed engine improvements. Fix what feels
  over-built, strengthen what the businesses proved.
- **Audit (first-class ask):** audit the open PRs, the CI checks run on every
  PR, and the post-release setup. The ideas are right; execution can be
  strengthened, tapered, or better enforced. Loop has judgment latitude here.
- **Session-log mining:** valuable Claude Code session logs live on this
  machine — especially one week-long BOR session (idea → built business →
  first leads). Mine them for engine signals. Subagents/workflows encouraged
  for large scrapes.
- **Plugin setup:** research and decide the right Claude Code + Codex plugin
  setup (a known hole); loop does the research and makes the call for Devon.
- **Setup revamp:** first-run setup should be "copy-paste this one prompt"
  (modeled on the Morning Paper install): tell the user to pick strongest
  settings (Claude: Fable 1M + extra reasoning; Codex: 5.5 + extra
  reasoning), then paste one prompt that explains Main Branch, opens the
  files, and teaches CLI/skills/primitives/GitHub from first principles.
  Loop to evaluate ("steal it or tell me").
- **Validated primitives:** Cloudflare, Resend, Apify are proven. Consider
  redoing/integrating impeccable + Corey's marketing skills with ours.
- Permissions granted: read keychain to understand provider state (never
  print a token), look at Facebook/Google ads, Cloudflare, fal.ai
  CLIs/MCPs; use subagents and workflows freely.

## Priority order (from the 2026-06-11 decision)

1. **#812 `mb connect token <provider>`** — smallest slice; unblocks every
   collector; de-fragiles the live BOR brief. START HERE.
2. **#804 worktree skills bug** — critical-tagged; silently breaks /mb-* in
   worktrees; blocks community usability.
3. **BOR brief → collector refactor** (pulse v0): split the 4 sources of
   `~/.claude/scheduled-tasks/bor-daily-operator-brief/SKILL.md` into
   deterministic collectors (morning-brief contract), definition versioned in
   the noontide hub. Proves the shape on a live business.
4. **#813 `mb pulse init` + /mb-pulse** — generalize step 3.
5. **#815 delivery-truth doctrine page** (pure docs, cheap), **#814 mb spine
   init/query**, **#816 mb canary init**, **#817 dossier + mb doctor**,
   **#820 operating-principles graduation**, **#803/#805/#806/#808** as specced.
6. **Hub hygiene** (interleave ≤1 small PR per few iterations): the kill/merge
   lists in the 2026-06-11 decision (stale CLAUDE.md lines, proposed-decision
   graveyard, product-ladder missing the live money path).

## Hard guardrails

- PR-only to every protected main (mainbranch main IS protected). Small PRs.
- READ-ONLY on all business data (D1/KV/Resend/Meta/Stripe/Shopify). No
  spend, no publish, no send, no contact mutations, no credential writes.
- Credentials via mb connect keychain / env.sh; never print a token.
- Graduate PROVEN patterns only; no new abstractions (operating-principles §10).
- Validate substantive work with fresh-context agents against LIVE state (§11).
- Never rule on Devon-only calls (Joel lane, bet-doctrine fork, offer-board,
  pulse-into-status question) — park in Flagged for Devon.

## Flagged for Devon

- (10 open questions live in the 2026-06-11 decision; loop appends new ones here)
- Open PRs #809, #810 (your feature branches) still fail Python CI on
  pre-#822 runs; likely fixed by rebase. Loop rebased #811 (Devon asked
  about symlinks) and triggered @dependabot rebase on #801/#802 — want the
  loop to rebase + babysit #809/#810 too, or leave them to you?
- First-win definition for the README "Set up with AI" prompt: loop chose
  "business folder with offer/audience/voice drafted and a clean `mb
  status`, then stop and show." Confirm or sharpen.
- RESOLVED 2026-06-11: the local `test_link_skills_removes_legacy_project_
  symlink` failure was a real engine bug (`bundled_skills()` trusted residue
  dirs), not environment-specific — fixed by #811.
- Priority order after the 2026-06-11 chat steering: loop is treating the
  audit (PRs/CI/post-release) + session-log-mining as the next slices ahead
  of #804, since Devon called the audit "first-class." Confirm or reorder.

## Shipped

- 2026-06-11: decision merged (noontide#173); issues #812–#820 filed; spine
  send-truth (bookedoutroofers#99) + privacy chat disclosure (#98) live;
  unattended-cron allow rules set in ~/.claude/settings.json.
- 2026-06-11: LOOP-STATE seed merged (#821). 15-min loop live on this machine.
- 2026-06-11: #812 `mb connect token <provider>` shipped (PR #823 merged) —
  scripted credential read path (stdout-only token, stderr errors,
  repo→user-scope fallback, --json rejected as pipe-unsafe).
- 2026-06-11: #811 rebased onto main and set to auto-merge — symlink
  root-cause fix (`bundled_skills()` requires SKILL.md; clears the
  local `test_link_skills_removes_legacy_project_symlink` failure) +
  plugin-first skills-distribution decision doc. Answers Devon's
  "symlinks aren't durable" steer; #804's fix path is now #811 Stage 2.
- 2026-06-11: three audits complete (details in loop session):
  (a) CI/release audit — strong release rail; gaps: docs-lint not in CI,
  no concurrency cancel, no job timeouts, no automated version-sync
  preflight; nothing worth tapering. (b) Session-log inventory — BOR
  week-long session found (`f29d63c5…`, nifty-franklin worktree dir, 120MB,
  683 operator prompts, 06-01→06-11) with a 12-day-chunk mining plan +
  privacy-guard distiller spec. (c) Morning Paper install pattern —
  verdict: steal; six-move paste-prompt anatomy documented.
- 2026-06-11: README "Set up with AI (recommended)" section merged (#824) —
  the Morning Paper six-move paste-prompt adapted to Main Branch.
- 2026-06-11: CI hardening — concurrency cancel-in-progress on PR re-push,
  job timeouts (25/15/30/5 min), docs-lint job mirroring check.sh's docs
  naming gate. This PR.

## Next intent

- CI hardening remainder: `scripts/release-preflight.sh` (3-file version
  sync + manifest pytest) referenced from release-agent-contract.md.
- After the docs-lint job proves green on a real PR: add "Docs naming
  convention" to required status checks in branch protection (admin
  mutation — loop will do it unless Devon objects).
- Setup-prompt follow-through: canonicalize the prompt (replace the
  defensive one in docs/beginner-setup.md lines 51–77) + teach
  mb-setup/mb-start to recognize the pasted README prompt as setup intent.
- #804 via #811 Stage 2: plugin-aware `link_status()` + tracked
  `.claude/settings.json` wiring; auto-heal hint on `mb start`/`mb doctor`.
- BOR session mining workflow: 12 day-chunks of `f29d63c5…` + the
  crazy-albattani closer; distiller pass first (drop tool_result bodies,
  redact token patterns), then fan-out extraction (intents, friction,
  primitives coverage, mb/skill invocations, AskUserQuestion decisions),
  then synthesis: timeline + friction leaderboard + primitives map.
- Migrate the BOR daily-brief keychain block to `mb connect token` once #812
  ships in a release (read-only change in the bookedoutroofers repo).
