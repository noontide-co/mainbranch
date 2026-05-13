"""``mb books check`` — first books safety surface."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import books as books_mod
from mb.cli import app

runner = CliRunner()


def _init_business_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "biz"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    return repo


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git_add_all(repo: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "test"],
        cwd=repo,
        check=True,
    )


def _findings_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {finding["id"]: finding for finding in report["findings"]}


def test_books_check_empty_repo_reports_recommendations(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert "books-policy-missing" in findings
    assert findings["books-policy-missing"]["state"] == "info"
    assert findings["books-policy-missing"]["audience"] == "informational"
    assert findings["books-policy-missing"]["operator_summary"]
    assert "chart-of-accounts-missing" in findings
    # No books vault present, but solo-local default applies → warn (not error).
    assert findings["vault-ignore-rule-missing"]["state"] == "warn"
    assert findings["vault-ignore-rule-missing"]["audience"] == "mechanical"
    assert "git ls-files" in findings["unsafe-paths-clean"]["detail"]
    assert report["ok"] is True
    assert report["state"] == "warn"


def test_books_check_passes_with_policy_and_ignore_rule(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
operating_currency: USD
storage_mode: solo-local
vault_location: ".mb/private/books/"
---

# Books
""",
    )
    _write(
        repo / "core/finance/chart-of-accounts.md",
        """---
type: chart-of-accounts
ledger: hledger
---

# Chart
""",
    )
    _write(repo / ".gitignore", ".mb/private/\n")
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["books-policy-ok"]["state"] == "ok"
    assert findings["chart-of-accounts-ok"]["state"] == "ok"
    assert findings["vault-ignore-rule-ok"]["state"] == "ok"
    assert findings["unsafe-paths-clean"]["state"] == "ok"
    assert report["state"] == "ok"
    assert report["ok"] is True
    assert report["errors"] == []


def test_books_check_flags_committed_ledger_file(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(repo / "core/finance/notes.md", "# notes\n")
    _write(repo / "core/finance/main.journal", "; leaked real journal\n")
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert "unsafe-paths-detected" in findings
    leak = findings["unsafe-paths-detected"]
    # Per the foundation decision, unsafe-path detection warns rather
    # than hard-fails so non-finance CSVs and marked fixtures stay
    # usable.
    assert leak["state"] == "warn"
    assert leak["audience"] == "operator_decision"
    assert "git rm --cached <file>" in leak["repair"]
    assert "core/finance/main.journal" in leak["evidence"]
    assert report["ok"] is True
    assert report["state"] == "warn"


def test_books_check_flags_committed_csv_statement(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(repo / "imports/bank-2026-01.csv", "date,amount\n")
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["unsafe-paths-detected"]["state"] == "warn"
    assert "imports/bank-2026-01.csv" in findings["unsafe-paths-detected"]["evidence"]


def test_books_check_exempts_marked_fixture(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "docs/examples/sample.journal",
        "; MB-FIXTURE — not a real ledger\n2026-01-01 sample\n",
    )
    _write(
        repo / "research/audience-survey.csv",
        "# MB-FIXTURE — synthetic responses\nq,a\n",
    )
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert "unsafe-paths-detected" not in findings
    assert findings["unsafe-paths-fixtures-detected"]["state"] == "info"
    assert "docs/examples/sample.journal" in findings["unsafe-paths-fixtures-detected"]["evidence"]
    assert "research/audience-survey.csv" in findings["unsafe-paths-fixtures-detected"]["evidence"]


def test_books_check_invalid_storage_mode_still_enforces_local_ignore(
    tmp_path: Path,
) -> None:
    """Invalid storage_mode must fail closed: enforce solo-local ignore."""
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: solo-loca
---

# Books
""",
    )
    # Vault directory exists but is not gitignored — must be flagged.
    (repo / ".mb" / "private").mkdir(parents=True)
    (repo / ".mb" / "private" / "main.journal").write_text("; real\n")

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["books-policy-storage-mode-invalid"]["state"] == "warn"
    # Critical: invalid mode does NOT route to skip; it routes to
    # enforcement so the leak is caught.
    assert "vault-ignore-rule-skipped" not in findings
    assert findings["vault-ignore-rule-missing"]["state"] == "error"
    assert report["ok"] is False


def test_books_check_team_mode_skips_local_ignore_rule(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: team-private-repo
vault_location: "acme-private-books"
---

# Books
""",
    )
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["vault-ignore-rule-skipped"]["state"] == "info"
    # No vault directory exists, so the leftover finding should not appear.
    assert "vault-directory-unexpected" not in findings
    assert report["ok"] is True


def test_books_check_warns_on_unknown_storage_mode(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: not-a-real-mode
---

# Books
""",
    )
    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["books-policy-storage-mode-invalid"]["state"] == "warn"


def test_books_check_warns_on_broken_frontmatter(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        "---\nstorage_mode: : : not-yaml\n---\n",
    )
    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["books-policy-frontmatter-error"]["state"] == "error"
    assert report["ok"] is False


def test_books_check_fixture_handles_missing_hledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "")

    report = books_mod.run(repo=str(repo), validate_fixture=True)
    findings = _findings_by_id(report)
    assert findings["hledger-missing"]["state"] == "info"
    assert findings["hledger-missing"]["audience"] == "informational"
    # Missing hledger must not break unrelated repo state.
    assert report["ok"] is True


def _hledger_dispatcher(
    monkeypatch: pytest.MonkeyPatch,
    *,
    returncode: int,
    stdout: str = "",
    stderr: str = "",
) -> list[list[str]]:
    """Fake subprocess.run that only intercepts hledger calls.

    Real git calls (used by ``_run_git`` for ``ls-files``) pass through
    to the real ``subprocess.run`` so a regression that calls the wrong
    binary cannot accidentally satisfy the test.
    """
    real_run = subprocess.run
    seen: list[list[str]] = []

    class _FakeCompleted:
        def __init__(self) -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def _dispatch(args: Any, *rest: Any, **kwargs: Any) -> Any:
        argv = list(args) if isinstance(args, (list, tuple)) else [args]
        seen.append(argv)
        if argv and Path(str(argv[0])).name == "hledger":
            return _FakeCompleted()
        return real_run(args, *rest, **kwargs)

    monkeypatch.setattr("mb.books.subprocess.run", _dispatch)
    return seen


def test_books_check_fixture_runs_when_hledger_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "/fake/hledger")
    seen = _hledger_dispatcher(monkeypatch, returncode=0)

    report = books_mod.run(repo=str(repo), validate_fixture=True)
    findings = _findings_by_id(report)
    assert findings["fixture-valid"]["state"] == "ok"
    # The real git ls-files call passed through, so the clean-paths
    # finding came from real evidence, not from the fake.
    assert findings["unsafe-paths-clean"]["state"] == "ok"
    # And at least one of the recorded calls was the hledger invocation.
    assert any(Path(str(call[0])).name == "hledger" for call in seen)


def test_books_check_fixture_reports_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "/fake/hledger")
    _hledger_dispatcher(monkeypatch, returncode=1, stderr="balance assertion failed")

    report = books_mod.run(repo=str(repo), validate_fixture=True)
    findings = _findings_by_id(report)
    assert findings["fixture-invalid"]["state"] == "error"
    assert "balance assertion failed" in findings["fixture-invalid"]["detail"]
    assert report["ok"] is False


def test_books_check_cli_emits_json_envelope(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "check", str(repo), "--json"])
    # warn-state run still exits 0 because no errors.
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mb_command"] == "mb books check"
    assert payload["result_schema"]["name"] == "mainbranch.books.check.result"
    assert payload["result_envelope_version"] == "1.0"
    for finding in payload["findings"]:
        assert "audience" in finding
        assert "operator_summary" in finding


def test_books_check_cli_human_output_mentions_docs(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "check", str(repo)])
    assert result.exit_code == 0, result.output
    assert "docs/books.md" in result.output


def test_books_check_cli_exits_one_on_error(tmp_path: Path) -> None:
    """A genuine error (broken policy frontmatter) still exits 1."""
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        "---\nstorage_mode: : : not-yaml\n---\n",
    )
    result = runner.invoke(app, ["books", "check", str(repo)])
    assert result.exit_code == 1, result.output
    assert "FAIL" in result.output


def test_books_check_unsafe_paths_warn_does_not_exit_one(tmp_path: Path) -> None:
    """Unsafe-path findings are warn, so the CLI must not exit 1 on them."""
    repo = _init_business_repo(tmp_path)
    _write(repo / "core/finance/main.journal", "; leak\n")
    _git_add_all(repo)
    result = runner.invoke(app, ["books", "check", str(repo)])
    assert result.exit_code == 0, result.output
    assert "WARN" in result.output


def test_books_status_json_reports_missing_hledger_and_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: solo-local
vault_location: ".mb/private/books/"
---

# Books
""",
    )
    _write(repo / ".gitignore", ".mb/private/\n*.journal\n*.hledger\n*.ledger\n*.beancount\n")
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "")

    result = runner.invoke(app, ["books", "status", str(repo), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mb_command"] == "mb books status"
    assert payload["result_schema"]["name"] == "mainbranch.books.status.result"
    assert payload["engine"] == "hledger"
    assert payload["hledger"]["available"] is False
    assert payload["vault"]["location"] == ".mb/private/books"
    assert payload["vault"]["exists"] is False
    assert payload["ignore"]["ok"] is True
    assert "books-vault-missing" in {finding["id"] for finding in payload["findings"]}


def test_books_status_and_doctor_accept_no_slash_private_ignore_entry(
    tmp_path: Path,
) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: solo-local
vault_location: ".mb/private/books/"
---

# Books
""",
    )
    _write(repo / ".gitignore", ".mb/private\n*.journal\n*.hledger\n*.ledger\n*.beancount\n")

    status_result = runner.invoke(app, ["books", "status", str(repo), "--json"])
    assert status_result.exit_code == 0, status_result.output
    status_payload = json.loads(status_result.output)
    assert status_payload["ignore"]["ok"] is True
    assert status_payload["ignore"]["missing"] == []

    doctor_result = runner.invoke(app, ["books", "doctor", str(repo), "--plan", "--json"])
    assert doctor_result.exit_code == 0, doctor_result.output
    doctor_payload = json.loads(doctor_result.output)
    actions = {action["id"] for action in doctor_payload["actions"]}
    assert "add-books-ignore-protections" not in actions


def test_books_status_reports_hledger_and_private_journal_without_reading_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: solo-local
vault_location: ".mb/private/books/"
---

# Books
""",
    )
    _write(repo / ".gitignore", ".mb/private/\n*.journal\n*.hledger\n*.ledger\n*.beancount\n")
    _write(repo / ".mb/private/books/main.journal", "; PRIVATE_ACCOUNT_ID\n")
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "/fake/private/bin/hledger")

    result = runner.invoke(app, ["books", "status", str(repo), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["hledger"]["available"] is True
    assert payload["vault"]["exists"] is True
    assert payload["vault"]["journal_placeholder"] == "present"
    assert "/fake/private/bin/hledger" not in result.output
    assert "PRIVATE_ACCOUNT_ID" not in result.output


def test_books_status_sanitizes_external_absolute_vault_path(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    private_path = tmp_path / "private-books" / "main.journal"
    _write(
        repo / "core/finance/books.md",
        f"""---
type: books
ledger: hledger
storage_mode: solo-local
vault_location: "{private_path.parent}"
---

# Books
""",
    )

    result = runner.invoke(app, ["books", "status", str(repo), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["vault"]["location"] == "external private path"
    assert str(private_path.parent) not in result.output


def test_books_check_status_and_doctor_flag_missing_external_vault_location(
    tmp_path: Path,
) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: team-private-repo
---

# Books
""",
    )
    _write(repo / ".gitignore", ".mb/private/\n*.journal\n*.hledger\n*.ledger\n*.beancount\n")

    check_result = runner.invoke(app, ["books", "check", str(repo), "--json"])
    assert check_result.exit_code == 0, check_result.output
    check_payload = json.loads(check_result.output)
    check_findings = _findings_by_id(check_payload)
    assert check_findings["books-vault-location-missing"]["state"] == "warn"

    status_result = runner.invoke(app, ["books", "status", str(repo), "--json"])
    assert status_result.exit_code == 0, status_result.output
    status_payload = json.loads(status_result.output)
    findings = _findings_by_id(status_payload)
    assert findings["books-vault-location-missing"]["state"] == "warn"
    assert status_payload["vault"]["location"] == "not configured"

    doctor_result = runner.invoke(app, ["books", "doctor", str(repo), "--plan", "--json"])
    assert doctor_result.exit_code == 0, doctor_result.output
    doctor_payload = json.loads(doctor_result.output)
    actions = {action["id"]: action for action in doctor_payload["actions"]}
    assert "configure-private-books-vault-location" in actions
    assert actions["configure-private-books-vault-location"]["writes"] == ["core/finance/books.md"]


def test_books_check_does_not_flag_configured_non_local_vault_location(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: team-private-repo
vault_location: "private-books-repo"
---

# Books
""",
    )

    result = runner.invoke(app, ["books", "check", str(repo), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    findings = _findings_by_id(payload)
    assert "books-vault-location-missing" not in findings


def test_books_doctor_plan_json_lists_safe_repairs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    _write(repo / "core/finance/main.journal", "; leaked real journal\n")
    _git_add_all(repo)
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "")

    result = runner.invoke(app, ["books", "doctor", str(repo), "--plan", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mb_command"] == "mb books doctor --plan"
    assert payload["result_schema"]["name"] == "mainbranch.books.doctor.plan.result"
    actions = {action["id"]: action for action in payload["actions"]}
    assert "install-hledger" in actions
    assert "create-private-books-vault" in actions
    assert "add-books-ignore-protections" in actions
    assert "move-unsafe-finance-artifacts" in actions
    assert "core/finance/main.journal" in actions["move-unsafe-finance-artifacts"]["evidence"]
    assert payload["safe_to_share"] is True


def test_books_doctor_plan_reports_missing_private_journal_placeholder(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(
        repo / "core/finance/books.md",
        """---
type: books
ledger: hledger
storage_mode: solo-local
vault_location: ".mb/private/books/"
---

# Books
""",
    )
    _write(repo / ".gitignore", ".mb/private/\n*.journal\n*.hledger\n*.ledger\n*.beancount\n")
    (repo / ".mb/private/books").mkdir(parents=True)

    result = runner.invoke(app, ["books", "doctor", str(repo), "--plan", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    actions = {action["id"]: action for action in payload["actions"]}
    assert "create-private-journal-placeholder" in actions
    assert actions["create-private-journal-placeholder"]["writes"] == [
        ".mb/private/books/main.journal"
    ]


def test_books_doctor_requires_plan(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "doctor", str(repo)])
    assert result.exit_code == 2
    assert "--plan is required" in result.output


def test_books_doctor_requires_plan_json_uses_plan_schema(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "doctor", str(repo), "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["result_schema"]["name"] == "mainbranch.books.doctor.plan.result"
    assert "--plan is required" in payload["summary"]


def test_books_status_cli_human_output_mentions_plan(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "status", str(repo)])
    assert result.exit_code == 0, result.output
    assert "mb books status" in result.output
    assert "Ignore rules:      missing" in result.output
    assert "Run `mb books doctor --plan`" in result.output


def test_books_doctor_plan_cli_human_output_formats_ignore_entries(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    result = runner.invoke(app, ["books", "doctor", str(repo), "--plan"])
    assert result.exit_code == 0, result.output
    assert "mb books doctor --plan" in result.output
    assert "Add books ignore protections" in result.output
    assert "plan: Add these lines to .gitignore: .mb/private/, *.journal" in result.output
    assert "`.mb/private/`" not in result.output


def test_books_check_packaged_fixtures_carry_marker() -> None:
    """The shipped fixtures must continue to carry an explicit marker.

    If a future edit drops the SAMPLE FIXTURE header we want the test
    suite to catch it immediately so the marker contract stays honest.
    """
    repo_root = Path(__file__).resolve().parents[2]
    for rel in (
        "docs/examples/books/acme-fixture.journal",
        "mb/mb/_data/books/acme-fixture.journal",
    ):
        assert books_mod._has_fixture_marker(repo_root / rel), rel


def test_bundled_fixture_matches_docs_fixture() -> None:
    """The packaged journal is a byte-identical mirror of the docs copy."""
    repo_root = Path(__file__).resolve().parents[2]
    docs_bytes = (repo_root / "docs/examples/books/acme-fixture.journal").read_bytes()
    pkg_bytes = (repo_root / "mb/mb/_data/books/acme-fixture.journal").read_bytes()
    assert docs_bytes == pkg_bytes, (
        "mb/mb/_data/books/acme-fixture.journal has drifted from "
        "docs/examples/books/acme-fixture.journal. Re-sync them."
    )
