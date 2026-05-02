"""Shared package freshness metadata and beginner-safe update copy."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mb import __version__
from mb.engine import install_mode

MINIMUM_SUPPORTED_VERSION = "0.2.0"
MB_UPDATE_AVAILABLE_VERSION = "0.2.0"
PYPI_PACKAGE_URL = "https://pypi.org/pypi/mainbranch/json"
_LATEST_AUTO = object()


def version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split("."):
        digits = ""
        for char in piece:
            if not char.isdigit():
                break
            digits += char
        parts.append(int(digits or "0"))
    return tuple(parts)


def latest_pypi_version(timeout: float = 3.0) -> str | None:
    try:
        with urllib.request.urlopen(PYPI_PACKAGE_URL, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        return None
    info = data.get("info", {})
    version = info.get("version") if isinstance(info, dict) else None
    return version if isinstance(version, str) and version else None


def looks_like_business_repo(repo: Path) -> bool:
    return (repo / "CLAUDE.md").is_file() and (
        (repo / "core").is_dir()
        or (repo / "reference" / "core").exists()
        or (repo / "research").is_dir()
        or (repo / "decisions").is_dir()
    )


def _post_update_commands(repo: str | Path | None) -> list[str]:
    if repo is None:
        return []
    return ["mb skill link --repo .", "mb doctor"]


def package_update_status(
    repo: str | Path | None = None,
    *,
    installed_version: str = __version__,
    latest_version: Any = _LATEST_AUTO,
    minimum_supported: str = MINIMUM_SUPPORTED_VERSION,
    mode: str | None = None,
) -> dict[str, Any]:
    """Return stable update metadata for CLI JSON and skill consumers."""
    mode = install_mode() if mode is None else mode
    latest = (
        latest_pypi_version()
        if latest_version is _LATEST_AUTO and mode not in {"clone", "source"}
        else latest_version
    )
    if latest is _LATEST_AUTO:
        latest = None
    latest_text = latest if isinstance(latest, str) else ""

    installed_key = version_key(installed_version)
    minimum_key = version_key(minimum_supported)
    latest_key = version_key(latest_text) if latest_text else ()

    severity = "current"
    command = ""
    reason = "Installed version is supported."

    if mode in {"clone", "source"}:
        reason = f"Package freshness does not apply in {mode} mode."
    elif installed_key < minimum_key:
        severity = "required"
        command = "pipx upgrade mainbranch"
        if installed_key < version_key(MB_UPDATE_AVAILABLE_VERSION):
            reason = "Installed version predates mb update and the current skill-link repair flow."
        else:
            reason = "Installed version is below the minimum supported Main Branch version."
    elif latest_text and latest_key > installed_key:
        severity = "recommended"
        command = "mb update"
        reason = "A newer compatible Main Branch package is available."
    elif latest_version is _LATEST_AUTO and mode not in {"clone", "source"} and not latest_text:
        severity = "unknown"
        reason = "Could not check PyPI for the latest Main Branch version."
    elif latest_text:
        reason = "Installed version is current."

    return {
        "installed": installed_version,
        "latest": latest_text,
        "minimum_supported": minimum_supported,
        "severity": severity,
        "command": command,
        "post_update_commands": _post_update_commands(repo),
        "reason": reason,
    }


def format_update_alert(update: dict[str, Any]) -> str:
    """Render the shared update object as direct beginner-safe terminal copy."""
    severity = str(update.get("severity", ""))
    if severity not in {"required", "recommended"}:
        return ""

    command = str(update.get("command") or "pipx upgrade mainbranch")
    post_update = [str(cmd) for cmd in update.get("post_update_commands", [])]
    installed = str(update.get("installed") or "")
    minimum_supported = str(update.get("minimum_supported") or "")

    if severity == "required":
        lines = [
            "Update required.",
            "",
            "Your Main Branch install is old enough that setup and skills may not work correctly.",
            "",
            "Run this first:",
            f"  {command}",
        ]
        if installed and version_key(installed) < version_key(MB_UPDATE_AVAILABLE_VERSION):
            lines.extend(
                [
                    "",
                    f"mb update is not available in {installed}; this first update must use pipx.",
                ]
            )
    else:
        lines = [
            "Update recommended.",
            "",
            "A newer Main Branch version is available. Your install is still supported.",
            "",
            "Run:",
            f"  {command}",
        ]

    if post_update:
        lines.extend(["", "Then, from your business repo:"])
        lines.extend(f"  {cmd}" for cmd in post_update)
    elif severity == "required" and minimum_supported:
        lines.extend(["", f"Minimum supported version: {minimum_supported}."])

    return "\n".join(lines)
