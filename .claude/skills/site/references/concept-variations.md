# Concept Variations — Parallel Generation on Localhost

After the brief is locked, `/site` generates **multiple visual concepts in parallel** so the operator can pick the one that lands best. Default is **2 concepts** to keep token cost low; the operator can raise the default once they've used the skill at least once.

Each concept is just the home page — no sublinks, no navigation, no per-page detail. The point is design choice, not full-site comparison. The picked concept becomes the seed for the rest of the minisite.

---

## Why parallel concepts

One generation produces one design language. Two produce a real choice. Three or five let the operator see a wider aesthetic space.

Token economics matter — each concept is a full home-page generation (HTML + CSS + signature visual SVG). Default 2 keeps the floor low. The operator opts up if they're OK spending more.

---

## The flow

1. **Brief locked.** The operator has confirmed offer framing, headline, value prop, conversion endpoint, and any framework choice.
2. **Determine concept count.** Read `~/.config/vip/local.yaml` for `default_concepts`. If absent, use `2`.
3. **Spawn N concept subagents in parallel** (foreground only). Each gets the same inputs:
   - Locked brief, `offer.md`, `audience.md`, `voice.md`, `soul.md`
   - **Conversion endpoint info** from `<repo>/.mainbranch/conversion.json` — kind (Stripe payment page / lead form / appointment booking / custom webhook), URL, and render mode (link-out / inline / embedded / form-POST). The home CTA rendering varies by kind, so concepts that don't know the kind will design the wrong shape (e.g., a pricing-card hero for what's actually a lead-form offer).
   - A different "lean" instruction per concept (one warmer, one more structured, etc.).
4. **Each subagent writes its concept to a separate localhost folder** under the project repo: `.mainbranch/concepts/concept-1/`, `concept-2/`, etc.
5. **Start a localhost preview** for each concept (e.g., `python3 -m http.server` on different ports, or a single static server with subpath routing).
6. **Surface URLs to operator.** "Open these and pick: http://localhost:8001 / http://localhost:8002. When you've picked, say `concept 1`."
7. **Operator picks one.** The picked concept's files move from `.mainbranch/concepts/concept-N/` to the project root (or replace whatever's there).
8. **Discard the rest.** Optionally archive to `.mainbranch/concepts/discarded/` for git history; otherwise delete.
9. **First commit goes in immediately.** This is the rawest working version — push to GitHub before iterating. Per the [`Operating principles`](../SKILL.md) section: publish-first, then iterate.

After pick + commit, the rest of the minisite (other pages — how-it-works, picked supporting pages, privacy/terms, /start/thanks/) generates with the picked concept as the design seed.

---

## Per-concept "lean"

When spawning N concepts, the skill assigns each a slightly different instruction so they're not just LLM-randomness variants of the same thing:

| Concept | Lean (example) |
|---|---|
| 1 | Editorial / typographic — type as the dominant visual element |
| 2 | Illustrated / signature artifact — one custom SVG anchors the page |
| 3 (if N≥3) | Documentarian / data-anchored — proof/numbers as the visual hook |
| 4 (if N≥4) | Minimalist / single bold color — restraint as the statement |
| 5 (if N=5) | Maximalist / motion-forward — animation drives the experience |

Operators can override by supplying their own leans (e.g., "I want one warm + one cold"). The lean is short — a sentence each — and feeds the concept subagent's prompt.

---

## Default concept count

Stored in `~/.config/vip/local.yaml` per the `start/references/config-system.md` config split:

```yaml
# ~/.config/vip/local.yaml
vip_path: /path/to/vip
user: dmthepm
default_concepts: 3  # optional; defaults to 2 if absent
```

**First-run nudge:** after the operator picks a concept on their first `/site` run, the skill prompts:

> Worked? Want more variations on the next run? You can raise the default — `default_concepts: 3` (or 5) in `~/.config/vip/local.yaml`. Each concept costs roughly the same token budget as one full home-page generation, so 5 ≈ 5x the home-page cost. 2 is fine if you're tight on budget.

---

## Foreground-only

Concept subagents must run in the foreground. Background subagents have a known file-write bug — files appear written but don't persist (per [Operating principles](../SKILL.md)). Concept generation specifically needs files on disk to start the localhost preview, so a silent write failure blocks the whole flow.

---

## Token-saving tips

- **Home page only.** No nav, no other pages. Each concept is one `index.html` + `styles.css` + `og.svg` + `favicon.svg`.
- **Reuse offer/audience/voice loads.** All N subagents read the same reference files; the orchestration loads once and passes the content into each subagent's prompt rather than having each re-read.
- **Discard fast.** When the operator picks, immediately delete the unpicked concepts so the project repo stays clean. The git history of the `.mainbranch/concepts/` folder shows what was tried.

---

## What this is NOT

- **Not multi-page generation.** Picked concept seeds the *rest* of the site; concepts themselves are home-only.
- **Not A/B testing.** That's a V2 feature — generating two minisites, deploying both, splitting paid traffic. Concept variations happen *before* deploy; A/B happens *after*.
- **Not endless retries.** If the operator doesn't like any of the 2–5 concepts, the fix is usually upstream (clarify the brief, fix `voice.md`, run review again). Don't loop on more concepts hoping for randomness to save you.

---

## Cross-references

- [`SKILL.md`](../SKILL.md) — Operating principles (foreground only, publish-first, parallel-by-default)
- [`minisite-build.md`](minisite-build.md) — where concept generation fits in the operator walkthrough
- [`minisite-generation-system.md`](minisite-generation-system.md) — the system prompt each concept subagent uses
- [`anti-patterns.md`](anti-patterns.md) — what NOT to bake into concept prompts (over-prescription kills variance)
- `start/references/config-system.md` — the `~/.config/vip/local.yaml` location for `default_concepts`
