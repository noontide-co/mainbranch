# Main Branch Update Check

Standard command for checking or applying Main Branch updates at the start of a
skill invocation. CWD is the business folder. **Do not silently swallow
failures.** Users on stale code get broken features.

`mb update` owns the install-mode mechanics. It detects pipx vs source
checkouts, runs the correct update command, and refreshes skill links for the
business folder.

```bash
mb update --repo . --json 2>&1
```

## Handle the Result

| Result | What to say |
|--------|-------------|
| JSON `"ok": true`, old_version == new_version | Say nothing |
| JSON `"ok": true`, old_version != new_version | "Updated Main Branch and refreshed skill links." |
| Invalid JSON or missing engine root | "Couldn't find Main Branch. Run `mb skill link --repo .`, then restart Claude." |
| JSON `"ok": false` or command failure | Show the warning below |

## If Update Fails - Show This Warning

> "I wasn't able to update Main Branch. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. Run `mb update --check --repo .` to see which install path Main Branch detects
> 2. Run `mb update --repo .` again after fixing the reported error
> 3. **Network issue?** Check your internet connection
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale Main Branch is the #1 cause of "why doesn't X work" support questions.
