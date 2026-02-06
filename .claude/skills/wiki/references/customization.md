# Customize Your Wiki

All personalization lives in `src/config.ts`. Components import from this file — you never need to edit Astro components directly for branding.

For home note content (Right Now, Looking For, Ask Me About), edit `src/content/notes/index.md` or use `/wiki home`.

---

## Site Config (`src/config.ts`)

```typescript
export const config: SiteConfig = {
  displayName: "Jane Smith",           // Full name (header, meta, structured data)
  shortName: "Jane",                   // Mobile header
  tagline: "Building in public",       // Meta description, OG tags
  siteUrl: "https://jane.pages.dev",   // Deployed URL (no trailing slash)
  avatar: "/avatar.jpg",               // Path in /public
  links: [                             // Social links (shown on home page)
    { label: "GitHub", url: "https://github.com/janesmith" },
    { label: "Twitter", url: "https://x.com/janesmith" },
    { label: "Website", url: "https://janesmith.com" },
  ],
  themeColor: "#3b82f6",               // Accent color (CSS value)
  footer: {
    text: "Powered by Commune",        // Footer link text
    url: "/",                          // Footer link URL
  },
  // Uncomment to enable Plausible analytics:
  // plausible: {
  //   domain: "jane.pages.dev",
  //   src: "https://plausible.io/js/script.js",
  // },
};
```

Leave `links` as `[]` to hide social links. Remove or comment out `plausible` to disable analytics.

---

## Home Note (`src/content/notes/index.md`)

The home note has structured frontmatter for future people-matching:

```yaml
---
title: "Jane's Working Notes"
created: 2026-02-06
updated: 2026-02-06
visibility: public
status: live
tags: [home, welcome]
aliases: ["home", "welcome"]
summary: "One-liner about who you are"
right_now: "What I'm working on or thinking about"
looking_for: "What I want from this community"
ask_me_about: ["topic-1", "topic-2", "topic-3"]
---
```

The body sections (Right Now, Looking For, Ask Me About, About) should mirror the frontmatter. Use `/wiki home` to update both at once.

---

## Profile Endpoint (`/api/profile.json`)

Generated at build time from `config.ts` + `index.md` frontmatter. No manual editing needed — it updates automatically when you change config or the home note and rebuild.

Returns:
```json
{
  "name": "Jane Smith",
  "bio": "Building in public",
  "right_now": "What I'm working on",
  "looking_for": "What I want from this community",
  "ask_me_about": ["topic-1", "topic-2"],
  "links": [{ "label": "GitHub", "url": "..." }],
  "last_updated": "2026-02-06"
}
```

---

## Avatar

**Via `/wiki configure`:**
- When prompted, drag and drop your image into the terminal
- The file path gets pasted automatically
- Image is copied to your wiki's `public/avatar.jpg`

**Manual:**
1. Replace `public/avatar.jpg` (or `.png`) with your image
2. Recommended size: 200x200px, square crop
3. Run `/wiki publish` to deploy

---

## Site URL / Domain

Edit `siteUrl` in `src/config.ts`:

```typescript
siteUrl: "https://yourdomain.com",
```

The Astro config reads from this value automatically. If changing domains, also update your Cloudflare Pages custom domain settings.

---

## After Any Changes

Run `/wiki publish` to deploy your updates.

Changes typically go live within 90 seconds.
Check status: https://dash.cloudflare.com → Workers & Pages → [project-name]
