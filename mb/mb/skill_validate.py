"""Validate bundled Main Branch skills.

This is structural validation only: frontmatter shape, local file references,
and the SKILL.md line-count gate. It deliberately does not judge whether the
skill accomplishes its workflow purpose.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mb import engine
from mb.validate import _check_one, _read_frontmatter

MAX_SKILL_LINES = 500
SKILL_SCHEMA: dict[str, Any] = {
    "glob": "SKILL.md",
    "required": ["name", "description"],
    "enums": {},
}

_INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_REFERENCE_DEF_RE = re.compile(r"^\s*\[[^\]\n]+\]:\s*(\S+)", re.MULTILINE)
_BARE_SKILL_REF_RE = re.compile(
    r"(?<![\w./(-])((?:\.\/)?(?:references|examples|scripts|assets)/[^\s`()\[\]<>,]+)"
)


def _clean_reference(raw: str) -> str | None:
    target = raw.strip()
    if not target:
        return None
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split()[0]
    target = target.strip().strip("'\"")
    if not target or target.startswith("#"):
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    return target.split("#", 1)[0].split("?", 1)[0].strip()


def _iter_references(text: str) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()

    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in _INLINE_LINK_RE.finditer(line):
            target = _clean_reference(match.group(1))
            if target:
                key = (line_number, target)
                if key not in seen:
                    refs.append({"line": line_number, "target": target, "source": "markdown-link"})
                    seen.add(key)
        for match in _BARE_SKILL_REF_RE.finditer(line):
            target = _clean_reference(match.group(1))
            if target:
                key = (line_number, target)
                if key not in seen:
                    refs.append({"line": line_number, "target": target, "source": "bare-path"})
                    seen.add(key)

    for match in _REFERENCE_DEF_RE.finditer(text):
        target = _clean_reference(match.group(1))
        if target:
            line_number = text.count("\n", 0, match.start()) + 1
            key = (line_number, target)
            if key not in seen:
                refs.append({"line": line_number, "target": target, "source": "reference-def"})
                seen.add(key)

    return refs


def _resolve_reference(skill_root: Path, target: str) -> tuple[Path | None, str | None]:
    normalized = target[2:] if target.startswith("./") else target
    if normalized.startswith("~") or Path(normalized).is_absolute():
        return None, f"{target!r} is an absolute/local machine path"
    candidate = (skill_root / normalized).resolve()
    try:
        candidate.relative_to(skill_root.resolve())
    except ValueError:
        return None, f"{target!r} resolves outside the skill directory"
    return candidate, None


def _check_references(skill_root: Path, text: str) -> list[str]:
    errors: list[str] = []
    for ref in _iter_references(text):
        target = str(ref["target"])
        candidate, err = _resolve_reference(skill_root, target)
        if err is not None:
            errors.append(f"line {ref['line']}: {err}")
            continue
        assert candidate is not None
        matches = (
            sorted(candidate.parent.glob(candidate.name)) if any(c in target for c in "*?[") else []
        )
        exists = bool(matches) if matches else candidate.exists()
        if not exists:
            errors.append(f"line {ref['line']}: {target!r} does not exist")
    return errors


def _validate_skill_at(name: str, skill_root: Path) -> dict[str, Any]:
    skill_file = skill_root / "SKILL.md"
    errors: list[str] = []
    warnings: list[str] = []
    line_count = 0

    if not skill_file.is_file():
        errors.append("missing SKILL.md")
        return {
            "ok": False,
            "name": name,
            "path": str(skill_root),
            "files": [
                {
                    "path": "SKILL.md",
                    "schema": "skill",
                    "ok": False,
                    "errors": errors,
                    "warnings": warnings,
                }
            ],
            "summary": {"errors": len(errors), "warnings": 0, "line_count": 0},
        }

    text = skill_file.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    frontmatter_result = _check_one(skill_file, SKILL_SCHEMA)
    errors.extend(frontmatter_result["errors"])

    fm, fm_err = _read_frontmatter(skill_file)
    if fm_err is None and fm is not None:
        skill_name = fm.get("name")
        description = fm.get("description")
        if not isinstance(skill_name, str) or not skill_name.strip():
            errors.append("name must be a non-empty string")
        elif skill_name != name:
            errors.append(f"name={skill_name!r} does not match skill directory {name!r}")
        if not isinstance(description, str) or not description.strip():
            errors.append("description must be a non-empty string")

    if line_count > MAX_SKILL_LINES:
        errors.append(f"SKILL.md has {line_count} lines; limit is {MAX_SKILL_LINES}")

    errors.extend(_check_references(skill_root, text))

    file_result = {
        "path": "SKILL.md",
        "schema": "skill",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "line_count": line_count,
    }
    return {
        "ok": not errors,
        "name": name,
        "path": str(skill_root),
        "files": [file_result],
        "summary": {"errors": len(errors), "warnings": len(warnings), "line_count": line_count},
    }


def run(name: str) -> dict[str, Any] | None:
    """Validate one bundled skill by name."""
    skill_root = engine.skill_path(name)
    if skill_root is None:
        return None
    return _validate_skill_at(name, skill_root)


def envelope(skill_reports: list[dict[str, Any]], *, mode: str) -> dict[str, Any]:
    """Return the deterministic JSON envelope shared by CLI, doctor, and CI."""
    failed = [report for report in skill_reports if not report["ok"]]
    errors = sum(int(report["summary"]["errors"]) for report in skill_reports)
    warnings = sum(int(report["summary"]["warnings"]) for report in skill_reports)
    return {
        "ok": not failed,
        "command": "mb skill validate",
        "mode": mode,
        "skills": skill_reports,
        "summary": {
            "skills": len(skill_reports),
            "passed": len(skill_reports) - len(failed),
            "failed": len(failed),
            "errors": errors,
            "warnings": warnings,
        },
    }


def run_all() -> dict[str, Any]:
    """Validate every bundled skill."""
    reports = []
    for name in engine.bundled_skills():
        report = run(name)
        if report is not None:
            reports.append(report)
    result = envelope(reports, mode="all")
    if not reports:
        result["ok"] = False
        result["summary"]["errors"] = 1
        result["errors"] = ["no bundled skills found"]
    return result


def render_human(report: dict[str, Any]) -> None:
    """Print skill validation results to stdout."""
    from rich.console import Console

    console = Console()
    console.print("\n[bold]mb skill validate[/bold]\n")
    for skill in report["skills"]:
        mark = "[green]ok[/green]" if skill["ok"] else "[red]fail[/red]"
        console.print(f"  {mark}  {skill['name']} ({skill['summary']['line_count']} lines)")
        for file_result in skill["files"]:
            for error in file_result["errors"]:
                console.print(f"        - {error}")
            for warning in file_result.get("warnings", []):
                console.print(f"        - {warning}")
    console.print()
    summary = report["summary"]
    if report["ok"]:
        console.print(f"[green]{summary['passed']} skill(s) validated.[/green]")
    else:
        console.print(
            f"[red]{summary['failed']} skill(s) failed with {summary['errors']} error(s).[/red]"
        )
