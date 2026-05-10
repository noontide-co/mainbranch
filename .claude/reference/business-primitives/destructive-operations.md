# Destructive Operations

Ask before operations that can erase context, rewrite history, mutate outside
accounts, or make business work hard to inspect later.

## Require Explicit Approval

- deleting, archiving, or moving user-authored files;
- renaming, merging, splitting, or deleting offer folders;
- layout migrations and archive moves;
- checkpoint creation or commits;
- publishing, deployment, provider/account mutation, or ad spend;
- customer/member contact;
- changing repo topology, remotes, or access boundaries.

## Default Pattern

1. Show the read-only facts from `mb status`, `mb validate`, `mb doctor repair --plan`, or the relevant provider check.
2. Name the exact files, folders, provider objects, or git action that would change.
3. Explain the reversible path or backup if there is one.
4. Wait for approval before applying.

Prefer archive-oriented moves for historical generated work. Do not fabricate
retroactive bets, pushes, or campaigns just to make old files fit the current
model.
