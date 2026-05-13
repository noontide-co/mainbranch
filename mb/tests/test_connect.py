"""``mb connect`` provider and credential foundation."""

from __future__ import annotations

import json
import stat
import sys
from pathlib import Path
from typing import Any

import pytest
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


def _connect_meta_ready_prereqs(monkeypatch) -> None:
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")


def _fake_meta_which(name: str) -> str | None:
    if name in {"meta", "python3.12"}:
        return f"/usr/bin/{name}"
    return None


def test_provider_registry_includes_initial_foundation() -> None:
    providers = {provider["id"]: provider for provider in connect_mod.provider_registry()}

    assert {
        "google",
        "meta",
        "cloudflare",
        "postiz",
        "apify",
        "hledger",
        "transcription",
    }.issubset(providers)
    assert "beancount" not in providers
    assert providers["cloudflare"]["required_secrets"] == ["api_token"]
    assert providers["meta"]["auth"] == "meta_ads_cli_read_only"
    assert providers["meta"]["required_secrets"] == ["access_token"]
    assert "ACCESS_TOKEN" in providers["meta"]["env_vars"]
    assert providers["hledger"]["required_secrets"] == []
    assert providers["hledger"]["metadata_fields"] == [
        "journal_path",
        "vault_path",
    ]


def test_connect_list_json_does_not_create_repo_metadata(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "missing_cli")
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(app, ["connect", "list", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any(provider["id"] == "cloudflare" for provider in payload["providers"])
    meta = next(provider for provider in payload["providers"] if provider["id"] == "meta")
    assert meta["auth"] == "meta_ads_cli_read_only"
    cloudflare = next(
        provider for provider in payload["providers"] if provider["id"] == "cloudflare"
    )
    assert "low-lock-in rail" in cloudflare["why"]
    assert cloudflare["status_command"] == "mb connect doctor --json"
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
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "missing_cli")

    result = runner.invoke(app, ["connect", "plan", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    steps = {step["id"]: step for step in payload["steps"]}
    assert list(steps) == ["github", "cloudflare", "google", "meta", "apify"]
    assert steps["github"]["next_command"] == "gh auth login"
    assert steps["github"]["safe_to_share"] is True
    assert steps["meta"]["state"] == "missing_cli"
    assert steps["meta"]["next_command"] == "pipx install --python <python3.12-or-newer> meta-ads"
    assert payload["summary"]["total"] == 5
    assert not (repo / ".mb" / "connect.yaml").exists()


def test_connect_meta_token_stdin_stores_secret_outside_repo(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "connect",
            "meta",
            "--repo",
            str(repo),
            "--token-stdin",
            "--metadata",
            "ad_account_id=act_test",
            "--account",
            "Meta Test",
            "--json",
        ],
        input="meta-secret-token\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"]["state"] == "unvalidated"
    assert payload["credential_source"]["type"] == "stdin"
    assert "Meta Business Portfolio" in payload["setup"]["requirements"][0]
    assert "Business portfolio ID" in payload["setup"]["requirements"][2]
    assert "act_" in payload["setup"]["safe_metadata"][0]
    assert "Business portfolio ID" in payload["setup"]["safe_metadata"][1]

    config_text = (repo / ".mb" / "connect.yaml").read_text(encoding="utf-8")
    assert "meta-secret-token" not in config_text
    config = yaml.safe_load(config_text)
    meta = config["providers"]["meta"]
    assert meta["metadata"] == {"ad_account_id": "act_test"}
    assert meta["account_label"] == "Meta Test"
    assert meta["secrets"]["access_token"]["backend"] == "local-file"

    secret_file = tmp_path / "home" / "secrets" / "connect.json"
    assert "meta-secret-token" in secret_file.read_text(encoding="utf-8")


def test_meta_status_preserves_stale_metadata_but_reports_missing_secret(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")
    repo = tmp_path / "biz"
    repo.mkdir()
    config_path = repo / ".mb" / "connect.yaml"
    config_path.parent.mkdir()
    config_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "repo_id": "repo",
                "providers": {
                    "meta": {
                        "provider": "meta",
                        "connected": True,
                        "account_label": "Old Meta",
                        "metadata": {"ad_account_id": "act_123"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    status = connect_mod.status_provider("meta", repo)

    assert status["state"] == "missing_secret"
    assert status["connected"] is True
    assert status["repair_command"] == (
        "mb connect meta --token-stdin --metadata ad_account_id=<act_id>"
    )
    assert status["metadata"] == {"ad_account_id": "act_123"}

    aggregate = connect_mod.status_all(repo)
    assert aggregate["ok"] is False
    assert aggregate["summary"]["configured"] == 1
    assert aggregate["summary"]["needs_repair"] == 1
    assert aggregate["providers"][0]["state"] == "missing_secret"

    check = connect_mod.doctor_check(repo, status=aggregate)
    assert check["ok"] is False
    assert "meta" in check["detail"]


def test_connect_test_meta_reports_missing_metadata(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    _connect_meta_ready_prereqs(monkeypatch)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        ["connect", "meta", "--repo", str(repo), "--token", "meta-secret-token"],
    )

    result = runner.invoke(app, ["connect", "test", "meta", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"]["state"] == "missing_metadata"
    assert (
        payload["status"]["repair_command"] == "mb connect meta --metadata ad_account_id=<act_id>"
    )
    assert "meta-secret-token" not in result.stdout


def test_connect_test_meta_missing_cli_has_python312_repair(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test"],
    )

    result = connect_mod.test_provider(
        "meta",
        repo,
        which_func=lambda name: "/usr/bin/python3.12" if name == "python3.12" else None,
        command_runner=lambda args, cwd=None, timeout=5.0: {
            "ok": True,
            "returncode": 0,
            "stdout": "3.12\n",
            "stderr": "",
        },
    )

    assert result["ok"] is False
    assert result["status"]["state"] == "missing_cli"
    assert result["status"]["repair_command"] == (
        "pipx install --python <python3.12-or-newer> meta-ads"
    )


def test_connect_test_meta_uses_installed_cli_before_python_repair(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setattr(sys, "version_info", (3, 11))
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test"],
    )
    calls: list[list[str]] = []

    def fake_run(
        args: list[str],
        cwd: Path | None = None,
        timeout: float = 5.0,
        *,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        calls.append(args)
        if args == ["meta", "--version"]:
            return {"ok": True, "returncode": 0, "stdout": "meta 1.0.1\n", "stderr": ""}
        return {"ok": True, "returncode": 0, "stdout": "{}\n", "stderr": ""}

    result = connect_mod.test_provider(
        "meta",
        repo,
        which_func=lambda name: "/opt/pipx/bin/meta" if name == "meta" else None,
        command_runner=fake_run,
    )

    assert result["ok"] is True
    assert result["status"]["state"] == "ready"
    assert calls[0] == ["meta", "--version"]
    assert all("python" not in call[0] for call in calls)


def test_connect_test_meta_read_only_smoke_passes_with_sanitized_env(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test", "business_id=biz_test"],
    )
    calls: list[tuple[list[str], dict[str, str]]] = []

    def fake_run(
        args: list[str],
        cwd: Path | None = None,
        timeout: float = 5.0,
        *,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if args == ["meta", "--version"]:
            return {"ok": True, "returncode": 0, "stdout": "meta 1.0.1\n", "stderr": ""}
        calls.append((args, env or {}))
        return {"ok": True, "returncode": 0, "stdout": "{}\n", "stderr": ""}

    result = connect_mod.test_provider(
        "meta",
        repo,
        which_func=_fake_meta_which,
        command_runner=fake_run,
    )

    assert result["ok"] is True
    assert result["status"]["state"] == "ready"
    assert [call[0] for call in calls] == [
        ["meta", "auth", "status"],
        ["meta", "-o", "json", "ads", "adaccount", "list"],
        ["meta", "-o", "json", "ads", "campaign", "list"],
        [
            "meta",
            "-o",
            "json",
            "ads",
            "insights",
            "get",
            "--fields",
            "spend,impressions,clicks,ctr,cpc",
        ],
        ["meta", "-o", "json", "ads", "dataset", "list"],
    ]
    assert calls[0][1]["ACCESS_TOKEN"] == "meta-secret-token"
    assert calls[0][1]["AD_ACCOUNT_ID"] == "act_test"
    assert calls[0][1]["BUSINESS_ID"] == "biz_test"
    assert "meta-secret-token" not in json.dumps(result)


def test_connect_test_meta_admin_approval_state(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test"],
    )

    def fake_run(
        args: list[str],
        cwd: Path | None = None,
        timeout: float = 5.0,
        *,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if args == ["meta", "--version"]:
            return {"ok": True, "returncode": 0, "stdout": "meta 1.0.1\n", "stderr": ""}
        return {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": "Waiting for another business admin approval.",
        }

    result = connect_mod.test_provider(
        "meta",
        repo,
        which_func=_fake_meta_which,
        command_runner=fake_run,
    )

    assert result["ok"] is False
    assert result["status"]["state"] == "waiting_for_admin_approval"
    assert result["status"]["summary"] == (
        "Meta needs another business admin to approve this connection."
    )
    assert result["status"]["repair"] == (
        "Meta needs another business admin to approve this connection. Nothing is broken locally."
    )


def test_connect_test_meta_read_smoke_failure_state(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test"],
    )
    calls: list[list[str]] = []

    def fake_run(
        args: list[str],
        cwd: Path | None = None,
        timeout: float = 5.0,
        *,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if args == ["meta", "--version"]:
            return {"ok": True, "returncode": 0, "stdout": "meta 1.0.1\n", "stderr": ""}
        calls.append(args)
        ok = args == ["meta", "auth", "status"]
        return {
            "ok": ok,
            "returncode": 0 if ok else 1,
            "stdout": "{}\n" if ok else "",
            "stderr": "" if ok else "permission denied",
        }

    result = connect_mod.test_provider(
        "meta",
        repo,
        which_func=_fake_meta_which,
        command_runner=fake_run,
    )

    assert result["ok"] is False
    assert result["status"]["state"] == "read_smoke_failed"
    assert calls == [
        ["meta", "auth", "status"],
        ["meta", "-o", "json", "ads", "adaccount", "list"],
    ]


def test_status_peek_exposes_meta_integration_state(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        metadata_pairs=["ad_account_id=act_test"],
    )

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    meta = payload["integrations"]["providers"][0]
    assert meta["provider"] == "meta"
    assert meta["state"] == "unvalidated"
    assert meta["repair_command"] == "mb connect test meta"
    assert "meta-secret-token" not in result.stdout


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
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "missing_cli")

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
    assert config["repo_identity"]["source"] in {"git_common_dir", "path"}

    secret_file = tmp_path / "home" / "secrets" / "connect.json"
    assert "cf-test-token" in secret_file.read_text(encoding="utf-8")
    assert stat.S_IMODE(secret_file.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(secret_file.stat().st_mode) == 0o600


def test_connect_repo_identity_is_stable_across_worktrees(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    first = tmp_path / "biz-one"
    second = tmp_path / "biz-two"
    first.mkdir()
    second.mkdir()

    def fake_git(repo: Path, args: list[str]) -> str:
        if args == ["config", "--get", "remote.origin.url"]:
            return "git@github.com:acme/business.git"
        return ""

    monkeypatch.setattr(connect_mod, "_git_output", fake_git)

    connect_mod.connect_provider("cloudflare", repo=first, token="first-token")
    connect_mod.connect_provider("cloudflare", repo=second, token="second-token")

    first_config = yaml.safe_load((first / ".mb" / "connect.yaml").read_text(encoding="utf-8"))
    second_config = yaml.safe_load((second / ".mb" / "connect.yaml").read_text(encoding="utf-8"))
    assert first_config["repo_id"] == second_config["repo_id"]
    assert first_config["repo_identity"]["source"] == "git_remote"
    assert (
        first_config["providers"]["cloudflare"]["secrets"]["api_token"]["ref"]
        == second_config["providers"]["cloudflare"]["secrets"]["api_token"]["ref"]
    )


def test_connect_normalizes_common_remote_protocol_variants() -> None:
    assert connect_mod._normalized_remote("git@gitlab.com:team/business.git") == (
        "https://gitlab.com/team/business"
    )
    assert connect_mod._normalized_remote("ssh://git@gitlab.com/team/business.git") == (
        "https://gitlab.com/team/business"
    )
    assert connect_mod._normalized_remote("https://gitlab.com/team/business.git") == (
        "https://gitlab.com/team/business"
    )


def test_connect_preserves_existing_repo_id_to_avoid_orphaned_secrets(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    (repo / ".mb").mkdir(parents=True)
    (repo / ".mb" / "connect.yaml").write_text(
        yaml.safe_dump({"version": 1, "repo_id": "legacy-random-id", "providers": {}}),
        encoding="utf-8",
    )

    connect_mod.connect_provider("cloudflare", repo=repo, token="cf-secret-token")

    config = yaml.safe_load((repo / ".mb" / "connect.yaml").read_text(encoding="utf-8"))
    assert config["repo_id"] == "legacy-random-id"
    assert config["repo_identity"]["repo_id_source"] == "existing_config"
    assert config["providers"]["cloudflare"]["secrets"]["api_token"]["ref"] == (
        connect_mod._secret_ref("legacy-random-id", "cloudflare", "api_token")
    )


def test_connect_provider_only_reads_env_when_explicit(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setenv("APIFY_TOKEN", "apify-test-token")
    repo = tmp_path / "biz"
    repo.mkdir()

    implicit = runner.invoke(app, ["connect", "apify", "--repo", str(repo), "--json"])

    assert implicit.exit_code == 1
    implicit_payload = json.loads(implicit.stdout)
    assert implicit_payload["status"]["state"] == "missing_secret"

    explicit = runner.invoke(
        app,
        ["connect", "apify", "--repo", str(repo), "--from-env", "--json"],
    )

    assert explicit.exit_code == 0
    explicit_payload = json.loads(explicit.stdout)
    assert explicit_payload["credential_source"] == {
        "type": "env",
        "env_var": "APIFY_TOKEN",
    }
    assert explicit_payload["status"]["state"] == "unvalidated"
    assert "apify-test-token" not in (repo / ".mb" / "connect.yaml").read_text(encoding="utf-8")


def test_connect_status_reports_missing_secret_as_repair_not_hard_crash(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(app, ["connect", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"]["state"] == "missing_secret"

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])
    assert status.exit_code == 1
    status_payload = json.loads(status.stdout)
    assert status_payload["summary"]["needs_repair"] == 1
    assert status_payload["providers"][0]["secrets"]["api_token"]["present"] is False
    assert status_payload["providers"][0]["state"] == "missing_secret"
    assert status_payload["providers"][0]["repair_command"] == "mb connect cloudflare --token-stdin"
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
        "hledger",
        repo=repo,
        metadata_pairs=[
            "journal_path=.mb/private/books/main.journal",
            "vault_path=.mb/private/books/",
        ],
    )

    result = runner.invoke(app, ["connect", "test", "hledger", "--repo", str(repo), "--json"])

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
        lambda url, headers=None, **kwargs: {
            "ok": False,
            "state": "invalid",
            "summary": "Cloudflare rejected the credential. Create a fresh token and reconnect it.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs["endpoint_family"],
                "http_status": 403,
                "response_received": True,
                "error_codes": ["9109"],
                "error_messages": ["Invalid access token"],
                "safe_to_share": True,
            },
        },
    )

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["status"]["state"] == "invalid"
    assert payload["status"]["repair_command"] == "mb connect cloudflare --token-stdin"
    assert "rejected the credential" in payload["status"]["validation"]["summary"]
    assert payload["validation"]["upstream"]["endpoint_family"] == "cloudflare_user_token_verify"
    assert payload["validation"]["upstream"]["http_status"] == 403
    assert payload["validation"]["upstream"]["error_codes"] == ["9109"]
    assert "cf-secret-token" not in result.stdout


def test_connect_test_routes_cloudflare_account_tokens_to_account_endpoint(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--repo",
            str(repo),
            "--token",
            "cf-secret-token",
            "--metadata",
            "token_type=account",
            "--metadata",
            "account_id=0123456789abcdef0123456789abcdef",
        ],
    )
    calls: list[str] = []

    def fake_http(url: str, headers=None, **kwargs) -> dict[str, Any]:
        calls.append(url)
        return {
            "ok": True,
            "state": "ready",
            "summary": "Cloudflare credential validated with provider.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs["endpoint_family"],
                "http_status": 200,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        }

    monkeypatch.setattr(connect_mod, "_http_get_json", fake_http)

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["validation"]["upstream"]["endpoint_family"] == "cloudflare_account_token_verify"
    assert calls == [
        "https://api.cloudflare.com/client/v4/accounts/0123456789abcdef0123456789abcdef/tokens/verify"
    ]


def test_connect_test_detects_cloudflare_account_token_prefix(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--repo",
            str(repo),
            "--token",
            "cfat_secret-token",
            "--metadata",
            "account_id=0123456789abcdef0123456789abcdef",
        ],
    )
    calls: list[str] = []

    def fake_http(url: str, headers=None, **kwargs) -> dict[str, Any]:
        calls.append(url)
        return {
            "ok": True,
            "state": "ready",
            "summary": "Cloudflare credential validated with provider.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs["endpoint_family"],
                "http_status": 200,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        }

    monkeypatch.setattr(connect_mod, "_http_get_json", fake_http)

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["validation"]["upstream"]["endpoint_family"] == (
        "cloudflare_account_token_verify"
    )
    assert calls == [
        "https://api.cloudflare.com/client/v4/accounts/0123456789abcdef0123456789abcdef/tokens/verify"
    ]


def test_connect_test_routes_cloudflare_user_tokens_to_user_endpoint(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        ["connect", "cloudflare", "--repo", str(repo), "--token", "cf-secret-token"],
    )
    calls: list[str] = []

    def fake_http(url: str, headers=None, **kwargs) -> dict[str, Any]:
        calls.append(url)
        return {
            "ok": True,
            "state": "ready",
            "summary": "Cloudflare credential validated with provider.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs["endpoint_family"],
                "http_status": 200,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        }

    monkeypatch.setattr(connect_mod, "_http_get_json", fake_http)

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["validation"]["upstream"]["endpoint_family"] == "cloudflare_user_token_verify"
    assert calls == ["https://api.cloudflare.com/client/v4/user/tokens/verify"]


def test_connect_test_account_token_uses_account_read_fallback_on_verify_404(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--repo",
            str(repo),
            "--token",
            "cf-secret-token",
            "--metadata",
            "token_type=account",
            "--metadata",
            "account_id=0123456789abcdef0123456789abcdef",
        ],
    )
    calls: list[tuple[str, str]] = []

    def fake_http(url: str, headers=None, **kwargs) -> dict[str, Any]:
        endpoint = kwargs["endpoint_family"]
        calls.append((endpoint, url))
        if endpoint == "cloudflare_account_token_verify":
            return {
                "ok": False,
                "state": "invalid",
                "summary": "Cloudflare could not find the requested account/token resource.",
                "safe_to_share": True,
                "upstream": {
                    "endpoint_family": endpoint,
                    "http_status": 404,
                    "response_received": True,
                    "error_codes": ["1003"],
                    "error_messages": ["Not found"],
                    "safe_to_share": True,
                },
            }
        return {
            "ok": True,
            "state": "ready",
            "summary": "Cloudflare credential validated with provider.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": endpoint,
                "http_status": 200,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        }

    monkeypatch.setattr(connect_mod, "_http_get_json", fake_http)

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["validation"]["upstream"]["endpoint_family"] == "cloudflare_account_read"
    assert payload["validation"]["upstream"]["fallback_from"] == "cloudflare_account_token_verify"
    assert "fallback" in payload["validation"]["summary"]
    assert calls == [
        (
            "cloudflare_account_token_verify",
            "https://api.cloudflare.com/client/v4/accounts/0123456789abcdef0123456789abcdef/tokens/verify",
        ),
        (
            "cloudflare_account_read",
            "https://api.cloudflare.com/client/v4/accounts/0123456789abcdef0123456789abcdef",
        ),
    ]


def test_connect_test_account_token_requires_account_id(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--repo",
            str(repo),
            "--token",
            "cf-secret-token",
            "--metadata",
            "token_type=account",
        ],
    )

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"]["state"] == "unvalidated"
    assert payload["status"]["repair_command"] == (
        "mb connect cloudflare --metadata token_type=account --metadata account_id=<account-id>"
    )
    assert "account_id" in payload["validation"]["summary"]
    assert payload["validation"]["repair_command"] == (
        "mb connect cloudflare --metadata token_type=account --metadata account_id=<account-id>"
    )
    assert payload["validation"]["upstream"]["response_received"] is False


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
        lambda url, headers=None, **kwargs: {
            "ok": False,
            "state": "unvalidated",
            "summary": (
                "Cloudflare validation returned HTTP 503. Retry after the provider recovers."
            ),
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs["endpoint_family"],
                "http_status": 503,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        },
    )

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["status"]["state"] == "unvalidated"
    assert payload["status"]["repair_command"] == "mb connect test cloudflare"
    assert "HTTP 503" in payload["status"]["validation"]["summary"]
    assert "cf-secret-token" not in result.stdout


def test_token_stdin_prints_interactive_eof_prompt(monkeypatch, capsys) -> None:
    class FakeStdin:
        def isatty(self) -> bool:
            return True

        def read(self) -> str:
            return "secret-token\n"

    monkeypatch.setattr(sys, "stdin", FakeStdin())

    token = connect_mod.read_stdin_token()

    assert token == "secret-token"
    assert "Ctrl-D" in capsys.readouterr().err


def test_connect_doctor_includes_github_context_and_provider_repairs(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    runner.invoke(app, ["connect", "cloudflare", "--repo", str(repo), "--json"])
    monkeypatch.setattr(connect_mod.shutil, "which", lambda name: "")  # type: ignore[attr-defined]

    result = runner.invoke(app, ["connect", "doctor", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["github-context"]["state"] == "missing_cli"
    assert checks["provider:cloudflare"]["state"] == "missing_secret"
    assert checks["provider:cloudflare"]["repair_command"] == "mb connect cloudflare --token-stdin"
    assert payload["safe_to_share"] is True


def test_github_context_distinguishes_missing_remote(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        connect_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/usr/bin/gh" if name == "gh" else "",
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


def test_connect_status_missing_config_still_reports_empty_state(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])

    assert status.exit_code == 0
    payload = json.loads(status.stdout)
    assert payload["summary"]["configured"] == 0
    assert not (repo / ".mb" / "connect.yaml").exists()


def test_connect_refuses_symlinked_mb_directory_without_leaking_path(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    (repo / ".mb").symlink_to(outside, target_is_directory=True)

    result = runner.invoke(
        app,
        [
            "connect",
            "hledger",
            "--repo",
            str(repo),
            "--metadata",
            "vault_path=.mb/private/books",
            "--json",
        ],
    )

    assert result.exit_code == 2
    assert "local state path is a symlink" in result.stderr
    assert str(tmp_path) not in result.stderr
    assert not (outside / "connect.yaml").exists()


def test_connect_refuses_symlinked_connect_yaml_without_leaking_path(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    (repo / ".mb").mkdir()
    (repo / ".mb" / "connect.yaml").symlink_to(outside / "connect.yaml")

    result = runner.invoke(
        app,
        [
            "connect",
            "hledger",
            "--repo",
            str(repo),
            "--metadata",
            "vault_path=.mb/private/books",
            "--json",
        ],
    )

    assert result.exit_code == 2
    assert "local state path is a symlink" in result.stderr
    assert str(tmp_path) not in result.stderr
    assert not (outside / "connect.yaml").exists()


def test_connect_status_refuses_config_that_resolves_outside_repo(
    tmp_path: Path, monkeypatch
) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    (outside / "connect.yaml").write_text(
        yaml.safe_dump({"version": 1, "providers": {"hledger": {"connected": True}}}),
        encoding="utf-8",
    )
    (repo / ".mb").symlink_to(outside, target_is_directory=True)

    status = runner.invoke(app, ["connect", "status", "--repo", str(repo), "--json"])

    assert status.exit_code == 2
    assert "local state path is a symlink" in status.stderr
    assert str(tmp_path) not in status.stderr


def test_checked_connect_config_path_rejects_outside_boundary(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "biz"
    outside = tmp_path / "outside" / "connect.yaml"
    repo.mkdir()
    outside.parent.mkdir()
    monkeypatch.setattr(connect_mod, "_config_path", lambda repo: outside)

    with pytest.raises(connect_mod.ConfigBoundaryError) as exc_info:
        connect_mod.status_all(repo)

    assert str(exc_info.value) == (
        "Refusing to use .mb/connect.yaml because it is outside the selected repo boundary."
    )
    assert str(tmp_path) not in str(exc_info.value)


def test_checked_connect_config_path_rejects_invalid_local_state_directory(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    (repo / ".mb").write_text("not a directory", encoding="utf-8")

    with pytest.raises(connect_mod.ConfigBoundaryError, match="local state directory is invalid"):
        connect_mod.status_all(repo)


def test_doctor_and_status_include_integration_state(tmp_path: Path, monkeypatch) -> None:
    _local_secret_env(monkeypatch, tmp_path)
    repo = tmp_path / "biz"
    repo.mkdir()
    connect_mod.connect_provider(
        "hledger",
        repo=repo,
        metadata_pairs=[
            "journal_path=.mb/private/books/main.journal",
            "vault_path=.mb/private/books/",
        ],
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

    monkeypatch.setattr(connect_mod.subprocess, "run", fake_run)  # type: ignore[attr-defined]

    store = connect_mod.SecretStore("macos-keychain")
    store.set("mainbranch://test/cloudflare/api_token", "cf-token")

    assert calls
    assert calls[0][:3] == ["security", "add-generic-password", "-a"]
    assert "cf-token" in calls[0]
