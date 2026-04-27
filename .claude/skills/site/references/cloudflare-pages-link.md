# Cloudflare Pages Git Link

Use this when the Pages project does not exist yet. This is the one V1 dashboard step that creates a Git-connected Pages project with auto-deploy.

1. Go to https://dash.cloudflare.com
2. Left sidebar: **Workers & Pages**
3. Click **Create application**
4. Click the small link at the bottom: **Pages: Get started**. Do not choose the Worker option.
5. Select **Connect to Git**
6. Authorize GitHub if prompted, then select the site repository.
7. Configure build settings:
   - Project name: the intended Pages project name, for example `thelastbill`
   - Production branch: `main`
   - Build command: empty for plain static HTML, or the template's build command
   - Build output directory: `/` for plain static HTML, or the template's output directory
8. Click **Save and Deploy**

First build usually takes 1-2 minutes. After the deploy succeeds, Cloudflare shows the `*.pages.dev` URL. The custom domain attachment is handled separately by `pages.py set-domain`.
