# Dependency Choices

Main Branch is public open-source infrastructure. Every dependency,
integration, sidecar, MCP server, CLI, and provider adapter should earn its
place by improving an operator loop while preserving the product boundary:
canonical business truth in git, deterministic `mb` commands, optional
sidecars, safe credentials, and honest runtime claims.

This document explains the default judgment. Specific implementation details
belong in accepted decisions, CLI tests, provider docs, or linked issues.

## Principles

1. **Curate rails instead of connecting everything.** Main Branch should choose
   a small set of boring, inspectable provider paths and make them easy to run
   well. A user may have many SaaS tools; the product does not need to integrate
   all of them.
2. **Prefer official provider surfaces.** Use official CLIs, APIs, MCP servers,
   connectors, or adapter docs when they are stable, documented, and
   smoke-testable.
3. **Prefer narrow deterministic CLIs over broad SDKs.** If the job is
   inspectable, scriptable, exit-coded, and easy to test through a CLI, that is
   usually a better Main Branch surface than importing a large SDK into core.
4. **Keep optional sidecars optional.** Specialized tools can enrich Sense and
   Ship workflows, but a missing sidecar must degrade gracefully instead of
   breaking the core install.
5. **Add dependencies for user loops, not novelty.** A tool earns its place
   when it makes Sense, Decide, Ship, or Reflect better for operators.
6. **Remove redundant or fragile surfaces.** Decline or remove dependencies
   that become redundant, unmaintained, private, fragile, confusing, or
   superseded by an official path.
7. **Keep secrets out of repos.** Credentials belong in the OS keychain,
   runtime-local config, environment variables, 1Password, or another explicit
   secret store. Repo files may hold only safe metadata.
8. **Describe capabilities before vendors.** User-facing copy should say what
   the operator can do. Name a vendor only when the vendor choice affects setup,
   support, credentials, cost, or a provider-specific workflow.
9. **Do not claim support before evidence.** A path is supported only when the
   adapter, docs, and smoke evidence exist. Until then, describe it as planned,
   experimental, or a target.
10. **Leave an exit path.** Every dependency should have a plausible removal,
   replacement, or graceful-degradation story before it becomes product shape.

## Build, Buy, Or Wrap

Main Branch should not absorb every useful tool into the core CLI. The default
choice is:

- **Use an official provider surface** when the provider already has a stable
  CLI, API, MCP server, or connector that can be smoke-tested and explained.
- **Wrap with `mb`** when operators need deterministic readiness checks,
  business-language routing, repair guidance, approval gates, or safe metadata
  around that provider.
- **Use an optional sidecar** when the work needs specialized data capture,
  scraping, analytics, bookkeeping, media generation, or scheduling that would
  make the core package heavy or provider-specific.
- **Build inside `mb`** only when the behavior is part of the common control
  plane: repo shape, validation, graph/status facts, update/repair paths,
  runtime wiring, provider readiness, issue drafting, or guarded checkpoints.
- **Defer** when the path would require unsupported runtime claims, untested
  account mutation, committed secrets, broad browser automation, or a hosted
  state model that has not been accepted.

This keeps the daily loop coherent. Users think in bets, pushes, playbooks,
outcomes, and checkpoints. `mb` checks whether the rails are ready. Provider
tools and sidecars do narrow jobs behind explicit contracts.

## Decision Rubric

Use this rubric before adding, promoting, replacing, or removing a dependency.

| Question | What to look for |
|---|---|
| Which operator loop improves? | Sense, Decide, Ship, or Reflect. Ops is a Ship channel, not a fifth loop. |
| Is there an official provider path? | Prefer official CLIs, APIs, connectors, MCP servers, docs, and account models when they can be tested. |
| Can Main Branch test it? | Local tests, CI tests, read-only smoke, package smoke, fixture repo smoke, or runtime smoke as appropriate. |
| Does it require paid access or hosted setup? | Document account requirements, OAuth/developer-app steps, billing assumptions, and no-account fallback behavior. |
| Where do secrets live? | Credentials must stay outside tracked repos; repo metadata must be safe to share. |
| Does it cross runtime boundaries? | Claude Code is first-class today; other runtimes need adapters and smoke evidence before support claims. |
| Can failures be explained? | `mb doctor`, `mb connect`, `mb status`, or provider docs should tell the user what failed and the next command. |
| Does it mutate external accounts? | Spending, publishing, emailing, deploying, and customer/account mutation need explicit operator action and provider authority. |
| What is the exit plan? | Record the replacement, fallback, deprecation path, or reason the dependency can stay optional. |

## Build, Wrap, Sidecar, Or Decline

Use this rule when a provider, CLI, API, MCP server, hosted workflow, or future
helper tool already exists.

| Product move | Use when | Do not use when | Main Branch owns |
|---|---|---|---|
| Use the provider directly | The official CLI, API, MCP server, or dashboard is already the right operator-facing surface; the workflow is low-risk, one-off, or provider-native; and Main Branch does not need repo context to explain it. | The workflow affects daily status, setup, repair, publishing, spending, account mutation, or business-memory routing. | Documentation, exact commands, and optional links from business files. |
| Wrap with `mb` | The provider affects a Main Branch loop and operators need readiness checks, safe metadata, repair commands, JSON facts, approval gates, or business-language routing. | The wrapper would hide provider authority, duplicate a large provider product, or run judgment-heavy synthesis inside `mb`. | Connection metadata, health/readiness states, repair guidance, deterministic checks, and approval boundaries. |
| Build an optional sidecar CLI | The job is specialized, provider-heavy, independently testable, and useful across workflows, but would bloat core `mb`; it can return a stable JSON envelope with provenance and safe failure behavior. | The behavior is universal repo structure, migration, validation, or runtime wiring that every business repo needs. | Discovery, invocation, envelope validation, cache policy, status surfacing, and graceful degradation. |
| Graduate into core `mb` | The behavior is deterministic, repo-structural, broadly needed by skills/status/dashboards, and does not require provider-specific bulk or background service state. | The behavior depends on synthesis, conversation, broad provider APIs, private account data, or optional enrichment. | A stable command, exit codes, tests, future JSON contract, package data, and repair path. |
| Keep manual or decline | The surface is fragile, policy-risky, private-data-heavy, not smoke-testable, not worth the setup burden, or would turn Main Branch into a SaaS hub, bot, scheduler, marketplace, or provider. | A narrow, official, smoke-testable path exists and materially improves an operator loop. | The reason, the fallback, and any follow-up research issue if the surface may become viable later. |

The default is not "build." The default is: use the official rail when it is
enough, wrap it only where Main Branch can make the daily loop safer and more
inspectable, build sidecars only for optional specialized evidence, and promote
to core only after the behavior proves it belongs to every repo.

## Promotion Evidence

A surface moves up the ladder only when the evidence matches the risk.

| Promotion | Minimum evidence |
|---|---|
| Reference or planned | Public docs or accepted decision; no support claim; clear fallback when missing. |
| Optional read-only wrapper | Safe setup path, read-only smoke, bounded output, provenance, failure/repair behavior, and no committed raw private data. |
| Optional mutation wrapper | Provider authority, explicit operator approval gate, dry-run or draft path when possible, mutation smoke in a safe account, rate-limit and rollback/failure notes, and public-safe evidence in the PR. |
| Optional sidecar | One-shot CLI contract, stable JSON envelope, exit-code semantics, schema validation, cache/degraded-state behavior, credential boundary, and package/install impact understood. |
| Core `mb` behavior | Focused CLI tests, exit codes, `--json` behavior where useful, fixture repo smoke when repo shape changes, package/install smoke when packaged data or entrypoints change, docs, changelog when user-visible, and runtime/manual smoke when skills depend on it. |

Secrets, OAuth refresh tokens, service-account JSON, API keys, raw provider
exports, ledgers, transcripts, customer/member data, raw DMs, conversion upload
rows, and private account analytics never become promotion evidence in public
docs or fixtures. Record sanitized summaries, command output shapes, and
public-safe screenshots or notes instead.

## Concrete Applications

Use these examples as the current boundary until a later accepted decision or
smoke result changes them.

| Surface | Current move | Boundary |
|---|---|---|
| Company/context enrichment | Optional sidecar reference | `companyctx` proves the sidecar contract for public company/domain context. `mb` may discover, invoke, validate, cache, and summarize it, but the core install must work without it. |
| Bookkeeping / Beancount-style finance | Optional future sidecar or private Ops workflow | Plain-text ledgers fit the files-first philosophy, but raw finance data has a stricter access boundary. Keep raw ledgers in private sources; write only approved summaries to shared repos. |
| Vercel-style platform workflows | Use provider directly unless a rail is adopted | Vercel CLI/API can own Vercel-native deploys, env pulls, logs, and domains. Main Branch should not wrap it by default or present it as the default site rail while Cloudflare is the adopted path. Wrap only if a specific tested business loop needs readiness, repair, or approval gates. |
| Cloudflare sites, DNS, and Pages | Adopted provider rail where smoke-tested; wrap with `mb` | Cloudflare remains the current low-lock-in rail for site/DNS/Page workflows. `mb connect`, site checks, and skill guidance should expose readiness and repair facts without committing tokens or hiding publish/deploy approval. |
| Postiz / social scheduling | Candidate scheduling rail after partial API smoke | Treat Postiz as planned for scheduling, drafting, connected-account inspection, and publishing support only after a connected-channel smoke proves draft or scheduled post creation. The first API smoke proved reachability/auth and found no connected channels, so Main Branch still does not claim support. It is not a general inbox, auto-DM, auto-like, or growth-bot dependency. |
| Apify / X/Twitter research | Optional read-only research sidecar, not an official X integration | Apify Store actors can help bounded public X post search, profile/timeline mining, replies, quotes, trends, and network research when the operator deliberately accepts the terms, privacy, reliability, and cost tradeoffs. Main Branch should wrap actor choice, limits, cost/token estimates, provenance, and raw-output handling rather than build a scraper or claim guaranteed reply-tree coverage. Posting, replies, likes, retweets, follows, DMs, browser automation, and comment-to-DM flows are declined unless a later decision accepts an official provider path with approvals, tests, docs, and smoke evidence. |
| Google Ads / GTM readiness | `mb` readiness wrapper plus possible future sidecar | `mb` owns static site instrumentation checks, safe metadata, readiness states, and repair guidance. Google owns account state. Publishing GTM, creating conversion actions, uploads, billing, budgets, and campaign launch require explicit operator approval and provider smoke before support claims. |
| Provider-readiness checks | Core `mb` when deterministic, sidecar when provider-heavy | Generic connection state, safe metadata, and repair commands belong in `mb connect`, `mb doctor`, and `mb status`. Deep provider inspection belongs in optional wrappers or sidecars when the provider-specific surface would bloat core. |

## Decision States

Use boring words when recording a choice:

- **Adopted**: part of the supported product surface with validation evidence.
- **Planned**: preferred direction, but not yet supported.
- **Reference**: useful implementation pattern, not required for core use.
- **Optional**: supported or planned enrichment path that must degrade
  gracefully when missing.
- **Removed**: no longer a supported or recommended path.
- **Declined**: considered and intentionally not adopted.
- **Superseded**: replaced by another path; keep the reason visible.

Decisions are revisable. When product direction changes, update the running
choices log or add a dated decision so future contributors do not have to infer
why a tool disappeared.

## Running Choices Log

| Date | Surface | Candidate | Decision | Why | Replacement / next path | Issue |
|---|---|---|---|---|---|---|
| 2026-05-05 | Meta Ads account access | Pipeboard MCP/tools | Removed | A third-party connector should not remain a Main Branch dependency or fallback after the product direction moved to the official Meta path. Keeping it would preserve confusing setup, pricing, and tool-name assumptions. | Use provider-agnostic Meta account-access guidance now; evaluate Meta's official Ads CLI / Ads AI Connectors as the planned path after detection and read-only smoke are wired. | [#304](https://github.com/noontide-co/mainbranch/issues/304) |
| 2026-05-05 | Meta Ads account access | Meta Ads CLI / Ads AI Connectors | Planned | Official provider surfaces are preferred, but Main Branch should not claim live support until setup, detection, and read-only smoke are verified. | Keep Meta readiness planned in `mb connect`; document exact supported commands only after smoke evidence exists. | [#304](https://github.com/noontide-co/mainbranch/issues/304) |
| 2026-05-05 | Google Ads / GTM | Official Google Ads and Tag Manager surfaces | Planned | Paid traffic needs deterministic measurement and conversion checks before spend. Main Branch should prefer official Google paths and local site checks over broad browser automation. | Keep current `mb site check` readiness states; promote Google Ads/GTM automation only behind approval gates and smoke evidence. | [#286](https://github.com/noontide-co/mainbranch/issues/286) |
| 2026-05-04 | Context enrichment | `companyctx` | Reference | Public company/domain context is useful across Sense and Ship workflows, but it should prove the sidecar contract without becoming a required core install. | Use the optional sidecar contract from [the sidecar enrichment decision](../decisions/2026-05-04-sidecar-enrichment-cli-contract.md). | [#265](https://github.com/noontide-co/mainbranch/issues/265) |
| 2026-05-04 | Bookkeeping and P&L | Beancount | Optional future sidecar | Plain-text ledgers are useful, but real finance data has stricter privacy and access boundaries than normal business repo files. | Keep bookkeeping out of core until `mb books` scope is accepted; write approved summaries to shared repos and keep raw ledgers in private sources. | [#128](https://github.com/noontide-co/mainbranch/issues/128) |
| 2026-05-04 | Research enrichment | Apify | Optional provider-readiness path | Scraping and research actors can enrich workflows, but they require explicit provider setup and should not make core install heavy. | Surface readiness through `mb connect plan` / `mb connect status`; promote only workflows with proven value and safe failure behavior. | [#273](https://github.com/noontide-co/mainbranch/issues/273) |
| 2026-05-07 | Public social research | Apify X/TikTok/YouTube actors | Reference optional path | Public social scraping can help Sense workflows and `/mb-think` research, especially comment mining and profile/post analysis, but actor reliability, platform limits, cookies, and terms vary. | Keep as optional read-only research enrichment. Save synthesized findings to `research/`; do not claim private DM access, account mutation, or guaranteed X reply-tree access. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-07 | X social research | Grok/xAI and public web fallbacks | Optional research path | Real-time X sentiment and public post/profile analysis can enrich Sense, but Main Branch should not require X credentials or imply full public reply access without an accepted adapter and smoke evidence. | Use configured Grok/xAI or public web/embeds/screenshots as fallback; route durable findings through `/mb-think` research files. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-07 | X posting, replies, and DMs | Official X API | Planned mutation path | X posting, replies, and DMs require developer approval, OAuth user authority, rate-limit handling, and explicit operator approval. Main Branch has no accepted adapter or smoke evidence today. | Treat as planned only. Do not automate X replies/DMs from Main Branch until provider authority, approval gates, tests, docs, and smoke evidence exist. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-08 | X resource delivery | Public resource playbooks, official scheduling, and DM/comment automation | Accepted boundary; execution declined | X is useful for public resource drops, build-in-public, and approved scheduling, but interaction-triggered DMs/replies create policy, opt-in, privacy, rate-limit, and support burden that Main Branch has not accepted. | Prefer public links, resource-in-post, build-in-public, manual fulfillment, or provider-native scheduling. Refuse Main Branch-executed comment-to-DM, keyword DM, auto-reply, bulk DM, auto-like, auto-follow, and browser automation; see [the X resource delivery decision](../decisions/2026-05-08-x-resource-delivery-boundary.md). | [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-04 | Sites and DNS | Cloudflare CLI/API | Adopted where smoke-tested | Cloudflare is an official provider path for site, DNS, Pages, and future deterministic CMS/site operations when a flow has a safe token boundary and validation evidence. | Keep credentials outside repos; expand only through explicit `mb connect`, site-readiness contracts, GitHub-linked deploy flows, and operator approval gates. | [#89](https://github.com/noontide-co/mainbranch/issues/89) |
| 2026-05-07 | Social scheduling | Postiz | Candidate rail; partial API smoke completed | Social scheduling is a clear Ship rail, and Postiz has documented MCP/API surfaces plus hosted and self-hosted deployment paths. A private API smoke proved endpoint reachability and auth, but the tested organization had zero connected channels, so Main Branch cannot yet claim draft or scheduling support. | Connect one safe test channel, create a harmless draft or scheduled item, confirm it appears, and record sanitized evidence; see [the Postiz scheduling smoke report](reports/2026-05-07-postiz-scheduling-smoke.md). | [#352](https://github.com/noontide-co/mainbranch/issues/352) |
| 2026-05-07 | Growth automation playbooks | Comment-to-DM and resource-delivery providers | Accepted add-on boundary | Comment-keyword and DM-keyword funnels are useful growth playbooks, but provider write actions mutate inboxes and customer conversations. Main Branch should own playbook specs, approval evidence, resources, and outcomes under `pushes/`, while partner tools or official APIs own mutation until tested. | Keep ManyChat-style tools as add-on candidates, not core dependencies. Defer X comment-to-DM execution, LinkedIn write automation, TikTok DM/comment write, and browser-automation mass-DM tools; see [the growth automation playbook decision](../decisions/2026-05-07-growth-automation-playbook-addons.md). | Schema: [#350](https://github.com/noontide-co/mainbranch/issues/350); X boundary: [#351](https://github.com/noontide-co/mainbranch/issues/351); source context: [#341](https://github.com/noontide-co/mainbranch/issues/341) |
| 2026-05-04 | Workspace docs and sheets | Google Workspace | Planned optional provider | Many operators already have Docs, Sheets, and Drive source material. Main Branch should ingest or reference that material without making Google the canonical memory. | Treat Google Workspace as source/input and provider metadata; durable summaries and decisions flow back into the business repo. | Follow-up issue needed |
| 2026-05-04 | GitHub-native task and release flow | GitHub CLI | Adopted core operational dependency | GitHub issues, pull requests, releases, and auth are central public primitives; `gh` is inspectable, scriptable, and already expected by contributor and issue-drafting flows. | Keep browser/manual fallbacks for user-facing issue submission where needed; use `gh` for GitHub truth and mutations in agent workflows. | [#264](https://github.com/noontide-co/mainbranch/issues/264) |
| 2026-05-07 | Provider/tool boundary | Build vs wrap vs sidecar rule | Adopted docs rule | Main Branch needs one public rule for when to use an external CLI/API/MCP directly, wrap it through `mb`, build an optional sidecar, promote behavior into core, or leave the surface manual or declined. | Apply the rule above before adding provider dependencies, sidecars, or support claims. Create follow-up implementation issues only when concrete smoke evidence or a specific user loop justifies them. | [#366](https://github.com/noontide-co/mainbranch/issues/366) |

## Related Public Contracts

- [ETHOS.md](ETHOS.md) defines the product principles, state model, runtime
  honesty, and optional-sidecar stance.
- [OPERATOR-LOOPS.md](OPERATOR-LOOPS.md) defines Sense, Decide, Ship, Reflect,
  and the Paid / Organic / Pages / Ops channels.
- [compatibility.md](compatibility.md) defines supported, experimental, and
  roadmap runtime surfaces.
- [Sidecar enrichment CLI contract](../decisions/2026-05-04-sidecar-enrichment-cli-contract.md)
  defines how optional sidecars should integrate.
- [Workspace, repo, and sensitive-data boundaries](../decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md)
  defines where secrets, finance/legal data, and provider authority belong.
