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
    assert leak["state"] == "error"
    assert leak["audience"] == "operator_decision"
    assert "core/finance/main.journal" in leak["evidence"]
    assert report["ok"] is False
    assert report["state"] == "error"


def test_books_check_flags_committed_csv_statement(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(repo / "imports/bank-2026-01.csv", "date,amount\n")
    _git_add_all(repo)

    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    assert findings["unsafe-paths-detected"]["state"] == "error"
    assert "imports/bank-2026-01.csv" in findings["unsafe-paths-detected"]["evidence"]


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


def test_books_check_fixture_runs_when_hledger_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)

    monkeypatch.setattr("mb.books.shutil.which", lambda name: "/fake/hledger")

    class _FakeCompleted:
        returncode = 0
        stdout = ""
        stderr = ""

    def _fake_run(*args: Any, **kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted()

    monkeypatch.setattr("mb.books.subprocess.run", _fake_run)

    report = books_mod.run(repo=str(repo), validate_fixture=True)
    findings = _findings_by_id(report)
    assert findings["fixture-valid"]["state"] == "ok"


def test_books_check_fixture_reports_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_business_repo(tmp_path)
    monkeypatch.setattr("mb.books.shutil.which", lambda name: "/fake/hledger")

    class _Failed:
        returncode = 1
        stdout = ""
        stderr = "balance assertion failed"

    monkeypatch.setattr("mb.books.subprocess.run", lambda *a, **k: _Failed())

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
    repo = _init_business_repo(tmp_path)
    _write(repo / "core/finance/main.journal", "; leak\n")
    _git_add_all(repo)
    result = runner.invoke(app, ["books", "check", str(repo)])
    assert result.exit_code == 1, result.output
    assert "FAIL" in result.output


def test_books_check_engine_fixture_paths_are_ignored(tmp_path: Path) -> None:
    repo = _init_business_repo(tmp_path)
    _write(repo / "docs/examples/books/acme.journal", "; engine fixture\n")
    _write(repo / "mb/mb/_data/books/acme-fixture.journal", "; pkg fixture\n")
    _git_add_all(repo)
    report = books_mod.run(repo=str(repo))
    findings = _findings_by_id(report)
    # Engine-fixture-shaped paths are skipped on purpose.
    assert "unsafe-paths-detected" not in findings
    assert findings["unsafe-paths-clean"]["state"] == "ok"
