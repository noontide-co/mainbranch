# Workspace-Isolated Tool Setup

Some workspace tools start Claude inside an isolated folder. When that happens,
Claude may not see the installed Main Branch skills until the workspace has
local bridge links and `settings.local.json` file access.

Prefer the CLI repair path from the business repo:

```bash
mb skill link --repo .
mb doctor
mb start --json
```

Restart Claude after repairing links. Slash-command skills load at startup.

## When A Pre-Start Hook Is Needed

If the workspace tool supports a script that runs before the agent starts, use
it only to create the same bridge links and file-access settings that
`mb skill link --repo .` manages.

```bash
ENGINE_PATH="/absolute/path/to/mainbranch"
mkdir -p .claude/skills .claude
for d in "$ENGINE_PATH"/.claude/skills/*/; do
  [ -d "$d" ] || continue
  skill="$(basename "$d")"
  link=".claude/skills/$skill"
  [ -e "$link" ] || ln -s "$d" "$link"
done
cat > .claude/settings.local.json << EOF
{
  "permissions": {
    "additionalDirectories": [
      "$ENGINE_PATH"
    ]
  }
}
EOF
exit
```

Replace `/absolute/path/to/mainbranch` with the actual Main Branch package or
source-checkout path. Most users should not hand-write this; run
`mb skill link --repo .` instead.

## Troubleshooting

If skills still do not appear:

1. Restart Claude from the business repo.
2. Confirm `.claude/skills/mb-start/SKILL.md` exists in the workspace.
3. Confirm the Main Branch path exists and contains `.claude/skills/mb-start/SKILL.md`.
4. Run `mb doctor` and follow the repair command it prints.

If the tool says it cannot edit files outside allowed directories, start the
workspace at the repo you want to edit. Main Branch business files should live
inside that workspace; Main Branch files are read through
`additionalDirectories`, not edited.
