---
type: educational
topic: cloudflare-vs-vercel
status: draft
last-updated: 2026-05-08
---

# Cloudflare vs. Vercel: why Main Branch defaults to boring site rails

Main Branch uses Cloudflare for sites and DNS because most business operators
need predictable publishing more than they need a fancy application platform.

The beginner question is not "which platform is coolest?" The question is:
"Can I publish the page, attach the domain, understand what changed, and avoid
surprise infrastructure work?"

## The beginner version

For Main Branch, a site should usually be:

1. files in a repo;
2. a GitHub-backed deploy;
3. a Cloudflare Pages project;
4. a domain connected through Cloudflare DNS;
5. a clear provider-readiness check before publishing work depends on it.

That path keeps the site close to the same durable memory model as the business
repo. A commit changes the site. Cloudflare publishes the result. The operator
can inspect the repo, the deploy, and the domain.

## Why Cloudflare Pages is the default

**It matches static marketing work.** Most Main Branch site work starts as a
landing page, minisite, wiki, or offer page. Those surfaces should be easy to
build, review, push, and roll back.

**DNS and publishing live together.** Domain setup is one of the places
beginners get stuck. Cloudflare keeps DNS, Pages, SSL, and future Workers close
enough that `mb` and skills can explain one rail instead of five disconnected
vendor surfaces.

**It is git-friendly.** Git-connected Pages projects fit the Main Branch rule:
files and commits are the source of truth, and the deploy is a view over that
truth.

**It leaves room for simple dynamic edges.** If a future workflow needs a small
endpoint, redirect, gate, or webhook, Cloudflare Workers sit near Pages without
turning the whole site into a hosted SaaS app.

## When Vercel or Netlify can still be right

Choose Vercel or Netlify when a project already depends on their platform
features, when a team is already fluent there, or when a specific framework
path is materially easier on that host.

Main Branch's default is not a moral judgment. It is a bias toward boring,
inspectable, low-surprise rails for business pages.

## The safe setup path

Do not connect Cloudflare on day one unless a site job needs it. From the
business repo, start with:

```bash
mb connect plan
```

When the next business action is publishing or attaching a domain, follow the
Cloudflare step that `mb connect plan` prints. Use:

```bash
mb educational provider-readiness
```

for the plain-English version of what connected accounts mean.

## What Main Branch does not claim

Main Branch does not claim every Cloudflare workflow is automated. Site and
provider behavior should be trusted only where the CLI, bundled skills, and
smoke evidence say that path is ready.

Main Branch also does not require every business to leave an existing Vercel or
Netlify site immediately. Migrate when the next business job benefits from the
repo-backed Cloudflare path.
