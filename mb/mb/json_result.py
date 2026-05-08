"""Shared JSON result envelope helpers for ``mb --json`` surfaces."""

from __future__ import annotations

from typing import Any

JSON_RESULT_ENVELOPE_VERSION = "1.0"


def _coerce_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if not value:
        return []
    return [value]


def _result_status(payload: dict[str, Any], errors: list[Any]) -> str:
    if errors:
        return "error"
    return "ok" if bool(payload.get("ok", True)) else "error"


def envelope(
    payload: dict[str, Any],
    *,
    command: str,
    schema_name: str,
) -> dict[str, Any]:
    """Return ``payload`` with stable top-level result metadata added.

    The first v1 contract is intentionally additive and non-colliding: existing
    command-specific keys stay at the top level so current skills, harnesses,
    and scripts do not need to move every read under a new ``data`` key in one
    release.
    """

    result = dict(payload)
    errors = _coerce_list(result.get("errors"))
    warnings = _coerce_list(result.get("warnings"))
    actions = _coerce_list(result.get("actions"))

    result["result_envelope_version"] = JSON_RESULT_ENVELOPE_VERSION
    result["result_schema"] = {
        "name": schema_name,
        "version": JSON_RESULT_ENVELOPE_VERSION,
    }
    result["mb_command"] = command
    result["ok"] = bool(result.get("ok", not errors))
    result["result_status"] = _result_status(result, errors)
    result["errors"] = errors
    result["warnings"] = warnings
    result["actions"] = actions
    return result
