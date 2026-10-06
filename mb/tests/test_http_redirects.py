"""Credential-carrying HTTP calls never follow a redirect (#1058).

A real HTTP server on 127.0.0.1 answers the first request with a 3xx whose
``Location`` is a second path on the same server, and records every request.
If a redirect were followed, the second path would see the credential.
"""

from __future__ import annotations

import json
import threading
import urllib.parse
import urllib.request
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
import yaml

from mb import connect as connect_mod
from mb import fleet as fleet_mod
from mb import image_rail as image_rail_mod

REDIRECT_CODES = (301, 302, 303, 307, 308)
SECOND_PATH = "/landed"
# A body the old code would have read as a valid, active credential.
LANDED_BODY = json.dumps({"success": True, "result": {"status": "active", "id": "x"}}).encode()


class _Server:
    def __init__(self) -> None:
        self.requests: list[dict[str, str]] = []
        self.status = 302
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _answer(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                outer.requests.append(
                    {
                        "method": self.command,
                        "path": self.path,
                        "authorization": self.headers.get("Authorization") or "",
                    }
                )
                if self.path == SECOND_PATH:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("X-OAuth-Scopes", "repo")
                    self.send_header("Content-Length", str(len(LANDED_BODY)))
                    self.end_headers()
                    self.wfile.write(LANDED_BODY)
                    return
                body = b"{}"
                self.send_response(outer.status)
                if 300 <= outer.status < 400:
                    self.send_header("Location", f"http://127.0.0.1:{outer.port}{SECOND_PATH}")
                self.send_header("Content-Type", "application/json")
                self.send_header("X-OAuth-Scopes", "repo")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = _answer
            do_POST = _answer

            def log_message(self, *args: Any) -> None:
                return None

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = int(self.httpd.server_address[1])
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    def second_requests(self) -> list[dict[str, str]]:
        return [item for item in self.requests if item["path"] == SECOND_PATH]


@pytest.fixture
def server(monkeypatch) -> Iterator[_Server]:
    """Serve on 127.0.0.1 and send every https:// provider URL there.

    Only https:// URLs are rewritten, so the plain-http ``Location`` the server
    hands back reaches the second path unchanged if anything follows it.
    """
    srv = _Server()
    real_request = urllib.request.Request

    class LocalRequest(real_request):  # type: ignore[valid-type,misc]
        def __init__(self, url: str, *args: Any, **kwargs: Any) -> None:
            if url.startswith("https://"):
                parts = urllib.parse.urlsplit(url)
                url = f"http://127.0.0.1:{srv.port}/start/{parts.hostname}{parts.path}"
            super().__init__(url, *args, **kwargs)

    monkeypatch.setattr(urllib.request, "Request", LocalRequest)
    for name in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    try:
        yield srv
    finally:
        srv.close()


# (provider id, metadata, secret, number of distinct probe URLs)
PROBES: list[tuple[str, dict[str, str], str, int]] = [
    ("github", {}, "ghp_" + "F4k3" * 9, 1),
    ("cloudflare", {}, "f4k3-cloudflare-user-token-000", 1),
    (
        "cloudflare",
        {"token_type": "account", "account_id": "0123456789abcdef0123456789abcdef"},
        "f4k3-cloudflare-account-token-0",
        1,
    ),
    ("apify", {}, "apify_api_f4k3f4k3f4k3f4k3", 1),
    ("stripe", {}, "rk_test_f4k3f4k3f4k3f4k3", len(connect_mod.STRIPE_SCOPE_PROBES)),
    ("ga4", {"property_id": "123456"}, "ya29.f4k3-ga4-token-000000", 1),
]


@pytest.mark.parametrize("code", REDIRECT_CODES)
@pytest.mark.parametrize(
    ("provider_id", "metadata", "secret", "probe_count"),
    PROBES,
    ids=["github", "cloudflare-user", "cloudflare-account", "apify", "stripe", "ga4"],
)
def test_provider_probe_never_follows_a_redirect(
    server: _Server,
    provider_id: str,
    metadata: dict[str, str],
    secret: str,
    probe_count: int,
    code: int,
) -> None:
    server.status = code

    result = connect_mod._validate_with_provider(
        connect_mod.normalize_provider(provider_id), secret, metadata
    )

    assert server.second_requests() == []
    assert len(server.requests) == probe_count
    sent = [item["authorization"] for item in server.requests]
    assert all(secret in value for value in sent)
    assert len({item["path"] for item in server.requests}) == probe_count
    assert result["ok"] is False
    assert result["provider_verified"] is False
    assert result["state"] == "unvalidated"
    assert result["upstream"]["rule"] == "provider_unexpected_redirect"
    assert result["upstream"]["http_status"] == code
    assert "reconnect" not in result["summary"].lower()
    assert not result["repair"]
    assert secret not in json.dumps(result)


@pytest.mark.parametrize("code", REDIRECT_CODES)
def test_connect_test_redirect_is_not_recorded_as_invalid(
    server: _Server, tmp_path: Path, monkeypatch, code: int
) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    for provider in connect_mod.PROVIDERS:
        for env_var in provider.env_vars:
            monkeypatch.delenv(env_var, raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()
    secret = "ghp_" + "F4k3" * 9
    connect_mod.connect_provider("github", repo=repo, token=secret)
    config_path = repo / ".mb" / "connect.yaml"
    before = config_path.read_bytes()
    server.status = code

    result = connect_mod.test_provider("github", repo)

    assert server.second_requests() == []
    assert len(server.requests) == 1
    after = config_path.read_bytes()
    assert secret.encode() not in after

    # Outside the one validation record, the stored connection is
    # byte-identical: nothing was marked for reconnect or replaced.
    def without_check(raw: bytes) -> bytes:
        data = yaml.safe_load(raw)
        entry = data["providers"]["github"]
        entry.pop("validation", None)
        entry.pop("last_checked_at", None)
        return yaml.safe_dump(data, sort_keys=True).encode()

    assert without_check(after) == without_check(before)
    recorded = yaml.safe_load(after)["providers"]["github"]["validation"]
    assert recorded["state"] == "unvalidated"
    assert recorded["provider_verified"] is False
    assert recorded["upstream"]["rule"] == "provider_unexpected_redirect"
    assert "repair" not in recorded
    assert result["ok"] is False
    assert result["status"]["state"] != "invalid"
    assert secret not in json.dumps(result)


@pytest.mark.parametrize(
    ("code", "state", "ok"),
    [(200, "ready", True), (401, "invalid", False), (403, "invalid", False)],
)
@pytest.mark.parametrize(
    ("provider_id", "metadata", "secret"),
    [
        ("github", {}, "ghp_" + "F4k3" * 9),
        ("cloudflare", {}, "f4k3-cloudflare-user-token-000"),
        ("ga4", {"property_id": "123456"}, "ya29.f4k3-ga4-token-000000"),
    ],
    ids=["github", "cloudflare", "ga4"],
)
def test_provider_probe_plain_answers_unchanged(
    server: _Server,
    provider_id: str,
    metadata: dict[str, str],
    secret: str,
    code: int,
    state: str,
    ok: bool,
) -> None:
    server.status = code

    result = connect_mod._validate_with_provider(
        connect_mod.normalize_provider(provider_id), secret, metadata
    )

    assert len(server.requests) == 1
    assert result["ok"] is ok
    assert result["state"] == state
    assert result["upstream"]["http_status"] == code
    assert "rule" not in result["upstream"]
    assert secret not in json.dumps(result)


@pytest.mark.parametrize("code", REDIRECT_CODES)
def test_fleet_cloudflare_read_never_follows_a_redirect(server: _Server, code: int) -> None:
    server.status = code
    secret = "f4k3-fleet-cloudflare-token-00"

    status, payload = fleet_mod._http_get(
        "https://api.cloudflare.com/client/v4/accounts/x/pages/projects",
        {"Authorization": f"Bearer {secret}"},
    )

    assert server.second_requests() == []
    assert len(server.requests) == 1
    assert status == code
    assert payload is None


# urllib already refuses a 307 or 308 on a POST, so only these three could
# carry the key to a second URL before #1058.
@pytest.mark.parametrize("code", (301, 302, 303))
def test_fal_image_request_never_follows_a_redirect(
    server: _Server, monkeypatch, code: int
) -> None:
    server.status = code
    monkeypatch.setenv("FAL_KEY", "f4k3-fal-key-not-written")

    with pytest.raises(RuntimeError) as caught:
        image_rail_mod._generate_fal_image(
            "fixture-safe fal prompt", model="fal-ai/flux/dev", size="1024x1536", quality="d"
        )

    assert server.second_requests() == []
    assert len(server.requests) == 1
    assert f"HTTP {code}" in str(caught.value)
