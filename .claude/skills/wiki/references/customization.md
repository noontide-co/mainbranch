# Customize Your Wiki

After initial setup, you can update any of these settings manually.

---

## Welcome Page

Edit `src/content/notes/my-working-notes.md`:

```markdown
---
title: Welcome
created: "2026-01-23"
visibility: public
status: live
summary: Your tagline here
---

# Your Heading

Your intro text here.
```

---

## Avatar

1. Replace `public/avatar.jpg` (or `.png`) with your image
2. Recommended size: 200x200px, square crop
3. Run `/wiki publish` to deploy

---

## Display Name / Tagline

Edit `src/config.ts` (or `astro.config.mjs` depending on template version):

```ts
export const SITE = {
  author: "Your Name",
  description: "Your Name's Notes",  // tagline
  // ...
}
```

---

## Social Links

Edit `src/config.ts`:

```ts
export const SOCIAL = {
  twitter: "yourhandle",        // without @
  github: "yourusername",
  websites: [                   // array of URLs
    "https://yoursite.com",
    "https://yourother.site"
  ],
}
```

Leave empty string `""` or remove the line to hide a social link.

---

## Site URL / Domain

Edit `astro.config.mjs`:

```js
export default defineConfig({
  site: "https://yourdomain.com",
  // ...
})
```

If changing domains, also update your Cloudflare Pages custom domain settings.
See `/wiki domain-setup` for help.

---

## After Any Changes

Run `/wiki publish` to deploy your updates.

Changes typically go live within 90 seconds.
Check status: https://dash.cloudflare.com → Workers & Pages → [project-name]
