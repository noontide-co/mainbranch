"""``mb dashboard`` read-only local server."""

from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from pathlib import Path

from typer.testing import CliRunner

from mb import dashboard
from mb.cli import app

runner = CliRunner()


def _fake_data(repo: str = ".") -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "schema": {"name": "mainbranch.dashboard", "version": "0.1", "stability": "preview"},
        "repo": {"path": str(Path(repo).resolve()), "view": "repo"},
        "status": {},
        "graph": {"summary": {"files": 2, "nodes": 3, "edges": 1}, "nodes": [], "edges": []},
        "local_state": {"path": ".mb", "exists": False, "files": [], "summary": {"files": 0}},
        "sections": {
            "repo_health": {"level": "ready", "score": 95, "drift": {"total": 0}},
            "bets": {
                "active": [
                    {"title": "Launch bet", "deadline": "2026-05-08", "public": True},
                    {"title": "Private bet", "deadline": "2026-05-09", "public": False},
                ],
                "due_soon": [],
                "overdue": [],
            },
            "github": {
                "available": True,
                "authenticated": True,
                "summary": {},
                "sections": {
                    "assigned_tasks": [{"title": "Ship dashboard", "business_status": "assigned"}],
                    "open_proposals": [{"title": "Review status", "business_status": "open"}],
                },
            },
            "graph": {"files": 2, "nodes": 3, "edges": 1},
            "next_actions": ["Run `claude`."],
            "similar_bets": {
                "available": True,
                "command": 'mb similar-bets "<thesis>" --json',
                "source": "bets/*.md plus core/offers/*/offer.md",
            },
        },
    }


def test_dashboard_json_cli_uses_existing_contracts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dashboard, "build_data", _fake_data)

    result = runner.invoke(app, ["dashboard", "--repo", str(tmp_path), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema"]["name"] == "mainbranch.dashboard"
    assert payload["sections"]["repo_health"]["score"] == 95
    assert payload["sections"]["similar_bets"]["command"].startswith("mb similar-bets")
    assert payload["schema"]["version"] == "0.1"


def test_dashboard_refuses_non_loopback_host_without_opt_in(tmp_path: Path) -> None:
    result = runner.invoke(app, ["dashboard", "--repo", str(tmp_path), "--host", "0.0.0.0"])

    assert result.exit_code == 2
    assert "only binds loopback hosts by default" in result.stderr


def test_dashboard_server_serves_nonblank_page_and_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dashboard, "build_data", _fake_data)
    server = dashboard.make_server(repo=str(tmp_path), port=0)
    host, port = server.server_address

    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
    )
    thread.start()
    try:
        conn = HTTPConnection(str(host), int(port), timeout=3)
        conn.request("GET", "/", headers={"Connection": "close"})
        response = conn.getresponse()
        page = response.read().decode("utf-8")
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=3)
        conn.request("GET", "/api/dashboard", headers={"Connection": "close"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    assert "Main Branch Dashboard" in page
    assert "Launch bet" in page
    assert "Private bet" not in page
    assert len(page) > 500
    assert payload["schema"]["name"] == "mainbranch.dashboard"
    assert payload["sections"]["graph"]["nodes"] == 3
