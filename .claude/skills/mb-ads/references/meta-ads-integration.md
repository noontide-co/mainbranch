# Meta Ads Account Access

Meta ad account awareness is additive. `/mb-ads` and `/mb-think` should use
live account context only after deterministic `mb` provider facts say the Meta
path is ready and the current runtime exposes verified read-only account tools.

Main Branch no longer supports third-party Meta MCP setup or detection as a
fallback. The official Meta Ads CLI is real, but Main Branch has not wired
safe detection and read-only smoke yet. Until `mb` reports Meta as ready, skills
must work from repo reference files and manual Ads Manager input.

---

## Current Support State

Meta Ads AI Connectors has two surfaces:

- **Meta Ads CLI**: local Python package `meta-ads`, binary `meta`. This is the
  Main Branch target because Claude Code-first workflows can call Bash.
- **Meta-hosted MCP**: remote server at `https://mcp.facebook.com/ads` for
  supported chat clients. Treat it as forward-looking for Claude Code until the
  OAuth handshake is proven there.

Meta's package metadata classifies the CLI as Alpha as of its 2026-04-29 launch.
Expect setup and command details to move over the next few months.

Main Branch has not wired the CLI into `mb connect` yet. Therefore:

- do not tell users Meta account access is ready unless `mb` says it is ready;
- do not ask users to configure third-party Meta connector fallbacks;
- do not ask users to paste Meta tokens into chat or repo files;
- do not run live campaign mutations from this skill.

Official docs:

- https://developers.facebook.com/blog/post/2026/04/29/introducing-ads-cli/
- https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/get-started
- https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/command-reference

---

## Official CLI Setup Facts

When Main Branch wires this provider, the setup path should follow Meta's CLI
docs:

1. Install the package as `meta-ads`; the binary is `meta`.
2. Use a Meta Developer App and a system user access token for the CLI path.
3. Store `ACCESS_TOKEN`, `AD_ACCOUNT_ID`, and optional `BUSINESS_ID` in a
   gitignored project-level `.env` file, or in Meta's user-level
   `~/.config/meta/` fallback.
4. Verify with `meta auth status`.

The CLI uses this precedence: CLI flag, environment variable, project `.env`,
then user-level `~/.config/meta/`.

Do not recommend `meta auth login`, `meta-ads-cli`, `npm install -g
@meta/ads-cli`, or `mcp.meta.com/ads`.

Meta's documented baseline token scopes are:

- `business_management`
- `ads_management`
- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_ads`
- `catalog_management`
- `read_insights`

Some Business Manager configurations require a second admin to approve system
user token generation. Surface that as conditional repair copy, not a universal
rule.

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
   for the verified official CLI:
   - `which meta`
   - `meta --version`
   - `meta auth status`
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

1. wired `mb connect` detection for `meta auth status`;
2. read-only smoke from a fresh business repo;
3. explicit preview of every account change;
4. explicit operator approval in chat;
5. PAUSED-by-default campaign/ad/ad-set creation preserved;
6. no budget changes without a separate approval gate.

Until those conditions are met, write operations are roadmap only.

---

## CLI Sharp Edges

Future implementers should preserve these constraints in setup and repair copy:

- `meta auth status` is the documented auth check. There is no documented
  `meta auth login`.
- Campaign and ad set creation default to PAUSED. Activation remains a separate
  operator action.
- Creating fresh creatives can require the Meta Developer App to be in Live
  Mode; document this because the CLI docs do not surface it clearly.
- Use project-level `.env` as the default credential location, and keep it
  gitignored.
- Use `~/.config/meta/` only as the user-level fallback.
- If the operator hits a two-admin token approval gate, explain that it depends
  on the Business Manager's security configuration.

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
