"""Install-mode-aware Main Branch engine updates."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mb import __version__
from mb import codex as codex_mod
from mb.engine import bundled_skills, engine_root, install_mode
from mb.freshness import (
    latest_pypi_version as _latest_pypi_version,
)
from mb.freshness import release_notes_url, version_key

VERSION_RE = re.compile(r'__version__\s*=\s*["\']([^"\']+)["\']')
CLONE_UPDATE_COMMAND = ["git", "pull", "--ff-only", "origin", "main"]
GITHUB_RELEASE_API_URL_TEMPLATE = (
    "https://api.github.com/repos/noontide-co/mainbranch/releases/tags/oe-v{version}"
)


def _run_command(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )


def _engine_version(root: Path | None = None) -> str:
    root = root or engine_root()
    if root is None:
        return __version__

    candidates = [
        root / "mb" / "mb" / "__init__.py",
        root / "mb" / "__init__.py",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        match = VERSION_RE.search(candidate.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return __version__


def _version_from_git_ref(root: Path, ref: str) -> str | None:
    result = _run_command(["git", "show", f"{ref}:mb/mb/__init__.py"], cwd=root)
    if result.returncode != 0:
        return None
    match = VERSION_RE.search(result.stdout)
    return match.group(1) if match else None


def _fetch_origin_main(root: Path) -> tuple[bool, str | None]:
    result = _run_command(
        ["git", "fetch", "origin", "main:refs/remotes/origin/main", "--quiet"],
        cwd=root,
    )
    if result.returncode == 0:
        return True, None
    return False, _command_error("git fetch origin main", result)


def _version_from_mb_command() -> str | None:
    result = _run_command(["mb", "--version"])
    if result.returncode != 0:
        return None
    match = re.search(r"\bmb\s+(.+)\s*$", result.stdout.strip())
    return match.group(1) if match else None


def _command_error(label: str, result: subprocess.CompletedProcess[str]) -> str:
    details = (result.stderr or result.stdout).strip()
    return f"{label} failed with exit code {result.returncode}: {details or 'no output'}"


def _list_field(result: dict[str, Any], key: str) -> list[str]:
    value = result.get(key, [])
    return [str(item) for item in value] if isinstance(value, list) else []


def _skill_count_from_link_result(result: dict[str, Any]) -> int:
    total = 0
    for key in ("linked", "copied"):
        total += len(_list_field(result, key))
    return total


def _release_summary(body: str) -> str:
    lines: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            if lines:
                break
            continue
        if line.startswith("#"):
            continue
        lines.append(line)
    return " ".join(lines)


def _release_context(version: str, *, timeout: float = 3.0) -> dict[str, Any]:
    version = version.strip()
    context: dict[str, Any] = {
        "version": version,
        "tag": f"oe-v{version}" if version else "",
        "url": release_notes_url(version),
        "name": "",
        "published_at": "",
        "summary": "",
        "available": False,
        "source": "github_release",
    }
    if not version:
        return context
    url = GITHUB_RELEASE_API_URL_TEMPLATE.format(version=version)
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        context["source"] = "github_release_unavailable"
        return context
    if not isinstance(data, dict):
        context["source"] = "github_release_unavailable"
        return context
    body = str(data.get("body") or "")
    context.update(
        {
            "url": str(data.get("html_url") or context["url"]),
            "name": str(data.get("name") or ""),
            "published_at": str(data.get("published_at") or ""),
            "summary": _release_summary(body),
            "available": True,
        }
    )
    return context


def _link_warnings(payload: dict[str, Any]) -> list[str]:
    skipped = _list_field(payload, "skipped")
    if not skipped:
        return []
    return [
        "could not refresh existing non-link skill path(s): " + ", ".join(skipped),
    ]


def _link_skills(repo: Path) -> tuple[int, list[str], list[str], dict[str, Any] | None]:
    result = _run_command(["mb", "skill", "link", "--repo", str(repo), "--json"])
    if result.returncode != 0:
        return 0, [_command_error("mb skill link", result)], [], None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return 0, ["mb skill link returned invalid JSON"], [], None
    if not isinstance(payload, dict):
        return 0, ["mb skill link returned an unexpected JSON payload"], [], None
    errors = payload.get("errors", [])
    parsed_errors = [str(error) for error in errors] if isinstance(errors, list) else []
    warnings = _link_warnings(payload)
    if payload.get("ok") is not True:
        return (
            _skill_count_from_link_result(payload),
            parsed_errors or ["mb skill link failed"],
            warnings,
            payload,
        )
    return _skill_count_from_link_result(payload), [], warnings, payload


def _base_result(repo: Path, *, check: bool, mode: str, root: Path | None) -> dict[str, Any]:
    return {
        "ok": True,
        "mode": mode,
        "check": check,
        "repo": str(repo),
        "engine_root": str(root) if root is not None else None,
        "old_version": _engine_version(root),
        "new_version": None,
        "skills_relinked_count": 0,
        "planned_skills_relink_count": 0,
        "release": {},
        "actions": [],
        "warnings": [],
        "errors": [],
        "next_actions": [],
        "codex_adapter": {},
    }


def _add_codex_follow_up(result: dict[str, Any], repo: Path) -> None:
    codex = codex_mod.readiness(repo)
    instructions = codex.get("instructions", {})
    plugin_install = codex.get("plugin_install", {})
    result["codex_adapter"] = {
        "ok": codex["ok"],
        "status": codex.get("status", ""),
        "static_ok": codex.get("static_ok", False),
        "runtime_ok": codex.get("runtime_ok", False),
        "plugin_ok": codex.get("plugin_ok", False),
        "command_surface_ok": codex.get("command_surface_ok", False),
        "slash_commands_ready": codex.get("slash_commands_ready", False),
        "exists": instructions.get("exists", False),
        "current": instructions.get("current", False),
        "repair_command": codex.get("repair", "") or instructions.get("repair_command", ""),
        "plugin_install": plugin_install,
    }
    if not codex["ok"]:
        next_actions: list[str]
        if not instructions.get("ok", False):
            message = (
                "Codex AGENTS.md guidance still needs repo repair. Run "
                "`mb doctor repair --plan --only codex`, review it, then approve "
                "`mb doctor repair --apply --only codex`."
            )
            next_actions = [
                "mb doctor repair --plan --only codex",
                "mb doctor repair --apply --only codex",
            ]
        elif not codex.get("plugin_ok", False):
            message = (
                "The global Main Branch Codex plugin is not ready, so generated Codex "
                "guidance may be unavailable. "
                "Run `mb doctor repair --plan --only codex`, review it, then approve "
                "`mb doctor repair --apply --only codex`."
            )
            next_actions = [
                "mb doctor repair --plan --only codex",
                "mb doctor repair --apply --only codex",
            ]
        else:
            message = (
                "Codex runtime readiness still needs attention. Run "
                "`mb status --json --peek` and repair the reported runtime issue."
            )
            next_actions = ["mb status --json --peek"]
        result["warnings"].append(message)
        result["next_actions"].extend(next_actions)


def run(repo: str | Path = ".", *, check: bool = False) -> dict[str, Any]:
    """Update the active Main Branch install and refresh business-repo skills."""
    target_repo = Path(repo).resolve()
    mode = install_mode()
    root = engine_root()
    result = _base_result(target_repo, check=check, mode=mode, root=root)

    if mode not in {"pipx", "clone"}:
        result["ok"] = False
        result["new_version"] = result["old_version"]
        result["errors"].append(
            f"unsupported install mode: {mode}. Expected a pipx install or git clone."
        )
        return result

    if check:
        if mode == "pipx":
            result["new_version"] = _latest_pypi_version() or result["old_version"]
            result["actions"] = [
                "would run `pipx upgrade mainbranch`",
                f"would run `mb skill link --repo {target_repo} --json`",
            ]
        else:
            if root is None:
                result["ok"] = False
                result["errors"].append("could not locate Main Branch engine root")
                result["new_version"] = result["old_version"]
                return result
            fetched, fetch_error = _fetch_origin_main(root)
            result["actions"].append(f"ran `git fetch origin main --quiet` in {root}")
            if not fetched:
                result["ok"] = False
                result["errors"].append(fetch_error or "git fetch origin main failed")
                result["new_version"] = result["old_version"]
                return result
            result["new_version"] = (
                _version_from_git_ref(root, "origin/main") or result["old_version"]
            )
            result["actions"].extend(
                [
                    f"would run `git pull --ff-only origin main` in {root}",
                    f"would run `mb skill link --repo {target_repo} --json`",
                ]
            )
        planned_count = len(bundled_skills())
        result["skills_relinked_count"] = planned_count
        result["planned_skills_relink_count"] = planned_count
        new_version = str(result.get("new_version") or "")
        old_version = str(result.get("old_version") or "")
        if new_version and version_key(new_version) > version_key(old_version):
            result["release"] = _release_context(new_version)
        elif new_version:
            result["release"] = {
                "version": new_version,
                "tag": f"oe-v{new_version}",
                "url": release_notes_url(new_version),
                "name": "",
                "published_at": "",
                "summary": "",
                "available": False,
                "source": "not_newer",
            }
        _add_codex_follow_up(result, target_repo)
        return result

    if mode == "pipx":
        if shutil.which("pipx") is None:
            result["ok"] = False
            result["new_version"] = result["old_version"]
            result["errors"].append("pipx install mode detected, but `pipx` is not on PATH")
            return result
        upgrade = _run_command(["pipx", "upgrade", "mainbranch"])
        result["actions"].append("ran `pipx upgrade mainbranch`")
        if upgrade.returncode != 0:
            result["ok"] = False
            result["new_version"] = result["old_version"]
            result["errors"].append(_command_error("pipx upgrade mainbranch", upgrade))
            return result
        result["new_version"] = _version_from_mb_command() or result["old_version"]
    else:
        if root is None:
            result["ok"] = False
            result["new_version"] = result["old_version"]
            result["errors"].append("could not locate Main Branch engine root")
            return result
        pull = _run_command(CLONE_UPDATE_COMMAND, cwd=root)
        result["actions"].append(f"ran `git pull --ff-only origin main` in {root}")
        if pull.returncode != 0:
            result["ok"] = False
            result["new_version"] = result["old_version"]
            result["errors"].append(_command_error("git pull", pull))
            return result
        result["new_version"] = _engine_version(root)

    linked_count, link_errors, link_warnings, _link_payload = _link_skills(target_repo)
    result["actions"].append(f"ran `mb skill link --repo {target_repo} --json`")
    result["skills_relinked_count"] = linked_count
    result["warnings"].extend(link_warnings)
    if link_errors:
        result["ok"] = False
        result["errors"].extend(link_errors)
    _add_codex_follow_up(result, target_repo)
    return result


def render_human(result: dict[str, Any]) -> None:
    """Print a concise human-readable update result."""
    old = result.get("old_version") or "unknown"
    new = result.get("new_version") or "unknown"
    mode = result.get("mode") or "unknown"
    count = result.get("skills_relinked_count", 0)

    if result.get("check"):
        print(f"install mode: {mode}")
        print(f"version: {old} -> {new}")
        raw_release = result.get("release")
        release = raw_release if isinstance(raw_release, dict) else {}
        release_url = str(release.get("url") or "")
        release_summary = str(release.get("summary") or "")
        release_available = release.get("available") is True
        if release_url and release_available:
            print(f"release notes: {release_url}")
        elif release_url and release.get("source") != "not_newer":
            print(f"expected release notes URL: {release_url}")
        if release_summary and release_available:
            print(f"release summary: {release_summary}")
        for action in result.get("actions", []):
            print(action)
        for action in result.get("next_actions", []):
            print(f"next: {action}")
        if count:
            print(f"would refresh {count} skill link(s)")
    elif result.get("ok"):
        print(f"updated Main Branch ({old} -> {new})")
        print(f"refreshed {count} skill link(s)")
        for action in result.get("next_actions", []):
            print(f"next: {action}")

    if result.get("errors"):
        for error in result["errors"]:
            print(f"error: {error}")
    if result.get("warnings"):
        for warning in result["warnings"]:
            print(f"warning: {warning}")
