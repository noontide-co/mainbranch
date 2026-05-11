# Repo Visibility Rubric (Setup Skill Reference)

Use this rubric when `/mb-setup` is creating, connecting, or migrating a
business or site repo. The engine ships the full product rubric
(`repo-visibility-rubric`) and the underlying decision
(`repo-setup-visibility-and-checks-model`); this file is the skill-local
summary.

## Defaults

- Business repos: **private**.
- Site repos: **private**, ask the visibility question once before creating.
- Data/source-record repos: **private**.
- Open-source tool/template/demo/docs repos: **public**.

## The One Question

For site repos, ask exactly this:

> "Should the source files and full change history be public?"

Default to private. Do not assume. Do not bundle this with the deploy
question. Cloudflare is the adopted deploy rail; the operator is not picking
a hosting platform during normal setup.

If the operator answers "I want the deployed site to be public," that is a
different question. Re-read the visibility question with them. Public deploy
is a Cloudflare concern; public source is a GitHub concern.

## Plain-Language Framing For The Operator

When introducing visibility, say something like:

> "Your deployed site can be public on Cloudflare even if the source repo
> stays private. Most people want private source — it keeps drafts, copy
> iterations, and revision history out of public view while the live site is
> still fully public. Choose public source only when the repo itself is meant
> to be public, like an open-source tool, template, demo, or build-in-public
> project."

## What "Private Business Information" Covers

Default to private when the repo will hold any of:

- offer experiments, strategy, plans, operating notes;
- client work, client identifiers, client artifacts;
- draft sites and copy iterations;
- screenshots of dashboards, inboxes, or accounts;
- raw provider exports, customer rows, analytics dumps;
- reports, internal write-ups, bets, decisions, research, pushes in
  progress;
- anything that would create risk, confusion, embarrassment, competitive
  disadvantage, client trust issues, or operational noise if a stranger
  saw it.

When unsure, the answer is private.

## What Visibility Does Not Decide

- Where the repo lives (local, personal GitHub, free GitHub org, paid org).
- Whether GitHub costs money. Free personal accounts and free organizations
  can hold private repos.
- Whether the deployed site is public. That is a Cloudflare deploy choice.
- Whether the operator has push access. That is a permission/publish
  question.

## What `gh repo create` Should Do

When `/mb-setup` or `/mb-site` shells out:

- **Default:** `gh repo create <owner>/<name> --private --add-readme`
- **Only when the operator explicitly answers "public source":**
  `gh repo create <owner>/<name> --public --add-readme`

Do not pass `--public` because the deployed site will be public. Those are
different concepts.
