"""Release simulation suite manifest and transcript scoring helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

KNOWN_FIXTURE_PROFILES = frozenset(
    {
        "fresh_sanitized_business_repo",
        "broken_skill_wiring_fixture",
        "public_safe_refusal_fixture",
        "legacy_drift_fixture",
        "dirty_checkpoint_fixture",
        "launch_readiness_fixture",
        "rich_multi_offer_migration_repo",
    }
)


@dataclass(frozen=True)
class BehaviorCheck:
    """One transcript behavior check from the simulation suite."""

    id: str
    description: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class Simulation:
    """One operator-moment simulation prompt and expected behavior contract."""

    id: str
    label: str
    title: str
    tiers: tuple[str, ...]
    prompt: str
    expected_route: tuple[str, ...]
    expected_behaviors: tuple[str, ...]
    must_observe: tuple[str, ...]
    must_not: tuple[str, ...]
    fixture_profile: str = "fresh_sanitized_business_repo"


def _default_manifest_path() -> Any:
    return (
        resources.files("mb")
        .joinpath("_data")
        .joinpath("release_simulations")
        .joinpath("manifest.json")
    )


@lru_cache(maxsize=1)
def load_manifest() -> dict[str, Any]:
    """Load the packaged release simulation manifest."""
    return load_manifest_from_path(None)


def load_manifest_from_path(path: Path | None) -> dict[str, Any]:
    """Load a release simulation manifest from packaged data or a test path."""
    ref = _default_manifest_path() if path is None else path
    payload = json.loads(ref.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("release simulation manifest must be a JSON object")
    if payload.get("schema_version") != "1.0":
        raise ValueError("release simulation manifest schema_version must be 1.0")
    return payload


def behavior_checks(manifest: dict[str, Any] | None = None) -> tuple[BehaviorCheck, ...]:
    """Return the manifest behavior checks used for transcript scoring."""
    data = load_manifest() if manifest is None else manifest
    checks: list[BehaviorCheck] = []
    for item in _list(data, "behavior_checks"):
        check_id = _required_str(item, "id")
        checks.append(
            BehaviorCheck(
                id=check_id,
                description=_required_str(item, "description"),
                keywords=tuple(_str_list(item, "keywords")),
            )
        )
    return tuple(checks)


def simulations(manifest: dict[str, Any] | None = None) -> tuple[Simulation, ...]:
    """Return all operator-moment simulations from the manifest."""
    data = load_manifest() if manifest is None else manifest
    sims: list[Simulation] = []
    for item in _list(data, "simulations"):
        sims.append(
            Simulation(
                id=_required_str(item, "id"),
                label=_required_str(item, "label"),
                title=_required_str(item, "title"),
                tiers=tuple(_str_list(item, "tiers")),
                prompt=_required_str(item, "prompt"),
                expected_route=tuple(_str_list(item, "expected_route")),
                expected_behaviors=tuple(_str_list(item, "expected_behaviors")),
                must_observe=tuple(_str_list(item, "must_observe")),
                must_not=tuple(_str_list(item, "must_not")),
                fixture_profile=_required_str(item, "fixture_profile"),
            )
        )
    return tuple(sims)


def simulations_for_tier(
    tier: str, manifest: dict[str, Any] | None = None
) -> tuple[Simulation, ...]:
    """Return simulations that belong to a release evidence tier."""
    data = load_manifest() if manifest is None else manifest
    tier_ids = {str(item.get("id", "")) for item in _list(data, "tiers")}
    if tier not in tier_ids:
        raise ValueError(f"unknown release simulation tier: {tier}")
    return tuple(sim for sim in simulations(manifest) if tier in sim.tiers)


def claude_prompts_for_tier(tier: str) -> tuple[tuple[str, str], ...]:
    """Return ``(label, prompt)`` pairs for a tier's Claude print/manual sims."""
    return tuple((sim.label, sim.prompt) for sim in simulations_for_tier(tier))


def score_transcript(text: str, checks: tuple[BehaviorCheck, ...] | None = None) -> dict[str, Any]:
    """Score a transcript with lightweight keyword checks.

    This is intentionally heuristic. It catches obvious regressions and points a
    human reviewer at the transcript; it does not replace manual review.
    """
    active_checks = behavior_checks() if checks is None else checks
    normalized = text.lower()
    observed_unknown_command = contains_observed_unknown_command_failure(text)
    results: dict[str, dict[str, Any]] = {}
    passed = 0
    for check in active_checks:
        ok = any(_keyword_matches(normalized, keyword) for keyword in check.keywords)
        if check.id == "skill_discovery" and observed_unknown_command:
            ok = False
        if check.id == "runtime_provider_honesty" and _contains_overclaim(normalized):
            ok = False
        results[check.id] = {
            "ok": ok,
            "description": check.description,
            "keywords": list(check.keywords),
        }
        if check.id == "skill_discovery":
            results[check.id]["observed_unknown_command_failure"] = observed_unknown_command
        if ok:
            passed += 1
    return {
        "passed": passed,
        "total": len(active_checks),
        "checks": results,
        "operator_language": analyze_operator_language(text),
        "heuristic_notice": (
            "Keyword scoring is proxy evidence; inspect transcript review "
            "categories before release acceptance."
        ),
    }


def analyze_operator_language(text: str) -> dict[str, Any]:
    """Return UX warnings for visible technical language in final responses.

    Release simulations pass Claude's final answer text into this helper. It is
    deliberately not meant for raw command output, JSON artifacts, fixture setup,
    or maintainer-only evidence.
    """
    visible_text = _strip_fenced_code(text)
    leakage_examples = _visible_technical_leakage(visible_text)
    checkpoint_examples = _broad_checkpoint_notes(visible_text)
    severity = _operator_language_severity(
        leakage_count=len(leakage_examples),
        checkpoint_count=len(checkpoint_examples),
    )
    return {
        "operator_language_first": severity == "none",
        "visible_technical_leakage": {
            "severity": severity,
            "examples": leakage_examples,
        },
        "checkpoint_note_specificity": {
            "ok": not checkpoint_examples,
            "examples": checkpoint_examples,
        },
        "scope": (
            "Scores visible Claude final responses only; raw tools, JSON, "
            "fixture setup, command artifacts, and maintainer evidence are "
            "outside this lexical warning layer."
        ),
    }


def contains_observed_unknown_command_failure(text: str) -> bool:
    """Return true when a transcript appears to report an observed slash failure.

    Claude may correctly mention ``Unknown command: /mb-start`` while triaging a
    repair path. Release acceptance should fail on observed runtime output or a
    final diagnosis, not quoted symptom options or conditional repair guidance.
    """
    raw_lines = text.splitlines()
    for index, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        normalized = _normalize_unknown_command_line(line)
        if "unknown command" not in normalized:
            continue
        if _is_raw_unknown_command_output(normalized):
            return True
        if index + 1 < len(raw_lines):
            next_line = _normalize_unknown_command_line(raw_lines[index + 1].strip())
            if next_line.startswith("/"):
                combined = _normalize_unknown_command_line(f"{line} {raw_lines[index + 1]}")
                if _is_raw_unknown_command_output(combined):
                    return True
                if _is_unknown_command_contextual_guidance(combined):
                    continue
                if _is_observed_unknown_command_line(combined):
                    return True
        if _is_unknown_command_contextual_guidance(normalized):
            continue
        if _is_observed_unknown_command_line(normalized):
            return True
    return False


def validate_manifest(manifest: dict[str, Any] | None = None) -> list[str]:
    """Return structural manifest validation errors."""
    data = load_manifest() if manifest is None else manifest
    errors: list[str] = []
    tier_ids = {str(item.get("id", "")) for item in _list(data, "tiers")}
    check_ids = {check.id for check in behavior_checks(data)}
    simulation_ids: set[str] = set()
    for sim in simulations(data):
        if sim.id in simulation_ids:
            errors.append(f"duplicate simulation id: {sim.id}")
        simulation_ids.add(sim.id)
        for tier in sim.tiers:
            if tier not in tier_ids:
                errors.append(f"{sim.id} references unknown tier {tier}")
        for check_id in sim.expected_behaviors:
            if check_id not in check_ids:
                errors.append(f"{sim.id} references unknown behavior check {check_id}")
        if sim.fixture_profile not in KNOWN_FIXTURE_PROFILES:
            errors.append(f"{sim.id} references unknown fixture_profile {sim.fixture_profile}")
        if not sim.prompt.strip():
            errors.append(f"{sim.id} has empty prompt")
        if not sim.must_observe:
            errors.append(f"{sim.id} has no expected-observation rubric")
    for tier_item in _list(data, "tiers"):
        tier_id = str(tier_item.get("id", ""))
        for sim_id in _str_list(tier_item, "simulations"):
            if sim_id not in simulation_ids:
                errors.append(f"{tier_id} references unknown simulation {sim_id}")
    return errors


def _contains_overclaim(text: str) -> bool:
    overclaim_terms = (
        "postiz is supported",
        "codex is supported",
        "cursor is supported",
        "will send the email",
        "sent the email for you",
        "will publish automatically",
        "published automatically",
        "will spend money",
        "spent money for you",
    )
    return any(term in text for term in overclaim_terms)


_TECHNICAL_LANGUAGE_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"\bclean on\s+`?main`?\b", re.IGNORECASE),
        "clean on main",
        "nothing unsaved locally in the current business folder",
    ),
    (
        re.compile(r"\bgit (?:tree )?is clean\b", re.IGNORECASE),
        "git is clean",
        "nothing unsaved locally",
    ),
    (
        re.compile(r"\brepo is clean\b", re.IGNORECASE),
        "repo is clean",
        "your business folder has no unsaved changes",
    ),
    (
        re.compile(r"\bworking tree (?:is )?clean\b", re.IGNORECASE),
        "working tree clean",
        "no unsaved file changes",
    ),
    (
        re.compile(r"\bbranch\s+`?main`?\b", re.IGNORECASE),
        "branch main",
        "current business folder",
    ),
    (
        re.compile(r"\bon\s+`main`(?=\W|$)|\bon main\b"),
        "on main",
        "in the current business folder",
    ),
    (
        re.compile(
            r"\bonly commit so far\b|"
            r"\b(?:the|your|this is your|this is the|it is your|it is the|"
            r"it's your|it's the|that is your|that is the|that's your|that's the)"
            r"\s+only commit\b",
            re.IGNORECASE,
        ),
        "only commit so far",
        "last saved checkpoint",
    ),
    (
        re.compile(r"\bone commit\b", re.IGNORECASE),
        "one commit",
        "one saved checkpoint",
    ),
    (
        re.compile(r"\bstaged files?\b", re.IGNORECASE),
        "staged files",
        "files queued for save",
    ),
    (
        re.compile(r"\bno github origin remote\b", re.IGNORECASE),
        "No GitHub origin remote",
        "no connected GitHub backup or shared task source",
    ),
    (
        re.compile(r"\borigin remote\b", re.IGNORECASE),
        "origin remote",
        "GitHub connection",
    ),
    (
        re.compile(r"\bpr/issue facts\b", re.IGNORECASE),
        "PR/issue facts",
        "GitHub task and proposal context",
    ),
    (
        re.compile(r"\bbefore (?:this|anything) goes to a remote\b", re.IGNORECASE),
        "before this goes to a remote",
        "before anything is shared outside your machine",
    ),
)

_BROAD_CHECKPOINT_NOTE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\[(?:added|updated|changed)\]\s+"
        r"(?:core\s*(?:and|&|\+|,)\s*research|files|stuff|changes)\b"
    ),
    re.compile(
        r"proposed message:\s*`?\[(?:added|updated|changed)\]\s+"
        r"core\s*(?:and|&|\+|,)\s*research`?"
    ),
)


def _strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def _visible_technical_leakage(text: str) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or _is_allowed_technical_detail_line(stripped):
            continue
        matched_spans: list[tuple[int, int]] = []
        for pattern, phrase, preferred in _TECHNICAL_LANGUAGE_PATTERNS:
            match = pattern.search(stripped)
            if match is None:
                continue
            span = match.span()
            if any(_spans_overlap(span, existing) for existing in matched_spans):
                continue
            matched_spans.append(span)
            examples.append(
                {
                    "phrase": phrase,
                    "preferred": preferred,
                    "excerpt": _short_excerpt(stripped, match.start(), match.end()),
                }
            )
    return examples


def _spans_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _broad_checkpoint_notes(text: str) -> list[dict[str, str]]:
    normalized = text.lower()
    examples: list[dict[str, str]] = []
    for pattern in _BROAD_CHECKPOINT_NOTE_PATTERNS:
        match = pattern.search(normalized)
        if match is None:
            continue
        examples.append(
            {
                "phrase": match.group(0),
                "preferred": "[updated] offer and founder-call research",
            }
        )
    return examples


def _operator_language_severity(*, leakage_count: int, checkpoint_count: int) -> str:
    total = leakage_count + checkpoint_count
    if total == 0:
        return "none"
    if total == 1:
        return "low"
    if total <= 3:
        return "medium"
    return "high"


def _is_allowed_technical_detail_line(line: str) -> bool:
    normalized = line.lower()
    return normalized.startswith(("technical detail:", "technical details:", "exact command:"))


def _short_excerpt(line: str, start: int, end: int) -> str:
    prefix_start = max(0, start - 60)
    suffix_end = min(len(line), end + 60)
    prefix = "..." if prefix_start > 0 else ""
    suffix = "..." if suffix_end < len(line) else ""
    return f"{prefix}{line[prefix_start:suffix_end]}{suffix}"


def _normalize_unknown_command_line(line: str) -> str:
    normalized = line.lower().strip()
    normalized = re.sub(r"^[>\-\*\s]+", "", normalized)
    normalized = normalized.replace("`", "").replace('"', "").replace("'", "")
    normalized = normalized.replace("\u2014", "-").replace("\u2013", "-")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _is_unknown_command_contextual_guidance(line: str) -> bool:
    if "?" in line and any(
        marker in line
        for marker in (
            "did you see",
            "do you see",
            "have you seen",
            "saw",
            "was it",
            "whether",
            "which symptom",
            "what symptom",
        )
    ):
        return True
    if re.search(r"\bif\b.+\bunknown command\b", line):
        return True
    if re.search(r"\bunknown command\b.+\b(if|then|run|repair|fix|use)\b", line):
        return True
    return any(
        marker in line
        for marker in (
            "diagnostic option",
            "possible symptom",
            "symptom option",
            "quoted symptom",
            "example symptom",
        )
    )


def _is_raw_unknown_command_output(line: str) -> bool:
    return (
        re.fullmatch(r"(error:\s*)?unknown command:?\s*/[a-z0-9-]+(?:[.!?].*)?", line) is not None
    )


def _is_observed_unknown_command_line(line: str) -> bool:
    if any(
        marker in line
        for marker in (
            "false positive",
            "not a discovery failure",
            "not an actual failure",
            "not a skill discovery failure",
        )
    ):
        return False
    if any(
        marker in line
        for marker in (
            "final diagnosis",
            "actual failure",
            "observed runtime",
            "runtime output",
            "discovery failure",
            "skill discovery failure",
            "symptom confirmed",
        )
    ):
        return True
    if re.search(
        r"\b(claude|runtime|slash command|/mb-start|mb-start)\b"
        r".{0,80}\b(reported|returned|emitted|showed|failed with)\b"
        r".{0,40}\bunknown command\b",
        line,
    ):
        return True
    return (
        re.search(
            r"\bunknown command\b.{0,40}\b"
            r"(reported|returned|emitted|showed|observed|confirmed)\b",
            line,
        )
        is not None
    )


def _keyword_matches(text: str, keyword: str) -> bool:
    normalized = keyword.lower().strip()
    if not normalized:
        return False
    if normalized[0].isalnum() and normalized[-1].isalnum():
        pattern = rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])"
        return re.search(pattern, text) is not None
    return normalized in text


def _list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"manifest field {key} must be a list")
    return [item for item in value if isinstance(item, dict)]


def _str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"manifest field {key} must be a list")
    return [str(item) for item in value if str(item).strip()]


def _required_str(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key, "")).strip()
    if not value:
        raise ValueError(f"manifest item missing required field {key}")
    return value
