# Site Recovery

Load this after compaction, context loss, repo switching, or unclear site state.

## Recovery From Compaction

1. Re-invoke `/mb-site` to reload skill context.
2. Check invocation mode: business repo mode (`core/`) or site repo mode (`.mainbranch/repo.json` or legacy `.mainbranch/source.json`).
3. Load links: read `.mainbranch/repo.json` or legacy `.mainbranch/source.json` in the site repo, or the push/site record in the business repo.
4. Identify the site shape from the push/site record or existing files.
5. Load only the corresponding build reference.
6. Check continuity: use business-repo `mb status --json --peek` facts first, then site-repo git history only for site-code changes.
7. Resume from the last completed step based on git history, descriptor links, and push launch status.

## Scope Boundaries

`/mb-site` covers these shapes:

- lander (1 page);
- minisite (~4-6 pages);
- website (full);
- graduation paths up the ladder, including a website with a CMS bolt-on.

Not for:

- wikis (`/mb-wiki`);
- email templates or newsletters;
- quick mockups without business context files;
- apps with auth, dashboards, or real-time features.

Use a separate app skill or repo for application surfaces that outgrow a site.
