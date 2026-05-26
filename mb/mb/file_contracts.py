"""Business-file contracts and guided route findings.

This module keeps owner-facing business file shape checks separate from
frontmatter schema validation. Frontmatter answers whether a record is
machine-readable; file contracts answer whether a file gives the operator and
agent enough business context to use the right workflow.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class SectionContract:
    id: str
    label: str
    purpose: str
    aliases: tuple[str, ...]
    signals: tuple[str, ...]
    missing_message: str
    empty_message: str


@dataclass(frozen=True)
class FileContract:
    id: str
    label: str
    glob: str
    purpose: str
    primitive: str
    lifecycle: tuple[str, ...]
    privacy_boundary: str
    required_frontmatter: tuple[str, ...]
    required_sections: tuple[SectionContract, ...]
    optional_sections: tuple[str, ...]
    validation_severity: str
    recommended_route: str
    route_reason: str
    approval_rule: str
    enforcement: str
    example_path: str


OFFER_SECTIONS = (
    SectionContract(
        id="audience",
        label="Who this is for",
        purpose="Name the buyer and the progress they want.",
        aliases=("audience", "who this is for", "buyer", "customer", "customer progress"),
        signals=("audience", "buyer", "customer", "founder", "operator", "who this is for"),
        missing_message="Your offer does not yet say who it is for.",
        empty_message="Your offer has an audience section, but it is still empty.",
    ),
    SectionContract(
        id="promise",
        label="Promise or transformation",
        purpose="State the outcome the offer helps create.",
        aliases=("promise", "transformation", "outcome", "result", "before after"),
        signals=("promise", "transformation", "outcome", "result", "before", "after"),
        missing_message="Your offer does not yet state the promised outcome.",
        empty_message="Your offer has a promise section, but it does not say the outcome yet.",
    ),
    SectionContract(
        id="mechanism",
        label="Mechanism",
        purpose="Explain how the offer creates the result.",
        aliases=("mechanism", "method", "how it works", "process", "delivery"),
        signals=("mechanism", "method", "how it works", "process", "delivery", "workflow"),
        missing_message="Your offer does not yet explain how the result happens.",
        empty_message="Your offer has a mechanism section, but it is still empty.",
    ),
    SectionContract(
        id="proof",
        label="Proof",
        purpose="Point to evidence, outcomes, testimonials, or typicality context.",
        aliases=("proof", "evidence", "testimonials", "case studies", "typicality"),
        signals=("proof", "evidence", "testimonial", "case study", "typicality", "outcome"),
        missing_message="Your offer does not yet point to proof or outcome evidence.",
        empty_message="Your offer has a proof section, but it does not name usable evidence yet.",
    ),
    SectionContract(
        id="price_value",
        label="Price or value",
        purpose="Make the exchange legible enough for sales-path decisions.",
        aliases=("pricing", "price", "investment", "value", "offer stack"),
        signals=("pricing", "price", "investment", "value", "$", "offer stack"),
        missing_message="Your offer does not yet make the price or value exchange clear.",
        empty_message="Your offer has a price/value section, but the exchange is still empty.",
    ),
    SectionContract(
        id="next_step",
        label="Next step",
        purpose="Name what a qualified buyer should do next.",
        aliases=("next step", "cta", "call to action", "apply", "book", "buy"),
        signals=("next step", "cta", "call to action", "apply", "book", "buy", "join"),
        missing_message="Your offer does not yet tell a qualified buyer what to do next.",
        empty_message="Your offer has a next-step section, but the action is still empty.",
    ),
)

CONTRACTS: tuple[FileContract, ...] = (
    FileContract(
        id="offer",
        label="Offer",
        glob="core/offer.md, core/offers/*/offer.md",
        purpose=(
            "Durable truth for what the business sells, who it helps, why it is "
            "credible, and what a buyer should do next."
        ),
        primitive="core",
        lifecycle=("draft", "running", "scaling", "retired"),
        privacy_boundary="Public-safe offer claims only; keep private customer details out.",
        required_frontmatter=("slug and status for per-offer files",),
        required_sections=OFFER_SECTIONS,
        optional_sections=(
            "qualification",
            "deliverables",
            "objections",
            "guarantee or risk reversal",
            "positioning notes",
        ),
        validation_severity="warn",
        recommended_route="mb-think",
        route_reason="Use mb-think to sharpen offer truth before ads, site, or organic work.",
        approval_rule="Ask before editing offer files or changing durable claims.",
        enforcement="active",
        example_path="core/offer.md",
    ),
)

DEFERRED_CONTRACTS: tuple[dict[str, Any], ...] = (
    {
        "id": "audience",
        "paths": ["core/audience.md", "core/offers/<slug>/audience.md"],
        "route": "mb-think",
        "status": "specified_deferred",
    },
    {
        "id": "proof",
        "paths": ["core/proof/", "core/offers/<slug>/proof/"],
        "route": "mb-think",
        "status": "specified_deferred",
    },
    {
        "id": "content_strategy",
        "paths": ["core/content-strategy.md", "core/marketing/**"],
        "route": "mb-organic",
        "status": "specified_deferred",
    },
    {
        "id": "decision",
        "paths": ["decisions/*.md"],
        "route": "mb-think",
        "status": "specified_deferred",
    },
    {
        "id": "research",
        "paths": ["research/*.md"],
        "route": "mb-think",
        "status": "specified_deferred",
    },
    {
        "id": "bet",
        "paths": ["bets/*.md"],
        "route": "mb-bet",
        "status": "specified_deferred",
    },
    {
        "id": "push",
        "paths": ["pushes/<date-slug>/push.md"],
        "route": "mb-start",
        "status": "specified_deferred",
    },
    {
        "id": "playbook_run",
        "paths": ["pushes/<date-slug>/playbooks/*.md"],
        "route": "mb-ads or owning workflow",
        "status": "specified_deferred",
    },
    {
        "id": "log",
        "paths": ["log/*.md"],
        "route": "mb-end",
        "status": "specified_deferred",
    },
    {
        "id": "document",
        "paths": ["documents/*.md"],
        "route": "mb-think",
        "status": "specified_deferred",
    },
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
WORD_RE = re.compile(r"[A-Za-z0-9]+")


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return text
    return text[end + len("\n---") :]


def _read_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}
    try:
        parsed = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_heading(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _section_blocks(body: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(body))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = _normalize_heading(match.group(2))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        blocks[title] = body[start:end].strip()
    return blocks


def _word_count(value: str) -> int:
    return len(WORD_RE.findall(value))


def _body_has_signal(body: str, signals: tuple[str, ...]) -> bool:
    lowered = body.lower()
    return any(signal.lower() in lowered for signal in signals)


def _contract_paths(repo: Path, contract: FileContract) -> list[Path]:
    if contract.id == "offer":
        paths = [repo / "core" / "offer.md"]
        paths.extend(sorted((repo / "core" / "offers").glob("*/offer.md")))
        return [path for path in paths if path.is_file()]
    return []


def _finding(
    *,
    contract: FileContract,
    path: Path,
    repo: Path,
    code: str,
    section: SectionContract,
    message: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "code": code,
        "contract_id": contract.id,
        "contract_label": contract.label,
        "path": path.relative_to(repo).as_posix(),
        "section": section.id,
        "section_label": section.label,
        "severity": contract.validation_severity,
        "state": "needs_review",
        "message": message,
        "owner_message": message,
        "detail": detail,
        "recommended_route": contract.recommended_route,
        "route_reason": contract.route_reason,
        "approval_required": True,
        "approval_rule": contract.approval_rule,
        "repair": f"Use `{contract.recommended_route}` to fill this before downstream work.",
        "safe_to_share": True,
    }


def _evaluate_offer(repo: Path, contract: FileContract, path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        rel = path.relative_to(repo).as_posix()
        return [
            {
                "schema_version": SCHEMA_VERSION,
                "code": "file_contract_unreadable",
                "contract_id": contract.id,
                "contract_label": contract.label,
                "path": rel,
                "section": "",
                "section_label": "",
                "severity": "error",
                "state": "blocked",
                "message": f"Main Branch could not read {rel}.",
                "owner_message": f"Main Branch could not read {rel}.",
                "detail": str(exc),
                "recommended_route": "mb-start",
                "route_reason": "Repair file access before business routing.",
                "approval_required": False,
                "approval_rule": "",
                "repair": "Check file permissions and rerun `mb validate --json`.",
                "safe_to_share": True,
            }
        ]
    body = _strip_frontmatter(text)
    headings = _section_blocks(body)
    findings: list[dict[str, Any]] = []
    for section in contract.required_sections:
        matched_content = ""
        matched_heading = False
        for alias in section.aliases:
            normalized = _normalize_heading(alias)
            if normalized in headings:
                matched_heading = True
                matched_content = headings[normalized]
                break
        if matched_heading:
            if _word_count(matched_content) < 4:
                findings.append(
                    _finding(
                        contract=contract,
                        path=path,
                        repo=repo,
                        code="file_contract_empty_section",
                        section=section,
                        message=section.empty_message,
                        detail=f"Section `{section.label}` needs enough detail to route work.",
                    )
                )
            continue
        if _body_has_signal(body, section.signals):
            continue
        findings.append(
            _finding(
                contract=contract,
                path=path,
                repo=repo,
                code="file_contract_missing_section",
                section=section,
                message=section.missing_message,
                detail=f"Expected business shape: {section.purpose}",
            )
        )
    return findings


def evaluate(repo: Path | str) -> dict[str, Any]:
    """Return file-contract findings for a business repo."""
    root = Path(repo).resolve()
    findings: list[dict[str, Any]] = []
    evaluated_contracts: list[dict[str, Any]] = []
    for contract in CONTRACTS:
        paths = _contract_paths(root, contract)
        evaluated_contracts.append(
            {
                "id": contract.id,
                "label": contract.label,
                "enforcement": contract.enforcement,
                "paths": [path.relative_to(root).as_posix() for path in paths],
                "recommended_route": contract.recommended_route,
                "validation_severity": contract.validation_severity,
                "safe_to_share": True,
            }
        )
        if contract.enforcement != "active":
            continue
        for path in paths:
            if contract.id == "offer":
                findings.extend(_evaluate_offer(root, contract, path))
    route_counts: dict[str, int] = {}
    contract_counts: dict[str, int] = {}
    for finding in findings:
        route = str(finding.get("recommended_route") or "")
        contract_id = str(finding.get("contract_id") or "")
        if route:
            route_counts[route] = route_counts.get(route, 0) + 1
        if contract_id:
            contract_counts[contract_id] = contract_counts.get(contract_id, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not findings,
        "summary": {
            "active_contracts": len(CONTRACTS),
            "deferred_contracts": len(DEFERRED_CONTRACTS),
            "findings": len(findings),
            "routes": route_counts,
            "contracts": contract_counts,
        },
        "contracts": evaluated_contracts,
        "deferred_contracts": list(DEFERRED_CONTRACTS),
        "findings": findings,
        "safe_to_share": True,
    }


def registry_payload() -> dict[str, Any]:
    """Return the public contract registry shape for docs and JSON consumers."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contracts": [
            {
                "id": contract.id,
                "label": contract.label,
                "glob": contract.glob,
                "purpose": contract.purpose,
                "primitive": contract.primitive,
                "lifecycle": list(contract.lifecycle),
                "privacy_boundary": contract.privacy_boundary,
                "required_frontmatter": list(contract.required_frontmatter),
                "required_sections": [
                    {
                        "id": section.id,
                        "label": section.label,
                        "purpose": section.purpose,
                    }
                    for section in contract.required_sections
                ],
                "optional_sections": list(contract.optional_sections),
                "validation_severity": contract.validation_severity,
                "recommended_route": contract.recommended_route,
                "route_reason": contract.route_reason,
                "approval_rule": contract.approval_rule,
                "enforcement": contract.enforcement,
                "example_path": contract.example_path,
            }
            for contract in CONTRACTS
        ],
        "deferred_contracts": list(DEFERRED_CONTRACTS),
        "safe_to_share": True,
    }
