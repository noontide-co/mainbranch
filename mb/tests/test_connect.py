"""``mb connect`` provider and credential foundation."""

from __future__ import annotations

import json
import stat
from pathlib import Path
from typing import Any

import yaml
from typer.testing import CliRunner

from mb import connect as connect_mod
from mb.cli import app

runner = CliRunner()


def _local_secret_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    for provider in connect_mod.PROVIDERS:
        for env_var in provider.env_vars:
            monkeypatch.delenv(env_var, raising=False)


def test_provider_registry_includes_initial_foundation() -> None:
    providers = {provider["id"]: provider for provider in connect_mod.provider_registry()}

    assert {
        "google",
        "meta",
        "cloudflare",
        "postiz",
        "apify",
        "beancount",
        "transcription",
    }.issubset(providers)
    assert providers["cloudflare"]["required_secrets"] == ["api_token"]
    assert providers["beancount"]["required_secrets"] == []


def test_connect_list_json_does_not_create_repo_metadata(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(app, ["connect", "list", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any(provider["id"] == "cloudflare" for provider in payload["providers"])
    cloudflare = next(
        provider for provider in payload["providers"] if provider["id"] == "cloudflare"
    )
    assert "low-lock-in rail" in cloudflare["why"]
    assert cloudflare["status_command"] == "mb connect status --all --json"
    assert not (repo / ".mb" / "connect.yaml").exists()


def test_connect_plan_returns_numbered_provider_choices(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    github_context = {
        "ok": False,
        "state": "unauthenticated",
        "summary": "GitHub CLI is installed but not authenticated.",
        "repair": "Run `gh auth login`.",
        "repair_command": "gh auth login",
        "safe_to_share": True,
    }
    monkeypatch.setattr(connect_mod, "github_context", lambda repo: github_context)

    result = runner.invoke(app, ["connect", "plan", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    steps = {step["id"]: step for step in payload["steps"]}
    assert list(steps) == ["github", "cloudflare", "google", "meta", "apify"]
    assert steps["github"]["next_command"] == "gh auth login"
    assert steps["github"]["safe_to_share"] is True
    assert steps["meta"]["next_command"] == "mb connect meta --token-stdin"
    assert payload["summary"]["total"] == 5
    assert not (repo / ".mb" / "connect.yaml").exists()


def test_connect_plan_human_output_uses_numbered_choices(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    github_context = {
        "ok": True,
        "state": "ready",
        "summary": "GitHub CLI auth and repo remote are ready.",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }
    monkeypatch.setattr(connect_mod, "github_context", lambda repo: github_context)

    result = runner.invoke(app, ["connect", "plan", "--repo", str(repo)])

    assert result.exit_code == 0
    assert "1. GitHub (ready)" in result.stdout
    assert "2. Cloudflare (not_connected)" in result.stdout
    assert "next: mb connect cloudflare --token-stdin" in result.stdout
    assert not (repo / ".mb" / "connect.yaml").exists()


def test_connect_provider_stores_secret_outside_repo(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--repo",
            str(repo),
            "--account",
            "Acme CF",
            "--token",
            "cf-test-token",
            "--metadata",
            "account_id=acct_123",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["ready"] is False
    assert payload["credential_backend"] == "local-file"
    assert payload["status"]["state"] == "unvalidated"
    assert payload["status"]["repair_command"] == "mb connect test cloudflare"

    config_path = repo / ".mb" / "connect.yaml"
    config_text = config_path.read_text(encoding="utf-8")
    assert "cf-test-token" not in config_text
    config = yaml.safe_load(config_text)
    cloudflare = config["providers"]["cloudflare"]
    assert cloudflare["metadata"] == {"account_id": "acct_123"}
    assert cloudflare["account_label"] == "Acme CF"

    secret_file = tmp_path / "home" / "secrets" / "connect.json"
    assert "cf-test-token" in secret_file.read_text(encoding="utf-8")
    assert stat.S_IMODE(secret_file.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(secret_file.stat().st_mode) == 0o600


def test_connect_provider_only_reads_env_when_explicit(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setenv("META_ACCESS_TOKEN", "meta-test-token")
    repo = tmp_path / "biz"
    repo.mkdir()

    implicit = runner.invoke(app, ["connect", "meta", "--repo", str(repo), "--json"])

    assert implicit.exit_code == 1
    implicit_payload = json.loads(implicit.stdout)
    assert implicit_payload["status"]["state"] == "missing_secret"

    explicit = runner.invoke(
        app,
        ["connect", "meta", "--repo", str(repo), "--from-env", "--json"],
    )

    assert explicit.exit_code == 0
    explicit_payload = json.loads(explicit.stdout)
    assert explicit_payload["credential_source"] == {
        "type": "env",
        "env_var": "META_ACCESS_TOKEN",
    }
    assert explicit_payload["status"]["state"] == "unvalidated"
    assert "meta-test-token" not in (repo / ".mb" / "connect.yaml").read_text(encoding="utf-8")


def test_connect_status_reports_missing_secret_as_repair_not_hard_crash(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(app, ["connect", "meta", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"]["state"] == "missing_secret"

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])
    assert status.exit_code == 1
    status_payload = json.loads(status.stdout)
    assert status_payload["summary"]["needs_repair"] == 1
    assert status_payload["providers"][0]["secrets"]["access_token"]["present"] is False
    assert status_payload["providers"][0]["state"] == "missing_secret"
    assert status_payload["providers"][0]["repair_command"] == "mb connect meta --token-stdin"
    assert status_payload["providers"][0]["safe_to_share"] is True


def test_connect_status_reports_unvalidated_secret_without_claiming_health(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        ["connect", "cloudflare", "--repo", str(repo), "--token", "cf-test-token", "--json"],
    )

    assert result.exit_code == 0
    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])
    assert status.exit_code == 1
    payload = json.loads(status.stdout)
    provider = payload["providers"][0]
    assert payload["summary"]["configured"] == 1
    assert payload["summary"]["healthy"] == 0
    assert payload["summary"]["unvalidated"] == 1
    assert provider["state"] == "unvalidated"
    assert provider["summary"]
    assert provider["repair"] == "Run `mb connect test cloudflare`."
    assert provider["repair_command"] == "mb connect test cloudflare"
    assert provider["safe_to_share"] is True
    assert "cf-test-token" not in status.stdout


def test_connect_test_marks_metadata_only_provider_ready(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "beancount", repo=repo, metadata_pairs=["ledger_path=core/finance/main.bean"]
    )

    result = runner.invoke(app, ["connect", "test", "beancount", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"]["state"] == "ready"
    assert payload["status"]["repair_command"] == ""


def test_connect_test_records_invalid_provider_without_leaking_secret(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        ["connect", "cloudflare", "--repo", str(repo), "--token", "cf-secret-token", "--json"],
    )
    monkeypatch.setattr(
        connect_mod,
        "_http_get_json",
        lambda url, headers=None: ("invalid", "provider rejected the credential"),
    )

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["status"]["state"] == "invalid"
    assert payload["status"]["repair_command"] == "mb connect cloudflare --token-stdin"
    assert payload["status"]["validation"]["summary"] == "provider rejected the credential"
    assert "cf-secret-token" not in result.stdout


def test_connect_test_no_probe_provider_reaches_ready_without_loop(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(app, ["connect", "google", "--repo", str(repo), "--token", "google-token"])

    result = runner.invoke(app, ["connect", "test", "google", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"]["state"] == "ready"
    assert payload["status"]["repair_command"] == ""
    assert "no automated safe validation probe" in payload["validation"]["summary"]
    assert "google-token" not in result.stdout

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])
    assert status.exit_code == 0
    status_payload = json.loads(status.stdout)
    assert status_payload["summary"]["healthy"] == 1
    assert status_payload["summary"]["needs_repair"] == 0
    assert status_payload["providers"][0]["state"] == "ready"


def test_connect_test_transient_provider_failure_stays_unvalidated(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(app, ["connect", "cloudflare", "--repo", str(repo), "--token", "cf-secret-token"])
    monkeypatch.setattr(
        connect_mod,
        "_http_get_json",
        lambda url, headers=None: ("unvalidated", "provider validation returned HTTP 503"),
    )

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["status"]["state"] == "unvalidated"
    assert payload["status"]["repair_command"] == "mb connect test cloudflare"
    assert payload["status"]["validation"]["summary"] == "provider validation returned HTTP 503"
    assert "cf-secret-token" not in result.stdout


def test_connect_doctor_includes_github_context_and_provider_repairs(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(app, ["connect", "meta", "--repo", str(repo), "--json"])
    monkeypatch.setattr(connect_mod.shutil, "which", lambda name: "")

    result = runner.invoke(app, ["connect", "doctor", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["github-context"]["state"] == "missing_cli"
    assert checks["provider:meta"]["state"] == "missing_secret"
    assert checks["provider:meta"]["repair_command"] == "mb connect meta --token-stdin"
    assert payload["safe_to_share"] is True


def test_github_context_distinguishes_missing_remote(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        connect_mod.shutil, "which", lambda name: "/usr/bin/gh" if name == "gh" else ""
    )

    def fake_run(args: list[str], cwd: Path | None = None, timeout: float = 5.0) -> dict[str, Any]:
        if args[:3] == ["gh", "auth", "status"]:
            return {"ok": True, "returncode": 0, "stdout": "", "stderr": ""}
        if args[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
            return {"ok": True, "returncode": 0, "stdout": "true\n", "stderr": ""}
        if args[:4] == ["git", "config", "--get", "remote.origin.url"]:
            return {"ok": False, "returncode": 1, "stdout": "", "stderr": ""}
        raise AssertionError(args)

    monkeypatch.setattr(connect_mod, "_run_command", fake_run)

    context = connect_mod.github_context(tmp_path)

    assert context["ok"] is False
    assert context["state"] == "missing_github_remote"
    assert context["repair_command"] == "gh repo create --source . --remote origin --push"


def test_status_all_reuses_supplied_github_context(monkeypatch, tmp_path: Path) -> None:
    context = {
        "ok": True,
        "state": "ready",
        "summary": "cached GitHub context",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }

    def fail_context(repo: Path) -> dict[str, Any]:
        raise AssertionError("github_context should not be recomputed")

    monkeypatch.setattr(connect_mod, "github_context", fail_context)

    status = connect_mod.status_all(tmp_path, github=context)

    assert status["github"] == context


def test_connect_status_tolerates_malformed_config_version(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    (repo / ".mb").mkdir()
    (repo / ".mb" / "connect.yaml").write_text(
        "version: not-a-number\nproviders: []\n",
        encoding="utf-8",
    )

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])

    assert status.exit_code == 0
    status_payload = json.loads(status.stdout)
    assert status_payload["summary"]["configured"] == 0


def test_doctor_and_status_include_integration_state(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "beancount", repo=repo, metadata_pairs=["ledger_path=core/finance/main.bean"]
    )

    doctor_report = runner.invoke(app, ["doctor", str(repo), "--json"])
    doctor_payload = json.loads(doctor_report.stdout)
    assert doctor_payload["integrations"]["summary"]["configured"] == 1
    assert "integration-credentials" in {check["name"] for check in doctor_payload["checks"]}

    status_report = runner.invoke(app, ["status", str(repo), "--json"])
    assert status_report.exit_code == 0
    status_payload = json.loads(status_report.stdout)
    assert status_payload["integrations"]["summary"]["healthy"] == 1


def test_macos_keychain_backend_uses_security(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], **kwargs: Any) -> Any:
        calls.append(args)

        class Result:
            returncode = 0
            stdout = ""

        return Result()

    monkeypatch.setattr(connect_mod.subprocess, "run", fake_run)

    store = connect_mod.SecretStore("macos-keychain")
    store.set("mainbranch://test/cloudflare/api_token", "cf-token")

    assert calls
    assert calls[0][:3] == ["security", "add-generic-password", "-a"]
    assert "cf-token" in calls[0]
