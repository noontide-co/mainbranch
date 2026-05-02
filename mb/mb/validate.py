"""``mb validate`` — frontmatter and optional cross-reference checks.

Hard-coded schema per the master decision. Cross-reference validation is
opt-in because local authoring should warn by default and CI can opt into
strict mode. Per-file frontmatter errors always fail.

The schemas tolerate extras; only listed required keys are checked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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

LINK_FIELDS = (
    "linked_research",
    "linked_decision",
    "linked_decisions",
    "linked_prd",
    "linked_prds",
    "related_prds",
    "supersedes",
)

LOCAL_REF_ROOTS = {
    "campaigns",
    "core",
    "decisions",
    "docs",
    "documents",
    "log",
    "outputs",
    "reference",
    "research",
}

DECISION_STATUS_ORDER = {
    "proposed": 0,
    "running": 1,
    "accepted": 2,
    "rejected": 2,
    "superseded": 2,
}
OFFER_STATUS_ORDER = {
    "proposed": 0,
    "running": 1,
    "accepted": 1,
    "rejected": 1,
    "scaling": 2,
    "killed": 3,
    "graduated": 3,
    "died": 3,
}

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
        return {"path": str(path), "ok": False, "errors": [err], "warnings": []}
    assert fm is not None
    errors: list[str] = []
    for k in schema["required"]:
        if k not in fm:
            errors.append(f"missing key: {k}")
    for k, allowed in schema.get("enums", {}).items():
        if k in fm and fm[k] not in allowed:
            errors.append(f"{k}={fm[k]!r} not in {sorted(allowed)}")
    return {"path": str(path), "ok": not errors, "errors": errors, "warnings": []}


def _is_hidden_or_generated(path: Path, repo: Path) -> bool:
    rel_parts = path.relative_to(repo).parts
    is_bundled_data = rel_parts[:2] == ("mb", "_data") or rel_parts[:1] == ("_data",)
    return (
        any(
            part.startswith(".") or part in {"__pycache__", "node_modules", ".venv", "venv"}
            for part in rel_parts
        )
        or is_bundled_data
    )


def _iter_frontmatter_files(repo: Path) -> list[Path]:
    return [
        f
        for f in sorted(repo.rglob("*.md"))
        if f.is_file() and not _is_hidden_or_generated(f, repo)
    ]


def _coerce_refs(value: Any) -> tuple[list[str], bool]:
    if value is None:
        return [], True
    if isinstance(value, str):
        return [value], True
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)], all(
            isinstance(item, str) for item in value
        )
    return [], False


def _is_external_ref(ref: str) -> bool:
    parsed = urlparse(ref)
    if bool(parsed.scheme) or ref.startswith("#"):
        return True
    parts = Path(_clean_ref(ref)).parts
    return (
        len(parts) > 1
        and parts[0] not in {".", ".."}
        and parts[0] not in LOCAL_REF_ROOTS
        and parts[1] in LOCAL_REF_ROOTS
    )


def _clean_ref(ref: str) -> str:
    without_anchor = ref.split("#", 1)[0]
    return without_anchor.split("?", 1)[0].strip()


def _status_order_for(path: Path) -> dict[str, int] | None:
    parts = path.parts
    if "decisions" in parts:
        return DECISION_STATUS_ORDER
    if "offers" in parts or "campaigns" in parts:
        return OFFER_STATUS_ORDER
    return None


def _finding(
    *,
    code: str,
    source: Path,
    repo: Path,
    field: str,
    target: str,
    message: str,
) -> dict[str, str]:
    return {
        "code": code,
        "path": str(source.relative_to(repo)),
        "field": field,
        "target": target,
        "message": message,
    }


def _add_file_warning(
    files_by_path: dict[str, dict[str, Any]],
    *,
    repo: Path,
    source: Path,
    message: str,
) -> None:
    rel = str(source.relative_to(repo))
    if rel not in files_by_path:
        files_by_path[rel] = {
            "path": rel,
            "ok": True,
            "errors": [],
            "warnings": [],
            "schema": "cross-refs",
        }
    files_by_path[rel].setdefault("warnings", []).append(message)


def _check_status_transition(
    *,
    source: Path,
    target: Path,
    repo: Path,
    field: str,
    ref: str,
    source_fm: dict[str, Any],
    findings: list[dict[str, str]],
) -> None:
    if field != "supersedes":
        return
    source_order = _status_order_for(source.relative_to(repo))
    target_order = _status_order_for(target.relative_to(repo))
    if source_order is None or target_order is None or source_order is not target_order:
        return
    source_status = source_fm.get("status")
    target_fm, target_err = _read_frontmatter(target)
    if target_err is not None or target_fm is None:
        return
    target_status = target_fm.get("status")
    if not isinstance(source_status, str) or not isinstance(target_status, str):
        return
    if source_status not in source_order or target_status not in source_order:
        return
    if source_order[source_status] < source_order[target_status]:
        findings.append(
            _finding(
                code="status-transition",
                source=source,
                repo=repo,
                field=field,
                target=ref,
                message=(
                    f"{field} target {ref!r} is status {target_status!r}; "
                    f"source status {source_status!r} would move backward"
                ),
            )
        )


def _check_cross_refs(
    repo: Path,
    files_by_path: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    orphan_offers: list[dict[str, str]] = []

    for source in _iter_frontmatter_files(repo):
        fm, err = _read_frontmatter(source)
        if err is not None or fm is None:
            continue
        for field in LINK_FIELDS:
            if field not in fm:
                continue
            refs, valid_type = _coerce_refs(fm.get(field))
            if not valid_type:
                findings.append(
                    _finding(
                        code="invalid-link-field",
                        source=source,
                        repo=repo,
                        field=field,
                        target="",
                        message=f"{field} must be a string or list of strings",
                    )
                )
                continue
            for ref in refs:
                if _is_external_ref(ref):
                    continue
                clean_ref = _clean_ref(ref)
                if not clean_ref:
                    continue
                target = (repo / clean_ref).resolve()
                try:
                    target.relative_to(repo)
                except ValueError:
                    findings.append(
                        _finding(
                            code="target-outside-repo",
                            source=source,
                            repo=repo,
                            field=field,
                            target=ref,
                            message=f"{field} target {ref!r} resolves outside the repo",
                        )
                    )
                    continue
                if not target.exists():
                    findings.append(
                        _finding(
                            code="missing-target",
                            source=source,
                            repo=repo,
                            field=field,
                            target=ref,
                            message=f"{field} target {ref!r} does not exist",
                        )
                    )
                    continue
                _check_status_transition(
                    source=source,
                    target=target,
                    repo=repo,
                    field=field,
                    ref=ref,
                    source_fm=fm,
                    findings=findings,
                )

    offers_root = repo / "core" / "offers"
    if offers_root.exists():
        for offer_dir in sorted(p for p in offers_root.iterdir() if p.is_dir()):
            if (offer_dir / "offer.md").exists():
                continue
            rel = str(offer_dir.relative_to(repo))
            orphan_offers.append(
                {
                    "code": "orphan-offer",
                    "path": rel,
                    "field": "core/offers",
                    "target": "offer.md",
                    "message": f"{rel}/ is missing offer.md",
                }
            )

    for finding in findings:
        _add_file_warning(
            files_by_path,
            repo=repo,
            source=repo / finding["path"],
            message=finding["message"],
        )
    for finding in orphan_offers:
        rel = finding["path"]
        files_by_path.setdefault(
            rel,
            {
                "path": rel,
                "ok": True,
                "errors": [],
                "warnings": [],
                "schema": "core/offers",
            },
        )
        files_by_path[rel].setdefault("warnings", []).append(finding["message"])

    return {
        "enabled": True,
        "checked_fields": list(LINK_FIELDS),
        "warnings": findings + orphan_offers,
        "orphan_offers": orphan_offers,
    }


def run(
    path: str,
    verbose: bool = False,
    cross_refs: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """Run validation across all known schemas. Verbose adds key dumps."""
    repo = Path(path).resolve()
    files_by_path: dict[str, dict[str, Any]] = {}
    for schema_name, schema in SCHEMAS.items():
        glob = schema["glob"]
        for f in sorted(repo.glob(glob)):
            r = _check_one(f, schema)
            r["schema"] = schema_name
            r["path"] = str(f.relative_to(repo))
            files_by_path[r["path"]] = r

    cross_ref_report = {"enabled": False, "checked_fields": [], "warnings": [], "orphan_offers": []}
    if cross_refs:
        cross_ref_report = _check_cross_refs(repo, files_by_path)

    files = list(files_by_path.values())
    warning_count = sum(len(f.get("warnings", [])) for f in files)
    error_count = sum(len(f.get("errors", [])) for f in files)
    ok = error_count == 0 and (warning_count == 0 or not strict)
    if strict:
        for file_result in files:
            if file_result.get("warnings"):
                file_result["ok"] = False
    return {
        "ok": ok,
        "files": files,
        "repo": str(repo),
        "strict": strict,
        "cross_refs": cross_ref_report,
        "summary": {"errors": error_count, "warnings": warning_count},
    }


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
            if f["errors"]:
                mark = "[red]fail[/red]"
            elif f.get("warnings"):
                mark = "[yellow]warn[/yellow]"
            else:
                mark = "[green]ok[/green]"
            console.print(f"  {mark}  {f['path']}")
            if f["errors"] or f.get("warnings") or verbose:
                for e in f["errors"]:
                    console.print(f"        - {e}")
                for warning in f.get("warnings", []):
                    console.print(f"        - {warning}")
    console.print()
    if report["ok"]:
        if report["summary"]["warnings"]:
            console.print(
                f"[yellow]{report['summary']['warnings']} warning(s) found; "
                "use --strict to fail on warnings.[/yellow]"
            )
        else:
            console.print("[green]all metadata looks right.[/green]")
    else:
        if report["summary"]["errors"]:
            bad = sum(1 for f in report["files"] if f["errors"])
            console.print(f"[red]{bad} file(s) need fixing — see above.[/red]")
        else:
            console.print(
                f"[red]{report['summary']['warnings']} warning(s) fail in strict mode.[/red]"
            )
