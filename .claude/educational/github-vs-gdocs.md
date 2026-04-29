---
type: educational
topic: github-vs-gdocs
status: stub
last-updated: 2026-04-29
---

# Why your business reference belongs in git, not Google Docs

## Why we don't recommend Google Docs as the company brain

Google Docs is the default place businesses put their thinking — meeting notes, briefs, SOPs, brand guidelines, decision logs. It works for a season and rots in three specific ways.

**Version history is opaque and losable.** Docs revision history exists, but it is not a forensic record. You cannot diff two arbitrary versions side-by-side as text. You cannot search "when did we change the pricing on the offer page" across the whole drive. You cannot revert a single paragraph from three months ago without manual copy-paste. And every Docs user has stories of revision history that quietly disappeared after a rename, a copy, or a long period of inactivity. Git's history is content-addressed, immutable, and forensic by default. Every change has an author, a timestamp, and a parent commit. This isn't a nice-to-have; it is the only honest way to know how your company's thinking evolved.

**Search is shallow.** Google Drive search is keyword search across titles and visible content — it does not handle regex, does not respect word boundaries reliably, and silently truncates very large drives. Once your reference corpus passes ~200 docs, finding the one paragraph you remember writing six months ago becomes a project. With markdown in git, `rg "the exact phrase"` is instant and exact. Composability with the rest of your shell (`rg | xargs sed`, for example) means you can refactor terminology across 500 files in 30 seconds.

**Portability is a fiction.** "Export to .docx" or "Download all" produces a folder of files that lose the comments, the suggestion threads, the embedded images, and most of the formatting fidelity. Markdown is text. Markdown in git is text plus history. You own it forever, and every tool in your future stack will read it natively.

**Agent-friendliness.** Claude, Codex, Cursor, and every AI coding agent speak markdown-and-git natively. They can `git log --follow` a file, read its history, and reason about why it changed. They cannot reason about a Google Doc except by exporting it, parsing the export, and losing the threading. As "AI that knows your business" becomes the operating model, the substrate has to be one agents can read. Git is that substrate. Docs is not.

**Lock-in.** Your company's thinking is in Google's database. Your account is one suspension away from being read-only. The TOS allows Google to terminate accounts at their discretion. Most businesses never hit this wall. The ones that do hit it discover that "export everything" is harder than they assumed.

## What we recommend instead

A private GitHub (or Forgejo) repo with a CLAUDE.md at the root and a six-primitive folder structure: `core/`, `research/`, `decisions/`, `log/`, `campaigns/`, `documents/`. Markdown for everything. Frontmatter for status. The repo is the company brain. Conductor or any AI agent reads it as the working substrate.

The pitch in one sentence: **your business is a tree of files**. Once it is, every agent that can read files becomes a coworker.

## Setup walkthrough

1. Create a private repo. From the GitHub UI: `New repository → Private → Initialize with README`. Name it something like `your-business` or `your-business-brain`.

2. Clone it locally:
   ```bash
   git clone git@github.com:yourname/your-business.git
   cd your-business
   ```

3. Add a `CLAUDE.md` at the root. This is the always-loaded context for any AI agent that opens the repo. A minimal first version:
   ```markdown
   # <Business Name>

   <One-sentence thesis: what this business is and who it serves.>

   ## Folder structure

   - core/ — soul, offer, audience, voice, visual identity, finance
   - research/ — dated investigations, never deleted
   - decisions/ — dated choices with rationale, frontmatter status field
   - log/ — daily/weekly notes, inbox-style dumps
   - campaigns/ — outputs grouped by campaign
   - documents/ — long-form artifacts (briefs, SOPs, contracts)
   ```

4. Set up the six-primitive folders:
   ```bash
   mkdir -p core/{soul,offer,audience,voice,visual-identity,finance} \
            research decisions log campaigns documents
   git add . && git commit -m "[init] six-primitive structure"
   git push
   ```

5. Connect to a Conductor workspace (or open the repo in Claude Code directly):
   ```bash
   # In Conductor: New Workspace -> point at the repo path
   # Or: cd into the repo and run `claude` to start a Claude Code session.
   ```

6. Migrate one Google Doc as a forcing function. Pick the most important one — usually a brand brief or a strategy doc. Paste it into `core/offer/offer.md` (or wherever it belongs). Commit. Notice how much faster every subsequent edit, search, and agent read becomes. Migrate the next doc when the next decision needs it. Don't try to bulk-migrate everything; that's a project that never ships.

Cost: $0/month for private repos on GitHub (free tier covers it for individuals and small teams). Forgejo on your own hardware is also free.

## Honest limitations

Markdown in git does not solve **real-time multiplayer editing**. If two people are typing in the same paragraph at the same time, Google Docs still wins. Most reference work isn't actually concurrent — it's "someone writes, others react" — but the few cases where it is concurrent (live meeting notes during a call, brainstorm with three people typing) are friction. We solve this by writing first in a scratch tool (Apple Notes, a shared scratchpad) and porting to git at the end of the session, but that's a workflow gap, not a no-op.

It also has a higher learning curve. A non-technical collaborator who is fluent in Docs needs an afternoon to learn `git pull / git commit / git push`. GitHub Desktop or the GitHub web editor lowers the bar; some collaborators will still bounce. Whether the learning curve is worth the durability gain is a per-person judgment call.

## Resources

- GitHub markdown reference: https://docs.github.com/en/get-started/writing-on-github
- GitHub Desktop (no-CLI git client): https://desktop.github.com/
- Conductor workspace docs: https://conductor.build/docs
- "Your business is a tree of files" (Main Branch positioning, internal): see `decisions/2026-04-29-mb-vip-v0-1-0-master.md`
