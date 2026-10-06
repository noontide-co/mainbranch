"""Tests for the typed Google reads (#1004, PR6).

`mb google sc query`, `mb google sc sitemaps list` and `mb google ga4 report`
read a Google sign-in's recorded site and property with a token minted in
process. No network: the token endpoint and both APIs are stub senders behind
the existing seams; the loopback-only guard, the local-file credential store
and the synthetic sentinels come from test_google_connect.
"""

# The fixtures are imported from test_google_connect, so test parameters
# share their names by design.
# ruff: noqa: F811, E501

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from mb import google_connect as gc
from mb import google_oauth as go
from mb import google_reads as gr
from mb.cli import app
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    ACCESS,
    CLIENT_SECRET,
    LEGACY_TOKEN,
    MINTED,
    REFRESH,
    SENTINELS,
    _connect_legacy_token,
    client_file,
    google,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_mint import DESCRIPTION
from tests.test_google_probe import GOOGLE_TEXT, _mint, _sign_in

SITE = "sc-domain:example.com"
PROPERTY = "123456789"
SC_QUERY_URL = (
    "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com/searchAnalytics/query"
)
SC_SITEMAPS_URL = "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com/sitemaps"
GA4_URL = "https://analyticsdata.googleapis.com/v1beta/properties/123456789:runReport"
# Never in any output: secrets, and Google's own error text.
NEVER_SHOWN = (CLIENT_SECRET, REFRESH, MINTED, ACCESS, DESCRIPTION, GOOGLE_TEXT, LEGACY_TOKEN)
UNDOCUMENTED = "SYNTH-UNDOCUMENTED-0001"

SC_ARGS = ["google", "sc", "query", "--start", "2026-09-01", "--end", "2026-09-30"]
SITEMAPS_ARGS = ["google", "sc", "sitemaps", "list"]
GA4_ARGS = [
    "google",
    "ga4",
    "report",
    "--metrics",
    "activeUsers,sessions",
    "--dimensions",
    "date",
    "--start",
    "2026-09-01",
    "--end",
    "2026-09-30",
]


def _sc_rows(count: int, *, prefix: str = "q") -> dict[str, Any]:
    return {
        "rows": [
            {
                "keys": [f"{prefix}{index}"],
                "clicks": 10.0 - index,
                "impressions": 100.0,
                "ctr": 0.1,
                "position": 3.25,
            }
            for index in range(count)
        ],
        "responseAggregationType": "byProperty",
    }


def _ga4_rows(count: int, *, total: int | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dimensionHeaders": [{"name": "date"}],
        "metricHeaders": [{"name": "activeUsers"}, {"name": "sessions"}],
        "rows": [
            {
                "dimensionValues": [{"value": f"202609{index + 1:02d}"}],
                "metricValues": [{"value": str(5 + index)}, {"value": str(7 + index)}],
            }
            for index in range(count)
        ],
        "kind": "analyticsData#runReport",
        "propertyQuota": {
            "tokensPerDay": {"consumed": 4, "remaining": 199990},
            "tokensPerHour": {"consumed": 4, "remaining": 39990},
            "concurrentRequests": {"consumed": 0, "remaining": 10},
            "undocumentedQuota": {"consumed": 1, "remaining": UNDOCUMENTED},
        },
    }
    if total is not None:
        body["rowCount"] = total
    return body


def _error(status: int, *reasons: str, canonical: str = "OTHER") -> dict[str, Any]:
    return {
        "error": {
            "code": status,
            "message": f"{GOOGLE_TEXT} {DESCRIPTION}",
            "status": canonical,
            "errors": [{"reason": reason, "message": GOOGLE_TEXT} for reason in reasons],
            "details": [{"reason": reason, "metadata": {"x": GOOGLE_TEXT}} for reason in reasons],
        }
    }


class ReadsEndpoint:
    """Stub for the read endpoints, keyed by URL.

    Each answer is ``(status, payload)``, ``(status, raw bytes)``, an exception
    to raise, or a list of those consumed in order.
    """

    def __init__(self, answers: dict[str, Any] | None = None) -> None:
        self.answers = dict(answers or {})
        self.calls: list[dict[str, Any]] = []

    def __call__(
        self,
        method: str,
        url: str,
        body: bytes | None,
        headers: Mapping[str, str],
        timeout: float,
    ) -> tuple[int, bytes]:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "body": json.loads(body.decode("utf-8")) if body is not None else None,
                "authorization": headers.get("Authorization"),
                "content_type": headers.get("Content-Type"),
            }
        )
        base = url.split("?", 1)[0]
        answer = self.answers.get(url, self.answers.get(base))
        if isinstance(answer, list):
            answer = answer.pop(0)
        if answer is None:
            if base == SC_QUERY_URL:
                answer = (200, _sc_rows(3))
            elif base == SC_SITEMAPS_URL:
                answer = (200, {"sitemap": []})
            elif base == GA4_URL:
                answer = (200, _ga4_rows(2, total=2))
            else:
                pytest.fail("unexpected Google URL")
        if isinstance(answer, BaseException):
            raise answer
        status, payload = answer
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        return status, raw


def _reads(monkeypatch: pytest.MonkeyPatch, **answers: Any) -> ReadsEndpoint:
    endpoint = ReadsEndpoint(
        {
            {"sc": SC_QUERY_URL, "sitemaps": SC_SITEMAPS_URL, "ga4": GA4_URL}[key]: value
            for key, value in answers.items()
        }
    )
    monkeypatch.setattr(gr, "api_sender", endpoint)
    return endpoint


def _signed_in(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, **kwargs: Any
) -> Any:
    """Sign in (stubbed), then stub the refresh grant. Returns the mint stub."""

    _sign_in(repo, client_file, google, monkeypatch, **kwargs)
    return _mint(monkeypatch)


def _run(repo: Path, args: list[str], *extra: str) -> Any:
    return runner.invoke(app, [*args, "--repo", str(repo), *extra])


def _json(repo: Path, args: list[str], *extra: str) -> tuple[int, dict[str, Any], str]:
    result = _run(repo, args, *extra, "--json")
    return result.exit_code, json.loads(result.stdout), result.stderr


def _assert_never_shown(text: str) -> None:
    for sentinel in (*NEVER_SHOWN, *SENTINELS):
        assert sentinel not in text


# --- Search Console: query ---------------------------------------------------------


def test_sc_query_reads_the_recorded_site(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch)

    code, payload, stderr = _json(repo, SC_ARGS, "--dimensions", "query")

    assert code == 0, stderr
    assert len(mint.calls) == 1
    assert api.calls == [
        {
            "method": "POST",
            "url": SC_QUERY_URL,
            "body": {
                "startDate": "2026-09-01",
                "endDate": "2026-09-30",
                "type": "web",
                "rowLimit": 1000,
                "startRow": 0,
                "dataState": "final",
                "dimensions": ["query"],
            },
            "authorization": f"Bearer {MINTED}",
            "content_type": "application/json",
        }
    ]
    assert payload["result_schema"]["name"] == "mb.google.sc.query"
    assert payload["mb_command"] == "mb google sc query"
    assert payload["ok"] is True and payload["errors"] == []
    assert payload["site"] == SITE
    assert payload["range"] == {
        "start": "2026-09-01",
        "end": "2026-09-30",
        "timezone": "America/Los_Angeles",
    }
    assert payload["row_count"] == 3 and payload["may_have_more"] is False
    assert payload["next_start_row"] is None
    assert payload["rows"][0] == {
        "keys": ["q0"],
        "clicks": 10.0,
        "impressions": 100.0,
        "ctr": 0.1,
        "position": 3.25,
    }
    assert payload["response_aggregation_type"] == "byProperty"
    assert payload["data_state"] == "final"


def test_sc_query_options_shape_the_request(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch)

    code, payload, _ = _json(
        repo,
        SC_ARGS,
        "--dimensions",
        "query,page",
        "--dimensions",
        "date",
        "--type",
        "discover",
        "--filter",
        "query:contains:blue shoes",
        "--filter",
        "page:includingRegex:^https://www.example.com/a:b/",
        "--row-limit",
        "25000",
        "--start-row",
        "50",
        "--fresh",
    )

    assert code == 0
    assert api.calls[0]["body"] == {
        "startDate": "2026-09-01",
        "endDate": "2026-09-30",
        "type": "discover",
        "rowLimit": 25000,
        "startRow": 50,
        "dataState": "all",
        "dimensions": ["query", "page", "date"],
        "dimensionFilterGroups": [
            {
                "groupType": "and",
                "filters": [
                    {"dimension": "query", "operator": "contains", "expression": "blue shoes"},
                    {
                        "dimension": "page",
                        "operator": "includingRegex",
                        "expression": "^https://www.example.com/a:b/",
                    },
                ],
            }
        ],
    }
    assert payload["data_state"] == "all"
    assert payload["filters"][1]["expression"] == "^https://www.example.com/a:b/"


def test_sc_query_paging_says_when_more_rows_may_follow(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(
        monkeypatch, sc=[(200, _sc_rows(2)), (200, _sc_rows(1, prefix="r")), (200, _sc_rows(2))]
    )

    code, first, _ = _json(repo, SC_ARGS, "--row-limit", "2")
    assert code == 0
    assert first["may_have_more"] is True and first["next_start_row"] == 2

    code, second, _ = _json(repo, SC_ARGS, "--row-limit", "2", "--start-row", "2")
    assert code == 0
    assert api.calls[1]["body"]["startRow"] == 2
    assert second["start_row"] == 2 and second["row_count"] == 1
    assert second["may_have_more"] is False and second["next_start_row"] is None

    human = _run(repo, SC_ARGS, "--row-limit", "2")
    assert "more rows may follow: --start-row 2" in human.stdout


@pytest.mark.parametrize(
    "answer", [(200, {"responseAggregationType": "auto"}), (200, {"rows": []}), (200, b"")]
)
def test_sc_query_zero_rows_is_ok(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    answer: Any,
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch, sc=answer)

    code, payload, _ = _json(repo, SC_ARGS)

    assert code == 0
    assert payload["rows"] == [] and payload["row_count"] == 0
    assert payload["may_have_more"] is False
    human = _run(repo, SC_ARGS)
    assert human.exit_code == 0 and "rows: 0" in human.stdout


def test_sc_query_url_prefix_site_is_percent_encoded(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    edit = runner.invoke(
        app,
        [
            "connect",
            "google",
            "--repo",
            str(repo),
            "--metadata",
            "search_console_site=https://www.example.com/blog/",
        ],
    )
    assert edit.exit_code == 0, edit.output
    _mint(monkeypatch)
    url = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        "https%3A%2F%2Fwww.example.com%2Fblog%2F/searchAnalytics/query"
    )
    api = ReadsEndpoint({url: (200, _sc_rows(1))})
    monkeypatch.setattr(gr, "api_sender", api)

    code, payload, _ = _json(repo, SC_ARGS)

    assert code == 0
    assert api.calls[0]["url"] == url
    assert payload["site"] == "https://www.example.com/blog/"


def test_sc_query_human_table(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch)

    result = _run(repo, SC_ARGS, "--dimensions", "query")

    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert lines[0] == f"Search Console: {SITE}"
    assert "2026-09-01 to 2026-09-30 (America/Los_Angeles)" in lines[1]
    assert lines[3].split() == ["query", "clicks", "impressions", "ctr", "position"]
    assert lines[4].split() == ["q0", "10", "100", "0.1000", "3.2"]


# --- Search Console: sitemaps --------------------------------------------------------


def test_sitemaps_list_passes_documented_fields_through(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    long_path = "https://www.example.com/" + "a" * 5000 + ".xml"
    api = _reads(
        monkeypatch,
        sitemaps=(
            200,
            {
                "sitemap": [
                    {
                        "path": "https://www.example.com/sitemap.xml",
                        "lastSubmitted": "2026-09-01T10:00:00.000Z",
                        "lastDownloaded": "2026-09-02T10:00:00.000Z",
                        "isPending": False,
                        "isSitemapsIndex": True,
                        "type": "sitemap",
                        "warnings": "2",
                        "errors": "0",
                        "contents": [{"type": "web", "submitted": "120", "indexed": "99"}],
                        "undocumented": UNDOCUMENTED,
                    },
                    {"path": long_path, "isPending": True, "warnings": 0, "errors": 1},
                ]
            },
        ),
    )

    code, payload, _ = _json(repo, SITEMAPS_ARGS)

    assert code == 0
    assert api.calls == [
        {
            "method": "GET",
            "url": SC_SITEMAPS_URL,
            "body": None,
            "authorization": f"Bearer {MINTED}",
            "content_type": None,
        }
    ]
    assert payload["result_schema"]["name"] == "mb.google.sc.sitemaps"
    assert payload["site"] == SITE and payload["sitemap_count"] == 2
    first, second = payload["sitemaps"]
    assert first == {
        "path": "https://www.example.com/sitemap.xml",
        "lastSubmitted": "2026-09-01T10:00:00.000Z",
        "lastDownloaded": "2026-09-02T10:00:00.000Z",
        "type": "sitemap",
        "isPending": False,
        "isSitemapsIndex": True,
        "warnings": 2,
        "errors": 0,
        "contents": [{"type": "web", "submitted": 120}],
    }
    assert len(second["path"]) == gr.STRING_MAX and second["path"].endswith("…")
    assert UNDOCUMENTED not in json.dumps(payload)

    human = _run(repo, SITEMAPS_ARGS)
    assert human.exit_code == 0
    assert "sitemaps: 2" in human.stdout
    assert max(len(line) for line in human.stdout.splitlines()) < 400


def test_sitemaps_list_with_an_index_and_none_submitted(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch, sitemaps=(200, {}))

    code, payload, _ = _json(
        repo, SITEMAPS_ARGS, "--sitemap-index", "https://www.example.com/sitemap_index.xml"
    )

    assert code == 0
    assert api.calls[0]["url"] == (
        SC_SITEMAPS_URL + "?sitemapIndex=https%3A%2F%2Fwww.example.com%2Fsitemap_index.xml"
    )
    assert payload["sitemaps"] == [] and payload["sitemap_count"] == 0
    assert payload["sitemap_index"] == "https://www.example.com/sitemap_index.xml"


# --- GA4: report ---------------------------------------------------------------------


def test_ga4_report_reads_the_recorded_property(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch)

    code, payload, stderr = _json(repo, GA4_ARGS, "--order-by", "sessions:desc")

    assert code == 0, stderr
    assert len(mint.calls) == 1
    assert api.calls == [
        {
            "method": "POST",
            "url": GA4_URL,
            "body": {
                "dateRanges": [{"startDate": "2026-09-01", "endDate": "2026-09-30"}],
                "metrics": [{"name": "activeUsers"}, {"name": "sessions"}],
                "dimensions": [{"name": "date"}],
                "limit": "1000",
                "offset": "0",
                "returnPropertyQuota": True,
                "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            },
            "authorization": f"Bearer {MINTED}",
            "content_type": "application/json",
        }
    ]
    assert payload["result_schema"]["name"] == "mb.google.ga4.report"
    assert payload["property_id"] == PROPERTY
    assert payload["dimensions"] == ["date"]
    assert payload["metrics"] == ["activeUsers", "sessions"]
    assert payload["rows"] == [
        {"dimensions": {"date": "20260901"}, "metrics": {"activeUsers": "5", "sessions": "7"}},
        {"dimensions": {"date": "20260902"}, "metrics": {"activeUsers": "6", "sessions": "8"}},
    ]
    assert payload["row_count"] == 2 and payload["total_row_count"] == 2
    assert payload["may_have_more"] is False
    assert payload["property_quota"] == {
        "tokensPerDay": {"consumed": 4, "remaining": 199990},
        "tokensPerHour": {"consumed": 4, "remaining": 39990},
        "concurrentRequests": {"consumed": 0, "remaining": 10},
    }
    assert UNDOCUMENTED not in json.dumps(payload)

    human = _run(repo, GA4_ARGS)
    assert human.exit_code == 0
    assert human.stdout.splitlines()[3].split() == ["date", "activeUsers", "sessions"]
    assert "quota: 199990 tokens left today, 39990 this hour, this read used 4" in human.stdout


def test_ga4_report_dimension_order_and_paging(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch, ga4=[(200, _ga4_rows(2, total=5)), (200, _ga4_rows(1, total=5))])

    code, first, _ = _json(repo, GA4_ARGS, "--limit", "2", "--order-by", "date")
    assert code == 0
    assert api.calls[0]["body"]["orderBys"] == [
        {"dimension": {"dimensionName": "date"}, "desc": False}
    ]
    assert first["may_have_more"] is True and first["next_offset"] == 2

    code, last, _ = _json(repo, GA4_ARGS, "--limit", "2", "--offset", "4")
    assert code == 0
    assert api.calls[1]["body"]["offset"] == "4"
    assert last["may_have_more"] is False and last["next_offset"] is None


def test_ga4_report_zero_rows_is_ok(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch, ga4=(200, {"kind": "analyticsData#runReport"}))

    code, payload, _ = _json(repo, GA4_ARGS)

    assert code == 0
    assert payload["rows"] == [] and payload["may_have_more"] is False
    assert "property_quota" not in payload


# --- Refusals (exit 2, nothing called) -------------------------------------------------


REFUSALS = [
    (SC_ARGS[:3] + ["--start", "2026-9-01", "--end", "2026-09-30"], "bad_date"),
    (SC_ARGS[:3] + ["--start", "2026-02-30", "--end", "2026-03-01"], "bad_date"),
    (SC_ARGS[:3] + ["--start", "2026-09-30", "--end", "2026-09-01"], "bad_date"),
    (SC_ARGS[:3] + ["--start", "2026-09-01\n", "--end", "2026-09-30"], "bad_date"),
    (GA4_ARGS[:3] + ["--metrics", "ses\nsions", "--start", "2026-09-01", "--end", "2026-09-30"], "name_format"),
    (GA4_ARGS + ["--order-by", "sessions\n"], "name_format"),
    (SC_ARGS + ["--row-limit", "0"], "row_limit_range"),
    (SC_ARGS + ["--row-limit", "25001"], "row_limit_range"),
    (SC_ARGS + ["--start-row", "-1"], "row_limit_range"),
    (SC_ARGS + ["--dimensions", "query,hour"], "unknown_dimension"),
    (SC_ARGS + ["--dimensions", "query,query"], "unknown_dimension"),
    (SC_ARGS + ["--filter", "query:contains"], "filter_format"),
    (SC_ARGS + ["--filter", "date:equals:2026-09-01"], "filter_format"),
    (SC_ARGS + ["--filter", "query:like:shoes"], "filter_format"),
    (SC_ARGS + ["--filter", "query:equals:" + "x" * 4097], "filter_format"),
    (SC_ARGS + ["--type", "shopping"], "unknown_type"),
    (SITEMAPS_ARGS + ["--sitemap-index", "ftp://www.example.com/index.xml"], "sitemap_index_format"),
    (SITEMAPS_ARGS + ["--sitemap-index", "https://u:p@www.example.com/i.xml"], "sitemap_index_format"),
    (GA4_ARGS[:3] + ["--metrics", "active users", "--start", "2026-09-01", "--end", "2026-09-30"], "name_format"),
    (GA4_ARGS + ["--dimensions", "1date"], "name_format"),
    (GA4_ARGS + ["--order-by", "sessions:sideways"], "name_format"),
    (GA4_ARGS + ["--order-by", "country"], "order_by_unknown"),
    (GA4_ARGS + ["--limit", "0"], "limit_range"),
    (GA4_ARGS + ["--limit", "250001"], "limit_range"),
    (GA4_ARGS + ["--offset", "-5"], "limit_range"),
    (GA4_ARGS[:5] + ["--start", "today", "--end", "2026-09-30"], "bad_date"),
]  # fmt: skip


@pytest.mark.parametrize(("args", "rule"), REFUSALS)
def test_refusals_exit_2_and_call_nothing(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
    rule: str,
) -> None:
    mint = _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch)

    code, payload, stderr = _json(repo, args)

    assert code == 2, stderr
    assert payload["ok"] is False and payload["rule"] == rule
    assert payload["state"] == "refused" and payload["exit_code"] == 2
    assert payload["errors"] == [{"code": rule, "message": payload["summary"]}]
    assert f"({rule})" in stderr
    assert mint.calls == [] and api.calls == []

    human = _run(repo, args)
    assert human.exit_code == 2 and human.stdout == ""


@pytest.mark.parametrize(
    ("args", "missing", "rule", "repair"),
    [
        (SC_ARGS, "site", "site_not_recorded", "search_console_site=<site>"),
        (SITEMAPS_ARGS, "site", "site_not_recorded", "search_console_site=<site>"),
        (GA4_ARGS, "property_id", "property_not_recorded", "ga4_property_id=<property-id>"),
    ],
)
def test_missing_recorded_ids_refuse_before_minting(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
    missing: str,
    rule: str,
    repair: str,
) -> None:
    _sign_in(repo, client_file, google, monkeypatch, **{missing: False})
    mint = _mint(monkeypatch)
    api = _reads(monkeypatch)

    code, payload, stderr = _json(repo, args)

    assert code == 2
    assert payload["rule"] == rule
    assert payload["repair_command"].endswith(repair)
    assert f"next: {payload['repair_command']}" in stderr
    assert mint.calls == [] and api.calls == []


# --- Credential failures (exit 1) -------------------------------------------------------


@pytest.mark.parametrize("args", [SC_ARGS, SITEMAPS_ARGS, GA4_ARGS])
def test_no_sign_in_is_not_connected(
    repo: Path, monkeypatch: pytest.MonkeyPatch, args: list[str]
) -> None:
    api = _reads(monkeypatch)

    code, payload, _ = _json(repo, args)

    assert code == 1
    assert payload["rule"] == "not_connected" and payload["state"] == "not_connected"
    assert payload["repair_command"].startswith("mb connect google --oauth")
    assert api.calls == []


def test_legacy_access_token_connection_is_not_read(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _connect_legacy_token(repo)
    api = _reads(monkeypatch)

    for args in (SC_ARGS, SITEMAPS_ARGS, GA4_ARGS):
        result = _run(repo, args, "--json")
        assert result.exit_code == 1
        assert json.loads(result.stdout)["rule"] == "not_connected"
        _assert_never_shown(result.output)
    assert api.calls == []


def test_a_product_not_granted_is_never_read(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch, scope=go.SCOPE_SEARCH_CONSOLE)
    mint = _mint(monkeypatch)
    api = _reads(monkeypatch)

    code, payload, _ = _json(repo, GA4_ARGS)

    assert code == 1
    assert payload["rule"] == "grant_missing"
    assert payload["repair_command"] == "mb connect google --oauth --reauth"
    assert mint.calls == [] and api.calls == []

    code, payload, _ = _json(repo, SC_ARGS)
    assert code == 0 and [call["url"] for call in api.calls] == [SC_QUERY_URL]


@pytest.mark.parametrize("args", [SC_ARGS, SITEMAPS_ARGS, GA4_ARGS])
def test_invalid_grant_is_reauth_required_and_recorded(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    _mint(
        monkeypatch,
        status=400,
        payload={"error": "invalid_grant", "error_description": DESCRIPTION},
    )
    api = _reads(monkeypatch)

    result = _run(repo, args, "--json")

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["rule"] == "reauth_required" and payload["state"] == "reauth_required"
    assert payload["repair_command"] == "mb connect google --oauth --reauth"
    assert api.calls == []
    _assert_never_shown(result.output)
    status = runner.invoke(app, ["connect", "status", "google", "--repo", str(repo), "--json"])
    assert json.loads(status.stdout)["state"] == "reauth_required"


# --- Provider failures (exit 1) ----------------------------------------------------------

PROVIDER_FAILURES = [
    ((401, _error(401, canonical="UNAUTHENTICATED")), "auth_rejected", "", 1),
    ((403, _error(403, canonical="PERMISSION_DENIED")), "no_access", "", 1),
    ((403, _error(403, "SERVICE_DISABLED", canonical="PERMISSION_DENIED")), "api_disabled", "", 1),
    ((403, _error(403, "accessNotConfigured")), "api_disabled", "", 1),
    ((404, _error(404)), "no_access", "", 1),
    ((400, _error(400, "invalidParameter", canonical="INVALID_ARGUMENT")), "request_rejected", "", 1),
    ((429, _error(429, canonical="RESOURCE_EXHAUSTED")), "quota_exhausted", "RESOURCE_EXHAUSTED", 1),
    ((403, _error(403, "quotaExceeded")), "quota_exhausted", "quotaExceeded", 1),
    ((429, b"<html>" + GOOGLE_TEXT.encode() + b"</html>"), "quota_exhausted", "", 1),
    ((301, b""), "unexpected_redirect", "", 1),
    ((307, _error(307)), "unexpected_redirect", "", 1),
    ((500, _error(500, canonical="INTERNAL")), "server_error", "", 1),
    ((503, _error(503, "backendError", canonical="UNAVAILABLE")), "server_error", "", 1),
    ((200, b"not json " + GOOGLE_TEXT.encode()), "response_malformed", "", 1),
    ((200, b"[" * 200000), "response_malformed", "", 1),
    (OSError(f"refused {GOOGLE_TEXT} {MINTED}"), "unreachable", "", 2),
    (TimeoutError(GOOGLE_TEXT), "unreachable", "", 2),
]  # fmt: skip


@pytest.mark.parametrize(
    ("which", "args"), [("sc", SC_ARGS), ("sitemaps", SITEMAPS_ARGS), ("ga4", GA4_ARGS)]
)
@pytest.mark.parametrize(("answer", "rule", "quota", "calls"), PROVIDER_FAILURES)
def test_provider_failures_exit_1_with_a_stable_rule(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    which: str,
    args: list[str],
    answer: Any,
    rule: str,
    quota: str,
    calls: int,
) -> None:  # fmt: skip
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch, **{which: [answer, answer]})

    result = _run(repo, args, "--json")

    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    prefix = "ga4" if which == "ga4" else "search_console"
    assert payload["rule"] == (rule if rule == "quota_exhausted" else f"{prefix}_{rule}")
    assert payload.get("quota", "") == quota
    assert payload["ok"] is False and payload["exit_code"] == 1
    # No retry on a 5xx or any answer; one retry only when Google was never reached.
    assert len(api.calls) == calls
    _assert_never_shown(result.output)


def test_one_retry_when_google_was_not_reached(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    api = _reads(monkeypatch, ga4=[OSError("reset"), (200, _ga4_rows(1, total=1))])

    code, payload, _ = _json(repo, GA4_ARGS)

    assert code == 0 and payload["row_count"] == 1
    assert len(api.calls) == 2


def test_a_crashing_sender_is_hidden_and_exits_1(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    _reads(monkeypatch, sc=RuntimeError(f"{GOOGLE_TEXT} {MINTED}"))

    result = _run(repo, SC_ARGS, "--json")

    assert result.exit_code == 1
    assert "unexpected error (RuntimeError)" in result.stderr
    _assert_never_shown(result.output)


# --- Leaks and terminal safety --------------------------------------------------------------


def test_nothing_secret_or_from_google_leaks(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    outputs: list[str] = []
    for answers in (
        {},
        {"sc": (403, _error(403)), "sitemaps": (500, _error(500)), "ga4": (429, _error(429))},
        {"sc": (401, _error(401)), "sitemaps": (404, _error(404)), "ga4": (400, _error(400))},
    ):
        _reads(monkeypatch, **answers)
        for args in (SC_ARGS, SITEMAPS_ARGS, GA4_ARGS):
            for extra in ((), ("--json",)):
                result = _run(repo, args, *extra)
                outputs += [result.stdout, result.stderr]

    for text in outputs:
        _assert_never_shown(text)
    # Library callers: neither the connection nor the grant shows a secret in repr.
    conn = gr.connect(gr.SEARCH_CONSOLE, repo)
    assert conn.bearer is not None and conn.bearer.token == MINTED
    for text in (repr(conn), repr(conn.bearer), str(conn)):
        _assert_never_shown(text)
    grant = gc._grant_fields(
        json.dumps({"client_id": "c", "client_secret": CLIENT_SECRET, "refresh_token": REFRESH})
    )
    assert grant is not None and grant.refresh_token == REFRESH
    _assert_never_shown(repr(grant))
    # Nothing a read did was written to the repo or the secret store.
    for path in repo.rglob("*"):
        if path.is_file():
            _assert_never_shown(path.read_text(encoding="utf-8", errors="replace"))


def test_terminal_escapes_are_stripped_from_human_output_only(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    hostile = "\x1b[31mred\x1b[0m \x1b]0;pwned\x07title\x07bell\rcr\nnl\x9b2Jcsi\x00nul"
    _reads(
        monkeypatch,
        sc=(200, {"rows": [{"keys": [hostile], "clicks": 1, "impressions": 2}]}),
        sitemaps=(200, {"sitemap": [{"path": hostile, "type": hostile}]}),
        ga4=(
            200,
            {
                "rows": [
                    {"dimensionValues": [{"value": hostile}], "metricValues": [{"value": hostile}]}
                ],
                "rowCount": 1,
            },
        ),
    )

    for args in (SC_ARGS + ["--dimensions", "query"], SITEMAPS_ARGS, GA4_ARGS):
        human = _run(repo, args)
        assert human.exit_code == 0
        for bad in ("\x1b", "\x07", "\x9b", "\x00", "\r", "pwned"):
            assert bad not in human.stdout
        assert "red" in human.stdout and "csi" in human.stdout
        # The CR and LF inside the value became spaces: the row stays on one line.
        assert "bell cr nl" in human.stdout

        machine = _run(repo, args, "--json")
        assert hostile in _strings(json.loads(machine.stdout))


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


@pytest.mark.parametrize(
    ("value", "shown"),
    [
        ("plain", "plain"),
        ("\x1b[1;31mbold\x1b[0m", "bold"),
        ("\x1b]8;;https://evil.example/\x1b\\link\x1b]8;;\x1b\\", "link"),
        ("tab\there", "tab here"),
        ("x" * 200, "x" * 79 + "…"),
    ],
)
def test_terminal_safe(value: str, shown: str) -> None:
    assert gr.terminal_safe(value) == shown


# --- Help, and user scope ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("args", "words"),
    [
        (["google"], ["sc", "ga4", "read-only"]),
        (["google", "sc"], ["query", "sitemaps"]),
        (["google", "sc", "query"], ["--start", "--end", "--row-limit", "--start-row", "--fresh"]),
        (["google", "sc", "sitemaps", "list"], ["--sitemap-index", "--json"]),
        (["google", "ga4", "report"], ["--metrics", "--dimensions", "--limit", "--order-by"]),
    ],
)
def test_help(args: list[str], words: list[str]) -> None:
    result = runner.invoke(app, [*args, "--help"])
    assert result.exit_code == 0
    for word in words:
        assert word in result.stdout
    assert "--site " not in result.stdout and "--property" not in result.stdout


def test_user_scope_sign_in_is_read(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch, "--scope", "user")
    _mint(monkeypatch)
    api = _reads(monkeypatch)

    code, payload, _ = _json(repo, GA4_ARGS)

    assert code == 0 and payload["property_id"] == PROPERTY
    assert len(api.calls) == 1


def test_reads_go_through_the_shared_google_sender(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    monkeypatch.setattr(gr, "api_sender", None)
    seen: list[tuple[str, str, bytes, int]] = []

    def shared(
        url: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
        *,
        method: str = "POST",
        max_bytes: int = 0,
    ) -> tuple[int, bytes]:
        seen.append((method, url, body, max_bytes))
        return 200, b"{}"

    monkeypatch.setattr(go, "_urllib_sender", shared)

    assert _run(repo, SITEMAPS_ARGS).exit_code == 0
    assert _run(repo, SC_ARGS).exit_code == 0
    assert [(method, url, body == b"") for method, url, body, _ in seen] == [
        ("GET", SC_SITEMAPS_URL, True),
        ("POST", SC_QUERY_URL, False),
    ]
    assert all(max_bytes == gr.RESPONSE_MAX_BYTES for *_, max_bytes in seen)


def test_a_redirect_is_never_followed_or_recorded(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, monkeypatch)
    before = (repo / ".mb" / "connect.yaml").read_bytes()
    status_before = runner.invoke(
        app, ["connect", "status", "google", "--repo", str(repo), "--json"]
    )
    api = _reads(monkeypatch, ga4=(302, b""), sc=(308, b""))

    for args, rule in (
        (GA4_ARGS, "ga4_unexpected_redirect"),
        (SC_ARGS, "search_console_unexpected_redirect"),
    ):
        code, payload, _ = _json(repo, args)
        assert code == 1 and payload["rule"] == rule
    assert len(api.calls) == 2
    assert (repo / ".mb" / "connect.yaml").read_bytes() == before
    status_after = runner.invoke(
        app, ["connect", "status", "google", "--repo", str(repo), "--json"]
    )
    assert json.loads(status_after.stdout)["state"] == json.loads(status_before.stdout)["state"]
