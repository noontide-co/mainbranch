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
- First-win definition for the README "Set up with AI" prompt: loop chose
  "business folder with offer/audience/voice drafted and a clean `mb
  status`, then stop and show." Confirm or sharpen.
- Backlog audit 2026-06-11 (Devon: "be ruthless"): 15 issues closed with
  rationale + reopen condition (#662 #649 #408 #647 #661 #774 #632 #515
  #615 #613 #772 #775 #159 #735 #189). #152 (Joel lane) untouched per
  guardrail. Skim the closures; reopen anything you disagree with.
- RESOLVED: #809/#810 validated (agent merge-gate reviews), fixed where
  needed (fal-rail FAL_KEY guard + HTTPError sanitization on #809),
  rebased, merged. #801 closed by dependabot itself; #802 merged.

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
- 2026-06-11: CI hardening merged (#825) — concurrency cancel-in-progress,
  job timeouts (25/15/30/5 min), docs-lint job mirroring check.sh.
- 2026-06-11: Devon granted merge autonomy ("validated → keep merging") +
  directed issue-tracker use + ruthless backlog audit. Merge train cleared:
  #809 (fal image rail, hardened per review), #802 (dependabot), #810
  (mb-site SEO reference) all merged. Issue queue refreshed: #826 (release
  preflight), #827 (docs-lint required-check flip), #828 (setup-prompt
  canonicalization, absorbed #632), #829 (BOR session mining) filed;
  15 misaligned issues closed; #735 folded into #741; #764 rescoped to
  "integrate impeccable/Corey as curated dependencies."
- 2026-06-11: test prompts handed to Devon for the BOR / Awake Happy /
  Morning Paper loop sessions (worktree-skill repair field test, setup-
  prompt cold read, plugin Stage 1 smoke after v0.3.43).
- 2026-06-11: #603 dashboard validated + merged after month-old staleness
  review (read-only verified, redaction tested; fix added: `.mb/dashboard/`
  now self-ignores so generated HTML can't be committed). Closes the #599
  implementation; dup #189 closed earlier.
- 2026-06-11: release prep v0.3.43 merged (#831); `oe-v0.3.43` release
  created; publish waiting at the pypi environment gate for Devon.
- 2026-06-11: #827 done — "Docs naming convention" added to required
  status checks after five green real-PR runs.
- 2026-06-11: #829 done — BOR session mined (13 distilled day-chunks,
  14-agent workflow): docs/reports/2026-06-11-bor-session-mining.md.
  Ten friction themes ranked; top three: credential/scope tax (every
  day), unverified provider writes (live money), save-state not
  worktree-real. Meta-signal: on the days the business shipped most,
  mb was used least — the deterministic plane must meet operators
  inside worktrees/fleets/dashboards. Eleven new issues filed from the
  report's [new] items; evidence comments on #803/#818/#820 (#832).
- 2026-06-11: #828 done (#844 merged) — beginner-setup.md carries the
  README paste-prompt (one prompt, two doors; lockstep test keeps them
  byte-identical), mb-setup recognizes the README prompt and follows
  its arc. CI's operator-docs language gate caught one word ("canonical")
  — the business-language rule working as designed.
- 2026-06-11: #804 slice — `link_status()` is now worktree-aware:
  detects a linked worktree (git-dir vs git-common-dir), exposes
  `is_linked_worktree`, and when wiring is broken in a worktree the
  summary explains that worktrees never inherit the machine-local
  wiring and names `mb skill link --repo .` — flows through to
  `mb start`, `mb status` ranked actions, and `mb doctor` untouched
  (#845 merged).
- 2026-06-11: #833 slice — Stripe and Resend are first-class mb connect
  providers (api_key slot, env-var fallbacks, identity metadata: Stripe
  `mode` records test-vs-live intent, Resend `sender_domain` makes
  identity a recorded fact). Roundtrip-tested through SecretStore +
  `mb connect token` (#846 merged).
- 2026-06-11: #833 slice 2 — key-shape validation at intake: malformed
  Stripe/Resend keys refused before storage (error names the expected
  shape, never echoes the value), and Stripe mode-vs-key cross-check
  catches mode=live with a TEST key (and vice versa) at connect time —
  the BOR live-vs-test mixup class, now an intake error. Metadata-only
  connects still allowed (#847 merged).
- 2026-06-11: #815 done — docs/delivery-truth.md: acceptance ≠ delivery
  doctrine (provider message id at send, separate delivery_state,
  webhook fast-path + GET ceiling, page on money-path failure, never
  trust the 200) + channel-agnostic send-function template; suppression
  named as the keystone case. Indexed in docs/README.md, cross-linked
  to #814/#656 (#848 merged).
- 2026-06-11: #805 done — research-placement contract ("research lives
  where its conclusions codify") landed in mb-think research-phase +
  codify-phase references and docs/business-file-contracts.md: codify-up
  invariant, rebuild-tomorrow test, offer frontmatter in multi-offer
  repos (#849 merged).
- 2026-06-11: #803 slice — push frontmatter gains optional
  media_location + media_backend (pushes.py parses them into facts;
  validator: non-empty when present, backend requires location; mb-ads
  push template asks "where do the finished files live?"). Full
  contract promotion + lock/reconcile semantics stay on #803
  (#850 merged).
- 2026-06-11: #820 done — docs/operating-principles.md: the twelve
  principles generalized business-agnostic from the hub source (which
  carried graduation_candidate: mb-vip), plus the decision rule and the
  subagent operating contract (mining rec 19's doctrine home:
  commit-before-return verified, worktree-per-agent, liveness,
  auditor/builder separation, docs-first + stale-doc cleanup).
  mb-setup points operators at it (#851 merged).
- 2026-06-11: #833 done — `mb connect <id> --custom` registers
  operator-named providers (slug-validated, api_key slot) on the same
  SecretStore/user-scope/token/status/test rails; once connected,
  reconnect and all read paths work without the flag
  (`resolve_provider` checks registry → connected customs). Unknown
  provider error now hints --custom. Closes the DataForSEO-class gap
  from mining friction #1. This PR.

## Next intent

Working practice (from Devon's 2026-06-11 grants): validate → merge without
asking; every slice references its issue and closes it via PR body; new
findings become issues (LOOP-STATE keeps ordering, issues keep content).

- **Waiting on Devon: pypi environment approval for v0.3.43** (build done,
  notes synced). Post-publish: verify per docs/post-release-alignment.md.
- Re-rank priority order against the mining report's leaderboard: top
  recommendation cluster is credentials (generic provider path + Stripe/
  Resend first-class, scope manifests, refresh tokens) and verification
  (provider-write receipts) — both currently mid-list as #807/#817/#656.
  Proposed next slices: #828 setup-prompt canonicalization (in flight
  queue), then #804 Stage 2, then the credentials cluster.
- Migrate the BOR daily-brief keychain block to `mb connect token` once
  v0.3.43 publishes (read-only change in the bookedoutroofers repo).
