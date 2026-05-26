# CWD Detection and Main Branch Wiring

Use this flow at the start of `/mb-setup`. The goal is to keep the user's
business repo as the working directory and let the `mb` CLI own Claude Code
skill wiring whenever it is available.

---

## Preferred Repair Path

From the business repo:

```bash
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb start --json
```

`mb skill link` rewrites `.claude/settings.local.json` to the active Main
Branch path, refreshes `mb-` bridge links, removes old project-local legacy
skill links, and cleans stale Main Branch paths from
`permissions.additionalDirectories`.

`mb skill repair` inspects personal `~/.claude/skills/` entries that can shadow
project-local Main Branch skills. It only moves provably stale Main Branch
symlinks when run with `--apply`; third-party and user-authored skills are
reported but not changed.

---

## Detect Where We Are

Detect current repos first, then old repo migration input, then source
checkouts:

```bash
test -d "core" && echo "IS_BUSINESS_REPO"
# Old repo migration input, not current paths.
if test ! -d "core" && { test -d "reference/core" || test -d "reference/offers" || test -d "reference/domain"; }; then echo "IS_OLD_BUSINESS_REPO"; fi
test -f ".claude/skills/mb-setup/SKILL.md" && echo "IS_MAINBRANCH_SOURCE"
```

### Case 1: CWD Is the Business Repo

Say:

> "You're in your business repo. I'll repair Main Branch skill discovery from
> here."

Run the preferred repair path above. If `mb start --json` reports
`handoff_ready: true`, tell the user to restart Claude and run `/mb-start`.

If `mb` is missing, ask the user to install Main Branch:

```bash
pipx install mainbranch
```

Then re-run the preferred repair path.

### Case 2: CWD Is an Old Main Branch Repo

Say:

> "You're in an old Main Branch repo. I'll read it as migration input, then
> show the repair plan before any normal workflow."

Run from this CWD before falling back to saved config or discovery:

```bash
mb status --json --peek
mb doctor repair --plan
```

Do not call `reference/core`, `reference/offers`, or `reference/domain`
current paths. Do not write new business truth there. Tell the operator to
follow the repair/migration plan.

### Case 3: CWD Is The Main Branch Source Checkout

Say:

> "You're in the Main Branch source checkout. The recommended workflow is to
> run Claude from your business folder so all writes land in the business
> brain."

Find or ask for the business repo path. Then run:

```bash
mb skill link --repo /absolute/path/to/business-repo
mb skill repair --repo /absolute/path/to/business-repo
mb start --repo /absolute/path/to/business-repo --json
```

If direct writes are blocked by the runtime sandbox, tell the user to open a
workspace rooted at the business repo and run the same commands there.

### Case 4: CWD Is Neither

Ask whether the user wants to create a new business repo or connect an existing
one.

For a new repo, prefer:

```bash
mb onboard --name "Business Name" --path /absolute/path/to/business-repo
```

For an existing repo, prefer:

```bash
mb onboard --mode connect --path /absolute/path/to/business-repo
```

After either path, run:

```bash
mb skill repair --repo /absolute/path/to/business-repo
mb start --repo /absolute/path/to/business-repo --json
```

---

## Legacy Fallback

Some old setups still have `~/.config/vip/local.yaml` with `vip_path`,
`default_repo`, and `recent_repos`. Treat that file as a compatibility fallback,
not as the primary repair mechanism.

If you must resolve it manually, use the standard resolver in
[`engine-path-resolution.md`](engine-path-resolution.md), then immediately route back
to:

```bash
mb skill link --repo "$REPO_PATH"
mb doctor "$REPO_PATH"
```

Never overwrite `~/.config/vip/local.yaml` with `cat >`. If you edit it, read
the existing file, preserve unknown keys, write absolute paths, and keep user
identity fields intact.
