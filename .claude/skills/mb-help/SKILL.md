---
name: mb-help
description: "Answer questions about Main Branch and Claude Code. Use when: user asks how/what/why questions, is confused about the business folder, CLI, skills, setup, errors, workflow, or what to do next."
loops: [sense, decide]
---

# Help

Answer questions, troubleshoot issues, explain philosophy, suggest next steps.

**CLI facts first:** For "what should I do?", setup, provider, skill wiring, or
troubleshooting questions, run `mb status --json --peek` and use `mb doctor`
for repair facts before giving prose-only advice.

---

## Workflow

1. **Triage** — Parse user's question/brain-dump
2. **Detect business type** — Check `core/*.md` (Skool? Ecommerce?), with legacy `reference/core/*.md` fallback only if `core/` is absent
3. **Load reference** — Find topic in references/ table below
4. **Answer** — Explain "why" not just "what"
5. **Route** — End with next skill or action

---

## Topic Router

| Keywords | Reference |
|----------|-----------|
| Terminal, drag files, cd, business folder vs site folder | [terminal-basics.md](references/terminal-basics.md) |
| Business folder, CLI, skills, linked site folder, system model | [system-model.md](references/system-model.md) |
| Philosophy, why, compound, passive memory | [philosophy.md](references/philosophy.md) |
| /mb-think, research, decide, codify | [the-think-cycle.md](references/the-think-cycle.md) |
| /mb-bet, bet, hypothesis, deadline, public narration, bet vs offer | [skills-guide.md](references/skills-guide.md) |
| Work continuity, where left off, GitHub issues | [work-continuity.md](references/work-continuity.md) |
| Error, command not found, MCP, Apify setup, GitHub issue | [troubleshooting.md](references/troubleshooting.md) |
| Provider readiness, GitHub setup, Cloudflare, Google Workspace, Meta Ads, Apify | [provider-readiness.md](references/provider-readiness.md) |
| Getting started, setup | Route to `/mb-setup` or `/mb-start` |
| Which skill, when to use | [skills-guide.md](references/skills-guide.md) |
| Create skill, Notion export, custom | [skills-guide.md](references/skills-guide.md) |
| Migrate from GPT, ChatGPT | [gpt-migration.md](references/gpt-migration.md) |
| Reels, TikTok, organic, /mb-organic | [organic-help.md](references/organic-help.md) |
| Skool, community | [skool-help.md](references/skool-help.md) |
| Wiki, atomic notes, publish, WikiLinks | Route to `/mb-wiki` |
| Site, landing page, lander, minisite, website, about page video, deploy site, publish site, conversion endpoint, concept variations | Route to `/mb-site` (see [skills-guide.md](references/skills-guide.md) for the full one-flow walkthrough) |
| Done, wrapping up, closing, end session, end of day | Route to `/mb-end` |
| multi-offer, product ladder, offers, switch offer | Multi-Offer FAQ (below) |
| Better outputs, quality, what next | [making-outputs-better.md](references/making-outputs-better.md) |
| Content strategy, pillars, platforms, newsletter, channel strategy, account strategy, founder voice, weekly content plan | [content-strategy-help.md](references/content-strategy-help.md) |
| Subagents, parallel, agents, context window, tokens | [working-with-agents.md](references/working-with-agents.md) |
| workspace-isolated tools, sandboxed workspace, skills not showing | [workspace-setup.md](references/workspace-setup.md) |
| Contribute, contributor | [becoming-contributor.md](references/becoming-contributor.md) |

---

## Principles

- **Explain "why"** — Not just steps
- **End with action** — Suggest next skill (`/mb-think`, `/mb-setup`, `/mb-ads`, `/mb-site`, `/mb-organic`)
- **Beginner-friendly** — Many never used Terminal
- **Honest about gaps** — The system is new and evolving. Acknowledge what's still being built rather than presenting everything as polished.
- **Public issue safety** — Suggest `mb issue draft` for reproducible Main Branch friction, but never submit issues for the operator.

---

## Quick Answers

| Question | Answer |
|----------|--------|
| Is this a bet or an offer? | If you're testing whether a direction should continue, it is a bet in `bets/`. If it is something the business sells or may sell repeatedly, it is an offer. A live idea can be both: open the bet first, then create or update the offer only when the operator wants durable sellable truth. |
| Start Claude in a folder? | `cd ~/Documents/GitHub/[your-business] && claude` — Claude sees files in that folder. Main Branch is linked via `settings.local.json`, with bridge links as a compatibility fallback for skill discovery. |
| I see `.mb/`, not `.mb-vip/`. Is that wrong? | You're good. `.mb/` is the current repo-local Main Branch state folder. `.mb-vip/` was old clone-based setup language and is not required. If slash commands are missing, use `/mb-update` or run `mb update --repo .`, then repair skill links and restart Claude. |
| Do I start Claude in the business folder or site folder? | Start in the business folder for strategy, bets, decisions, offers, and routing. Switch to a linked site folder only for site implementation work. Linked site folders should have `.mainbranch/repo.json`; older site folders may still use `.mainbranch/source.json`. |
| When use skill prompts? | For structured tasks: `/mb-start`, `/mb-think`, `/mb-ads`, `/mb-site`, `/mb-organic` |
| Drag files in? | Drag from Finder into Terminal, path appears |
| Voice input? | [Wispr Flow](https://ref.wisprflow.ai/main) (affiliate link) |
| What is content-strategy.md? | The business-level content strategy and index: what you want to be known for, who content is for, pillars, content jobs, and what not to publish. Use `core/marketing/` and `core/people/` only when you need channel, account, or person-specific layers. |
| How do I build a content strategy? | Run `/mb-think`. Start with offer clarity, recognition target, audience, and 3-5 pillars in `core/content-strategy.md`. Add distribution, channel, account, and person files only when the simple file gets crowded. |
| How do pillars work? | Each pillar is a content theme that passes three tests: Soul test (connects to why), Offer test (leads to mechanism), Audience test (they care). 3-5 pillars cover your content universe. |
| What's the content pipeline? | Strategy first, then distribution. Owned assets, email, social, communities, wiki, changelog, and paid amplification should point at the same offer and recognition target. Specific execution lives in `pushes/`; results land in `log/`. |
| What are subagents? | Claude can spawn parallel agents to research or review simultaneously. You'll see it happen automatically in `/mb-think` (multi-source research) and `/mb-ads review` (6 compliance lenses). Each agent gets its own context window so your main conversation stays clean. |
| How do I manage context/tokens? | Context management is a skill that develops over time. Your files (`core/`, `research/`, `decisions/`) survive compaction — only conversation memory compresses. After compaction, help Claude rebuild by pointing it at recent files or running /mb-start. Save insights to research files early — if it's in a file, it's safe. |
| How do I close a session? | Run `/mb-end`. It summarizes what happened, asks if you have final thoughts, offers a crystallize moment if you made decisions, and guides an approved checkpoint instead of raw git commits. Bookend to `/mb-start`. |
| What is multi-offer? | Multiple products under one brand, one business folder. Each offer gets its own `core/offers/[name]/offer.md`. Soul and voice stay in `core/` because they're brand-level. Use when you sell multiple things (community + newsletter + done-for-you). If you have no `core/offers/` folder, you're in single-offer mode — everything reads from `core/` and nothing changes. |
| How do I switch offers? | Say `/mb-start [offer-name]` or answer when /mb-start prompts. The choice is session-scoped unless you explicitly approve saving it as local active-offer state. |
| Where do offer files go? | In a single-offer repo, `core/offer.md` is the durable offer truth. In a multi-offer repo, `core/offer.md` is the portfolio thesis and `core/offers/[name]/offer.md` holds offer-specific details. Legacy `reference/offers` and `reference/core` may point at those folders as compatibility bridges; do not edit both. |
| What stays in core with multiple offers? | `soul.md` (always), `voice.md` (always), `audience.md` (base, with optional per-offer overrides), `content-strategy.md` (business-level content strategy), and optional `core/marketing/` / `core/people/` layers. |
| Where does proof go? | Company-wide testimonials go in `core/proof/testimonials.md`, average-case context in `core/proof/typicality.md`, and angles in `core/proof/angles/`. Offer-specific proof uses matching files under `core/offers/[name]/proof/`. |
| Can I delete or rename an old offer folder? | Ask first. Offer folders are durable business history. Rename, delete, merge, or move them only after an accepted decision, approved migration plan, or explicit operator instruction. |
| How do I add another offer? | Run `/mb-setup` -- it detects your existing setup and offers a migration path. Or use `/mb-think` to plan the new offer first. |
| Do I need separate folders for separate businesses? | If they share `soul.md` and `voice.md`, use one business folder with `offers/`. If they have different identities, use separate folders. The test: shared soul = shared folder. |
| Do my files disappear when context compacts? | No. Compaction compresses Claude's conversation memory, not your files. Everything in `core/`, `research/`, and `decisions/` is on your hard drive, version controlled with git. If it's in a file, it's permanent. |
| How do I recover after compaction? | Point Claude at recent files: "look at my last 3 decisions" or "read the commits from today." Or just run /mb-start — it scans your folders and rebuilds context automatically. You can also open files yourself in Cursor, Warp, VS Code, or any text editor. |
| Is this system finished? | Still new and actively being tuned. We're building around Claude Code, minimizing commands you need to learn while giving you real power. There's progressive discovery in /mb-think — the more you use it, the more it reveals. You might find workflows we haven't documented yet. Post them in Skool. |
| Where can I see my files? | Open your business repo folder in Finder, Cursor, Warp, VS Code, or any text editor. They're regular .md files on your hard drive. GitHub Desktop also shows them with version history. |
| What should I connect first? | Run `mb connect plan` from your business repo. It shows GitHub, Cloudflare, Google/Workspace, Meta Ads, and Apify as numbered choices with readiness and exact next commands. |
| Skills not showing in a workspace-isolated tool? | Run `mb skill link --repo .` from the business repo when possible, then restart Claude. Some tools also support a pre-start script that creates bridge links and `settings.local.json`; see [workspace-setup.md](references/workspace-setup.md) for the generic pattern. |
| What's a pre-start script? | A workspace tool hook that runs before the agent starts. Use it to set up Main Branch bridge links only when `mb skill link --repo .` is not enough. |
