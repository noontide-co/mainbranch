"""Dry-run gate for `/ads` compliance copy changes."""

from __future__ import annotations

import argparse
import difflib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SEVERITIES = ("P2", "P3")


@dataclass(frozen=True)
class ProposedChange:
    severity: str
    item_ref: str
    issue: str
    evidence: str
    fix: str
    rule: str


@dataclass(frozen=True)
class AppliedChange:
    change: ProposedChange
    count: int


@dataclass(frozen=True)
class SkippedChange:
    change: ProposedChange
    reason: str
    count: int


@dataclass(frozen=True)
class PlannedReplacement:
    change: ProposedChange
    start: int
    end: int


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _findings_from_payload(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        findings = payload.get("findings", [])
        if isinstance(findings, list):
            return [item for item in findings if isinstance(item, dict)]
    raise ValueError("Findings JSON must be a list or an object with a `findings` list.")


def load_proposed_changes(
    findings_path: Path,
    *,
    severities: tuple[str, ...] = DEFAULT_SEVERITIES,
) -> list[ProposedChange]:
    """Load compliance findings that are eligible for human-approved replacement."""

    payload = json.loads(findings_path.read_text(encoding="utf-8"))
    allowed = {severity.upper() for severity in severities}
    changes: list[ProposedChange] = []

    for finding in _findings_from_payload(payload):
        severity = _as_text(finding.get("severity")).upper()
        evidence = _as_text(finding.get("evidence"))
        fix = _as_text(finding.get("fix"))
        if severity not in allowed or not evidence or not fix:
            continue
        changes.append(
            ProposedChange(
                severity=severity,
                item_ref=_as_text(finding.get("item_ref")),
                issue=_as_text(finding.get("issue")),
                evidence=evidence,
                fix=fix,
                rule=_as_text(finding.get("rule")),
            )
        )

    return changes


def _find_offsets(source_text: str, evidence: str) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = source_text.find(evidence, start)
        if offset == -1:
            return offsets
        offsets.append(offset)
        start = offset + len(evidence)


def _plan_replacements(
    source_text: str, changes: list[ProposedChange]
) -> tuple[list[PlannedReplacement], list[SkippedChange]]:
    replacements: list[PlannedReplacement] = []
    skipped: list[SkippedChange] = []

    for change in changes:
        offsets = _find_offsets(source_text, change.evidence)
        if not offsets:
            skipped.append(
                SkippedChange(
                    change=change,
                    reason="evidence not found in original source",
                    count=0,
                )
            )
            continue
        if len(offsets) > 1:
            skipped.append(
                SkippedChange(
                    change=change,
                    reason="evidence matched multiple locations; refusing ambiguous rewrite",
                    count=len(offsets),
                )
            )
            continue

        start = offsets[0]
        replacements.append(
            PlannedReplacement(
                change=change,
                start=start,
                end=start + len(change.evidence),
            )
        )

    return _without_overlaps(replacements, skipped)


def _without_overlaps(
    replacements: list[PlannedReplacement], skipped: list[SkippedChange]
) -> tuple[list[PlannedReplacement], list[SkippedChange]]:
    safe: list[PlannedReplacement] = []
    last_end = -1

    for replacement in sorted(replacements, key=lambda item: item.start):
        if replacement.start < last_end:
            skipped.append(
                SkippedChange(
                    change=replacement.change,
                    reason="evidence overlaps another proposed rewrite",
                    count=1,
                )
            )
            continue
        safe.append(replacement)
        last_end = replacement.end

    return safe, skipped


def propose_text(
    source_text: str, changes: list[ProposedChange]
) -> tuple[str, list[AppliedChange], list[SkippedChange]]:
    """Return proposed text without mutating the source file."""

    replacements, skipped = _plan_replacements(source_text, changes)
    chunks: list[str] = []
    applied: list[AppliedChange] = []
    cursor = 0

    for replacement in replacements:
        chunks.append(source_text[cursor : replacement.start])
        chunks.append(replacement.change.fix)
        cursor = replacement.end
        applied.append(AppliedChange(change=replacement.change, count=1))

    chunks.append(source_text[cursor:])
    return "".join(chunks), applied, skipped


def unified_diff(source_path: Path, original: str, proposed: str) -> str:
    """Render the exact proposed copy edits as a unified diff."""

    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=f"{source_path} (current)",
            tofile=f"{source_path} (proposed)",
        )
    )


def render_review_log(source_path: Path, applied: list[AppliedChange]) -> str:
    lines = [
        "# Ads Compliance Proposed Changes",
        "",
        f"**Source:** `{source_path}`",
        "",
        "These changes were generated by the compliance gate and require explicit approval before",
        "the source copy is rewritten.",
        "",
        "| Severity | Item | Original | Proposed | Rule |",
        "|----------|------|----------|----------|------|",
    ]

    for applied_change in applied:
        change = applied_change.change
        item_ref = _escape_table(change.item_ref)
        evidence = _escape_table(change.evidence)
        fix = _escape_table(change.fix)
        rule = _escape_table(change.rule or change.issue)
        lines.append(f"| {change.severity} | {item_ref} | {evidence} | {fix} | {rule} |")

    return "\n".join(lines) + "\n"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def _render_skipped(skipped: list[SkippedChange]) -> str:
    lines = ["Skipped findings:"]
    for item in skipped:
        ref = item.change.item_ref or item.change.evidence
        lines.append(f"- {item.change.severity} {ref}: {item.reason} ({item.count})")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show `/ads` compliance copy changes before rewriting the source file."
    )
    parser.add_argument("source", type=Path, help="Ad copy markdown file to review.")
    parser.add_argument("findings", type=Path, help="JSON findings with evidence/fix fields.")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Apply the proposed copy changes. Omit for dry-run mode.",
    )
    parser.add_argument(
        "--review-log",
        type=Path,
        help="Optional path for the proposed/applied change log.",
    )
    parser.add_argument(
        "--severity",
        action="append",
        dest="severities",
        help="Severity to include. Defaults to P2 and P3. Repeat for multiple values.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    source_path = args.source
    findings_path = args.findings
    severities = tuple(args.severities) if args.severities else DEFAULT_SEVERITIES

    original = source_path.read_text(encoding="utf-8")
    changes = load_proposed_changes(findings_path, severities=severities)
    proposed, applied, skipped = propose_text(original, changes)

    print("ADS COMPLIANCE PROPOSED CHANGES")
    print(f"Mode: {'approve' if args.approve else 'dry-run'}")
    print(f"Source: {source_path}")
    print(f"Eligible findings: {len(changes)}")
    print(f"Matched replacements: {sum(item.count for item in applied)}")
    print(f"Skipped findings: {len(skipped)}")
    print()

    if skipped:
        print(_render_skipped(skipped))
        print()

    if proposed == original:
        print("No source copy changes are proposed.")
        return 0

    print(unified_diff(source_path, original, proposed))

    if not args.approve:
        print("Dry run complete: source copy was not modified.")
        return 0

    source_path.write_text(proposed, encoding="utf-8")
    if args.review_log:
        args.review_log.write_text(render_review_log(source_path, applied), encoding="utf-8")
    print("Approved changes applied to source copy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
