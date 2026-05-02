"""``mb validate`` — frontmatter shape only (v0.1).

Hard-coded schema per the master decision. No cross-reference validation.
No content rules. Per-file pass/fail. Exit 1 on any fail.

The schemas tolerate extras; only listed required keys are checked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DECISION_STATUS = {"proposed", "accepted", "rejected", "superseded", "running"}
OFFER_STATUS = {
    "proposed",
    "running",
    "scaling",
    "killed",
    "graduated",
    "died",
    "accepted",
    "rejected",
}
RESEARCH_STATUS = {"complete", "in-progress", "stale"}

SCHEMAS: dict[str, dict[str, Any]] = {
    "decisions": {
        "glob": "decisions/*.md",
        "required": ["date", "status"],
        "enums": {"status": DECISION_STATUS},
    },
    "core/offers": {
        "glob": "core/offers/*/offer.md",
        "required": ["slug", "status"],
        "enums": {"status": OFFER_STATUS},
    },
    "research": {
        "glob": "research/*.md",
        "required": ["date", "topic", "source"],
        "enums": {},
    },
    "log": {
        "glob": "log/*.md",
        "required": ["date"],
        "enums": {},
    },
    "campaigns": {
        "glob": "campaigns/*/campaign.md",
        "required": ["slug", "status"],
        "enums": {"status": OFFER_STATUS},
    },
    "documents": {
        "glob": "documents/*.md",
        "required": ["title"],
        "enums": {},
    },
}


def _read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Return (frontmatter dict, error). Either may be None."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if not text.startswith("---"):
        return None, "no frontmatter"
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None, "unterminated frontmatter"
    body = text[3:end].lstrip("\n")
    try:
        data = yaml.safe_load(body) or {}
    except yaml.YAMLError as exc:
        return None, f"yaml error: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter not a mapping"
    return data, None


def _check_one(path: Path, schema: dict[str, Any]) -> dict[str, Any]:
    fm, err = _read_frontmatter(path)
    if err is not None:
        return {"path": str(path), "ok": False, "errors": [err]}
    assert fm is not None
    errors: list[str] = []
    for k in schema["required"]:
        if k not in fm:
            errors.append(f"missing key: {k}")
    for k, allowed in schema.get("enums", {}).items():
        if k in fm and fm[k] not in allowed:
            errors.append(f"{k}={fm[k]!r} not in {sorted(allowed)}")
    return {"path": str(path), "ok": not errors, "errors": errors}


def run(path: str, verbose: bool = False) -> dict[str, Any]:
    """Run validation across all known schemas. Verbose adds key dumps."""
    repo = Path(path).resolve()
    files: list[dict[str, Any]] = []
    for schema_name, schema in SCHEMAS.items():
        glob = schema["glob"]
        for f in sorted(repo.glob(glob)):
            r = _check_one(f, schema)
            r["schema"] = schema_name
            r["path"] = str(f.relative_to(repo))
            files.append(r)

    ok = all(f["ok"] for f in files)
    return {"ok": ok, "files": files, "repo": str(repo)}


def render_human(report: dict[str, Any], verbose: bool = False) -> None:
    """Print results to stdout."""
    from rich.console import Console

    console = Console()
    if not report["files"]:
        console.print("[yellow]nothing to check yet.[/yellow]")
        return
    by_schema: dict[str, list[dict[str, Any]]] = {}
    for f in report["files"]:
        by_schema.setdefault(f["schema"], []).append(f)
    for schema, items in by_schema.items():
        console.print(f"\n[bold]{schema}[/bold]")
        for f in items:
            mark = "[green]ok[/green]" if f["ok"] else "[red]fail[/red]"
            console.print(f"  {mark}  {f['path']}")
            if not f["ok"] or verbose:
                for e in f["errors"]:
                    console.print(f"        - {e}")
    console.print()
    if report["ok"]:
        console.print("[green]all metadata looks right.[/green]")
    else:
        bad = sum(1 for f in report["files"] if not f["ok"])
        console.print(f"[red]{bad} file(s) need fixing — see above.[/red]")
