"""Reusable GitHub activity primitives backed by the GitHub CLI."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from typing import Any

CommandResult = dict[str, Any]
CommandRunner = Callable[[list[str], Path | None, float], CommandResult]
JsonRunner = Callable[[list[str], Path], tuple[bool, Any, str]]
Which = Callable[[str], str]

ISSUE_FIELDS = "number,title,url,updatedAt,closedAt,labels,state"
PR_FIELDS = "number,title,url,updatedAt,mergedAt,author,isDraft,reviewDecision,body,state"


def which(name: str) -> str:
    return shutil.which(name) or ""


def run_command(args: list[str], cwd: Path | None = None, timeout: float = 5.0) -> CommandResult:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "returncode": 127, "stdout": "", "stderr": f"{args[0]} not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": 124, "stdout": "", "stderr": "command timed out"}
    except subprocess.SubprocessError as exc:
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": str(exc)}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
    result = run_command(args, cwd=repo, timeout=5.0)
    if not result["ok"]:
        return False, None, str(result["stderr"]).strip() or str(result["stdout"]).strip()
    try:
        return True, json.loads(str(result["stdout"]) or "[]"), ""
    except json.JSONDecodeError:
        return False, None, "gh returned invalid JSON"


def repo_full_name(remote: str) -> str:
    if not remote:
        return ""
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", remote)
    if not match:
        return ""
    return f"{match.group('owner')}/{match.group('repo')}"


def collect(
    repo: Path,
    *,
    remote: str = "",
    today: date | None = None,
    which_func: Which = which,
    command_runner: CommandRunner = run_command,
    json_runner: JsonRunner = gh_json,
) -> dict[str, Any]:
    """Collect business-language GitHub activity through `gh`.

    The returned shape is intentionally stable for CLI JSON consumers. Legacy
    aliases are included for `mb status` callers that already read v0.2.0 keys.
    """
    repo_name = repo_full_name(remote)
    if not which_func("gh"):
        return _empty_report(
            repo_name=repo_name,
            available=False,
            authenticated=False,
            errors=["gh not on PATH"],
        )

    auth = command_runner(["gh", "auth", "status"], repo, 5.0)
    if not auth["ok"]:
        return _empty_report(
            repo_name=repo_name,
            available=True,
            authenticated=False,
            errors=["gh not authenticated"],
        )

    today_value = today or date.today()
    week_start = today_value - timedelta(days=today_value.weekday())
    errors: list[str] = []

    assigned = _query(
        "assigned tasks",
        _issue_list_args(repo_name, ["--state", "open", "--assignee", "@me"]),
        repo,
        json_runner,
        errors,
    )
    review_requests = _query(
        "review requests",
        _pr_list_args(repo_name, ["--state", "open", "--search", "review-requested:@me"]),
        repo,
        json_runner,
        errors,
    )
    mentioned_issues = _query(
        "mentioned tasks",
        _issue_list_args(repo_name, ["--state", "open", "--search", "mentions:@me"]),
        repo,
        json_runner,
        errors,
    )
    mentioned_prs = _query(
        "mentioned proposals",
        _pr_list_args(repo_name, ["--state", "open", "--search", "mentions:@me"]),
        repo,
        json_runner,
        errors,
    )
    open_prs = _query(
        "open proposals",
        _pr_list_args(repo_name, ["--state", "open", "--author", "@me"]),
        repo,
        json_runner,
        errors,
    )
    merged = _query(
        "shipped proposals",
        _pr_list_args(repo_name, ["--state", "merged", "--search", f"merged:>={week_start}"]),
        repo,
        json_runner,
        errors,
        limit="20",
    )
    closed = _query(
        "closed tasks",
        _issue_list_args(repo_name, ["--state", "closed"]),
        repo,
        json_runner,
        errors,
        limit="10",
    )
    blocked = _query(
        "blocked tasks",
        _issue_list_args(repo_name, ["--state", "open", "--search", "label:blocked"]),
        repo,
        json_runner,
        errors,
    )
    stale = _query(
        "stale tasks",
        _issue_list_args(repo_name, ["--state", "open", "--search", "label:stale"]),
        repo,
        json_runner,
        errors,
    )

    assigned_tasks = [
        _task_item(item, repo_name, business_status="assigned", reason="Assigned to you")
        for item in assigned
    ]
    attention_requests = _dedupe(
        [
            *[
                _proposal_item(
                    item,
                    repo_name,
                    business_status="needs_review",
                    reason="Your review is requested",
                )
                for item in review_requests
            ],
            *[
                _task_item(
                    item,
                    repo_name,
                    business_status="mentioned",
                    reason="You were mentioned",
                )
                for item in mentioned_issues
            ],
            *[
                _proposal_item(
                    item,
                    repo_name,
                    business_status="mentioned",
                    reason="You were mentioned",
                )
                for item in mentioned_prs
            ],
        ]
    )
    open_proposals = [
        _proposal_item(
            item,
            repo_name,
            business_status="open_proposal",
            reason="Your open proposal may need follow-up",
        )
        for item in open_prs
    ]
    shipped_this_week = recent_merged_prs(merged, repo_name=repo_name)
    recently_closed_tasks = [
        _task_item(item, repo_name, business_status="closed", reason="Recently closed")
        for item in closed
    ]
    blocked_or_stale_tasks = _dedupe(
        [
            *[
                _task_item(item, repo_name, business_status="blocked", reason="Blocked label")
                for item in blocked
            ],
            *[
                _task_item(item, repo_name, business_status="stale", reason="Stale label")
                for item in stale
            ],
        ]
    )

    sections = {
        "assigned_tasks": assigned_tasks,
        "attention_requests": attention_requests,
        "open_proposals": open_proposals,
        "shipped_this_week": shipped_this_week,
        "recently_closed_tasks": recently_closed_tasks,
        "blocked_or_stale_tasks": blocked_or_stale_tasks,
    }
    report = _empty_report(
        repo_name=repo_name,
        available=True,
        authenticated=True,
        errors=errors,
    )
    report["degraded"] = bool(errors)
    report["sections"] = sections
    report["summary"] = _summary(sections)
    report["assigned_issues"] = assigned
    report["review_requests"] = review_requests
    report["recent_merged_prs"] = shipped_this_week
    return report


def recent_merged_prs(prs: list[dict[str, Any]], repo_name: str = "") -> list[dict[str, Any]]:
    sorted_prs = sorted(prs, key=lambda pr: str(pr.get("mergedAt", "") or ""), reverse=True)
    return [summarize_pr(pr, repo_name=repo_name) for pr in sorted_prs[:5]]


def summarize_pr(pr: dict[str, Any], repo_name: str = "") -> dict[str, Any]:
    title = str(pr.get("title", "") or "")
    body = str(pr.get("body", "") or "")
    summary = ""
    for line in body.splitlines():
        stripped = line.strip().strip("-* ")
        if stripped and not stripped.startswith("#"):
            summary = stripped
            break
    if not summary:
        summary = title

    item = _proposal_item(
        pr,
        repo_name=repo_name,
        business_status="shipped",
        reason="Merged this week",
    )
    item["what_shipped"] = summary[:220]
    item["mergedAt"] = item["merged_at"]
    return item


def _empty_report(
    *,
    repo_name: str,
    available: bool,
    authenticated: bool,
    errors: list[str],
) -> dict[str, Any]:
    sections: dict[str, list[dict[str, Any]]] = {
        "assigned_tasks": [],
        "attention_requests": [],
        "open_proposals": [],
        "shipped_this_week": [],
        "recently_closed_tasks": [],
        "blocked_or_stale_tasks": [],
    }
    return {
        "available": available,
        "authenticated": authenticated,
        "degraded": bool(errors) or not available or not authenticated,
        "source": "gh",
        "repo": repo_name,
        "summary": _summary(sections),
        "sections": sections,
        "errors": errors,
        "assigned_issues": [],
        "review_requests": [],
        "recent_merged_prs": [],
    }


def _summary(sections: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "assigned_tasks": len(sections["assigned_tasks"]),
        "attention_requests": len(sections["attention_requests"]),
        "open_proposals": len(sections["open_proposals"]),
        "shipped_this_week": len(sections["shipped_this_week"]),
        "recently_closed_tasks": len(sections["recently_closed_tasks"]),
        "blocked_or_stale_tasks": len(sections["blocked_or_stale_tasks"]),
    }


def _query(
    label: str,
    args: list[str],
    repo: Path,
    json_runner: JsonRunner,
    errors: list[str],
    *,
    limit: str = "10",
) -> list[dict[str, Any]]:
    full_args = [*args, "--limit", limit]
    ok, payload, error = json_runner(full_args, repo)
    if not ok:
        errors.append(f"{label}: {error}")
        return []
    if not isinstance(payload, list):
        errors.append(f"{label}: gh returned non-list JSON")
        return []
    return [item for item in payload if isinstance(item, dict)]


def _issue_list_args(repo_name: str, filters: list[str]) -> list[str]:
    args = ["gh", "issue", "list", *filters, "--json", ISSUE_FIELDS]
    return _with_repo(args, repo_name)


def _pr_list_args(repo_name: str, filters: list[str]) -> list[str]:
    args = ["gh", "pr", "list", *filters, "--json", PR_FIELDS]
    return _with_repo(args, repo_name)


def _with_repo(args: list[str], repo_name: str) -> list[str]:
    if repo_name:
        return [*args, "--repo", repo_name]
    return args


def _task_item(
    issue: dict[str, Any],
    repo_name: str,
    *,
    business_status: str,
    reason: str,
) -> dict[str, Any]:
    labels = _label_names(issue.get("labels"))
    return {
        "type": "task",
        "github_type": "issue",
        "business_status": business_status,
        "reason": reason,
        "number": issue.get("number"),
        "title": str(issue.get("title", "") or ""),
        "url": str(issue.get("url", "") or ""),
        "repo": repo_name,
        "state": str(issue.get("state", "") or ""),
        "updated_at": str(issue.get("updatedAt", "") or ""),
        "closed_at": str(issue.get("closedAt", "") or ""),
        "labels": labels,
    }


def _proposal_item(
    pr: dict[str, Any],
    repo_name: str,
    *,
    business_status: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "type": "proposal",
        "github_type": "pull_request",
        "business_status": business_status,
        "reason": reason,
        "number": pr.get("number"),
        "title": str(pr.get("title", "") or ""),
        "url": str(pr.get("url", "") or ""),
        "repo": repo_name,
        "state": str(pr.get("state", "") or ""),
        "updated_at": str(pr.get("updatedAt", "") or ""),
        "merged_at": str(pr.get("mergedAt", "") or ""),
        "author": _author_login(pr.get("author")),
        "is_draft": bool(pr.get("isDraft", False)),
        "review_decision": str(pr.get("reviewDecision", "") or ""),
    }


def _label_names(labels: Any) -> list[str]:
    if not isinstance(labels, list):
        return []
    names: list[str] = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
            if isinstance(name, str):
                names.append(name)
        elif isinstance(label, str):
            names.append(label)
    return names


def _author_login(author: Any) -> str:
    if isinstance(author, dict):
        login = author.get("login")
        if isinstance(login, str):
            return login
    return ""


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = (
            str(item.get("github_type", "")),
            str(item.get("repo", "")),
            str(item.get("number", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
