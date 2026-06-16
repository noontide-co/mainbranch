"""Production-posture plan (`mb production plan`).

When a business starts taking real money, its default branch should be armed:
require a pull request, require the CI check and the money-path canary as
status checks before merge, and block force-push and branch deletion. A real
business we built improvised this twice with raw `gh api` calls when an offer
went live — this surfaces the gap deterministically and emits the exact
commands.

Applying branch protection is a GitHub account mutation, so it runs the
provider-mutation contract (docs/provider-mutation-contract.md): this command
is the read-only PLAN half. It reports present-vs-missing and prints the apply
commands; the operator applies them (explicit approval, their account). The
engine never flips protection itself.

Solo operators on a solo-on-main workflow may decline protection — that is a
valid stance (docs/checks-and-review-model.md). Pass ``solo=True`` and the
plan records the deliberate skip instead of a gap.
"""

from __future__ import annotations

from typing import Any

# The money-taking protection posture, as deterministic engine knowledge.
# Each item: (key, human label, how to read it off a GitHub protection dict).
DESIRED_POSTURE: tuple[tuple[str, str], ...] = (
    ("required_pull_request", "require a pull request before merge"),
    ("required_status_checks", "require the CI check + money-path canary as status checks"),
    ("block_force_push", "block force-push to the default branch"),
    ("block_deletion", "block deletion of the default branch"),
)


def _present_flags(protection: dict[str, Any] | None) -> dict[str, bool]:
    """Read which posture items a GitHub branch-protection dict already covers."""
    if not protection:
        return {key: False for key, _ in DESIRED_POSTURE}
    checks = protection.get("required_status_checks") or {}
    contexts: list[Any] = []
    strict = False
    if isinstance(checks, dict):
        contexts = checks.get("contexts") or checks.get("checks") or []
        strict = bool(checks.get("strict"))
    has_canary = any("canary" in str(ctx).lower() for ctx in contexts)
    # A real CI gate is a non-canary required check; the canary alone is not
    # "CI + canary". And the apply command sets strict=true, so the posture is
    # only armed when the existing gate is strict too.
    has_ci = any("canary" not in str(ctx).lower() for ctx in contexts)
    return {
        "required_pull_request": bool(protection.get("required_pull_request_reviews")),
        # Armed only when a CI check AND the canary are required, branch-strict.
        "required_status_checks": has_ci and has_canary and strict,
        "block_force_push": not _allowed(protection, "allow_force_pushes"),
        "block_deletion": not _allowed(protection, "allow_deletions"),
    }


def _allowed(protection: dict[str, Any], key: str) -> bool:
    node = protection.get(key)
    if isinstance(node, dict):
        return bool(node.get("enabled"))
    return bool(node)


def _apply_commands(repo_slug: str, branch: str, missing: list[str]) -> list[str]:
    """Exact gh commands the operator runs to arm the missing posture items."""
    if not missing:
        return []
    nwo = repo_slug or "<owner>/<repo>"
    # One PUT sets the full protection object; we name the money-taking shape.
    return [
        (
            f"gh api -X PUT repos/{nwo}/branches/{branch}/protection "
            "-H 'Accept: application/vnd.github+json' "
            '-f "required_status_checks[strict]=true" '
            '-f "required_status_checks[contexts][]=<your-ci-check>" '
            '-f "required_status_checks[contexts][]=<your-canary-check>" '
            '-F "enforce_admins=true" '
            '-f "required_pull_request_reviews[required_approving_review_count]=1" '
            '-F "restrictions=null" '
            '-F "allow_force_pushes=false" '
            '-F "allow_deletions=false"'
        ),
        f"gh api repos/{nwo}/branches/{branch}/protection  # verify the result",
    ]


def plan(
    repo_slug: str = "",
    *,
    branch: str = "main",
    current_protection: dict[str, Any] | None = None,
    solo: bool = False,
) -> dict[str, Any]:
    """Plan the money-taking branch-protection posture (read-only).

    ``current_protection`` is the parsed GitHub branch-protection object (or
    None when the branch is unprotected). The CLI fetches it via gh; tests pass
    it directly so the gap logic stays deterministic and offline.
    """
    if solo:
        return {
            "ok": True,
            "repo": repo_slug,
            "branch": branch,
            "solo_on_main": True,
            "present": [],
            "missing": [],
            "apply_commands": [],
            "summary": (
                "solo-on-main: branch protection is a deliberate skip, not a gap "
                "(docs/checks-and-review-model.md). Re-run without --solo when "
                "you add a teammate or take real money you cannot afford to lose."
            ),
            "safe_to_share": True,
        }
    flags = _present_flags(current_protection)
    labels = dict(DESIRED_POSTURE)
    present = [labels[key] for key, _ in DESIRED_POSTURE if flags[key]]
    missing_keys = [key for key, _ in DESIRED_POSTURE if not flags[key]]
    missing = [labels[key] for key in missing_keys]
    apply_commands = _apply_commands(repo_slug, branch, missing_keys)
    if not missing:
        summary = (
            f"production posture is armed on {branch}: PR required, CI + canary "
            "gate merges, force-push and deletion blocked"
        )
    else:
        summary = (
            f"{len(missing)} production-posture gap(s) on {branch} — applying "
            "branch protection is a provider mutation (see "
            "docs/provider-mutation-contract.md): review the commands below, "
            "then you apply them (the engine never flips protection for you)"
        )
    return {
        "ok": not missing,
        "repo": repo_slug,
        "branch": branch,
        "solo_on_main": False,
        "present": present,
        "missing": missing,
        "apply_commands": apply_commands,
        "summary": summary,
        "safe_to_share": True,
    }


def render_plan(result: dict[str, Any]) -> None:
    print(f"mb production plan  {result.get('repo') or '(repo)'}  branch={result['branch']}")
    print(result["summary"])
    for item in result["present"]:
        print(f"  ok    {item}")
    for item in result["missing"]:
        print(f"  gap   {item}")
    if result["apply_commands"]:
        print("\noperator-applies (provider mutation; your account, your approval):")
        for command in result["apply_commands"]:
            print(f"  {command}")
