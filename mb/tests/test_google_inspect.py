"""Tests for `mb google sc inspect` (#1004, PR7).

One URL of the recorded Search Console site, index status only. No network:
the token endpoint and the URL Inspection API are stub senders behind the
existing seams, as in test_google_reads.
"""

# The fixtures are imported from test_google_connect, so test parameters
# share their names by design.
# ruff: noqa: F811, E501

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from mb import google_oauth as go
from mb import google_reads as gr
from mb.cli import app
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    MINTED,
    client_file,
    google,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_probe import GOOGLE_TEXT, _mint, _sign_in
from tests.test_google_reads import (
    SITE,
    UNDOCUMENTED,
    ReadsEndpoint,
    _assert_never_shown,
    _error,
    _json,
    _run,
    _signed_in,
    _strings,
)

INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
PAGE = "https://www.example.com/shoes/"
INSPECT_ARGS = ["google", "sc", "inspect", "--url", PAGE]
LINK = "https://search.google.com/search-console/inspect?resource_id=sc-domain:example.com&id=abc"


def _inspection(**index: Any) -> dict[str, Any]:
    """A full documented answer, plus an undocumented field at every level."""

    return {
        "inspectionResult": {
            "inspectionResultLink": LINK,
            "indexStatusResult": {
                "verdict": "PASS",
                "coverageState": "Submitted and indexed",
                "robotsTxtState": "ALLOWED",
                "indexingState": "INDEXING_ALLOWED",
                "lastCrawlTime": "2026-09-20T10:00:00Z",
                "pageFetchState": "SUCCESSFUL",
                "googleCanonical": PAGE,
                "userCanonical": PAGE,
                "crawledAs": "MOBILE",
                "sitemap": ["https://www.example.com/sitemap.xml"],
                "referringUrls": ["https://www.example.com/", "https://www.example.com/sale/"],
                "undocumented": UNDOCUMENTED,
                **index,
            },
            "ampResult": {
                "verdict": "PASS",
                "ampUrl": "https://www.example.com/shoes/amp/",
                "robotsTxtState": "ALLOWED",
                "indexingState": "AMP_INDEXING_ALLOWED",
                "ampIndexStatusVerdict": "PASS",
                "lastCrawlTime": "2026-09-19T10:00:00Z",
                "pageFetchState": "SUCCESSFUL",
                "issues": [{"issueMessage": "m", "severity": "WARNING", "x": UNDOCUMENTED}],
                "undocumented": UNDOCUMENTED,
            },
            "mobileUsabilityResult": {
                "verdict": "PASS",
                "issues": [
                    {"issueType": "CONFIGURE_VIEWPORT", "severity": "ERROR", "message": "v"}
                ],
            },
            "richResultsResult": {
                "verdict": "PASS",
                "detectedItems": [
                    {
                        "richResultType": "Product snippets",
                        "items": [
                            {
                                "name": "Shoe",
                                "issues": [{"issueMessage": "i", "severity": "WARNING"}],
                                "undocumented": UNDOCUMENTED,
                            }
                        ],
                        "undocumented": UNDOCUMENTED,
                    }
                ],
            },
            "undocumented": UNDOCUMENTED,
        },
        "undocumented": UNDOCUMENTED,
    }


def _inspect_api(monkeypatch: pytest.MonkeyPatch, answer: Any = None) -> ReadsEndpoint:
    endpoint = ReadsEndpoint({INSPECT_URL: answer if answer is not None else (200, _inspection())})
    monkeypatch.setattr(gr, "api_sender", endpoint)
    return endpoint


def _record_site(repo: Path, site: str) -> None:
    edit = runner.invoke(
        app, ["connect", "google", "--repo", str(repo), "--metadata", f"search_console_site={site}"]
    )
    assert edit.exit_code == 0, edit.output


# --- The request and the result --------------------------------------------------------


def test_inspect_reads_the_recorded_site(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, stderr = _json(repo, INSPECT_ARGS)

    assert code == 0, stderr
    assert len(mint.calls) == 1
    # urlInspection.index.inspect: POST, inspectionUrl and siteUrl in the body,
    # no languageCode (Google's default), nothing in the query string.
    assert api.calls == [
        {
            "method": "POST",
            "url": INSPECT_URL,
            "body": {"inspectionUrl": PAGE, "siteUrl": SITE},
            "authorization": f"Bearer {MINTED}",
            "content_type": "application/json",
        }
    ]
    assert payload["result_schema"]["name"] == "mb.google.sc.inspect"
    assert payload["mb_command"] == "mb google sc inspect"
    assert payload["ok"] is True and payload["errors"] == []
    assert payload["site"] == SITE and payload["inspection_url"] == PAGE
    result = payload["inspection_result"]
    assert result["inspectionResultLink"] == LINK
    assert result["indexStatusResult"] == {
        "verdict": "PASS",
        "coverageState": "Submitted and indexed",
        "robotsTxtState": "ALLOWED",
        "indexingState": "INDEXING_ALLOWED",
        "lastCrawlTime": "2026-09-20T10:00:00Z",
        "pageFetchState": "SUCCESSFUL",
        "googleCanonical": PAGE,
        "userCanonical": PAGE,
        "crawledAs": "MOBILE",
        "sitemap": ["https://www.example.com/sitemap.xml"],
        "referringUrls": ["https://www.example.com/", "https://www.example.com/sale/"],
    }
    assert result["ampResult"]["issues"] == [{"issueMessage": "m", "severity": "WARNING"}]
    assert result["ampResult"]["ampIndexStatusVerdict"] == "PASS"
    assert result["mobileUsabilityResult"] == {
        "verdict": "PASS",
        "issues": [{"issueType": "CONFIGURE_VIEWPORT", "severity": "ERROR", "message": "v"}],
    }
    assert result["richResultsResult"] == {
        "verdict": "PASS",
        "detectedItems": [
            {
                "richResultType": "Product snippets",
                "items": [
                    {"name": "Shoe", "issues": [{"issueMessage": "i", "severity": "WARNING"}]}
                ],
            }
        ],
    }
    # Only documented fields pass through.
    assert UNDOCUMENTED not in json.dumps(payload)


def test_inspect_human_summary(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _inspect_api(monkeypatch)

    result = _run(repo, INSPECT_ARGS)

    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        f"Search Console: {SITE}",
        f"URL: {PAGE}",
        "verdict: PASS (Submitted and indexed)",
        "robots.txt: ALLOWED, indexing: INDEXING_ALLOWED, page fetch: SUCCESSFUL",
        "last crawl: 2026-09-20T10:00:00Z (MOBILE)",
        f"Google canonical: {PAGE}",
        f"your canonical: {PAGE}",
        "sitemaps: 1, referring URLs: 2",
        "rich results: PASS (Product snippets)",
        "AMP: PASS, 1 issue",
        f"open in Search Console: {LINK}",
    ]


def test_inspect_of_a_page_google_never_crawled(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _inspect_api(
        monkeypatch,
        (
            200,
            {
                "inspectionResult": {
                    "indexStatusResult": {
                        "verdict": "NEUTRAL",
                        "coverageState": "URL is unknown to Google",
                    }
                }
            },
        ),
    )

    code, payload, _ = _json(repo, INSPECT_ARGS)
    assert code == 0
    assert payload["inspection_result"] == {
        "indexStatusResult": {
            "verdict": "NEUTRAL",
            "coverageState": "URL is unknown to Google",
            "sitemap": [],
            "referringUrls": [],
        }
    }
    human = _run(repo, INSPECT_ARGS)
    assert "last crawl: never" in human.stdout
    assert "open in Search Console" not in human.stdout

    _inspect_api(monkeypatch, (200, {}))
    code, payload, _ = _json(repo, INSPECT_ARGS)
    assert code == 0 and payload["inspection_result"] == {}
    assert "index status: none returned" in _run(repo, INSPECT_ARGS).stdout


@pytest.mark.parametrize(
    "link",
    [
        "https://evil.example/search-console/inspect",
        "http://search.google.com/search-console/inspect",
        "https://search.google.com.evil.example/x",
        "https://search.google.com@evil.example/x",
        "javascript:alert(1)",
        "https://search.google.com/" + "x" * 3000,
        "https://search.google.com/\x1b]8;;x",
        42,
    ],
)
def test_inspection_link_only_into_search_console(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, link: Any
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    answer = _inspection()
    answer["inspectionResult"]["inspectionResultLink"] = link
    _inspect_api(monkeypatch, (200, answer))

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 0
    assert "inspectionResultLink" not in payload["inspection_result"]


def test_inspect_cuts_long_strings_and_caps_lists(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _inspect_api(
        monkeypatch,
        (
            200,
            _inspection(
                coverageState="c" * 5000,
                referringUrls=[f"https://www.example.com/{n}" for n in range(100)] + [7, None],
                verdict=["PASS"],
            ),
        ),
    )

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 0
    index = payload["inspection_result"]["indexStatusResult"]
    assert len(index["coverageState"]) == gr.STRING_MAX and index["coverageState"].endswith("…")
    assert len(index["referringUrls"]) == gr.LIST_MAX
    assert "verdict" not in index


# --- Refusals (exit 2, nothing called) ----------------------------------------------------

URL_FORMAT = [
    "",
    "www.example.com/shoes/",
    "ftp://www.example.com/shoes/",
    "file:///etc/passwd",
    "https://user@www.example.com/shoes/",
    "https://user:pass@www.example.com/shoes/",
    "https://www.example.com/shoes/#reviews",
    "https://www.example.com/shoes/#",
    "https://www.example.com/sh oes/",
    " https://www.example.com/shoes/",
    "https://www.example.com/shoes/\n",
    "https://www.example.com/\tshoes/",
    "https://www.example.com/\x1b[31m",
    "https://www.example.com/\x7f",
    "https://www.example.com/‮shoes",
    "https://www.example.com/ ",
    "https://www.example.com\\@evil.example/",
    "https://www.example.com:99999/",
    "https://www.example.com:x/",
    "https://localhost/",
    "https:///shoes/",
    "https://www.example.com/" + "x" * 2048,
]


@pytest.mark.parametrize("url", URL_FORMAT)
def test_malformed_url_is_refused_before_anything(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, stderr = _json(repo, ["google", "sc", "inspect", "--url", url])

    assert code == 2, stderr
    assert payload["rule"] == "url_format" and payload["state"] == "refused"
    assert "(url_format)" in stderr
    assert mint.calls == [] and api.calls == []


DOMAIN_OUTSIDE = [
    "https://evil.example/shoes/",
    "https://notexample.com/",
    "https://example.com.evil.example/",
    "https://wwwexample.com/",
    "https://example.co/",
    "https://127.0.0.1/",
]
DOMAIN_INSIDE = [
    "https://example.com/",
    "http://example.com/",
    "https://www.example.com/shoes/",
    "https://shop.eu.example.com/a?b=c",
    "HTTPS://WWW.EXAMPLE.COM/Shoes/",
    "https://www.example.com:8443/",
]


@pytest.mark.parametrize("url", DOMAIN_OUTSIDE)
def test_url_outside_a_domain_site_is_refused(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, stderr = _json(repo, ["google", "sc", "inspect", "--url", url])

    assert code == 2, stderr
    assert payload["rule"] == "url_outside_site" and payload["exit_code"] == 2
    assert "nothing was sent" in payload["summary"]
    assert mint.calls == [] and api.calls == []
    human = _run(repo, ["google", "sc", "inspect", "--url", url])
    assert human.exit_code == 2 and human.stdout == ""


@pytest.mark.parametrize("url", DOMAIN_INSIDE)
def test_url_inside_a_domain_site_is_inspected(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, ["google", "sc", "inspect", "--url", url])

    assert code == 0
    assert api.calls[0]["body"] == {"inspectionUrl": url, "siteUrl": SITE}
    assert payload["inspection_url"] == url


PREFIX_SITE = "https://www.example.com/blog/"
PREFIX_CASES = [
    ("https://www.example.com/blog/", True),
    ("https://www.example.com/blog/post-1", True),
    ("https://WWW.Example.COM/blog/post-1?x=1", True),
    ("HTTPS://www.example.com/blog/x", True),
    ("https://www.example.com:443/blog/x", True),
    ("https://www.example.com/blog", False),
    ("https://www.example.com/Blog/x", False),
    ("https://www.example.com/blogger/x", False),
    ("https://www.example.com/", False),
    ("http://www.example.com/blog/x", False),
    ("https://www.example.com:8443/blog/x", False),
    ("https://example.com/blog/x", False),
    ("https://shop.www.example.com/blog/x", False),
    ("https://www.example.com.evil.example/blog/x", False),
]


@pytest.mark.parametrize(("url", "inside"), PREFIX_CASES)
def test_url_prefix_site_matches_on_the_normalised_prefix(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    inside: bool,
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    _record_site(repo, PREFIX_SITE)
    mint = _mint(monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, ["google", "sc", "inspect", "--url", url])

    if inside:
        assert code == 0
        assert api.calls[0]["body"] == {"inspectionUrl": url, "siteUrl": PREFIX_SITE}
        assert payload["site"] == PREFIX_SITE
    else:
        assert code == 2 and payload["rule"] == "url_outside_site"
        assert mint.calls == [] and api.calls == []


@pytest.mark.parametrize(
    "url",
    [
        "https://www.example.com/blog/../admin/",
        "https://www.example.com/blog/%2e%2e/admin/",
        "https://www.example.com/blog/%2E%2E%2Fadmin/",
        "https://www.example.com/blog/./x",
    ],
)
def test_dot_segments_cannot_leave_the_prefix(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    _record_site(repo, PREFIX_SITE)
    mint = _mint(monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, ["google", "sc", "inspect", "--url", url])

    assert code == 2 and payload["rule"] == "url_format"
    assert mint.calls == [] and api.calls == []


def test_no_recorded_site_refuses_before_minting(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch, site=False)
    mint = _mint(monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 2 and payload["rule"] == "site_not_recorded"
    assert mint.calls == [] and api.calls == []


def test_url_is_required(repo: Path) -> None:
    result = _run(repo, ["google", "sc", "inspect"])
    assert result.exit_code == 2


# --- Credential failures (exit 1) -----------------------------------------------------------


def test_no_sign_in_is_not_connected(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 1 and payload["rule"] == "not_connected"
    assert api.calls == []


def test_search_console_not_granted_is_never_read(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch, scope=go.SCOPE_ANALYTICS)
    mint = _mint(monkeypatch)
    api = _inspect_api(monkeypatch)

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 1 and payload["rule"] == "grant_missing"
    assert payload["repair_command"] == "mb connect google --oauth --reauth"
    assert mint.calls == [] and api.calls == []


def test_invalid_grant_is_reauth_required_and_recorded(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    _mint(monkeypatch, status=400, payload={"error": "invalid_grant"})
    api = _inspect_api(monkeypatch)

    result = _run(repo, INSPECT_ARGS, "--json")

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["rule"] == "reauth_required" and payload["state"] == "reauth_required"
    assert payload["repair_command"] == "mb connect google --oauth --reauth"
    assert api.calls == []
    status = runner.invoke(app, ["connect", "status", "google", "--repo", str(repo), "--json"])
    assert json.loads(status.stdout)["state"] == "reauth_required"


# --- Provider failures (exit 1) -------------------------------------------------------------

INSPECT_FAILURES = [
    ((401, _error(401, canonical="UNAUTHENTICATED")), "search_console_auth_rejected", "", 1),
    ((403, _error(403, canonical="PERMISSION_DENIED")), "search_console_no_access", "", 1),
    ((403, _error(403, "SERVICE_DISABLED", canonical="PERMISSION_DENIED")), "search_console_api_disabled", "", 1),
    ((404, _error(404)), "search_console_no_access", "", 1),
    ((400, _error(400, canonical="INVALID_ARGUMENT")), "search_console_request_rejected", "", 1),
    ((429, _error(429, canonical="RESOURCE_EXHAUSTED")), "quota_exhausted", "RESOURCE_EXHAUSTED", 1),
    ((403, _error(403, "quotaExceeded")), "quota_exhausted", "quotaExceeded", 1),
    ((301, b""), "search_console_unexpected_redirect", "", 1),
    ((302, _error(302)), "search_console_unexpected_redirect", "", 1),
    ((500, _error(500, canonical="INTERNAL")), "search_console_server_error", "", 1),
    ((503, _error(503, canonical="UNAVAILABLE")), "search_console_server_error", "", 1),
    ((200, b"not json " + GOOGLE_TEXT.encode()), "search_console_response_malformed", "", 1),
    ((200, b"[]"), "search_console_response_malformed", "", 1),
    (OSError(f"refused {GOOGLE_TEXT} {MINTED}"), "search_console_unreachable", "", 2),
    (TimeoutError(GOOGLE_TEXT), "search_console_unreachable", "", 2),
]  # fmt: skip


@pytest.mark.parametrize(("answer", "rule", "quota", "calls"), INSPECT_FAILURES)
def test_provider_failures_exit_1_with_a_stable_rule(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    answer: Any,
    rule: str,
    quota: str,
    calls: int,
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    before = (repo / ".mb" / "connect.yaml").read_bytes()
    api = _inspect_api(monkeypatch, [answer, answer])

    result = _run(repo, INSPECT_ARGS, "--json")

    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["rule"] == rule and payload["exit_code"] == 1
    assert payload.get("quota", "") == quota
    # One retry only when no answer came back; never on a 5xx, 429 or 3xx.
    assert len(api.calls) == calls
    _assert_never_shown(result.output)
    # A provider failure is not recorded on the sign-in.
    assert (repo / ".mb" / "connect.yaml").read_bytes() == before
    if rule == "quota_exhausted":
        assert "2,000 a day and 600 a minute per site" in payload["summary"]
    if rule.endswith("_unreachable"):
        assert "could not be reached, or did not answer" in payload["summary"]


def test_one_retry_when_no_answer_came_back(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _inspect_api(monkeypatch, [TimeoutError("slow"), (200, _inspection())])

    code, payload, _ = _json(repo, INSPECT_ARGS)

    assert code == 0 and payload["inspection_result"]["indexStatusResult"]["verdict"] == "PASS"
    assert len(api.calls) == 2


def test_inspect_goes_through_the_shared_google_sender(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    monkeypatch.setattr(gr, "api_sender", None)
    seen: list[tuple[str, str, dict[str, Any], int]] = []

    def shared(
        url: str,
        body: bytes,
        headers: Any,
        timeout: float,
        *,
        method: str = "POST",
        max_bytes: int = 0,
    ) -> tuple[int, bytes]:
        seen.append((method, url, json.loads(body), max_bytes))
        return 200, b"{}"

    monkeypatch.setattr(go, "_urllib_sender", shared)

    assert _run(repo, INSPECT_ARGS).exit_code == 0
    assert seen == [
        ("POST", INSPECT_URL, {"inspectionUrl": PAGE, "siteUrl": SITE}, gr.RESPONSE_MAX_BYTES)
    ]


# --- Leaks, terminal safety and help -----------------------------------------------------------


def test_nothing_secret_or_from_google_leaks(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    outputs: list[str] = []
    for answer in (
        (200, _inspection()),
        (401, _error(401)),
        (403, _error(403)),
        (429, _error(429)),
        (500, _error(500)),
        (302, _error(302)),
        OSError(f"{GOOGLE_TEXT} {MINTED}"),
        RuntimeError(f"{GOOGLE_TEXT} {MINTED}"),
    ):
        _inspect_api(monkeypatch, answer)
        for extra in ((), ("--json",)):
            result = _run(repo, INSPECT_ARGS, *extra)
            outputs += [result.stdout, result.stderr]
    for args in (
        ["google", "sc", "inspect", "--url", "https://evil.example/"],
        ["google", "sc", "inspect", "--url", "ftp://www.example.com/"],
    ):
        result = _run(repo, args, "--json")
        outputs += [result.stdout, result.stderr]

    for text in outputs:
        _assert_never_shown(text)
    for path in repo.rglob("*"):
        if path.is_file():
            _assert_never_shown(path.read_text(encoding="utf-8", errors="replace"))


def test_terminal_escapes_are_stripped_from_the_summary_only(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    hostile = "\x1b]0;pwned\x07a‮b c\rd\x9b2J"
    _inspect_api(
        monkeypatch,
        (200, _inspection(coverageState=hostile, googleCanonical=hostile, crawledAs=hostile)),
    )

    human = _run(repo, INSPECT_ARGS)

    assert human.exit_code == 0
    for bad in ("\x1b", "\x07", "\x9b", "\r", "‮", " ", "pwned"):
        assert bad not in human.stdout
    assert "verdict: PASS (ab c d)" in human.stdout
    machine = _run(repo, INSPECT_ARGS, "--json")
    assert hostile in _strings(json.loads(machine.stdout))


_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def test_help() -> None:
    result = runner.invoke(app, ["google", "sc", "inspect", "--help"])
    assert result.exit_code == 0
    # CI renders Rich help with colour codes inside option names; compare plain text.
    text = " ".join(_ANSI.sub("", result.stdout).split())
    for words in ("--url", "--json", "--repo", "2,000", "600", "no live test"):
        assert words in text
    assert "--site " not in text and "--property" not in text
    group = _ANSI.sub("", runner.invoke(app, ["google", "sc", "--help"]).stdout)
    assert "inspect" in group
