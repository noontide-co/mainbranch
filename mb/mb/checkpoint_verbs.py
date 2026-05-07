"""Business-readable checkpoint verb registry and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

import yaml

VALID_LOOPS = {"sense", "decide", "ship", "reflect"}
MAX_SUBJECT_LENGTH = 90

PREFIX_RE = re.compile(r"^\[(?P<verb>[a-z]+)\]\s+(?P<object>.+?)\s*$")
RESULT_SPLIT_RE = re.compile(r"\s+--\s+", re.ASCII)
PRIVATE_PATH_RE = re.compile(
    r"(?i)(^|\s)(/Users/[^/\s]+/|/home/[^/\s]+/|[A-Z]:\\Users\\[^\\\s]+\\|~/)"
)
SECRET_TEXT_RE = re.compile(
    r"(?i)("
    r"(api[_-]?key|access[_-]?token|secret|client[_-]?secret)\s*[:=]\s*['\"]?\S{6,}"
    r"|authorization:\s*bearer\s+\S+"
    r"|sk-[A-Za-z0-9_-]{12,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r")"
)
FUTURE_TENSE_RE = re.compile(r"(?i)\b(will|going to|plan to|planning to|todo|next)\b")
VAGUE_OBJECT_RE = re.compile(
    r"(?i)^(work|stuff|things|misc|miscellaneous|updates?|changes?|checkpoint|wip)$"
)
VAGUE_SUBJECT_RE = re.compile(
    r"(?i)^(wip|misc|stuff|things|updated things|fix stuff|work saved|checkpoint)$"
)
LOOP_PREFIXES = {"sense", "decide", "ship", "reflect"}


@dataclass(frozen=True)
class VerbEntry:
    """One accepted business checkpoint verb."""

    verb: str
    prefix: str
    loops: tuple[str, ...]
    default_loop: str
    channel_hint: str | None
    use_when: str


def _data_path() -> Any:
    return resources.files("mb").joinpath("_data").joinpath("checkpoint_verbs.yaml")


@lru_cache(maxsize=1)
def registry() -> dict[str, VerbEntry]:
    """Load accepted checkpoint verbs from packaged data."""
    raw = yaml.safe_load(_data_path().read_text(encoding="utf-8")) or {}
    entries: dict[str, VerbEntry] = {}
    for item in raw.get("verbs", []):
        if not isinstance(item, dict):
            continue
        verb = str(item.get("verb", "")).strip()
        loops = tuple(str(loop).strip() for loop in item.get("loops", []) if str(loop).strip())
        default_loop = str(item.get("default_loop", "")).strip()
        if not verb or not loops or default_loop not in VALID_LOOPS:
            continue
        if any(loop not in VALID_LOOPS for loop in loops):
            continue
        channel_hint = item.get("channel_hint")
        entries[verb] = VerbEntry(
            verb=verb,
            prefix=str(item.get("prefix") or f"[{verb}]"),
            loops=loops,
            default_loop=default_loop,
            channel_hint=str(channel_hint) if channel_hint else None,
            use_when=str(item.get("use_when", "")),
        )
    return entries


def accepted_prefix_pattern() -> str:
    """Return an extended-regexp alternation for git log prefix matching."""
    verbs = "|".join(sorted(registry()))
    return rf"^\[({verbs}|checkpoint)\]"


def parse_subject(subject: str) -> dict[str, Any]:
    """Parse a checkpoint subject without judging whether it is acceptable."""
    first_line = subject.strip().splitlines()[0] if subject.strip() else ""
    match = PREFIX_RE.match(first_line)
    if not match:
        return {
            "recognized": False,
            "subject": first_line,
            "verb": None,
            "prefix": None,
            "loop": None,
            "loops": [],
            "channel_hint": None,
            "object": "",
            "result": "",
        }

    verb = match.group("verb")
    entry = registry().get(verb)
    body = match.group("object").strip()
    parts = RESULT_SPLIT_RE.split(body, maxsplit=1)
    obj = parts[0].strip()
    result = parts[1].strip() if len(parts) > 1 else ""
    return {
        "recognized": entry is not None,
        "subject": first_line,
        "verb": verb if entry else None,
        "prefix": f"[{verb}]",
        "loop": entry.default_loop if entry else None,
        "loops": list(entry.loops) if entry else [],
        "channel_hint": entry.channel_hint if entry else None,
        "object": obj,
        "result": result,
    }


def _problem(code: str, message: str, guidance: str) -> dict[str, str]:
    return {"code": code, "message": message, "guidance": guidance}


def validate_subject(message: str) -> dict[str, Any]:
    """Validate a business checkpoint message subject for ``mb checkpoint``."""
    raw = message.strip()
    subject = raw.splitlines()[0] if raw else ""
    parsed = parse_subject(subject)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not subject:
        errors.append(
            _problem(
                "empty_subject",
                "Checkpoint subject is empty.",
                "Use a business verb, for example `[updated] offer.md -- clarified price`.",
            )
        )
    if len(subject) > MAX_SUBJECT_LENGTH:
        errors.append(
            _problem(
                "overlong_subject",
                (
                    f"Checkpoint subject is {len(subject)} characters; "
                    f"keep it under {MAX_SUBJECT_LENGTH}."
                ),
                "Move detail into the commit body and keep the subject scannable.",
            )
        )
    if VAGUE_SUBJECT_RE.match(subject):
        errors.append(
            _problem(
                "vague_subject",
                "Checkpoint subject is too vague to help future you.",
                "Name what changed, for example `[updated] offer.md -- clarified guarantee`.",
            )
        )
    if PRIVATE_PATH_RE.search(subject):
        errors.append(
            _problem(
                "private_local_path",
                "Checkpoint subject includes a private local machine path.",
                "Use the business object name instead of a path like `/Users/name/...`.",
            )
        )
    if SECRET_TEXT_RE.search(subject):
        errors.append(
            _problem(
                "secret_like_subject",
                "Checkpoint subject looks like it may include a token or secret.",
                "Remove credentials from the message and rotate the secret if it was exposed.",
            )
        )
    if FUTURE_TENSE_RE.search(subject):
        errors.append(
            _problem(
                "future_tense_subject",
                "Checkpoint subjects should describe work that already happened.",
                "Use a past-tense verb prefix such as `[updated]`, `[drafted]`, or `[ran]`.",
            )
        )

    prefix = str(parsed.get("prefix") or "")
    verb_text = prefix.strip("[]")
    if not parsed.get("recognized"):
        if verb_text == "checkpoint":
            errors.append(
                _problem(
                    "generic_checkpoint_prefix",
                    "`[checkpoint]` is not a business-readable checkpoint verb.",
                    (
                        "Replace it with an accepted verb such as `[updated]`, "
                        "`[drafted]`, or `[ran]`."
                    ),
                )
            )
        elif verb_text in LOOP_PREFIXES:
            errors.append(
                _problem(
                    "loop_prefix",
                    "Loop names are metadata, not checkpoint subject prefixes.",
                    "Use the business action instead, for example `[shipped] lander`.",
                )
            )
        elif subject and not prefix:
            errors.append(
                _problem(
                    "missing_prefix",
                    "Checkpoint subject must start with an accepted business verb prefix.",
                    (
                        "Use `[verb] object -- result`, for example "
                        "`[updated] offer.md -- raised price`."
                    ),
                )
            )
        elif subject:
            errors.append(
                _problem(
                    "unknown_prefix",
                    f"`{prefix}` is not an accepted business checkpoint verb.",
                    "Use one of: " + ", ".join(entry.prefix for entry in registry().values()) + ".",
                )
            )

    obj = str(parsed.get("object") or "").strip()
    if parsed.get("recognized") and not obj:
        errors.append(
            _problem(
                "missing_object",
                "Checkpoint subject names a verb but not the business object.",
                "Name the file, bet, provider, artifact, or workflow that changed.",
            )
        )
    if parsed.get("recognized") and VAGUE_OBJECT_RE.match(obj):
        errors.append(
            _problem(
                "vague_object",
                "Checkpoint object is too vague.",
                "Replace words like `stuff`, `things`, or `work` with the actual business object.",
            )
        )

    severity = "error" if errors else "warning" if warnings else "ok"
    guidance = [problem["guidance"] for problem in [*errors, *warnings]]
    return {
        "ok": not errors,
        "status": "valid" if not errors else "invalid",
        "message": raw,
        "subject": subject,
        "parsed": parsed,
        "severity": severity,
        "acceptable_for_beginner": not errors,
        "errors": errors,
        "warnings": warnings,
        "guidance": guidance,
    }
