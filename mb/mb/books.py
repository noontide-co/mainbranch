"""``mb books check`` — first safe books surface.

Validates Main Branch's bookkeeping contract per
``decisions/2026-05-11-mb-books-foundation.md``:

- detects ``core/finance/books.md`` and parses its frontmatter (when
  present);
- detects ``core/finance/chart-of-accounts.md`` (when present);
- verifies the configured storage mode's ignore rules so the private
  books vault stays out of the business repo's tracked content;
- warns when ledger-shaped or statement-shaped files appear in the
  business repo's tracked content (likely Class B leak);
- when ``--fixture`` is opted in and ``hledger`` is on PATH, validates a
  bundled fake journal fixture via ``hledger -f <fixture> check`` and
  reports the structured outcome;
- explains a missing ``hledger`` binary as ``info`` without breaking
  base installs.

This surface only **reads** files. It never imports or writes ledger
data. Real ledger contents under the private books vault are not read.
"""

from __future__ import annotations

import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

STATE_ORDER = {"ok": 0, "info": 1, "warn": 2, "error": 3}
AUDIENCE_VALUES = frozenset({"mechanical", "operator_decision", "informational"})

LEDGER_EXTENSIONS = (".journal", ".hledger", ".ledger", ".beancount")
STATEMENT_EXTENSIONS = (".csv", ".ofx", ".qfx", ".qbo", ".qif")
UNSAFE_EXTENSIONS = LEDGER_EXTENSIONS + STATEMENT_EXTENSIONS

VAULT_RELATIVE = Path(".mb/private")
DEFAULT_BOOKS_VAULT_RELATIVE = Path(".mb/private/books")
VAULT_IGNORE_ENTRIES = (".mb/private/", ".mb/private")
BOOKS_IGNORE_ENTRIES = (
    ".mb/private/",
    "*.journal",
    "*.hledger",
    "*.ledger",
    "*.beancount",
)

VALID_STORAGE_MODES = frozenset({"solo-local", "team-private-repo", "advanced-vault"})
NON_LOCAL_STORAGE_MODES = frozenset({"team-private-repo", "advanced-vault"})

BUNDLED_FIXTURE_NAME = "acme-fixture.journal"
DOCS_BOOKS_PATH = "docs/books.md"
GITHUB_PRIVATE_WARNING = (
    "GitHub private repos are private, not financial vaults. Anyone with repo "
    "access can read the full ledger and history. Removing a transaction later "
    "does not remove it from history."
)

# Fixture markers an operator can put in a sample journal/CSV to opt the
# file out of unsafe-path detection. See the foundation decision.
FIXTURE_MARKER_TOKENS = ("mb-fixture", "sample fixture", "not a real ledger")
FIXTURE_MARKER_BYTES = 1024


def _max_state(states: list[str]) -> str:
    if not states:
        return "ok"
    return max(states, key=lambda state: STATE_ORDER.get(state, 3))


def _finding(
    *,
    id: str,
    title: str,
    state: str,
    detail: str,
    audience: str,
    operator_summary: str,
    repair: str = "",
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    resolved_audience = audience if audience in AUDIENCE_VALUES else "operator_decision"
    return {
        "id": id,
        "title": title,
        "state": state,
        "detail": detail,
        "audience": resolved_audience,
        "operator_summary": operator_summary or detail or title,
        "repair": repair,
        "evidence": evidence or [],
    }


def _read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, f"cannot read {path}: {exc}"
    if not text.startswith("---"):
        return {}, ""
    end = text.find("\n---", 3)
    if end == -1:
        return {}, "frontmatter is not closed by a trailing '---' line"
    try:
        parsed = yaml.safe_load(text[3:end].strip()) or {}
    except yaml.YAMLError as exc:
        return {}, f"frontmatter does not parse as YAML: {exc}"
    if not isinstance(parsed, dict):
        return {}, "frontmatter is not a YAML mapping"
    return parsed, ""


def _gitignore_entries(repo: Path) -> set[str]:
    gitignore = repo / ".gitignore"
    if not gitignore.exists():
        return set()
    try:
        text = gitignore.read_text(encoding="utf-8")
    except OSError:
        return set()
    return {line.strip() for line in text.splitlines() if line.strip()}


def _run_git(repo: Path, args: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False, ""
    if proc.returncode != 0:
        return False, proc.stdout.strip()
    return True, proc.stdout.strip()


def _tracked_files(repo: Path) -> tuple[list[str], bool]:
    """Return git-tracked file paths and whether git was usable."""
    ok, stdout = _run_git(repo, ["ls-files"])
    if not ok:
        return [], False
    return [line for line in stdout.splitlines() if line], True


def _walk_files_fallback(repo: Path) -> list[str]:
    skip = {
        ".git",
        ".mb",
        ".mainbranch",
        ".claude",
        "node_modules",
        ".next",
        ".venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
    }
    out: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(repo)
        except ValueError:
            continue
        parts = rel.parts
        if any(part in skip for part in parts):
            continue
        out.append(rel.as_posix())
    return out


def _has_fixture_marker(path: Path) -> bool:
    """Return True when ``path`` carries an explicit fixture marker.

    The foundation decision allows an escape hatch from unsafe-path
    detection when a sample file is explicitly marked. Marker tokens
    are matched case-insensitively in the first ``FIXTURE_MARKER_BYTES``
    of the file. Operators can put them in a header comment so the
    same fixture file can live anywhere in the business repo.
    """
    try:
        with path.open("rb") as handle:
            head = handle.read(FIXTURE_MARKER_BYTES)
    except OSError:
        return False
    try:
        text = head.decode("utf-8", errors="ignore").lower()
    except UnicodeDecodeError:
        return False
    return any(token in text for token in FIXTURE_MARKER_TOKENS)


def _ignore_rule_present(entries: set[str]) -> bool:
    return any(entry in entries for entry in VAULT_IGNORE_ENTRIES)


def _books_ignore_missing(entries: set[str]) -> list[str]:
    missing: list[str] = []
    if not _ignore_rule_present(entries):
        missing.append(".mb/private/")
    missing.extend(
        entry
        for entry in BOOKS_IGNORE_ENTRIES
        if entry not in VAULT_IGNORE_ENTRIES and entry not in entries
    )
    return missing


def _has_books_policy(repo: Path) -> bool:
    return (repo / "core" / "finance" / "books.md").exists()


def _policy_storage_mode(fm: dict[str, Any]) -> str:
    return str(fm.get("storage_mode") or "").strip()


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _vault_info(repo: Path, fm: dict[str, Any]) -> dict[str, Any]:
    """Return sanitized private-books-vault facts.

    The report deliberately avoids printing absolute vault paths outside the
    business repo. It only stats relative paths or absolute paths that resolve
    under ``repo``. External locations are reported as configured, but the
    literal path is not included.
    """
    storage_mode = _policy_storage_mode(fm)
    raw_location = str(fm.get("vault_location") or "").strip()
    defaulted = False
    if not raw_location and storage_mode not in NON_LOCAL_STORAGE_MODES:
        raw_location = DEFAULT_BOOKS_VAULT_RELATIVE.as_posix()
        defaulted = True

    if storage_mode in NON_LOCAL_STORAGE_MODES:
        configured = bool(raw_location)
        return {
            "storage_mode": storage_mode,
            "configured": configured,
            "defaulted": False,
            "location": (
                "configured external private books repo"
                if storage_mode == "team-private-repo" and configured
                else "configured external private books vault"
                if configured
                else "not configured"
            ),
            "location_kind": "external",
            "local_path": "",
            "exists": None,
            "journal_placeholder": "not_checked",
        }

    candidate = Path(raw_location)
    repo_resolved = repo.resolve()
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            rel = resolved.relative_to(repo_resolved)
        except ValueError:
            return {
                "storage_mode": storage_mode,
                "configured": True,
                "defaulted": defaulted,
                "location": "external private path",
                "location_kind": "external",
                "local_path": "",
                "exists": None,
                "journal_placeholder": "not_checked",
            }
        local_path = repo / rel
        display = rel.as_posix()
    else:
        local_path = repo / candidate
        display = candidate.as_posix().rstrip("/") or "."

    exists = local_path.exists()
    journal = local_path / "main.journal"
    return {
        "storage_mode": storage_mode,
        "configured": True,
        "defaulted": defaulted,
        "location": display,
        "location_kind": "repo_relative",
        "local_path": display,
        "exists": exists,
        "journal_placeholder": "present" if journal.exists() else "missing",
    }


def _status_extra_findings(
    repo: Path, fm: dict[str, Any], check_report: dict[str, Any]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    hledger_path = shutil.which("hledger")
    if hledger_path:
        findings.append(
            _finding(
                id="hledger-available",
                title="hledger is available",
                state="ok",
                detail="The hledger command is available on PATH.",
                audience="informational",
                operator_summary="hledger is installed for deeper local books checks.",
            )
        )
    else:
        findings.append(
            _finding(
                id="hledger-missing",
                title="hledger is not installed",
                state="info",
                detail=(
                    "hledger is optional for base Main Branch installs, but it is "
                    "needed for real local journal checks."
                ),
                audience="informational",
                operator_summary="Install hledger before validating real local journals.",
                repair="Install hledger from https://hledger.org/install.html",
            )
        )

    entries = _gitignore_entries(repo)
    missing_ignore = _books_ignore_missing(entries)
    if missing_ignore:
        findings.append(
            _finding(
                id="books-ignore-protections-missing",
                title="Bookkeeping ignore protections are incomplete",
                state="warn",
                detail=(
                    "The business repo .gitignore is missing bookkeeping safety "
                    f"entries: {', '.join(missing_ignore)}."
                ),
                audience="mechanical",
                operator_summary=(
                    "Add the missing books ignore rules so real ledgers and the "
                    "private vault do not enter tracked history."
                ),
                repair="Add the missing entries to .gitignore.",
                evidence=missing_ignore,
            )
        )
    else:
        findings.append(
            _finding(
                id="books-ignore-protections-ok",
                title="Bookkeeping ignore protections are present",
                state="ok",
                detail="The expected private-vault and ledger-extension ignore rules are present.",
                audience="informational",
                operator_summary="Books ignore protections are present.",
            )
        )

    vault = _vault_info(repo, fm)
    policy_present = _has_books_policy(repo)
    if vault["exists"] is True:
        findings.append(
            _finding(
                id="books-vault-present",
                title="Private books vault exists",
                state="ok",
                detail=f"Configured vault location: {vault['location']}.",
                audience="informational",
                operator_summary="Private books vault directory exists.",
            )
        )
    elif vault["exists"] is False:
        findings.append(
            _finding(
                id="books-vault-missing",
                title="Private books vault is not set up yet",
                state="warn" if policy_present else "info",
                detail=f"Configured vault location: {vault['location']}.",
                audience="mechanical" if policy_present else "informational",
                operator_summary=(
                    "Create the private books vault before storing real journals."
                    if policy_present
                    else "No private books vault yet. Set it up when you start real bookkeeping."
                ),
                repair=f"mkdir -p {DEFAULT_BOOKS_VAULT_RELATIVE.as_posix()}",
            )
        )

    if vault["journal_placeholder"] == "missing" and vault["exists"] is True:
        findings.append(
            _finding(
                id="books-journal-placeholder-missing",
                title="No private main.journal placeholder",
                state="info",
                detail=(
                    f"{vault['location']}/main.journal is not present. Main Branch "
                    "does not create or edit real journals in this slice."
                ),
                audience="operator_decision",
                operator_summary=(
                    "Create a private hledger main.journal when you are ready to start books."
                ),
                repair=(
                    "Create a private hledger journal inside the books vault; use "
                    "docs/examples/books/acme-fixture.journal only as a fake shape reference."
                ),
            )
        )
    elif vault["journal_placeholder"] == "present":
        findings.append(
            _finding(
                id="books-journal-placeholder-present",
                title="Private main.journal placeholder exists",
                state="ok",
                detail=f"{vault['location']}/main.journal exists; contents were not read.",
                audience="informational",
                operator_summary="Private main.journal exists; Main Branch did not read it.",
            )
        )

    if check_report.get("storage_mode") == "team-private-repo" or _safe_bool(
        fm.get("github_backup")
    ):
        findings.append(
            _finding(
                id="github-private-books-warning",
                title="GitHub private repo warning",
                state="warn",
                detail=GITHUB_PRIVATE_WARNING,
                audience="operator_decision",
                operator_summary=GITHUB_PRIVATE_WARNING,
            )
        )
    return findings


def _non_local_vault_location_findings(fm: dict[str, Any]) -> list[dict[str, Any]]:
    storage_mode = _policy_storage_mode(fm)
    raw_location = str(fm.get("vault_location") or "").strip()
    if storage_mode not in NON_LOCAL_STORAGE_MODES or raw_location:
        return []
    return [
        _finding(
            id="books-vault-location-missing",
            title="Private books vault location is not configured",
            state="warn",
            detail=(
                f"storage_mode={storage_mode!r} expects the real books to live "
                "outside this repo, but core/finance/books.md does not name "
                "the private repo or vault handle."
            ),
            audience="operator_decision",
            operator_summary=(
                "Set vault_location in core/finance/books.md so the operator "
                "knows where the private books live."
            ),
            repair=(
                "Add a safe vault_location label to core/finance/books.md; "
                "do not paste an absolute private path or real ledger data."
            ),
        )
    ]


def _detect_books_policy(repo: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    path = repo / "core" / "finance" / "books.md"
    if not path.exists():
        findings.append(
            _finding(
                id="books-policy-missing",
                title="No bookkeeping policy file",
                state="info",
                detail=(
                    "core/finance/books.md is not present. Books policy is "
                    "optional. Add it when you are ready to run real books."
                ),
                audience="informational",
                operator_summary=(
                    "No books policy yet. Add core/finance/books.md when you "
                    "want Main Branch to track bookkeeping."
                ),
                repair="See docs/books.md for a starter shape.",
            )
        )
        return {}, findings

    fm, err = _read_frontmatter(path)
    if err:
        findings.append(
            _finding(
                id="books-policy-frontmatter-error",
                title="Bookkeeping policy frontmatter does not parse",
                state="error",
                detail=err,
                audience="operator_decision",
                operator_summary=(
                    "core/finance/books.md exists but its frontmatter is "
                    "broken; Main Branch cannot read storage mode."
                ),
                repair=f"Fix the YAML frontmatter at {path.as_posix()}.",
            )
        )
        return {}, findings

    storage_mode = str(fm.get("storage_mode") or "").strip()
    if not storage_mode:
        findings.append(
            _finding(
                id="books-policy-storage-mode-missing",
                title="Bookkeeping policy is missing storage_mode",
                state="warn",
                detail=(
                    "core/finance/books.md has no storage_mode. Set it to "
                    "solo-local, team-private-repo, or advanced-vault."
                ),
                audience="operator_decision",
                operator_summary=(
                    "Books policy needs a storage_mode so Main Branch knows "
                    "where the real books live."
                ),
                repair=(
                    "Add `storage_mode: solo-local` (default) to core/finance/books.md frontmatter."
                ),
            )
        )
    elif storage_mode not in VALID_STORAGE_MODES:
        findings.append(
            _finding(
                id="books-policy-storage-mode-invalid",
                title="Bookkeeping policy uses an unknown storage_mode",
                state="warn",
                detail=(
                    f"storage_mode={storage_mode!r} is not one of "
                    "solo-local, team-private-repo, advanced-vault. "
                    "Treating as solo-local for vault enforcement so a "
                    "typo cannot silently allow a books leak."
                ),
                audience="operator_decision",
                operator_summary=(
                    f"Unknown storage_mode {storage_mode!r}; assuming "
                    "solo-local until corrected. Use one of the three "
                    "documented values."
                ),
                repair=f"See {DOCS_BOOKS_PATH} for valid storage modes.",
            )
        )
    else:
        findings.append(
            _finding(
                id="books-policy-ok",
                title="Bookkeeping policy present",
                state="ok",
                detail=f"core/finance/books.md declares storage_mode={storage_mode}.",
                audience="informational",
                operator_summary=(f"Books policy in place; storage mode is {storage_mode}."),
            )
        )
    return fm, findings


def _detect_chart_of_accounts(repo: Path) -> list[dict[str, Any]]:
    path = repo / "core" / "finance" / "chart-of-accounts.md"
    if not path.exists():
        return [
            _finding(
                id="chart-of-accounts-missing",
                title="No chart of accounts",
                state="info",
                detail=(
                    "core/finance/chart-of-accounts.md is not present. "
                    "Add it when you settle on an account-naming convention."
                ),
                audience="informational",
                operator_summary=(
                    "No chart of accounts yet. Optional until you start real bookkeeping."
                ),
                repair="See docs/books.md for the shape.",
            )
        ]
    fm, err = _read_frontmatter(path)
    if err:
        return [
            _finding(
                id="chart-of-accounts-frontmatter-error",
                title="Chart of accounts frontmatter does not parse",
                state="warn",
                detail=err,
                audience="operator_decision",
                operator_summary=("core/finance/chart-of-accounts.md frontmatter cannot be read."),
                repair=f"Fix the YAML frontmatter at {path.as_posix()}.",
            )
        ]
    return [
        _finding(
            id="chart-of-accounts-ok",
            title="Chart of accounts present",
            state="ok",
            detail="core/finance/chart-of-accounts.md is in place.",
            audience="informational",
            operator_summary="Chart of accounts is documented.",
        )
    ]


def _check_vault_ignore_rule(repo: Path, storage_mode: str) -> list[dict[str, Any]]:
    """Enforce the private books vault contract.

    For ``solo-local``, ``.mb/private/`` must be ignored by the
    business repo's ``.gitignore`` so the real books never enter
    tracked history. For team/advanced modes the vault lives
    elsewhere so the rule is informational.
    """
    findings: list[dict[str, Any]] = []
    entries = _gitignore_entries(repo)
    ignored = _ignore_rule_present(entries)
    vault_path = repo / VAULT_RELATIVE
    vault_exists = vault_path.exists()

    # Fail closed: only the two explicitly non-local modes skip the
    # local vault ignore check. Anything else — empty, unknown,
    # typo'd — gets solo-local enforcement so a misconfigured policy
    # does not silently allow a leak.
    treat_as_local = storage_mode not in NON_LOCAL_STORAGE_MODES

    if treat_as_local:
        if ignored:
            findings.append(
                _finding(
                    id="vault-ignore-rule-ok",
                    title="Private books vault ignore rule present",
                    state="ok",
                    detail=(
                        ".mb/private/ is gitignored; the books vault will "
                        "stay out of the business repo's tracked history."
                    ),
                    audience="informational",
                    operator_summary=("Private books vault is properly ignored."),
                )
            )
        else:
            findings.append(
                _finding(
                    id="vault-ignore-rule-missing",
                    title="Private books vault is not gitignored",
                    state="error" if vault_exists else "warn",
                    detail=(
                        ".mb/private/ is not in .gitignore. The solo-local "
                        "storage mode keeps real books in this directory; "
                        "they must never enter tracked history."
                    ),
                    audience="mechanical",
                    operator_summary=(
                        "Add `.mb/private/` to .gitignore so the books vault stays local."
                    ),
                    repair=("echo '.mb/private/' >> .gitignore && git add .gitignore"),
                )
            )
    else:
        findings.append(
            _finding(
                id="vault-ignore-rule-skipped",
                title="Private books vault is not local to this repo",
                state="info",
                detail=(
                    f"storage_mode={storage_mode!r}; the real books live "
                    "in a separate vault, not in this repo."
                ),
                audience="informational",
                operator_summary=(
                    "Real books live outside this repo for the configured storage mode."
                ),
            )
        )
        if vault_exists and not ignored:
            findings.append(
                _finding(
                    id="vault-directory-unexpected",
                    title=".mb/private/ exists but storage mode is not solo-local",
                    state="warn",
                    detail=(
                        ".mb/private/ exists in this repo but storage_mode "
                        f"is {storage_mode!r}. Confirm the real books "
                        "have moved and remove the leftover directory."
                    ),
                    audience="operator_decision",
                    operator_summary=(
                        f"Leftover .mb/private/ vault under {storage_mode} mode; confirm migration."
                    ),
                )
            )
    return findings


def _detect_unsafe_paths(repo: Path) -> list[dict[str, Any]]:
    """Flag ledger or statement files saved in the business repo.

    Per the foundation decision this is a ``warn``, not a hard fail:
    operators may legitimately save non-finance CSVs (research
    exports, audience data) and may ship sample fixtures. Files
    carrying an explicit fixture marker (see ``FIXTURE_MARKER_TOKENS``)
    are exempted.
    """
    tracked, used_git = _tracked_files(repo)
    if used_git:
        candidates = tracked
        method = "git ls-files"
    else:
        candidates = _walk_files_fallback(repo)
        method = "filesystem walk"

    leaks: list[str] = []
    fixtures: list[str] = []
    for rel in candidates:
        if not rel:
            continue
        if rel.startswith(".mb/private/"):
            continue
        suffix = Path(rel).suffix.lower()
        if suffix not in UNSAFE_EXTENSIONS:
            continue
        absolute = repo / rel
        if _has_fixture_marker(absolute):
            fixtures.append(rel)
            continue
        leaks.append(rel)

    findings: list[dict[str, Any]] = []
    if fixtures:
        findings.append(
            _finding(
                id="unsafe-paths-fixtures-detected",
                title="Marked fixture files detected",
                state="info",
                detail=(
                    "These files carry an explicit fixture marker and are "
                    "exempted from the unsafe-path check."
                ),
                audience="informational",
                operator_summary=(
                    f"{len(fixtures)} file(s) marked as sample fixtures; "
                    "skipping unsafe-path enforcement."
                ),
                evidence=fixtures[:20],
            )
        )

    if not leaks:
        findings.append(
            _finding(
                id="unsafe-paths-clean",
                title="No ledger or statement files tracked in the business repo",
                state="ok",
                detail=f"Checked via {method}; no unmarked ledger-shaped files found.",
                audience="informational",
                operator_summary=("No raw ledgers or statements saved in the business repo."),
            )
        )
        return findings

    findings.append(
        _finding(
            id="unsafe-paths-detected",
            title="Ledger or statement files found in the business repo",
            state="warn",
            detail=(
                "These files look like raw books or statement exports. "
                "Real books belong in the private books vault, not the "
                "team-visible business repo. If a flagged file is a sample, "
                "add a fixture marker line (for example "
                "'; MB-FIXTURE — sample, not a real ledger') in the first "
                f"{FIXTURE_MARKER_BYTES} bytes."
            ),
            audience="operator_decision",
            operator_summary=(
                f"{len(leaks)} ledger/statement-shaped file(s) saved in the business repo; "
                "move them into the private books vault or mark them as "
                "fixtures."
            ),
            repair=(
                "Move each file into .mb/private/books/ (solo-local) or "
                "the private books repo, then run `git rm --cached <file>` for "
                "each leaked file and save a checkpoint. Rotate the data if it "
                "is sensitive."
            ),
            evidence=leaks[:20],
        )
    )
    return findings


def _bundled_fixture_path() -> Path | None:
    try:
        ref = (
            resources.files("mb").joinpath("_data").joinpath("books").joinpath(BUNDLED_FIXTURE_NAME)
        )
        with resources.as_file(ref) as resolved:
            if resolved.exists():
                return Path(resolved)
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    fallback = Path(__file__).resolve().parent / "_data" / "books" / BUNDLED_FIXTURE_NAME
    if fallback.exists():
        return fallback
    return None


def _validate_fixture(
    fixture: Path | None,
) -> list[dict[str, Any]]:
    """Optionally validate a fake hledger journal fixture."""
    target = fixture or _bundled_fixture_path()
    if target is None:
        return [
            _finding(
                id="fixture-missing",
                title="Books fixture not found",
                state="warn",
                detail=("No fixture path was given and the bundled fixture could not be located."),
                audience="operator_decision",
                operator_summary=("Pass --fixture <path> or reinstall Main Branch."),
            )
        ]

    if not target.exists():
        return [
            _finding(
                id="fixture-missing",
                title="Books fixture not found",
                state="warn",
                detail=f"{target} does not exist.",
                audience="operator_decision",
                operator_summary=(f"Fixture path {target} not found; check the spelling."),
            )
        ]

    if not shutil.which("hledger"):
        return [
            _finding(
                id="hledger-missing",
                title="hledger is not installed",
                state="info",
                detail=(
                    "hledger is optional for base Main Branch installs. "
                    "Install it to run deeper books validation."
                ),
                audience="informational",
                operator_summary=(
                    "Install hledger to validate journal fixtures. Base "
                    "Main Branch continues to work without it."
                ),
                repair=(
                    "Install hledger from the prebuilt binary at https://hledger.org/install.html"
                ),
            )
        ]

    try:
        proc = subprocess.run(
            ["hledger", "-f", str(target), "check"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        return [
            _finding(
                id="hledger-invocation-error",
                title="hledger could not be invoked",
                state="warn",
                detail=str(exc),
                audience="informational",
                operator_summary=("Main Branch found hledger on PATH but could not run it."),
            )
        ]

    if proc.returncode != 0:
        return [
            _finding(
                id="fixture-invalid",
                title="hledger could not validate the books fixture",
                state="error",
                detail=(proc.stderr.strip() or proc.stdout.strip())[:2000],
                audience="operator_decision",
                operator_summary=(
                    "Books fixture failed hledger validation. Fix the "
                    "journal or pass a different --fixture."
                ),
                repair=f"hledger -f {target} check",
            )
        ]

    return [
        _finding(
            id="fixture-valid",
            title="Books fixture validates with hledger",
            state="ok",
            detail=f"hledger -f {target} check passed.",
            audience="informational",
            operator_summary="Fake hledger fixture passes structural checks.",
        )
    ]


def run(
    repo: str | Path = ".",
    *,
    validate_fixture: bool = False,
    fixture: str | Path | None = None,
) -> dict[str, Any]:
    """Run ``mb books check`` against ``repo``.

    Read-only. Never mutates files. Never reads the contents of the
    private books vault.
    """
    repo_path = Path(repo).resolve()

    findings: list[dict[str, Any]] = []
    fm, policy_findings = _detect_books_policy(repo_path)
    findings.extend(policy_findings)
    findings.extend(_detect_chart_of_accounts(repo_path))
    storage_mode = str(fm.get("storage_mode") or "").strip()
    findings.extend(_non_local_vault_location_findings(fm))
    findings.extend(_check_vault_ignore_rule(repo_path, storage_mode))
    findings.extend(_detect_unsafe_paths(repo_path))

    fixture_findings: list[dict[str, Any]] = []
    if validate_fixture:
        fixture_path = Path(fixture).resolve() if fixture else None
        fixture_findings = _validate_fixture(fixture_path)
        findings.extend(fixture_findings)

    state = _max_state([finding["state"] for finding in findings])
    errors = [finding["operator_summary"] for finding in findings if finding["state"] == "error"]
    warnings = [finding["operator_summary"] for finding in findings if finding["state"] == "warn"]

    summary = _summary(state, findings)

    return {
        "ok": state not in {"error"},
        "state": state,
        "repo": str(repo_path),
        "storage_mode": storage_mode,
        "fixture_validated": validate_fixture,
        "summary": summary,
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
        "safe_to_share": True,
    }


def status(repo: str | Path = ".") -> dict[str, Any]:
    """Return read-only books setup and storage health.

    This is the safe operator-facing status surface for the private hledger
    books vault. It never reads real ledger contents and it sanitizes private
    vault paths that point outside the business repo.
    """
    repo_path = Path(repo).resolve()
    check_report = run(repo=repo_path)
    fm, _ = _detect_books_policy(repo_path)
    extra_findings = _status_extra_findings(repo_path, fm, check_report)
    findings = [*check_report["findings"], *extra_findings]
    state = _max_state([finding["state"] for finding in findings])
    errors = [finding["operator_summary"] for finding in findings if finding["state"] == "error"]
    warnings = [finding["operator_summary"] for finding in findings if finding["state"] == "warn"]

    hledger_available = any(finding["id"] == "hledger-available" for finding in extra_findings)
    entries = _gitignore_entries(repo_path)
    missing_ignore = _books_ignore_missing(entries)
    vault = _vault_info(repo_path, fm)
    storage_mode = check_report.get("storage_mode") or _policy_storage_mode(fm)
    status_summary = "Books setup passed." if state == "ok" else _summary(state, findings)

    return {
        "ok": state not in {"error"},
        "state": state,
        "repo": str(repo_path),
        "engine": "hledger",
        "hledger": {
            "available": hledger_available,
            "command": "hledger",
            "install": "https://hledger.org/install.html",
        },
        "policy": {
            "present": _has_books_policy(repo_path),
            "path": "core/finance/books.md",
            "storage_mode": storage_mode,
            "valid_storage_mode": bool(storage_mode in VALID_STORAGE_MODES),
        },
        "vault": vault,
        "ignore": {
            "missing": missing_ignore,
            "ok": not missing_ignore,
            "expected": list(BOOKS_IGNORE_ENTRIES),
        },
        "check": {
            "state": check_report["state"],
            "summary": check_report["summary"],
            "warnings": check_report["warnings"],
            "errors": check_report["errors"],
        },
        "github_private_warning": (
            GITHUB_PRIVATE_WARNING
            if storage_mode == "team-private-repo" or _safe_bool(fm.get("github_backup"))
            else ""
        ),
        "summary": status_summary,
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
        "safe_to_share": True,
    }


def _unsafe_artifact_count(findings: list[dict[str, Any]]) -> int:
    for finding in findings:
        if finding.get("id") == "unsafe-paths-detected":
            evidence = finding.get("evidence")
            return len(evidence) if isinstance(evidence, list) else 0
    return 0


def _readiness_state(status_report: dict[str, Any], unsafe_count: int) -> str:
    policy = status_report.get("policy") or {}
    raw_state = str(status_report.get("state") or "")
    if raw_state == "error":
        return "blocked"
    if unsafe_count:
        return "warn"
    if not policy.get("present"):
        return "not_configured"
    if raw_state == "warn":
        return "warn"
    if raw_state == "info":
        return "missing"
    return "ok"


def _readiness_summary(state: str, status_report: dict[str, Any]) -> str:
    if state == "not_configured":
        return "Bookkeeping is not configured."
    if state == "blocked":
        return "Bookkeeping setup is blocked; run the books repair plan."
    if state == "warn":
        return "Bookkeeping setup has warnings."
    if state == "missing":
        return "Bookkeeping setup is missing optional pieces."
    return str(status_report.get("summary") or "Bookkeeping setup passed.")


def _readiness_route(state: str) -> dict[str, str]:
    if state in {"blocked", "warn", "missing"}:
        return {
            "tool": "mb books doctor --plan",
            "reason": "plan bookkeeping setup repairs",
        }
    return {
        "tool": "mb books status",
        "reason": "inspect bookkeeping setup",
    }


def readiness(repo: str | Path = ".") -> dict[str, Any]:
    """Return compact books readiness facts for daily status/start JSON.

    This adapter intentionally exposes less than ``mb books status``. It keeps
    routing signals and counts, but omits ledger contents, hledger binary paths,
    private vault paths, raw exports, and unsafe artifact filenames.
    """
    status_report = status(repo=repo)
    policy = status_report.get("policy") or {}
    vault = status_report.get("vault") or {}
    ignore = status_report.get("ignore") or {}
    hledger = status_report.get("hledger") or {}
    unsafe_count = _unsafe_artifact_count(status_report.get("findings") or [])
    chart_present = any(
        finding.get("id") == "chart-of-accounts-ok"
        for finding in status_report.get("findings") or []
    )
    state = _readiness_state(status_report, unsafe_count)
    next_command = (
        "mb books doctor --plan --json"
        if state in {"blocked", "warn", "missing"}
        else "mb books status --json"
    )
    recommended_route = _readiness_route(state)
    return {
        "schema_version": "1.0",
        "state": state,
        "summary": _readiness_summary(state, status_report),
        "configured": bool(policy.get("present")),
        "mention": state in {"blocked", "warn", "missing"},
        "hledger": {"available": bool(hledger.get("available"))},
        "policy": {
            "present": bool(policy.get("present")),
            "storage_mode": str(policy.get("storage_mode") or ""),
            "valid_storage_mode": bool(policy.get("valid_storage_mode")),
        },
        "vault": {
            "configured": bool(vault.get("configured")),
            "location_kind": str(vault.get("location_kind") or ""),
            "exists": vault.get("exists") if vault.get("location_kind") != "external" else None,
        },
        "ignore": {
            "ok": bool(ignore.get("ok")),
            "missing_count": len(ignore.get("missing") or []),
        },
        "unsafe_artifacts": {"count": unsafe_count},
        "chart_of_accounts": {"present": chart_present},
        "next_command": next_command,
        "recommended_route": recommended_route,
        "source": "mb books status",
        "safe_to_share": True,
    }


def _plan_action(
    *,
    id: str,
    title: str,
    state: str,
    reason: str,
    command: str,
    writes: list[str] | None = None,
    evidence: list[str] | None = None,
    audience: str = "operator_decision",
) -> dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "state": state,
        "mode": "plan",
        "safe_to_apply": False,
        "reason": reason,
        "command": command,
        "writes": writes or [],
        "evidence": evidence or [],
        "audience": audience if audience in AUDIENCE_VALUES else "operator_decision",
        "operator_summary": reason,
    }


def doctor_plan(repo: str | Path = ".") -> dict[str, Any]:
    """Return a non-mutating books repair plan."""
    status_report = status(repo=repo)
    findings = {finding["id"]: finding for finding in status_report["findings"]}
    actions: list[dict[str, Any]] = []

    if "hledger-missing" in findings:
        finding = findings["hledger-missing"]
        actions.append(
            _plan_action(
                id="install-hledger",
                title="Install hledger",
                state="info",
                reason=finding["operator_summary"],
                command="Install hledger from https://hledger.org/install.html",
                evidence=finding.get("evidence") or [],
                audience="informational",
            )
        )

    if "books-policy-missing" in findings:
        finding = findings["books-policy-missing"]
        actions.append(
            _plan_action(
                id="add-books-policy",
                title="Add a safe books policy",
                state="info",
                reason=finding["operator_summary"],
                command=(
                    "Use docs/examples/books/books.md as the shape for "
                    "core/finance/books.md; keep real ledger data out of it."
                ),
                writes=["core/finance/books.md"],
                audience="informational",
            )
        )
    elif "books-policy-frontmatter-error" in findings:
        finding = findings["books-policy-frontmatter-error"]
        actions.append(
            _plan_action(
                id="fix-books-policy-frontmatter",
                title="Fix books policy frontmatter",
                state="error",
                reason=finding["operator_summary"],
                command=finding["repair"],
                writes=["core/finance/books.md"],
            )
        )
    elif (
        "books-policy-storage-mode-missing" in findings
        or "books-policy-storage-mode-invalid" in findings
    ):
        key = (
            "books-policy-storage-mode-missing"
            if "books-policy-storage-mode-missing" in findings
            else "books-policy-storage-mode-invalid"
        )
        finding = findings[key]
        actions.append(
            _plan_action(
                id="fix-books-storage-mode",
                title="Fix books storage mode",
                state="warn",
                reason=finding["operator_summary"],
                command=finding["repair"],
                writes=["core/finance/books.md"],
            )
        )

    if "chart-of-accounts-missing" in findings:
        finding = findings["chart-of-accounts-missing"]
        actions.append(
            _plan_action(
                id="add-chart-of-accounts",
                title="Add chart of accounts when ready",
                state="info",
                reason=finding["operator_summary"],
                command=(
                    "Use docs/examples/books/chart-of-accounts.md as the shape "
                    "for core/finance/chart-of-accounts.md; do not include real balances."
                ),
                writes=["core/finance/chart-of-accounts.md"],
                audience="informational",
            )
        )

    if "books-vault-location-missing" in findings:
        finding = findings["books-vault-location-missing"]
        actions.append(
            _plan_action(
                id="configure-private-books-vault-location",
                title="Configure private books vault location",
                state="warn",
                reason=finding["operator_summary"],
                command=(
                    "Set vault_location in core/finance/books.md to a safe private "
                    "repo or vault label; keep raw finance data out of this repo."
                ),
                writes=["core/finance/books.md"],
                audience="operator_decision",
            )
        )

    missing_ignore = status_report["ignore"]["missing"]
    if missing_ignore:
        actions.append(
            _plan_action(
                id="add-books-ignore-protections",
                title="Add books ignore protections",
                state="warn",
                reason=(
                    "The business repo is missing books ignore rules for the "
                    "private vault or ledger-shaped files."
                ),
                command=("Add these lines to .gitignore: " + ", ".join(missing_ignore)),
                writes=[".gitignore"],
                evidence=missing_ignore,
                audience="mechanical",
            )
        )

    if "books-vault-missing" in findings:
        finding = findings["books-vault-missing"]
        actions.append(
            _plan_action(
                id="create-private-books-vault",
                title="Create private books vault",
                state=finding["state"],
                reason=finding["operator_summary"],
                command=f"mkdir -p {DEFAULT_BOOKS_VAULT_RELATIVE.as_posix()}",
                writes=[DEFAULT_BOOKS_VAULT_RELATIVE.as_posix()],
                audience=finding["audience"],
            )
        )

    if "books-journal-placeholder-missing" in findings:
        finding = findings["books-journal-placeholder-missing"]
        actions.append(
            _plan_action(
                id="create-private-journal-placeholder",
                title="Create private hledger journal placeholder",
                state="info",
                reason=finding["operator_summary"],
                command=finding["repair"],
                writes=[f"{DEFAULT_BOOKS_VAULT_RELATIVE.as_posix()}/main.journal"],
                audience="operator_decision",
            )
        )

    if "unsafe-paths-detected" in findings:
        finding = findings["unsafe-paths-detected"]
        actions.append(
            _plan_action(
                id="move-unsafe-finance-artifacts",
                title="Move unsafe tracked finance artifacts",
                state="warn",
                reason=finding["operator_summary"],
                command=finding["repair"],
                evidence=finding.get("evidence") or [],
                audience="operator_decision",
            )
        )

    action_state = _max_state([action["state"] for action in actions])
    state = action_state if actions else "ok"
    return {
        "ok": True,
        "state": state,
        "repo": status_report["repo"],
        "summary": (
            f"{len(actions)} planned repair action(s)." if actions else "No books repairs planned."
        ),
        "actions": actions,
        "status": {
            "state": status_report["state"],
            "summary": status_report["summary"],
            "hledger": status_report["hledger"],
            "vault": status_report["vault"],
            "ignore": status_report["ignore"],
        },
        "safe_to_share": True,
    }


def _summary(state: str, findings: list[dict[str, Any]]) -> str:
    counts = {"ok": 0, "info": 0, "warn": 0, "error": 0}
    for finding in findings:
        counts[finding.get("state", "info")] = counts.get(finding.get("state", "info"), 0) + 1
    if state == "error":
        return (
            f"{counts['error']} error(s), {counts['warn']} warning(s); "
            "see findings for repair commands."
        )
    if state == "warn":
        return f"{counts['warn']} warning(s); see findings for repair commands."
    if state == "info":
        return "No errors. See info findings for optional bookkeeping setup."
    return "Books check passed."


def render_human(report: dict[str, Any]) -> None:
    """Print a short human summary to stdout."""
    import typer

    typer.echo(f"mb books check — {report['summary']}")
    if report.get("storage_mode"):
        typer.echo(f"storage mode: {report['storage_mode']}")
    typer.echo("")
    for finding in report.get("findings", []):
        marker = {
            "ok": " ok ",
            "info": "info",
            "warn": "WARN",
            "error": "FAIL",
        }.get(finding.get("state", "info"), "    ")
        typer.echo(f"  [{marker}] {finding['title']}")
        if finding.get("operator_summary"):
            typer.echo(f"         {finding['operator_summary']}")
        if finding.get("repair"):
            typer.echo(f"         repair: {finding['repair']}")
        evidence = finding.get("evidence") or []
        for item in evidence[:5]:
            typer.echo(f"           - {item}")
    typer.echo("")
    typer.echo(f"See {DOCS_BOOKS_PATH} for the full books contract.")


def render_status(report: dict[str, Any]) -> None:
    """Print ``mb books status`` for humans."""
    import typer

    hledger = "available" if report["hledger"]["available"] else "missing"
    vault = report["vault"]
    typer.echo(f"mb books status — {report['summary']}")
    typer.echo(f"Books engine:      {report['engine']}")
    typer.echo(f"hledger:           {hledger}")
    typer.echo(f"Storage mode:      {report['policy']['storage_mode'] or 'not configured'}")
    typer.echo(f"Bookkeeping vault: {vault['location']}")
    if vault["exists"] is not None:
        typer.echo(f"Vault exists:      {'yes' if vault['exists'] else 'no'}")
    typer.echo(f"Ignore rules:      {'ok' if report['ignore']['ok'] else 'missing'}")
    if report.get("github_private_warning"):
        typer.echo("")
        typer.echo(report["github_private_warning"])
    typer.echo("")
    for finding in report.get("findings", []):
        if finding.get("state") == "ok":
            continue
        marker = {"info": "info", "warn": "WARN", "error": "FAIL"}.get(
            finding.get("state", "info"), "    "
        )
        typer.echo(f"  [{marker}] {finding['title']}")
        if finding.get("operator_summary"):
            typer.echo(f"         {finding['operator_summary']}")
        if finding.get("repair"):
            typer.echo(f"         repair: {finding['repair']}")
        for item in (finding.get("evidence") or [])[:5]:
            typer.echo(f"           - {item}")
    typer.echo("")
    typer.echo("Run `mb books doctor --plan` for safe setup repair guidance.")


def render_doctor_plan(report: dict[str, Any]) -> None:
    """Print ``mb books doctor --plan`` for humans."""
    import typer

    typer.echo(f"mb books doctor --plan — {report['summary']}")
    if not report.get("actions"):
        return
    typer.echo("")
    for action in report["actions"]:
        marker = {"info": "info", "warn": "WARN", "error": "FAIL"}.get(
            action.get("state", "info"), "    "
        )
        typer.echo(f"  [{marker}] {action['title']}")
        typer.echo(f"         {action['reason']}")
        if action.get("command"):
            typer.echo(f"         plan: {action['command']}")
        for item in (action.get("evidence") or [])[:5]:
            typer.echo(f"           - {item}")
