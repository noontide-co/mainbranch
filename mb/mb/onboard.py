"""``mb onboard`` — adaptive human setup flow for Main Branch."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mb import checkpoint as checkpoint_mod
from mb import connect as connect_mod
from mb import init as init_mod
from mb.engine import link_skills, link_status

LEVELS = {"beginner", "intermediate", "power"}
MODES = {"new", "connect", "auto"}
ONBOARDING_STATE_RELATIVE_PATH = Path(".mb") / "onboarding.json"
ONBOARDING_STATE_VERSION = 1
TEAM_SIZES = {"unknown", "solo", "small_team", "larger_team"}
SUCCESS_STAGES = {"unknown", "prelaunch", "working", "successful", "scaling"}

BOUNDARIES = {
    "collect_now": [
        "business type and team size",
        "current success stage and desired direction",
        "primary offer, audience, voice, proof, and operating constraints",
        "GitHub/team workflow needs for this business size",
    ],
    "defer_until_needed": [
        "full finances or ledgers",
        "raw customer/member exports",
        "credentials, tokens, and private account secrets",
        "exhaustive operations documentation outside the core files",
    ],
}

ONBOARDING_GITIGNORE_ENTRY = ".mb/onboarding.json"
LOCAL_SETUP_PATH_PREFIXES = (
    ".git/",
    ".mb/",
    ".claude/settings.local.json",
    ".claude/worktrees/",
    ".claude/skills/",
)


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _run_command(args: list[str], cwd: Path | None = None, timeout: float = 5.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "stdout": "", "stderr": f"{args[0]} not found", "returncode": 127}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "command timed out", "returncode": 124}
    except subprocess.SubprocessError as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "returncode": 1}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def _git_output(repo: Path, args: list[str], timeout: float = 5.0) -> dict[str, Any]:
    return _run_command(["git", *args], cwd=repo, timeout=timeout)


def _has_git_commit(repo: Path) -> bool:
    head = _git_output(repo, ["rev-parse", "--verify", "HEAD"])
    return bool(head["ok"])


def _git_remote(repo: Path) -> str:
    remote = _git_output(repo, ["config", "--get", "remote.origin.url"])
    return remote["stdout"].strip() if remote["ok"] else ""


def _git_branch(repo: Path) -> str:
    branch = _git_output(repo, ["branch", "--show-current"])
    return branch["stdout"].strip() if branch["ok"] else ""


def _tracking_branch(repo: Path) -> str:
    tracking = _git_output(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    return tracking["stdout"].strip() if tracking["ok"] else ""


def _working_tree_dirty(repo: Path) -> bool:
    status = _git_output(repo, ["status", "--porcelain"])
    return bool(status["ok"] and status["stdout"].strip())


def _durable_generated_paths(paths: list[str]) -> list[str]:
    durable: list[str] = []
    for raw in paths:
        rel = raw.strip().replace("\\", "/").strip("/")
        if not rel or rel == ".git":
            continue
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts:
            continue
        if any(
            rel == prefix.rstrip("/") or rel.startswith(prefix)
            for prefix in LOCAL_SETUP_PATH_PREFIXES
        ):
            continue
        if rel not in durable:
            durable.append(rel)
    return durable


def _commit_generated_scaffold(
    repo: Path,
    *,
    business_name: str,
    generated_paths: list[str],
) -> dict[str, Any]:
    commit_message = f"[opened] Main Branch scaffold for {business_name or repo.name}"
    result: dict[str, Any] = {
        "ok": False,
        "committed": False,
        "commands": [],
        "errors": [],
        "repair": "",
    }
    durable_paths = _durable_generated_paths(generated_paths)
    if durable_paths:
        add = _git_output(repo, ["add", "--", *durable_paths])
        result["commands"].append("git add -- " + " ".join(durable_paths))
        if not add["ok"]:
            result["errors"].append(add["stderr"].strip() or "git add failed")
            result["repair"] = "Review `git status`, then commit the scaffold manually."
            return result

    staged = _git_output(repo, ["diff", "--cached", "--quiet", "--"])
    staged_changes = staged["returncode"] == 1
    if staged["returncode"] not in {0, 1}:
        result["errors"].append(staged["stderr"].strip() or "git staged diff failed")
        result["repair"] = "Review `git status`, then commit the scaffold manually."
        return result
    if staged_changes:
        commit = _git_output(repo, ["commit", "-m", commit_message], timeout=15.0)
        result["commands"].append(f"git commit -m {commit_message!r}")
        if not commit["ok"]:
            result["errors"].append(commit["stderr"].strip() or commit["stdout"].strip())
            result["repair"] = (
                "Configure git author identity if needed, then run "
                f'`git commit -m "{commit_message}"`.'
            )
            return result
        result["committed"] = True
    elif not _has_git_commit(repo):
        result["errors"].append("No durable scaffold files were staged for the first commit.")
        result["repair"] = "Review `git status`, then commit the scaffold manually."
        return result

    if _working_tree_dirty(repo):
        result["errors"].append(
            "Working tree has uncommitted files outside the generated Main Branch scaffold."
        )
        result["repair"] = (
            "Review `git status`; commit, ignore, or move private files before pushing."
        )
        return result

    result["ok"] = True
    return result


def _github_create_push(
    repo: Path,
    *,
    business_name: str,
    github_repo: str,
    visibility: str,
    push: bool,
    generated_paths: list[str] | None = None,
) -> dict[str, Any]:
    requested = bool(github_repo.strip())
    result: dict[str, Any] = {
        "requested": requested,
        "ok": not requested,
        "repo": github_repo.strip(),
        "visibility": visibility,
        "committed": False,
        "clean_tree": not _working_tree_dirty(repo),
        "remote_set": bool(_git_remote(repo)),
        "pushed": False,
        "tracking": _tracking_branch(repo),
        "commands": [],
        "errors": [],
        "repair": "",
    }
    if not requested:
        return result
    if visibility not in {"private", "public"}:
        result["errors"].append("github visibility must be private or public")
        result["repair"] = "Use `--github-visibility private` or `--github-visibility public`."
        return result
    if not _which("gh"):
        result["errors"].append("GitHub CLI is not installed.")
        result["repair"] = "Install GitHub CLI, then run `gh auth login`."
        return result
    if not _which("git"):
        result["errors"].append("git is not installed.")
        result["repair"] = "Install git before creating the GitHub repo."
        return result

    commit_result = _commit_generated_scaffold(
        repo,
        business_name=business_name,
        generated_paths=generated_paths or [],
    )
    result["commands"].extend(commit_result["commands"])
    result["committed"] = bool(commit_result["committed"])
    result["clean_tree"] = commit_result["ok"]
    if not commit_result["ok"]:
        result["errors"].extend(str(item) for item in commit_result["errors"])
        result["repair"] = str(commit_result["repair"])
        return result

    args = ["gh", "repo", "create", github_repo.strip(), f"--{visibility}", "--source", "."]
    if not _git_remote(repo):
        args.extend(["--remote", "origin"])
    if push:
        args.append("--push")
    create = _run_command(args, cwd=repo, timeout=30.0)
    result["commands"].append(" ".join(args))
    if not create["ok"]:
        result["errors"].append(create["stderr"].strip() or create["stdout"].strip())
        result["repair"] = (
            "Run `gh auth login`, then rerun onboarding or create the GitHub repo manually."
        )
        return result
    result["remote_set"] = bool(_git_remote(repo))
    result["tracking"] = _tracking_branch(repo)
    result["pushed"] = bool(push and result["tracking"])
    result["clean_tree"] = not _working_tree_dirty(repo)
    result["ok"] = True
    return result


def _setup_complete(repo: Path, *, github_requested: bool = False) -> dict[str, Any]:
    markers = _repo_markers(repo)
    git_repo = _git_output(repo, ["rev-parse", "--is-inside-work-tree"])
    branch = _git_branch(repo)
    remote = _git_remote(repo)
    tracking = _tracking_branch(repo)
    checkpoint_hook = checkpoint_mod.hook_status(repo)
    wiring = link_status(repo)
    committed = _has_git_commit(repo)
    dirty = _working_tree_dirty(repo)
    return {
        "scaffolded": _looks_initialized(markers),
        "initialized_on_main": bool(git_repo["ok"] and branch == "main"),
        "checkpoint_hook_ready": bool(checkpoint_hook.get("ok")),
        "checkpoint_hook_repair": ""
        if checkpoint_hook.get("ok")
        else "mb checkpoint --install-hook",
        "committed_with_durable_files": bool(committed and not dirty),
        "github_remote_connected": bool(remote),
        "github_remote": remote,
        "pushed_tracking_remote": bool(tracking),
        "tracking_branch": tracking,
        "github_requested": github_requested,
        "claude_code_handoff_ready": bool(wiring.get("ok")),
        "codex_instructions_present": (repo / "AGENTS.md").is_file(),
        "owner_outcome": (
            "This business folder is created, saved, synced to GitHub, and ready to open "
            "in Claude Code."
            if github_requested
            and remote
            and tracking
            and wiring.get("ok")
            and committed
            and not dirty
            else "This business folder is created and ready for the next setup step."
        ),
    }


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "my-business"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_path(repo: Path) -> Path:
    return repo / ONBOARDING_STATE_RELATIVE_PATH


def _ensure_onboarding_gitignore(repo: Path) -> bool:
    gitignore = repo / ".gitignore"
    existing_text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    entries = {line.strip() for line in existing_text.splitlines()}
    if ONBOARDING_GITIGNORE_ENTRY in entries or ".mb/" in entries:
        return False
    prefix = "" if not existing_text or existing_text.endswith("\n") else "\n"
    gitignore.write_text(
        existing_text + prefix + ONBOARDING_GITIGNORE_ENTRY + "\n",
        encoding="utf-8",
    )
    return True


def _normalize_team_size(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "": "unknown",
        "one": "solo",
        "one_person": "solo",
        "1": "solo",
        "solo_operator": "solo",
        "small": "small_team",
        "team": "small_team",
        "2_5": "small_team",
        "2_to_5": "small_team",
        "larger": "larger_team",
        "large": "larger_team",
        "6_plus": "larger_team",
        "20_person": "larger_team",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in TEAM_SIZES:
        raise ValueError("team-size must be solo, small-team, larger-team, or unknown")
    return normalized


def _normalize_success_stage(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "": "unknown",
        "not_started": "prelaunch",
        "already_successful": "successful",
        "success": "successful",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in SUCCESS_STAGES:
        raise ValueError(
            "success-stage must be prelaunch, working, successful, scaling, or unknown"
        )
    return normalized


def _load_state(repo: Path) -> dict[str, Any] | None:
    path = _state_path(repo)
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _initial_state(
    *,
    repo: Path,
    business_name: str = "",
    team_size: str = "unknown",
    business_type: str = "",
    success_stage: str = "unknown",
    desired_outcome: str = "",
) -> dict[str, Any]:
    now = _now()
    return {
        "schema_version": ONBOARDING_STATE_VERSION,
        "kind": "mainbranch.onboarding",
        "created_at": now,
        "updated_at": now,
        "profile": {
            "business_name": business_name.strip(),
            "business_type": business_type.strip(),
            "team_size": _normalize_team_size(team_size),
            "success_stage": _normalize_success_stage(success_stage),
            "desired_outcome": desired_outcome.strip(),
        },
        "contract": {
            "state_path": str(ONBOARDING_STATE_RELATIVE_PATH),
            "canonical_business_truth": [
                "accepted offer, audience, voice, proof, decisions, and durable summaries",
                (
                    "files under core/, research/, decisions/, bets/, "
                    "pushes/ (legacy campaigns/), log/, and documents/"
                ),
            ],
            "operational_progress": [
                "checklist state, missing input labels, persona/team-size routing, and next action",
                "safe setup metadata that lets a later agent resume without a transcript",
            ],
            "never_store_here": [
                "credentials, secrets, raw customer/member exports, or full finances",
                "chat transcripts or large pasted source dumps",
            ],
        },
        "boundaries": BOUNDARIES,
        "notes": [],
        "source": "mb onboard",
    }


def _merge_state(existing: dict[str, Any] | None, updates: dict[str, Any]) -> dict[str, Any]:
    state = existing.copy() if existing else {}
    if not state:
        state = updates
    else:
        state["schema_version"] = ONBOARDING_STATE_VERSION
        state["kind"] = "mainbranch.onboarding"
        state.setdefault("created_at", updates.get("created_at", _now()))
        state["updated_at"] = _now()
        state.setdefault("contract", updates["contract"])
        state.setdefault("boundaries", BOUNDARIES)
        state.setdefault("notes", [])
        profile = dict(state.get("profile") or {})
        for key, value in updates["profile"].items():
            if value not in {"", "unknown"}:
                profile[key] = value
            else:
                profile.setdefault(key, value)
        state["profile"] = profile
        state["source"] = updates.get("source", "mb onboard")
    return state


def write_plan(
    repo: str | Path = ".",
    *,
    business_name: str = "",
    team_size: str = "unknown",
    business_type: str = "",
    success_stage: str = "unknown",
    desired_outcome: str = "",
) -> dict[str, Any]:
    """Create or update the lightweight onboarding progress plan."""
    target = Path(repo).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    existing = _load_state(target)
    updates = _initial_state(
        repo=target,
        business_name=business_name,
        team_size=team_size,
        business_type=business_type,
        success_stage=success_stage,
        desired_outcome=desired_outcome,
    )
    state = _merge_state(existing, updates)
    path = _state_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _ensure_onboarding_gitignore(target)
    return onboarding_status(target)


def _repo_markers(repo: Path) -> dict[str, bool]:
    return {
        "exists": repo.exists(),
        "git": (repo / ".git").exists(),
        "claude_md": (repo / "CLAUDE.md").is_file(),
        "core": (repo / "core").is_dir() or (repo / "reference" / "core").exists(),
        "research": (repo / "research").is_dir(),
        "decisions": (repo / "decisions").is_dir(),
        "skill_start": (repo / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file(),
    }


def _looks_initialized(markers: dict[str, bool]) -> bool:
    shaped_dirs = sum(1 for key in ("core", "research", "decisions") if markers[key])
    return markers["claude_md"] and shaped_dirs >= 2


def _tool_readiness(
    repo: Path,
    *,
    github_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    git_path = _which("git")
    gh_path = _which("gh")
    claude_path = _which("claude")
    gh_auth = False
    gh_repair = ""
    gh_state = "missing_cli"
    git_repo = False

    if git_path:
        git_probe = _run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)
        git_repo = git_probe["ok"] and git_probe["stdout"].strip() == "true"
    if github_context is not None:
        gh_auth = bool(github_context.get("ok"))
        gh_state = str(github_context.get("state") or ("ready" if gh_auth else "unknown"))
        gh_repair = str(github_context.get("repair") or github_context.get("repair_command") or "")
    elif gh_path:
        gh_probe = _run_command(["gh", "auth", "status"], cwd=repo)
        gh_auth = gh_probe["ok"]
        gh_state = "ready" if gh_auth else "unauthenticated"
        gh_repair = "" if gh_auth else "Run `gh auth login` to connect GitHub tasks and proposals."

    return {
        "git": {
            "found": bool(git_path),
            "path": git_path,
            "repo": git_repo,
            "repair": "" if git_path else "Install git, then run `mb doctor`.",
        },
        "github_cli": {
            "found": bool(gh_path),
            "authenticated": gh_auth,
            "state": gh_state,
            "path": gh_path,
            "repair": ""
            if gh_path and gh_auth
            else gh_repair
            or (
                "Install GitHub CLI: https://cli.github.com/ and run `gh auth login`."
                if not gh_path
                else "Run `gh auth login` to connect GitHub tasks and proposals."
            ),
        },
        "claude_code": {
            "found": bool(claude_path),
            "path": claude_path,
            "repair": "" if claude_path else "Install Claude Code: https://claude.ai/install",
        },
    }


def _infer_level(tool_readiness: dict[str, Any]) -> str:
    git = bool(tool_readiness["git"]["found"])
    gh = bool(
        tool_readiness["github_cli"]["found"] and tool_readiness["github_cli"]["authenticated"]
    )
    claude = bool(tool_readiness["claude_code"]["found"])
    if git and gh and claude:
        return "power"
    if git and (gh or claude):
        return "intermediate"
    return "beginner"


def _normalize_level(level: str) -> str:
    normalized = level.strip().lower().replace("_", "-")
    if normalized == "power-user":
        normalized = "power"
    if normalized and normalized not in LEVELS and normalized != "auto":
        raise ValueError("level must be beginner, intermediate, power, or auto")
    return normalized or "auto"


def _normalize_mode(mode: str, existing: bool) -> str:
    normalized = mode.strip().lower()
    if normalized not in MODES:
        raise ValueError("mode must be new, connect, or auto")
    if normalized == "auto":
        return "connect" if existing else "new"
    return normalized


def _next_steps(repo: Path) -> list[str]:
    return [
        f"cd {repo}",
        "claude",
        "/mb-start",
    ]


def _has_any_file(paths: list[Path]) -> bool:
    for path in paths:
        if path.is_file() and path.name != ".gitkeep" and path.stat().st_size > 0:
            return True
        if path.is_dir():
            for child in path.rglob("*.md"):
                if child.is_file() and child.stat().st_size > 0:
                    return True
    return False


def _core_inputs(repo: Path) -> dict[str, bool]:
    core = repo / "core"
    reference_core = repo / "reference" / "core"
    return {
        "offer": _has_any_file(
            [
                core / "offer.md",
                core / "offers",
                reference_core / "offer.md",
                repo / "reference" / "offers",
            ]
        ),
        "audience": _has_any_file([core / "audience.md", reference_core / "audience.md"]),
        "voice": _has_any_file([core / "voice.md", reference_core / "voice.md"]),
        "soul": _has_any_file([core / "soul.md", reference_core / "soul.md"]),
        "proof": _has_any_file(
            [
                core / "proof",
                core / "proof.md",
                core / "testimonials.md",
                repo / "reference" / "proof",
            ]
        ),
    }


def _profile_missing(profile: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key in ("business_type", "success_stage", "desired_outcome"):
        if not str(profile.get(key) or "").strip() or profile.get(key) == "unknown":
            missing.append(key)
    if profile.get("team_size") in {"", "unknown", None}:
        missing.append("team_size")
    return missing


def _team_step(profile: dict[str, Any], repo: Path) -> dict[str, Any]:
    team_size = str(profile.get("team_size") or "unknown")
    if team_size == "unknown":
        return {
            "id": "team_layer",
            "title": "Team operating loop",
            "status": "pending",
            "owner": "agent",
            "missing_inputs": ["team_size"],
            "next_action": "Ask whether this is a solo operator, small team, or larger team.",
            "required": False,
        }
    if team_size == "solo":
        return {
            "id": "team_layer",
            "title": "Solo operating loop",
            "status": "complete",
            "owner": "agent",
            "missing_inputs": [],
            "next_action": (
                "Use GitHub issues as your personal task list when work starts to sprawl."
            ),
            "required": False,
        }

    missing = []
    if not (repo / ".github" / "CODEOWNERS").exists():
        missing.append(".github/CODEOWNERS")
    if not _has_any_file([repo / "decisions", repo / "documents" / "team-workflow.md"]):
        missing.append("team workflow or decision note")
    label = "Small-team GitHub loop" if team_size == "small_team" else "Larger-team GitHub loop"
    return {
        "id": "team_layer",
        "title": label,
        "status": "complete" if not missing else "pending",
        "owner": "agent",
        "missing_inputs": missing,
        "next_action": (
            "Document owners, review expectations, and where team tasks/proposals live."
        ),
        "required": team_size in {"small_team", "larger_team"},
    }


def _step(
    *,
    step_id: str,
    title: str,
    complete: bool,
    missing_inputs: list[str],
    next_action: str,
    owner: str = "agent",
    required: bool = True,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "title": title,
        "status": "complete" if complete else "pending",
        "owner": owner,
        "required": required,
        "missing_inputs": missing_inputs,
        "next_action": next_action,
    }


def _checklist(repo: Path, state: dict[str, Any], markers: dict[str, bool]) -> list[dict[str, Any]]:
    profile = dict(state.get("profile") or {})
    core_inputs = _core_inputs(repo)
    missing_core = [key for key, ok in core_inputs.items() if not ok]
    wiring = link_status(repo)
    checkpoint_hook = checkpoint_mod.hook_status(repo)
    return [
        _step(
            step_id="repo_scaffold",
            title="Business repo scaffold",
            complete=_looks_initialized(markers),
            missing_inputs=[]
            if _looks_initialized(markers)
            else ["CLAUDE.md", "core/", "research/", "decisions/"],
            next_action="Run `mb onboard --mode new --path <repo> --name <business>`.",
            owner="mb",
        ),
        _step(
            step_id="business_profile",
            title="Business profile and success direction",
            complete=not _profile_missing(profile),
            missing_inputs=_profile_missing(profile),
            next_action=(
                "Ask only for business type, team size, current success stage, "
                "and desired outcome; do not collect full operations detail yet."
            ),
        ),
        _step(
            step_id="core_reference",
            title="Core files",
            complete=not missing_core,
            missing_inputs=missing_core,
            next_action=(
                "Collect just enough to draft core offer, audience, voice, soul, and proof files."
            ),
        ),
        _team_step(profile, repo),
        _step(
            step_id="runtime_handoff",
            title="Runtime handoff",
            complete=bool(wiring["ok"]),
            missing_inputs=[] if wiring["ok"] else ["Claude Code skill wiring"],
            next_action="Run `mb skill link --repo .`, then `mb start --json`.",
            owner="mb",
        ),
        _step(
            step_id="checkpoint_hook",
            title="Checkpoint save hook",
            complete=bool(checkpoint_hook["ok"]),
            missing_inputs=[]
            if checkpoint_hook["ok"]
            else ["business-readable checkpoint commit hook"],
            next_action=("Run `mb doctor repair --plan`, then `mb doctor repair --apply`."),
            owner="mb",
            required=False,
        ),
    ]


def onboarding_status(repo: str | Path = ".") -> dict[str, Any]:
    """Return the deterministic onboarding progress envelope for a business repo."""
    target = Path(repo).expanduser().resolve()
    loaded = _load_state(target)
    state = loaded or _initial_state(repo=target)
    markers = _repo_markers(target)
    checklist = _checklist(target, state, markers)
    required = [step for step in checklist if step.get("required", True)]
    complete = [step for step in required if step["status"] == "complete"]
    next_step = next((step for step in checklist if step["status"] != "complete"), None)
    return {
        "ok": _looks_initialized(markers),
        "repo": str(target),
        "state_path": str(_state_path(target)),
        "state_exists": loaded is not None,
        "state_valid": loaded is not None or not _state_path(target).exists(),
        "profile": state.get("profile") or {},
        "contract": state.get("contract") or {},
        "boundaries": state.get("boundaries") or BOUNDARIES,
        "checklist": checklist,
        "summary": {
            "status": "ready" if len(complete) == len(required) else "in_progress",
            "completed_required": len(complete),
            "total_required": len(required),
            "missing_inputs": [
                item for step in required for item in step.get("missing_inputs", [])
            ],
            "next_step": next_step["id"] if next_step else "",
            "next_recommended_action": next_step["next_action"] if next_step else "Run `mb start`.",
        },
    }


def run(
    *,
    path: str,
    name: str = "",
    mode: str = "auto",
    level: str = "auto",
    team_size: str = "unknown",
    business_type: str = "",
    success_stage: str = "unknown",
    desired_outcome: str = "",
    github_repo: str = "",
    github_visibility: str = "private",
    github_push: bool = False,
) -> dict[str, Any]:
    """Create or connect a business repo and verify the Claude Code handoff."""
    target = Path(path).expanduser().resolve()
    before = _repo_markers(target)
    normalized_mode = _normalize_mode(mode, _looks_initialized(before))

    errors: list[str] = []
    warnings: list[str] = []
    created: list[str] = []
    action = normalized_mode
    result_business_name = name.strip() if normalized_mode == "connect" else ""
    init_result: dict[str, Any] | None = None
    link_result: dict[str, Any] | None = None
    github_result: dict[str, Any] | None = None

    if normalized_mode == "connect" and not target.exists():
        errors.append(f"cannot connect missing repo: {target}")
    elif normalized_mode == "connect" and not _looks_initialized(before):
        errors.append(
            "Existing repo does not look like a Main Branch repo. "
            "Run `mb onboard --mode new --path <repo> --name <business>` to scaffold it."
        )
    elif normalized_mode == "connect":
        link_result = link_skills(target)
        created.extend(str(item) for item in link_result.get("created", []))
        if not link_result.get("ok"):
            errors.extend(str(item) for item in link_result.get("errors", []))
        action = "repaired" if before["claude_md"] else "connected"
    else:
        business_name = name.strip() or target.name.replace("-", " ").title()
        result_business_name = business_name
        init_result = init_mod.run(path=str(target), name=business_name)
        created.extend(str(item) for item in init_result.get("created", []))
        if init_result["status"] == "error":
            errors.append(str(init_result.get("error") or "mb init failed"))
        elif init_result["status"] == "already-initialized":
            action = "repaired"
        else:
            action = "created"

    after = _repo_markers(target)
    wiring = link_status(target)
    tools = _tool_readiness(target)
    selected_level = _normalize_level(level)

    if not after["git"]:
        warnings.append("Repo is not a git work tree. Run `git init` or `mb doctor` for repair.")
    checkpoint_hook = (
        init_result.get("checkpoint_hook")
        if init_result
        else checkpoint_mod.hook_status(target)
        if target.exists()
        else None
    )
    if isinstance(checkpoint_hook, dict) and not checkpoint_hook.get("ok"):
        warnings.append(str(checkpoint_hook.get("summary") or "Checkpoint hook needs repair."))

    if github_repo.strip() and target.exists() and not errors:
        github_result = _github_create_push(
            target,
            business_name=result_business_name,
            github_repo=github_repo,
            visibility=github_visibility.strip().lower(),
            push=github_push,
            generated_paths=created,
        )
        if not github_result.get("ok"):
            errors.extend(str(item) for item in github_result.get("errors", []))
            if github_result.get("repair"):
                warnings.append(str(github_result["repair"]))
        else:
            github_context = connect_mod.github_context(
                target,
                which_func=_which,
                command_runner=_run_command,
            )
            tools = _tool_readiness(target, github_context=github_context)

    if selected_level == "auto":
        selected_level = _infer_level(tools)

    if not tools["github_cli"]["found"] or not tools["github_cli"]["authenticated"]:
        warnings.append(str(tools["github_cli"]["repair"]))
    if not tools["claude_code"]["found"]:
        warnings.append(str(tools["claude_code"]["repair"]))
    if not wiring["ok"]:
        warnings.append("Claude Code skill discovery is not wired. Run `mb doctor` for details.")

    ok = not errors and wiring["ok"] and after["claude_md"]
    progress = (
        write_plan(
            target,
            business_name=result_business_name,
            team_size=team_size,
            business_type=business_type,
            success_stage=success_stage,
            desired_outcome=desired_outcome,
        )
        if target.exists() and not errors
        else onboarding_status(target)
    )
    return {
        "ok": ok,
        "status": "ok" if ok else "error",
        "action": action,
        "path": str(target),
        "mode": normalized_mode,
        "level": selected_level,
        "business_name": result_business_name,
        "created": created,
        "repo": {
            "before": before,
            "after": after,
            "looks_initialized": _looks_initialized(after),
        },
        "tools": tools,
        "skill_wiring": wiring,
        "warnings": [warning for warning in warnings if warning],
        "errors": errors,
        "doctor_command": f"mb doctor {target}",
        "checkpoint_hook": checkpoint_hook,
        "github": github_result
        or _github_create_push(
            target,
            business_name=result_business_name,
            github_repo="",
            visibility=github_visibility.strip().lower(),
            push=False,
        ),
        "setup_complete": _setup_complete(target, github_requested=bool(github_repo.strip()))
        if target.exists()
        else {},
        "onboarding": progress,
        "next_steps": _next_steps(target),
        "init": init_result,
        "link": link_result,
    }


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()
