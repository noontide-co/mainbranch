# Troubleshooting

Common issue fixes for `/mb-site`. Load this only when the operator is blocked or reporting a specific failure.

## No Site Configured

Run `/mb-site` and pick "new site from scratch." The skill walks setup, then writes repo-local `.mainbranch/source.json` in the site repo and a reverse site record in the business repo. Treat `~/.mainbranch/sites.json` as a legacy fallback.

## Cloudflare Pages `github_app_not_installed`

The Cloudflare Pages GitHub App OAuth handshake has not been completed for the account.

Walk through it once:

1. Open https://dash.cloudflare.com.
2. Go to Workers & Pages.
3. Create application.
4. Continue with GitHub.
5. Connect any repo.
6. Close the tab after the handshake.

After that, `pages.py create-project --repo-owner ... --repo-name ...` works.

See [`cloudflare-pages-link.md`](cloudflare-pages-link.md) for the full walkthrough.

## `verify_live.py` Fails

First check the canonical Main Branch provider state:

```bash
mb connect doctor --json
```

If `provider:cloudflare` is not `ready`, reconnect and retest before running
Cloudflare-dependent `/mb-site` tools:

```bash
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=...
mb connect test cloudflare
```

Use a user API token only as a fallback by omitting `token_type=account`.
After `mb connect` is ready, `verify_live.py` is the deeper manual smoke.
Porkbun skipped is fine for the Cloudflare-registered path.

## Website Build Failing

This applies to Website shape with a build step, not minisites.

```bash
cd <site_repo>
node --version
pnpm install
pnpm build
```

Common causes:

- wrong Node version; use Node 18+;
- missing dependencies;
- TypeScript errors.

The minisite shape is static HTML and does not have a build step. If you are getting build errors on a minisite, the project repo is configured like the wrong shape.

## Styles Not Applying

Minisite: each generation produces self-contained HTML/CSS. The issue is usually stale browser cache or a missing file. Hard-refresh the browser and check `_headers` if cache-control is aggressive.

Website (Next.js): check `globals.css` for correct CSS variable names, `layout.tsx` for font imports, and run `pnpm dev` locally.

## Business Context Not Found

Check `.mainbranch/source.json` in the site repo or the reverse site record in `pushes/`. Inspect `campaigns/` only for legacy repos.

The `business_repo` path must point to a business repo with canonical `core/` files. Legacy `reference/core` and `reference/offers` paths are compatibility bridges only.

## Site Looks Generic Or AI-Written

Run `/mb-site` again and trigger review gates.

- The De-AI'd gate flags AI tells.
- The Voice gate checks against `voice.md`.
- If `voice.md` is thin, strengthen it via `/mb-think codify`.

For Website shape, read [`frontend-design.md`](frontend-design.md).

## Conversion Endpoint URL Not Wired

Check `<site_repo>/.mainbranch/conversion.json`.

The generation subagent reads `kind`, `url`, and `render`, then substitutes the URL into CTA hrefs. If the file is missing or has `https://CONVERSION-PLACEHOLDER`, run `/mb-site` again and re-run [`minisite-conversion.md`](minisite-conversion.md).

## Netlify Legacy

If the site is a pre-V1 Next.js template still deploying to Netlify, see [`deployment.md`](deployment.md).

## See Also

- [`examples.md`](examples.md) - usage examples.
- [`minisite-setup.md`](minisite-setup.md) - setup flow.
- [`site-recovery.md`](site-recovery.md) - compaction and repo-switch recovery.
