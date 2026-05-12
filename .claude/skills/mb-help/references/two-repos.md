# Main Branch Engine And Business Repos

This is the key concept. Once you get this, everything else makes sense.

---

## Main Branch Engine

The shared system everyone uses. Contains:
- Skills (`/mb-ads`, `/mb-think`, `/mb-setup`, `/mb-site`, etc.; `/mb-vsl` is a compatibility router)
- Templates and frameworks
- Compliance resources
- Business setup patterns and primitive guidance

**You download updates from this. You never edit it.**

You have read-only access. Think of it like software you install. You use it, you don't rewrite it.

---

## Your Business Repo

YOUR personal folder. Contains everything about YOUR business:
- Your offer, pricing, mechanism
- Your audience, their pains and desires
- Your voice, tone, phrases
- Your testimonials and proof
- Your research and decisions

**You create this when you run `/mb-setup`. You own and control everything in it.**

This is what makes your outputs sound like YOU.

---

## How They Work Together

```
your-business/                    mainbranch/ (linked from business repo)
├── Your offer                    ├── Skills
├── Your audience                 ├── Templates
├── Your voice                    ├── Frameworks
├── .claude/settings.local.json   └── (shared, read-only)
├── .claude/skills/* (bridge links)
└── (yours, you own it)
```

You start Claude in your business repo. `/mb-setup` connects Main Branch through `.claude/settings.local.json` for file access, and adds bridge links when needed for skill discovery. The engine then reads your business files and generates content that sounds like you.

**Same engine + different business repo = different outputs for each business.**

---

## The Game Engine Analogy

Unity (the game engine) provides physics, rendering, audio systems. But Unity alone isn't a game. You need assets: characters, levels, sounds.

The engine + your assets = your game.

- **Main Branch** = Unity (the engine)
- **Your business repo** = Your game assets
- **Skills** = Engine features you can use
- **Reference files** = The assets that make it yours

---

## Why Separate Engine And Business Repos?

**Separation of concerns:**
- Engine updates don't touch your business files
- Your changes don't break the engine
- You can back up your business repo separately
- Multiple businesses can use the same engine

**Portability:**
- Your business memory is yours forever
- You can move it anywhere
- Not locked into any platform

---

## Where Files Live

| Content | Location | Why |
|---------|----------|-----|
| Skills, templates | Main Branch | Packaged with Main Branch |
| Your offer, audience, voice | Your repo | Business-specific |
| Your testimonials and proof | Your repo | Business-specific |
| Your research and decisions | Your repo | Business-specific |
| Generated outputs | Your repo | Business-specific |
