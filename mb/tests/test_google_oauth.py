"""Tests for mb.google_oauth: PKCE, loopback receiver, paste parser, token calls.

No network: an autouse guard fails any DNS lookup or connection that is not
127.0.0.1, and token calls go through an injected sender. Every secret is a
synthetic sentinel so leak checks can search for it.
"""

from __future__ import annotations

import getpass
import http.client
import io
import json
import socket
import threading
import urllib.error
import urllib.parse
from collections.abc import Callable, Iterator, Mapping
from contextlib import suppress
from typing import Any

import pytest

from mb import google_oauth as go

CLIENT_ID = "0000-synthetic.apps.example.invalid"
CLIENT_SECRET = "SYNTH-CLIENT-SECRET-0001"
REFRESH = "SYNTH-REFRESH-0001"
ACCESS = "SYNTH-ACCESS-0001"
CODE = "SYNTH-CODE-0001"
VERIFIER = "SYNTH-VERIFIER-0001-" + "v" * 40
SENTINELS = (CLIENT_SECRET, REFRESH, ACCESS, CODE, VERIFIER)

_REAL_GETADDRINFO = socket.getaddrinfo
_REAL_CREATE_CONNECTION = socket.create_connection


@pytest.fixture(autouse=True)
def loopback_only_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any lookup or connection to a host other than 127.0.0.1."""

    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        if host not in {"127.0.0.1", b"127.0.0.1"}:
            raise OSError("network blocked in tests")
        return _REAL_GETADDRINFO(host, *args, **kwargs)

    def guarded_create_connection(address: Any, *args: Any, **kwargs: Any) -> Any:
        if address[0] != "127.0.0.1":
            raise OSError("network blocked in tests")
        return _REAL_CREATE_CONNECTION(address, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)


def test_network_guard_blocks_non_loopback() -> None:
    with pytest.raises(OSError):
        socket.getaddrinfo("oauth2.googleapis.com", 443)
    with pytest.raises(OSError):
        socket.create_connection(("oauth2.googleapis.com", 443))


def assert_no_sentinel(text: str) -> None:
    for sentinel in SENTINELS:
        assert sentinel not in text


# --- PKCE and state ---------------------------------------------------------


def test_pkce_rfc7636_vector() -> None:
    # RFC 7636 Appendix B.
    assert (
        go.code_challenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk")
        == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    )


def test_new_verifier_in_range_and_unique() -> None:
    first, second = go.new_code_verifier(), go.new_code_verifier()
    assert first != second
    assert go.PKCE_VERIFIER_MIN <= len(first) <= go.PKCE_VERIFIER_MAX
    assert len(go.code_challenge(first)) == 43
    assert "=" not in go.code_challenge(first)


@pytest.mark.parametrize("bad", ["a" * 42, "a" * 129, "a" * 42 + "!", "a" * 42 + " "])
def test_verifier_format_refused_with_fixed_text(bad: str) -> None:
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.code_challenge(bad)
    assert caught.value.rule == "pkce_verifier_format"
    assert bad not in str(caught.value)


def test_state_compare() -> None:
    state = go.new_state()
    assert go.states_match(state, state)
    assert not go.states_match(state, state + "x")
    assert not go.states_match("", "")
    assert go.new_state() != state


# --- Authorization URL ------------------------------------------------------


def test_auth_url_has_required_params_and_no_secret() -> None:
    challenge = go.code_challenge(VERIFIER)
    url = go.build_auth_url(
        client_id=CLIENT_ID,
        redirect_uri=go.loopback_redirect_uri(8085),
        code_challenge=challenge,
        state="STATE-0001",
    )
    assert url.startswith(go.AUTH_ENDPOINT + "?")
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    assert query["client_id"] == [CLIENT_ID]
    assert query["redirect_uri"] == ["http://127.0.0.1:8085"]
    assert query["response_type"] == ["code"]
    assert query["scope"] == [" ".join(go.SCOPES)]
    assert query["code_challenge"] == [challenge]
    assert query["code_challenge_method"] == ["S256"]
    assert query["state"] == ["STATE-0001"]
    assert "access_type" not in query
    assert "prompt" not in query
    assert "client_secret" not in query
    assert_no_sentinel(url)


@pytest.mark.parametrize(
    "uri",
    [
        "http://0.0.0.0:8085",
        "http://localhost:8085",
        "https://127.0.0.1:8085",
        "http://127.0.0.1",
        "http://127.0.0.1:8085/cb?x=1",
        "http://example.com:8085",
    ],
)
def test_auth_url_refuses_non_loopback_redirect(uri: str) -> None:
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.build_auth_url(client_id=CLIENT_ID, redirect_uri=uri, code_challenge="c", state="s")
    assert caught.value.rule == "redirect_uri_not_loopback"


def test_auth_url_refuses_missing_client_id() -> None:
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.build_auth_url(
            client_id="", redirect_uri=go.loopback_redirect_uri(1), code_challenge="c", state="s"
        )
    assert caught.value.rule == "client_id_missing"


def test_granted_labels() -> None:
    assert go.granted_labels(" ".join(go.SCOPES)) == ["search_console", "ga4"]
    assert go.granted_labels(go.SCOPE_ANALYTICS + " openid") == ["ga4"]
    assert go.granted_labels("") == []


# --- Paste parser -----------------------------------------------------------


def _query(**fields: str) -> str:
    return urllib.parse.urlencode(fields)


@pytest.mark.parametrize(
    "text",
    [
        f"http://127.0.0.1:8085/?{_query(state='S1', code=CODE, scope='x')}",
        f"  http://127.0.0.1:8085/?{_query(code=CODE, state='S1')}\n",
        _query(code=CODE, state="S1"),
        "?" + _query(code=CODE, state="S1"),
        "/?" + _query(code=CODE, state="S1"),
    ],
)
def test_paste_parser_accepts_url_or_query(text: str) -> None:
    assert go.parse_pasted_redirect(text, "S1") == CODE


@pytest.mark.parametrize(
    ("text", "rule", "state"),
    [
        (_query(code=CODE, state="S2"), "state_mismatch", go.STATE_INVALID),
        (_query(code=CODE), "state_mismatch", go.STATE_INVALID),
        (_query(error="access_denied", state="S1"), "consent_denied", go.STATE_CONSENT_DENIED),
        (_query(error="invalid_scope", state="S1"), "authorization_error", go.STATE_INVALID),
        (_query(state="S1"), "code_missing", go.STATE_INVALID),
        (f"code={CODE}&code=other&state=S1", "redirect_ambiguous", go.STATE_INVALID),
        (
            f"https://evil.example/?{_query(code=CODE, state='S1')}",
            "redirect_host",
            go.STATE_INVALID,
        ),
        (
            f"http://localhost:8085/?{_query(code=CODE, state='S1')}",
            "redirect_host",
            go.STATE_INVALID,
        ),
        ("   ", "paste_empty", go.STATE_INVALID),
    ],
)
def test_paste_parser_refusals(text: str, rule: str, state: str) -> None:
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.parse_pasted_redirect(text, "S1")
    assert caught.value.rule == rule
    assert caught.value.state == state
    assert_no_sentinel(str(caught.value))
    assert_no_sentinel(repr(caught.value.upstream))


def test_access_denied_with_wrong_state_is_state_mismatch() -> None:
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.parse_pasted_redirect(_query(error="access_denied", state="S2"), "S1")
    assert caught.value.rule == "state_mismatch"


class _FakeStream(io.StringIO):
    def __init__(self, tty: bool) -> None:
        super().__init__()
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def test_paste_reader_refuses_without_tty() -> None:
    called: list[str] = []

    def reader(prompt: str) -> str:
        called.append(prompt)
        return ""

    with pytest.raises(go.GoogleOAuthError) as caught:
        go.read_pasted_redirect("S1", stdin=_FakeStream(False), reader=reader)
    assert caught.value.rule == "paste_needs_tty"
    assert called == []


def test_paste_reader_refuses_closed_stream() -> None:
    stream = io.StringIO()
    stream.close()  # isatty() on a closed stream raises ValueError
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.read_pasted_redirect("S1", stdin=stream, reader=lambda prompt: "")
    assert caught.value.rule == "paste_needs_tty"


def test_paste_reader_uses_hidden_reader_on_tty(capsys: pytest.CaptureFixture[str]) -> None:
    prompts: list[str] = []

    def reader(prompt: str) -> str:
        prompts.append(prompt)
        return f"http://127.0.0.1:9/?{_query(code=CODE, state='S1')}"

    assert go.read_pasted_redirect("S1", stdin=_FakeStream(True), reader=reader) == CODE
    assert len(prompts) == 1
    assert "hidden" in prompts[0]
    captured = capsys.readouterr()
    assert_no_sentinel(captured.out + captured.err)


def test_paste_reader_defaults_to_getpass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(getpass, "getpass", lambda prompt: _query(code=CODE, state="S1"))
    assert go.read_pasted_redirect("S1", stdin=_FakeStream(True)) == CODE


# --- Loopback receiver (real 127.0.0.1 listener) ----------------------------


Opener = Callable[[str], None]


def _request(port: int, method: str, path: str) -> int:
    # http.client, not urllib: a proxy variable in the environment must not
    # route a loopback request anywhere else.
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        body = response.read().decode("utf-8")
        assert_no_sentinel(body)
        return int(response.status)
    finally:
        conn.close()


def _get(port: int, path: str) -> int:
    return _request(port, "GET", path)


@pytest.fixture()
def run_receiver() -> Iterator[Callable[..., tuple[go.LoopbackReceiver, Any, list[int]]]]:
    """Start a receiver, fire ``act(port)`` in a thread, return the wait outcome."""

    threads: list[threading.Thread] = []

    def run(
        act: Callable[[int], int], *, state: str = "S1", **kwargs: Any
    ) -> tuple[go.LoopbackReceiver, Any, list[int]]:
        receiver = go.LoopbackReceiver(state, **kwargs)
        statuses: list[int] = []
        thread = threading.Thread(target=lambda: statuses.append(act(receiver.port)))
        threads.append(thread)
        thread.start()
        try:
            outcome: Any = receiver.wait()
        except go.GoogleOAuthError as exc:
            outcome = exc
        thread.join(timeout=10)
        return receiver, outcome, statuses

    yield run
    for thread in threads:
        thread.join(timeout=1)


def _assert_closed(port: int) -> None:
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=1).close()


def test_receiver_binds_loopback_only() -> None:
    with go.LoopbackReceiver("S1") as receiver:
        assert receiver._server.server_address[0] == "127.0.0.1"
        assert receiver.redirect_uri == f"http://127.0.0.1:{receiver.port}"
        assert receiver.port > 0


def test_receiver_success_then_closed(run_receiver: Any, capfd: pytest.CaptureFixture[str]) -> None:
    receiver, outcome, statuses = run_receiver(
        lambda port: _get(port, f"/?{_query(state='S1', code=CODE, scope='s')}")
    )
    assert outcome == CODE
    assert statuses == [200]
    _assert_closed(receiver.port)
    # log_message is silenced: the request line carries ?code= and must not reach stderr.
    captured = capfd.readouterr()
    assert_no_sentinel(captured.out + captured.err)
    assert "GET /" not in captured.err


@pytest.mark.parametrize(
    ("query", "rule", "state"),
    [
        (_query(state="WRONG", code=CODE), "state_mismatch", go.STATE_INVALID),
        (_query(state="S1", error="access_denied"), "consent_denied", go.STATE_CONSENT_DENIED),
    ],
)
def test_receiver_refusals(
    run_receiver: Any, capfd: pytest.CaptureFixture[str], query: str, rule: str, state: str
) -> None:
    receiver, outcome, statuses = run_receiver(lambda port: _get(port, f"/?{query}"))
    assert isinstance(outcome, go.GoogleOAuthError)
    assert outcome.rule == rule
    assert outcome.state == state
    assert statuses == [400]
    _assert_closed(receiver.port)
    captured = capfd.readouterr()
    assert_no_sentinel(captured.out + captured.err + str(outcome))


def test_receiver_wrong_path_answered_404_then_real_callback_succeeds(
    run_receiver: Any, capfd: pytest.CaptureFixture[str]
) -> None:
    def act(port: int) -> list[int]:
        return [
            _get(port, f"/favicon.ico?{_query(state='S1', code=CODE)}"),
            _get(port, "/robots.txt"),
            _get(port, f"/?{_query(state='S1', code=CODE)}"),
        ]

    receiver, outcome, statuses = run_receiver(act)
    assert outcome == CODE
    assert statuses == [[404, 404, 200]]
    _assert_closed(receiver.port)
    captured = capfd.readouterr()
    assert_no_sentinel(captured.out + captured.err)


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "HEAD", "OPTIONS", "BREW"])
def test_receiver_wrong_method_answered_then_real_callback_succeeds(
    run_receiver: Any, capfd: pytest.CaptureFixture[str], method: str
) -> None:
    def act(port: int) -> list[int]:
        return [
            _request(port, method, f"/?{_query(state='S1', code=CODE)}"),
            _get(port, f"/?{_query(state='S1', code=CODE)}"),
        ]

    receiver, outcome, statuses = run_receiver(act)
    assert outcome == CODE
    assert statuses == [[501 if method == "BREW" else 405, 200]]
    _assert_closed(receiver.port)
    captured = capfd.readouterr()
    assert_no_sentinel(captured.out + captured.err)


def _raw_exchange(port: int, payload: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as conn:
        conn.sendall(payload)
        chunks = []
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    return b"".join(chunks)


def test_receiver_malformed_request_line_is_not_echoed(run_receiver: Any) -> None:
    replies: list[bytes] = []

    def act(port: int) -> int:
        replies.append(_raw_exchange(port, f"GET /?code={CODE} BOGUS/9 extra\r\n\r\n".encode()))
        return _get(port, f"/?{_query(state='S1', code=CODE)}")

    receiver, outcome, statuses = run_receiver(act)
    assert outcome == CODE
    assert statuses == [200]
    # A request line that does not parse gets the fixed failure page only.
    assert replies and go._FAILURE_PAGE in replies[0]
    assert CODE.encode() not in replies[0]
    assert b"BOGUS" not in replies[0]


def test_receiver_send_error_page_is_fixed_text() -> None:
    handler = go._CallbackHandler.__new__(go._CallbackHandler)
    sent: list[tuple[int, bytes]] = []
    handler._reply = lambda status, body: sent.append((status, body))  # type: ignore[method-assign]
    handler.send_error(400, f"Bad request version ('{CODE}')", CODE)
    assert sent == [(400, go._FAILURE_PAGE)]
    assert handler.close_connection is True


def test_receiver_trickled_request_is_bounded_by_the_deadline() -> None:
    import time as _time

    receiver = go.LoopbackReceiver("S1", timeout=1.5)
    port = receiver.port
    stop = threading.Event()

    def trickle() -> None:
        with suppress(OSError), socket.create_connection(("127.0.0.1", port), timeout=5) as conn:
            for byte in b"GET /?state=S1&code=" + b"x" * 200:
                if stop.is_set():
                    return
                conn.sendall(bytes([byte]))
                _time.sleep(0.2)

    thread = threading.Thread(target=trickle)
    thread.start()
    started = _time.monotonic()
    try:
        with pytest.raises(go.GoogleOAuthError) as caught:
            receiver.wait()
    finally:
        stop.set()
        thread.join(timeout=5)
    elapsed = _time.monotonic() - started
    assert caught.value.rule == "bootstrap_timeout"
    # One trickler gets at most the wait's own deadline, not 5 s per byte.
    assert elapsed < 3.0
    _assert_closed(port)


def test_receiver_ignores_idle_connection_then_succeeds(run_receiver: Any) -> None:
    def act(port: int) -> int:
        socket.create_connection(("127.0.0.1", port), timeout=1).close()
        return _get(port, f"/?{_query(state='S1', code=CODE)}")

    receiver, outcome, statuses = run_receiver(act)
    assert outcome == CODE
    assert statuses == [200]
    _assert_closed(receiver.port)


def test_receiver_timeout_with_injected_clock() -> None:
    ticks = iter([0.0, 0.0, 301.0, 301.0])
    receiver = go.LoopbackReceiver("S1", timeout=300, clock=lambda: next(ticks))
    port = receiver.port
    with pytest.raises(go.GoogleOAuthError) as caught:
        receiver.wait()
    assert caught.value.rule == "bootstrap_timeout"
    assert caught.value.state == go.STATE_BOOTSTRAP_TIMEOUT
    _assert_closed(port)


def test_receiver_handler_silences_log_message(capsys: pytest.CaptureFixture[str]) -> None:
    handler = go._CallbackHandler.__new__(go._CallbackHandler)
    handler.log_message('"%s" %s %s', f"GET /?code={CODE} HTTP/1.1", "200", "-")
    assert_no_sentinel(capsys.readouterr().err)


# --- Token POST transport and calls -----------------------------------------


class FakeSender:
    def __init__(self, status: int = 200, body: Any = None, raises: BaseException | None = None):
        self.status = status
        self.body = body
        self.raises = raises
        self.calls: list[tuple[str, dict[str, list[str]], dict[str, str]]] = []

    def __call__(
        self, url: str, body: bytes, headers: Mapping[str, str], timeout: float
    ) -> tuple[int, bytes]:
        self.calls.append((url, urllib.parse.parse_qs(body.decode("ascii")), dict(headers)))
        if self.raises is not None:
            raise self.raises
        if isinstance(self.body, bytes):
            return self.status, self.body

        return self.status, json.dumps(self.body or {}).encode("utf-8")


def _echo_everything() -> dict[str, Any]:
    """A hostile error body that echoes every secret in every field."""

    echoed = " ".join(SENTINELS)
    return {
        "error": f"invalid_grant {echoed}",
        "error_subtype": echoed,
        "error_description": f"Bad request: {echoed}",
        "access_token": ACCESS,
        "refresh_token": REFRESH,
    }


def test_post_helper_redacts_body_and_header_secrets() -> None:
    sender = FakeSender(400, _echo_everything())
    result = go.http_post_form(
        go.TOKEN_ENDPOINT,
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH,
            "code": CODE,
            "code_verifier": VERIFIER,
        },
        headers={"Authorization": f"Bearer {ACCESS}"},
        sender=sender,
    )
    assert not result.ok
    assert result.payload == {}
    assert_no_sentinel(repr(result))
    assert_no_sentinel(repr(result.upstream))
    assert result.upstream["error_code"] == "other"
    assert result.upstream["http_status"] == 400
    assert result.upstream["safe_to_share"] is True
    assert "error_description" not in result.upstream


def test_post_helper_sends_form_post() -> None:
    sender = FakeSender(200, {"access_token": ACCESS})
    result = go.http_post_form(go.TOKEN_ENDPOINT, {"grant_type": "refresh_token"}, sender=sender)
    assert result.ok
    assert result.state == "ok"
    url, fields, headers = sender.calls[0]
    assert url == go.TOKEN_ENDPOINT
    assert fields == {"grant_type": ["refresh_token"]}
    assert headers.get("Content-Type") == "application/x-www-form-urlencoded"
    assert_no_sentinel(repr(result))


def test_post_helper_network_failure_is_unvalidated() -> None:
    result = go.http_post_form(
        go.TOKEN_ENDPOINT,
        {"refresh_token": REFRESH},
        sender=FakeSender(raises=urllib.error.URLError(f"boom {REFRESH}")),
    )
    assert not result.ok
    assert result.state == go.STATE_UNVALIDATED
    assert result.upstream["response_received"] is False
    assert_no_sentinel(repr(result))


def test_post_helper_default_sender_is_blocked_by_guard() -> None:
    result = go.http_post_form(go.TOKEN_ENDPOINT, {"refresh_token": REFRESH})
    assert result.state == go.STATE_UNVALIDATED
    assert_no_sentinel(repr(result))


def test_post_helper_unreadable_body() -> None:
    result = go.http_post_form(
        go.TOKEN_ENDPOINT, {"code": CODE}, sender=FakeSender(502, b"\xff<html>" + CODE.encode())
    )
    assert result.state == go.STATE_UNVALIDATED
    assert result.upstream["http_status"] == 502
    assert_no_sentinel(repr(result))


def test_exchange_code_returns_only_token_fields() -> None:
    sender = FakeSender(
        200,
        {
            "access_token": ACCESS,
            "expires_in": 3599,
            "scope": " ".join(go.SCOPES),
            "token_type": "Bearer",
            "refresh_token": REFRESH,
            "refresh_token_expires_in": 604799,
            "id_token": "SYNTH-ID-0001",
            "extra": "x",
        },
    )
    tokens = go.exchange_code(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=CODE,
        code_verifier=VERIFIER,
        redirect_uri="http://127.0.0.1:8085",
        sender=sender,
    )
    assert sorted(tokens) == sorted(go.TOKEN_FIELDS)
    assert tokens.get("refresh_token_expires_in") == 604799
    _, fields, _ = sender.calls[0]
    assert fields == {
        "client_id": [CLIENT_ID],
        "client_secret": [CLIENT_SECRET],
        "code": [CODE],
        "code_verifier": [VERIFIER],
        "grant_type": ["authorization_code"],
        "redirect_uri": ["http://127.0.0.1:8085"],
    }


def test_token_response_never_shows_values() -> None:
    sender = FakeSender(
        200, {"access_token": ACCESS, "refresh_token": REFRESH, "scope": go.SCOPE_ANALYTICS}
    )
    tokens = go.exchange_code(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=CODE,
        code_verifier=VERIFIER,
        redirect_uri="http://127.0.0.1:8085",
        sender=sender,
    )
    assert isinstance(tokens, go.TokenResponse)
    assert not isinstance(tokens, dict)
    assert tokens["refresh_token"] == REFRESH
    for shown in (repr(tokens), str(tokens), f"{tokens}", repr([tokens]), repr({"t": tokens})):
        assert_no_sentinel(shown)
        assert "refresh_token" in shown


def test_exchange_code_omits_absent_client_secret() -> None:
    sender = FakeSender(200, {"access_token": ACCESS})
    tokens = go.exchange_code(
        client_id=CLIENT_ID,
        client_secret=None,
        code=CODE,
        code_verifier=VERIFIER,
        redirect_uri="http://127.0.0.1:8085",
        sender=sender,
    )
    assert tokens == {"access_token": ACCESS}
    assert "client_secret" not in sender.calls[0][1]


def test_refresh_access_token_fields() -> None:
    sender = FakeSender(200, {"access_token": ACCESS, "expires_in": 3599, "token_type": "Bearer"})
    tokens = go.refresh_access_token(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, refresh_token=REFRESH, sender=sender
    )
    assert tokens == {"access_token": ACCESS, "expires_in": 3599, "token_type": "Bearer"}
    assert sender.calls[0][1] == {
        "client_id": [CLIENT_ID],
        "client_secret": [CLIENT_SECRET],
        "grant_type": ["refresh_token"],
        "refresh_token": [REFRESH],
    }


@pytest.mark.parametrize(
    ("status", "body", "raises", "rule", "state"),
    [
        (400, {"error": "invalid_grant"}, None, "token_request_failed", go.STATE_REAUTH_REQUIRED),
        (
            400,
            {"error": "invalid_grant", "error_subtype": "invalid_rapt"},
            None,
            "token_request_failed",
            go.STATE_REAUTH_REQUIRED,
        ),
        (401, {"error": "invalid_client"}, None, "token_request_failed", go.STATE_INVALID),
        (503, {}, None, "token_request_failed", go.STATE_UNVALIDATED),
        (0, None, TimeoutError("slow"), "token_unreachable", go.STATE_UNVALIDATED),
        (200, {"token_type": "Bearer"}, None, "token_response_malformed", go.STATE_UNVALIDATED),
        (200, b"not json", None, "token_response_malformed", go.STATE_UNVALIDATED),
    ],
)
def test_refresh_failures_raise_fixed_text(
    status: int, body: Any, raises: BaseException | None, rule: str, state: str
) -> None:
    hostile = body
    if isinstance(body, dict) and status >= 400:
        # Google's free text echoes every secret; it must never surface.
        hostile = {**body, "error_description": " ".join(SENTINELS)}
    sender = FakeSender(status, hostile, raises)
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.refresh_access_token(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, refresh_token=REFRESH, sender=sender
        )
    error = caught.value
    assert error.rule == rule
    assert error.state == state
    assert str(error) == go._RULE_MESSAGES[rule]
    assert error.repair == go.REPAIRS[state]
    assert_no_sentinel(str(error) + repr(error.args) + repr(error.upstream))
    assert "error_description" not in error.upstream


def test_exchange_failure_never_echoes_code_or_verifier() -> None:
    sender = FakeSender(400, _echo_everything())
    with pytest.raises(go.GoogleOAuthError) as caught:
        go.exchange_code(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=CODE,
            code_verifier=VERIFIER,
            redirect_uri="http://127.0.0.1:8085",
            sender=sender,
        )
    assert_no_sentinel(str(caught.value) + repr(caught.value.upstream))


# --- Classifier -------------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"error_code": "invalid_grant"}, go.STATE_REAUTH_REQUIRED),
        (
            {"error_code": "invalid_grant", "error_subtype": "invalid_rapt"},
            go.STATE_REAUTH_REQUIRED,
        ),
        ({"error_subtype": "invalid_rapt"}, go.STATE_REAUTH_REQUIRED),
        ({"error_code": "invalid_client", "http_status": 401}, go.STATE_INVALID),
        ({"error_code": "invalid_request", "http_status": 400}, go.STATE_INVALID),
        ({"error_code": "access_denied"}, go.STATE_CONSENT_DENIED),
        ({"network_failure": True}, go.STATE_UNVALIDATED),
        ({"http_status": 500}, go.STATE_UNVALIDATED),
        ({"error_code": "invalid_grant", "http_status": 503}, go.STATE_UNVALIDATED),
        ({"timed_out": True}, go.STATE_BOOTSTRAP_TIMEOUT),
    ],
)
def test_classifier_table(kwargs: dict[str, Any], expected: str) -> None:
    assert go.classify_error(**kwargs) == expected


def test_classifier_ignores_error_description() -> None:
    import inspect

    assert "error_description" not in inspect.signature(go.classify_error).parameters
    assert "error_description" not in inspect.getsource(go.http_post_form)
