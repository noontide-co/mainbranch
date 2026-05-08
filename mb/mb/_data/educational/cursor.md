---
type: educational
topic: cursor
status: draft
last-updated: 2026-05-08
---

# Cursor: useful editor, not a supported Main Branch runtime yet

Cursor is an AI code editor. It can be useful for reading and editing a Main
Branch business repo because the repo is just files.

That is different from saying Main Branch supports Cursor as a full runtime.

## The beginner version

You can open your business repo folder in Cursor to inspect or edit files:

- `core/` for offer, audience, voice, proof, strategy, and operations;
- `research/` for investigations;
- `decisions/` for accepted or proposed choices;
- `pushes/` for launches, drops, challenges, promos, and playbooks;
- `log/` for operating notes;
- `documents/` for long-form artifacts.

Claude Code remains the supported slash-skill runtime today.

## What Cursor is good for

- reading markdown files;
- making careful edits;
- searching the repo;
- reviewing diffs;
- helping power users understand the folder tree.

Because Main Branch keeps memory in markdown and git, tools like Cursor can
operate on the files without a proprietary export.

## What is not supported yet

Do not assume Cursor can run `/mb-start`, `/mb-think`, `/mb-status`, or bundled
Claude Code skills as first-class Main Branch workflows.

Future adapter work should call deterministic `mb` commands, read JSON output
where available, and prove runtime behavior with smoke evidence before public
support is claimed.

## The safe beginner path

For supported workflows:

```bash
cd /path/to/your-business
claude
/mb-start
```

Use Cursor as an editor if it helps you see the files. Use Claude Code for the
shipped Main Branch skill flows.

## What Main Branch does not claim

Cursor is a roadmap compatibility target, not a supported adapter today. Do not
represent Cursor workflow behavior as shipped until there is adapter code,
documentation, and smoke evidence.
