"""``mb ads`` read-only account summaries."""

from __future__ import annotations

import json
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


def _ready_meta_repo(tmp_path: Path, monkeypatch, *, include_business_id: bool = True) -> Path:
    _local_secret_env(monkeypatch, tmp_path)
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")
    repo = tmp_path / "biz"
    repo.mkdir()
    metadata_pairs = ["ad_account_id=act_123456789"]
    if include_business_id:
        metadata_pairs.append("business_id=biz_987654321")
    connect_mod.connect_provider(
        "meta",
        repo=repo,
        token="meta-secret-token",
        account_label="Primary Meta",
        metadata_pairs=metadata_pairs,
    )
    config_path = repo / ".mb" / "connect.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    meta = config["providers"]["meta"]
    meta["validation"] = {
        "state": "ready",
        "checked_at": "2026-05-13T00:00:00Z",
        "summary": "Meta read-only account smoke passed.",
        "safe_to_share": True,
    }
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return repo


def _fake_meta_runner(calls: list[list[str]]):
    def fake_run(
        args: list[str],
        cwd: Path | None = None,
        timeout: float = 5.0,
        *,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        calls.append(args)
        assert env is not None
        assert env["ACCESS_TOKEN"] == "meta-secret-token"
        assert env["AD_ACCOUNT_ID"] == "act_123456789"
        if "BUSINESS_ID" in env:
            assert env["BUSINESS_ID"] == "biz_987654321"
        if args[:4] == ["meta", "-o", "json", "ads"] and args[4:6] == [
            "adaccount",
            "list",
        ]:
            stdout = json.dumps(
                {
                    "data": [
                        {
                            "id": "act_123456789",
                            "name": "Private account name",
                            "currency": "USD",
                            "timezone_name": "America/Los_Angeles",
                        }
                    ]
                }
            )
        elif args[:4] == ["meta", "-o", "json", "ads"] and args[4:6] == [
            "campaign",
            "list",
        ]:
            stdout = json.dumps(
                {
                    "data": [
                        {
                            "id": "111",
                            "name": "Spring private campaign",
                            "effective_status": "ACTIVE",
                        },
                        {
                            "id": "222",
                            "name": "Old private campaign",
                            "effective_status": "PAUSED",
                        },
                    ]
                }
            )
        elif args[:4] == ["meta", "-o", "json", "ads"] and args[4:6] == [
            "insights",
            "get",
        ]:
            stdout = json.dumps({"data": [{"spend": "123.45"}]})
        elif args[:4] == ["meta", "-o", "json", "ads"] and args[4:6] == [
            "dataset",
            "list",
        ]:
            stdout = json.dumps({"data": [{"id": "dataset-private"}]})
        else:
            raise AssertionError(f"unexpected Meta command: {args}")
        return {"ok": True, "returncode": 0, "stdout": stdout, "stderr": ""}

    return fake_run


def _repo_snapshot(repo: Path) -> dict[str, str]:
    return {
        str(path.relative_to(repo)): path.read_text(encoding="utf-8")
        for path in repo.rglob("*")
        if path.is_file()
    }


def test_ads_meta_summary_command_exists_and_reports_not_ready_without_probe(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(connect_mod, "_meta_prerequisite_state", lambda **kwargs: "")
    repo = tmp_path / "biz"
    repo.mkdir()
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(app, ["ads", "meta", "summary", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["result_schema"]["name"] == "mainbranch.ads.meta.summary.v1"
    assert payload["mb_command"] == "mb ads meta summary --window 7d"
    assert payload["provider"] == "meta"
    assert payload["state"] == "not_connected"
    assert payload["readiness"]["repair_command"].startswith("mb connect meta")
    assert payload["safe_to_share"] is False
    assert calls == []


def test_ads_meta_summary_ready_uses_read_only_commands_and_redacts_defaults(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _ready_meta_repo(tmp_path, monkeypatch)
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(app, ["ads", "meta", "summary", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [call[:6] for call in calls] == [
        ["meta", "-o", "json", "ads", "adaccount", "list"],
        ["meta", "-o", "json", "ads", "campaign", "list"],
        ["meta", "-o", "json", "ads", "insights", "get"],
        ["meta", "-o", "json", "ads", "dataset", "list"],
    ]
    assert all("create" not in " ".join(call).lower() for call in calls)
    assert all("update" not in " ".join(call).lower() for call in calls)
    assert all("delete" not in " ".join(call).lower() for call in calls)
    assert payload["ok"] is True
    assert payload["safe_to_share"] is False
    assert payload["privacy"]["raw_payload_written"] is False
    assert payload["privacy"]["tracked_files_written"] is False
    assert payload["privacy"]["account_ids_redacted"] is True
    assert payload["privacy"]["business_ids_redacted"] is True
    assert payload["account"]["ad_account_id"] == "<redacted>"
    assert payload["account"]["business_id"] == "<redacted>"
    assert payload["account"]["label"] == "Primary Meta"
    assert payload["account"]["currency"] == "USD"
    assert payload["account"]["timezone"] == "America/Los_Angeles"
    assert payload["campaigns"]["active_count"] == 1
    assert payload["campaigns"]["names"] == []
    assert payload["campaigns"]["names_redacted"] is True
    assert payload["spend"]["amount"] == "redacted"
    assert payload["spend"]["range_label"] == "recent spend 100-999"
    assert payload["datasets"]["state"] == "readable"
    assert "act_123456789" not in result.stdout
    assert "biz_987654321" not in result.stdout
    assert "Spring private campaign" not in result.stdout
    assert "123.45" not in result.stdout
    assert "meta-secret-token" not in result.stdout


def test_ads_meta_summary_skips_datasets_without_business_id(tmp_path: Path, monkeypatch) -> None:
    repo = _ready_meta_repo(tmp_path, monkeypatch, include_business_id=False)
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(app, ["ads", "meta", "summary", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [call[:6] for call in calls] == [
        ["meta", "-o", "json", "ads", "adaccount", "list"],
        ["meta", "-o", "json", "ads", "campaign", "list"],
        ["meta", "-o", "json", "ads", "insights", "get"],
    ]
    assert all(call[4:6] != ["dataset", "list"] for call in calls)
    assert payload["state"] == "ready"
    assert payload["datasets"] == {"state": "not_configured", "count": None}
    assert payload["campaigns"]["active_count"] == 1
    assert payload["spend"]["amount"] == "redacted"


def test_ads_meta_summary_includes_campaign_names_and_exact_spend_only_with_flags(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _ready_meta_repo(tmp_path, monkeypatch)
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(
        app,
        [
            "ads",
            "meta",
            "summary",
            "--repo",
            str(repo),
            "--include-campaign-names",
            "--include-exact-spend",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["privacy"]["campaign_names_included"] is True
    assert payload["privacy"]["exact_spend_included"] is True
    assert payload["safe_to_share"] is False
    assert payload["campaigns"]["names"] == ["Spring private campaign"]
    assert payload["campaigns"]["names_redacted"] is False
    assert payload["spend"]["amount"] == "123.45"
    assert "act_123456789" not in result.stdout
    assert "biz_987654321" not in result.stdout


def test_ads_meta_summary_supports_since_until_and_validates_windows(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _ready_meta_repo(tmp_path, monkeypatch)
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(
        app,
        [
            "ads",
            "meta",
            "summary",
            "--repo",
            str(repo),
            "--since",
            "2026-05-01",
            "--until",
            "2026-05-08",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["window"] == {
        "label": "2026-05-01..2026-05-08",
        "since": "2026-05-01",
        "until": "2026-05-08",
    }
    insights_call = next(call for call in calls if call[4:6] == ["insights", "get"])
    assert "--since" in insights_call
    assert "2026-05-01" in insights_call
    assert "--until" in insights_call
    assert "2026-05-08" in insights_call

    invalid = runner.invoke(
        app,
        [
            "ads",
            "meta",
            "summary",
            "--repo",
            str(repo),
            "--window",
            "365d",
            "--json",
        ],
    )

    assert invalid.exit_code == 2
    invalid_payload = json.loads(invalid.stdout)
    assert invalid_payload["state"] == "invalid_arguments"
    assert invalid_payload["result_status"] == "error"


def test_ads_meta_summary_does_not_write_raw_payloads_or_cache_files(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _ready_meta_repo(tmp_path, monkeypatch)
    before = _repo_snapshot(repo)
    calls: list[list[str]] = []
    monkeypatch.setattr(connect_mod, "_run_command", _fake_meta_runner(calls))

    result = runner.invoke(app, ["ads", "meta", "summary", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    assert _repo_snapshot(repo) == before
    assert not (repo / ".mb" / "ads").exists()
    assert not (repo / ".mb" / "cache").exists()
