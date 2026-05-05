# Meta Ads Account Access

Meta ad account awareness is additive. `/mb-ads` and `/mb-think` should use
live account context only after deterministic `mb` provider facts say the Meta
path is ready and the current runtime exposes verified read-only account tools.

Main Branch no longer supports third-party Meta MCP setup or detection as a
fallback. Until the official Meta Ads AI Connectors path has setup proof and a
read-only smoke, skills must work from repo reference files and manual Ads
Manager input.

---

## Current Support State

Meta's official Ads AI Connectors path is the intended supported route:

- remote MCP for AI clients that can connect to Meta-hosted MCP servers;
- local Ads CLI shape for terminal agents;
- Meta-authenticated account access rather than committed tokens;
- read and write surfaces reported by Meta's launch materials, with mutation
  gated by explicit operator approval in Main Branch.

This repository has not yet verified the official setup command, tool names, or
authenticated read-only smoke from a fresh business repo. Therefore:

- do not tell users Meta account access is ready unless `mb` says it is ready;
- do not ask users to configure third-party Meta connector fallbacks;
- do not ask users to paste Meta tokens into chat or repo files;
- do not run live campaign mutations from this skill.

---

## Provider Facts

Provider metadata and repair state come from the CLI:

```bash
mb status --json --peek
mb connect plan
mb connect doctor --json
```

Use the CLI's `summary`, `next_command`, and `repair_command` fields. Do not
write provider readiness into business-repo config from this skill.

If `mb connect` reports Meta as `planned`, explain that live Meta account access
is not wired yet and continue from reference files.

---

## Readiness Flow

Triggered lazily at `/mb-think` or `/mb-ads` when the topic is ads-related:

```
1. Read `mb status --json --peek`.
2. If the operator needs setup choices, run `mb connect plan`.
3. If provider facts are degraded, missing, or planned, run
   `mb connect doctor --json` and quote the repair/setup guidance.
4. Only if `mb` reports Meta account context ready, check the current runtime
   for the verified official read-only account tools.
5. Never block generation on missing account access.
```

---

## Account Context Uses

When read-only account context is verified, use it for these workflows:

| Workflow | Purpose |
|----------|---------|
| Account overview | See active campaigns, current spend, and broad performance direction |
| Creative audit | Find winning angles, hooks, offers, formats, and naming conventions |
| Performance check | Compare recent CPA, ROAS, spend, and volume trends |
| Performance iteration | Generate variants that build on known winners |

Keep account data in conversation context only. Do not write raw account exports,
customer data, tokens, or sensitive performance details into public files.

---

## Graceful Degradation

Ad account context is optional. The entire `/mb-ads` skill works without it.

| With Account Context | Without Account Context |
|----------------------|-------------------------|
| Ask whether to pull live performance before generating | Skip to generation |
| Use winning patterns before generating | Generate from reference files |
| Match account naming conventions | Ask the operator for naming conventions if needed |
| Suggest where new creative fits | Operator decides placement in Ads Manager |

If live account access is missing, mention the option once per session and move
on. Use this framing:

> "Live Meta ad account context is optional. It is not ready in this repo yet,
> so I will work from your reference files. If you want account context today,
> check Ads Manager manually and paste the specific metrics you want me to use."

---

## Mutation Boundary

Read-only account context may inform recommendations. It does not authorize
campaign changes.

Before any future write operation exists, Main Branch needs:

1. verified official tool names and setup docs;
2. read-only smoke from a fresh business repo;
3. explicit preview of every account change;
4. explicit operator approval in chat;
5. paused-by-default campaign/ad/ad-set creation where the official surface
   supports it;
6. no budget changes without a separate approval gate.

Until those conditions are met, write operations are roadmap only.

---

## Proactive Suggestions

When account context is verified, skills can suggest it at natural moments.
Describe the capability, not the vendor or transport.

| Context | Suggestion |
|---------|------------|
| Before generating new creative | "Your Meta ad account is connected. Want me to pull live performance data first? I can see what's spending, which creative has the best CPA, and use that to inform what we create." |
| After generating a batch | "Want to compare this against what's currently live before you upload it?" |
| In `/mb-think` with an ad-related topic | "Should we use live ad account data for this research, or stay with reference files?" |
| Monday review cadence | "Want to check this week's Meta ad performance?" |

Rules:

- suggest once per context;
- user can decline;
- frame as optional account context;
- fall back to reference files or manual Ads Manager notes.

---

## See Also

- [entry-points.md](entry-points.md) - how account access composes with other entry points
- [post-generation-pipeline.md](post-generation-pipeline.md) - where account awareness fits in post-generation review
- `/mb-think` SKILL.md - ad-account research routing
