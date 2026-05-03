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
        "exhaustive operations documentation outside the core reference",
    ],
}


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


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "my-business"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_path(repo: Path) -> Path:
    return repo / ONBOARDING_STATE_RELATIVE_PATH


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
                "files under core/, research/, decisions/, campaigns/, log/, and documents/",
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
    return onboarding_status(target)


def _repo_markers(repo: Path) -> dict[str, bool]:
    return {
        "exists": repo.exists(),
        "git": (repo / ".git").exists(),
        "claude_md": (repo / "CLAUDE.md").is_file(),
        "core": (repo / "core").is_dir() or (repo / "reference" / "core").exists(),
        "research": (repo / "research").is_dir(),
        "decisions": (repo / "decisions").is_dir(),
        "skill_start": (repo / ".claude" / "skills" / "start" / "SKILL.md").is_file(),
    }


def _looks_initialized(markers: dict[str, bool]) -> bool:
    shaped_dirs = sum(1 for key in ("core", "research", "decisions") if markers[key])
    return markers["claude_md"] and shaped_dirs >= 2


def _tool_readiness(repo: Path) -> dict[str, Any]:
    git_path = _which("git")
    gh_path = _which("gh")
    claude_path = _which("claude")
    gh_auth = False
    git_repo = False

    if git_path:
        git_probe = _run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)
        git_repo = git_probe["ok"] and git_probe["stdout"].strip() == "true"
    if gh_path:
        gh_probe = _run_command(["gh", "auth", "status"], cwd=repo)
        gh_auth = gh_probe["ok"]

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
            "path": gh_path,
            "repair": ""
            if gh_path and gh_auth
            else (
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
        "/start",
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
            title="Core reference",
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
            complete=bool(link_status(repo)["ok"]),
            missing_inputs=[] if link_status(repo)["ok"] else ["Claude Code skill wiring"],
            next_action="Run `mb skill link --repo .`, then `mb start --json`.",
            owner="mb",
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
    if selected_level == "auto":
        selected_level = _infer_level(tools)

    if not after["git"]:
        warnings.append("Repo is not a git work tree. Run `git init` or `mb doctor` for repair.")
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
        if target.exists()
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
        "onboarding": progress,
        "next_steps": _next_steps(target),
        "init": init_result,
        "link": link_result,
    }


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()
