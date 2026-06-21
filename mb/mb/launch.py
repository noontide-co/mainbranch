"""Read-only launch readiness summary checks."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from mb import site as site_mod

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".mb",
    ".mainbranch",
    ".next",
    "dist",
    "node_modules",
}
SOURCE_SUFFIXES = {
    ".astro",
    ".js",
    ".jsx",
    ".liquid",
    ".mdx",
    ".mjs",
    ".ts",
    ".tsx",
    ".vue",
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _existing(root: Path, candidates: Iterable[str]) -> list[str]:
    found: list[str] = []
    for value in candidates:
        if (root / value).exists():
            found.append(value)
    return found


def _package_json(repo: Path) -> dict[str, Any]:
    return _read_json(repo / "package.json")


def _package_deps(package: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            names.update(str(name) for name in value)
    return names


def _package_scripts(package: dict[str, Any]) -> dict[str, str]:
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def _source_files(repo: Path, *, limit: int = 200) -> list[Path]:
    files: list[Path] = []
    for path in repo.rglob("*"):
        if len(files) >= limit:
            break
        try:
            rel_parts = path.relative_to(repo).parts
        except ValueError:
            continue
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
        if path.is_file() and path.suffix in SOURCE_SUFFIXES:
            files.append(path)
    return sorted(files)


def _source_marker_files(repo: Path, markers: Iterable[str], *, limit: int = 10) -> list[str]:
    lowered_markers = [marker.lower() for marker in markers]
    found: list[str] = []
    for path in _source_files(repo):
        text = _read_text(path).lower()
        if any(marker in text for marker in lowered_markers):
            found.append(_relative(repo, path))
            if len(found) >= limit:
                break
    return found


def _stack_facts(repo: Path) -> dict[str, Any]:
    package = _package_json(repo)
    deps = _package_deps(package)
    scripts = _package_scripts(package)
    config_files = _existing(
        repo,
        [
            "astro.config.mjs",
            "astro.config.js",
            "astro.config.ts",
            "vite.config.mjs",
            "vite.config.js",
            "vite.config.ts",
            "next.config.js",
            "next.config.mjs",
            "wrangler.toml",
            "wrangler.json",
            "wrangler.jsonc",
            "netlify.toml",
            "vercel.json",
        ],
    )
    frameworks: list[str] = []
    if "astro" in deps or any(path.startswith("astro.config.") for path in config_files):
        frameworks.append("astro")
    if "@shopify/hydrogen" in deps:
        frameworks.append("hydrogen")
    if "next" in deps or any(path.startswith("next.config.") for path in config_files):
        frameworks.append("next")
    if "vite" in deps or any(path.startswith("vite.config.") for path in config_files):
        frameworks.append("vite")
    if not frameworks and package:
        frameworks.append("node")

    package_manager = "unknown"
    for lockfile, name in (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("package-lock.json", "npm"),
    ):
        if (repo / lockfile).exists():
            package_manager = name
            break

    launch_scripts = {
        name: command
        for name, command in scripts.items()
        if any(token in name.lower() for token in ("build", "check", "test", "smoke", "deploy"))
    }
    return {
        "frameworks": frameworks,
        "package_manager": package_manager,
        "package_json": bool(package),
        "config_files": config_files,
        "scripts": launch_scripts,
    }


def _deploy_facts(repo: Path, deps: set[str], scripts: dict[str, str]) -> dict[str, Any]:
    cloudflare_files = _existing(
        repo,
        [
            "wrangler.toml",
            "wrangler.json",
            "wrangler.jsonc",
            "_headers",
            "_redirects",
        ],
    )
    functions_present = (repo / "functions").is_dir()
    workers_present = (repo / "workers").is_dir() or (repo / "worker").is_dir()
    script_text = "\n".join(scripts.values()).lower()
    cloudflare = bool(
        cloudflare_files
        or functions_present
        or workers_present
        or "wrangler" in deps
        or "wrangler" in script_text
        or "pages deploy" in script_text
    )
    return {
        "cloudflare": cloudflare,
        "config_files": cloudflare_files,
        "functions_dir": functions_present,
        "workers_dir": workers_present,
        "wrangler_dependency": "wrangler" in deps,
        "deploy_scripts": {
            name: command
            for name, command in scripts.items()
            if any(token in command.lower() for token in ("wrangler", "pages deploy", "shopify"))
        },
    }


def _commerce_facts(repo: Path, deps: set[str]) -> dict[str, Any]:
    liquid_files = sorted(
        _relative(repo, path)
        for path in repo.rglob("*.liquid")
        if not any(part in EXCLUDED_DIRS for part in path.relative_to(repo).parts)
    )
    shopify_files = _existing(
        repo,
        [
            "config/settings_schema.json",
            "shopify.theme.toml",
            ".shopifyignore",
        ],
    )
    platforms: list[str] = []
    if liquid_files or shopify_files or "@shopify/hydrogen" in deps or "shopify" in deps:
        platforms.append("shopify")
    return {
        "platforms": platforms,
        "shopify": "shopify" in platforms,
        "liquid_files": liquid_files[:25],
        "liquid_file_count": len(liquid_files),
        "config_files": shopify_files,
    }


def _email_facts(repo: Path, deps: set[str]) -> dict[str, Any]:
    marker_files = _source_marker_files(
        repo,
        ["resend", "RESEND_API_KEY", "react-email", "@react-email"],
    )
    providers: list[str] = []
    if "resend" in deps or marker_files:
        providers.append("resend")
    react_email = any(name.startswith("@react-email/") for name in deps) or "react-email" in deps
    return {
        "providers": providers,
        "resend": "resend" in providers,
        "react_email": react_email,
        "marker_files": marker_files,
    }


def _smoke_facts(package_scripts: dict[str, str]) -> dict[str, Any]:
    scripts = {
        name: command
        for name, command in package_scripts.items()
        if any(token in name.lower() for token in ("smoke", "e2e", "check", "test"))
    }
    return {
        "scripts": scripts,
        "has_smoke_script": any("smoke" in name.lower() for name in scripts),
        "has_test_script": any(
            token in name.lower() for name in scripts for token in ("test", "e2e", "check")
        ),
    }


def _site_summary(site_result: dict[str, Any]) -> dict[str, Any]:
    facts = site_result.get("facts") if isinstance(site_result, dict) else {}
    facts = facts if isinstance(facts, dict) else {}
    return {
        "state": str(site_result.get("state") or ""),
        "ok": bool(site_result.get("ok")),
        "summary": str(site_result.get("summary") or ""),
        "blocked_count": len(site_result.get("blocked") or []),
        "manual_count": len(site_result.get("manual") or []),
        "instrumentation": facts.get("instrumentation") or {},
        "provider_state": facts.get("provider_state") or {},
    }


def _checks(
    *,
    stack: dict[str, Any],
    deploy: dict[str, Any],
    commerce: dict[str, Any],
    email: dict[str, Any],
    smoke: dict[str, Any],
    site_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    frameworks = stack.get("frameworks") or []
    checks.append(
        {
            "kind": "app_stack",
            "state": "passed" if frameworks else "manual",
            "summary": (
                f"Detected app stack: {', '.join(frameworks)}."
                if frameworks
                else "No app framework was detected from local config."
            ),
            "evidence": stack.get("config_files") or [],
        }
    )
    checks.append(
        {
            "kind": "deploy_rail",
            "state": "passed" if deploy.get("cloudflare") else "manual",
            "summary": (
                "Cloudflare/Wrangler deploy rail is detectable."
                if deploy.get("cloudflare")
                else "No Cloudflare/Wrangler deploy rail was detected."
            ),
            "evidence": deploy.get("config_files") or [],
        }
    )
    platforms = commerce.get("platforms") or []
    checks.append(
        {
            "kind": "commerce_rail",
            "state": "passed" if platforms else "missing",
            "summary": (
                f"Detected commerce platform: {', '.join(platforms)}."
                if platforms
                else "No commerce platform was detected from local files."
            ),
            "evidence": commerce.get("config_files") or commerce.get("liquid_files") or [],
        }
    )
    providers = email.get("providers") or []
    checks.append(
        {
            "kind": "email_rail",
            "state": "manual" if providers else "missing",
            "summary": (
                f"Detected email provider code: {', '.join(providers)}; "
                "delivery truth still needs a smoke/export."
                if providers
                else "No email delivery provider was detected from local files."
            ),
            "evidence": email.get("marker_files") or [],
        }
    )
    site_state = str(site_summary.get("state") or "")
    if site_state in {"ready", "ready_for_operator_review", "ready_for_preview"}:
        check_state = "passed"
    elif site_state:
        check_state = "manual"
    else:
        check_state = "missing"
    checks.append(
        {
            "kind": "measurement_rail",
            "state": check_state,
            "summary": (
                f"`mb site check` reports {site_state}."
                if site_state
                else "`mb site check` was not available for this launch check."
            ),
        }
    )
    scripts = smoke.get("scripts") or {}
    checks.append(
        {
            "kind": "local_smoke_scripts",
            "state": "passed" if smoke.get("has_smoke_script") else "manual",
            "summary": (
                "Local smoke scripts are named in package.json."
                if smoke.get("has_smoke_script")
                else (
                    "No explicit smoke script was found; use the closest test/check "
                    "script or run the golden path manually."
                )
            ),
            "evidence": sorted(scripts),
        }
    )
    return checks


def _recommended_action(
    checks: list[dict[str, Any]],
    *,
    site_summary: dict[str, Any],
    email: dict[str, Any],
) -> str:
    site_state = str(site_summary.get("state") or "")
    instrumentation = site_summary.get("instrumentation")
    instrumentation = instrumentation if isinstance(instrumentation, dict) else {}
    conversion_surface = instrumentation.get("conversion_surface")
    conversion_surface = conversion_surface if isinstance(conversion_surface, dict) else {}
    if site_state == "blocked":
        return "Fix the blocked `mb site check` measurement items, then rerun `mb launch check`."
    if conversion_surface.get("requires_submit_or_booking_smoke"):
        return (
            "Run the form-submit or booking-link smoke and record whether a real "
            "notification/lead arrives."
        )
    if email.get("providers"):
        return (
            "Run a read-only email delivery smoke/export for the detected email "
            "provider before launch."
        )
    for check in checks:
        if check["kind"] == "deploy_rail" and check["state"] != "passed":
            return (
                "Record the deploy rail (Cloudflare/Wrangler, Shopify, or other) "
                "before launch review."
            )
    return (
        "Review the launch plan with the operator; do not publish, spend, or mutate "
        "providers without explicit approval."
    )


def check(
    site_repo: str | Path = ".",
    *,
    business_repo: str | Path | None = None,
) -> dict[str, Any]:
    """Summarize launch-readiness rails from local files only."""

    site = Path(site_repo).resolve()
    if not site.exists():
        return {
            "ok": False,
            "schema": {"name": "mainbranch.launch_readiness", "version": "1.0"},
            "site_repo": str(site),
            "business_repo": str(Path(business_repo).resolve()) if business_repo else "",
            "state": "blocked",
            "summary": "Site repo path does not exist.",
            "facts": {},
            "checks": [
                {
                    "kind": "site_repo",
                    "state": "blocked",
                    "summary": "Site repo path does not exist.",
                }
            ],
            "recommended_action": "Pass the site repo path to `mb launch check`.",
            "next_actions": ["mb launch check <site-repo> --business-repo <business-repo> --json"],
            "safe_to_share": True,
        }

    package = _package_json(site)
    deps = _package_deps(package)
    scripts = _package_scripts(package)
    stack = _stack_facts(site)
    deploy = _deploy_facts(site, deps, scripts)
    commerce = _commerce_facts(site, deps)
    email = _email_facts(site, deps)
    smoke = _smoke_facts(scripts)
    site_result = site_mod.check(site, business_repo=business_repo)
    site_summary = _site_summary(site_result)
    checks = _checks(
        stack=stack,
        deploy=deploy,
        commerce=commerce,
        email=email,
        smoke=smoke,
        site_summary=site_summary,
    )
    required_kinds = {"app_stack", "deploy_rail", "measurement_rail"}
    if all(
        check["state"] == "passed"
        for check in checks
        if str(check.get("kind") or "") in required_kinds
    ):
        state = "ready_for_operator_review"
    else:
        state = "needs_review"
    recommended = _recommended_action(checks, site_summary=site_summary, email=email)
    next_actions = [recommended]
    if site_summary.get("state") not in {"ready", "ready_for_operator_review"}:
        next_actions.append("mb site check <site-repo> --business-repo <business-repo> --json")

    return {
        "ok": True,
        "schema": {"name": "mainbranch.launch_readiness", "version": "1.0"},
        "site_repo": str(site),
        "business_repo": str(Path(business_repo).resolve()) if business_repo else "",
        "state": state,
        "summary": "Launch readiness facts were inspected from local files.",
        "facts": {
            "app_stack": stack,
            "deploy": deploy,
            "commerce": commerce,
            "email": email,
            "local_smoke": smoke,
            "measurement": site_summary,
        },
        "checks": checks,
        "recommended_action": recommended,
        "next_actions": next_actions,
        "safe_to_share": True,
    }


def render_check(result: dict[str, Any]) -> None:
    """Render a concise human launch readiness report."""

    print(f"mb launch check  {result['site_repo']}")
    print(f"state: {result['state']}")
    print(result["summary"])
    print("")
    print("checks:")
    for item in result["checks"]:
        evidence = item.get("evidence") or []
        evidence_text = f" ({', '.join(evidence[:5])})" if evidence else ""
        print(f"  {item['state']:<8} {item['kind']}: {item['summary']}{evidence_text}")
    print("")
    print(f"next: {result['recommended_action']}")
