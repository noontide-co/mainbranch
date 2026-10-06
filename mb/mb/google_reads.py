"""Typed read-only Google reads: ``mb google sc query``, ``sc sitemaps list``, ``ga4 report``.

These read a Google sign-in made with ``mb connect google --oauth`` (#1004).
The site and property come only from the metadata recorded on that sign-in
(``search_console_site``, ``ga4_property_id``); there is no override flag,
because agents read identity from recorded facts, never infer it (#834).

The access token is minted in this process through
``google_connect.read_minted_token`` and is held only in a ``repr=False``
wrapper. It is never printed, returned, written, or handed to a child or
argv. Only products the sign-in granted are read; ``invalid_grant`` is
recorded as ``reauth_required`` by ``read_minted_token``, as for
``mb connect token``/``exec``/``test``.

Each command makes one request. A request that never reached Google is
retried once; nothing else is retried (GA4 charges server errors against
quota). Google's error text is never read into the output: an error answer is
matched only against short allowlists of status codes and reasons, and the
command reports a stable ``rule`` with fixed text.

Exit codes: 0 ok (zero rows is ok); 1 credential or provider failure; 2 a
usage error or refusal. Every result carries ``rule`` when it is not ok.
"""

from __future__ import annotations

import http.client
import json
import re
import urllib.parse
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from mb import connect as connect_mod
from mb import google_connect as gc
from mb import google_oauth as go

SEARCH_CONSOLE = "search_console"
GA4 = "ga4"
PRODUCT_NAMES = {SEARCH_CONSOLE: "Search Console", GA4: "Analytics (GA4)"}

SC_QUERY_URL = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
SC_SITEMAPS_URL = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps"
GA4_RUN_REPORT_URL = "https://analyticsdata.googleapis.com/v1beta/properties/{property}:runReport"

SC_QUERY_COMMAND = "mb google sc query"
SC_SITEMAPS_COMMAND = "mb google sc sitemaps list"
GA4_REPORT_COMMAND = "mb google ga4 report"
SCHEMA_SC_QUERY = "mb.google.sc.query"
SCHEMA_SC_SITEMAPS = "mb.google.sc.sitemaps"
SCHEMA_GA4_REPORT = "mb.google.ga4.report"

# Search Console dates are Pacific Time (searchAnalytics.query docs).
SC_TIMEZONE = "America/Los_Angeles"
SC_ROW_LIMIT_DEFAULT = 1000
SC_ROW_LIMIT_MAX = 25000
SC_DIMENSIONS = ("query", "page", "date", "country", "device", "searchAppearance")
SC_FILTER_DIMENSIONS = ("query", "page", "country", "device", "searchAppearance")
SC_FILTER_OPERATORS = (
    "equals",
    "notEquals",
    "contains",
    "notContains",
    "includingRegex",
    "excludingRegex",
)
SC_FILTER_EXPRESSION_MAX = 4096
SC_TYPES = ("web", "image", "video", "news", "discover", "googleNews")
GA4_LIMIT_DEFAULT = 1000
GA4_LIMIT_MAX = 250000
# Sitemap strings longer than this are cut (JSON); human cells are cut shorter.
STRING_MAX = 2048
HUMAN_CELL_MAX = 80
SITEMAP_INDEX_MAX = 2048

REQUEST_TIMEOUT_SECONDS = 60.0
# A report of 25,000 rows is a few MiB; anything far bigger is not an answer.
RESPONSE_MAX_BYTES = 64 * 1024 * 1024

# Matched with `fullmatch`: `$` alone would accept a trailing newline.
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_GA4_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_:]*")
# C0/C1 control characters (ESC included, so ANSI sequences lose their
# introducer) and the ANSI CSI/OSC sequences themselves.
_ANSI_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?|\x9b[0-?]*[ -/]*[@-~]"
)
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Google error reasons matched by exact value (never shown as Google sent
# them): quota or rate limits, and an API not enabled in the Cloud project.
QUOTA_REASONS = (
    "RESOURCE_EXHAUSTED",
    "RATE_LIMIT_EXCEEDED",
    "quotaExceeded",
    "rateLimitExceeded",
    "userRateLimitExceeded",
    "dailyLimitExceeded",
    "concurrentLimitExceeded",
)
_API_DISABLED_REASONS = frozenset({"SERVICE_DISABLED", "accessNotConfigured"})

ApiSender = Callable[[str, str, bytes | None, Mapping[str, str], float], tuple[int, bytes]]


def _default_sender(
    method: str, url: str, body: bytes | None, headers: Mapping[str, str], timeout: float
) -> tuple[int, bytes]:
    """Google's shared sender (``google_oauth._urllib_sender``), for GET and POST."""
    return go._urllib_sender(
        url, body or b"", headers, timeout, method=method, max_bytes=RESPONSE_MAX_BYTES
    )


# Test seams. The CLI uses these defaults; tests replace them.
api_sender: ApiSender | None = None


class ReadRefusal(ValueError):
    """A usage error or refusal: exit 2 with a stable ``rule`` and fixed text."""

    def __init__(self, rule: str, message: str, *, repair_command: str = "") -> None:
        super().__init__(message)
        self.rule = rule
        self.repair_command = repair_command


@dataclass(frozen=True)
class _Bearer:
    """The minted access token, kept out of ``repr`` and every result."""

    token: str = field(repr=False)


@dataclass(frozen=True)
class _Connection:
    product: str
    target: Path
    site: str = ""
    property_id: str = ""
    bearer: _Bearer | None = field(default=None, repr=False)


# --- Display safety ------------------------------------------------------------


def terminal_safe(value: Any, limit: int = HUMAN_CELL_MAX) -> str:
    """``value`` as one line with ANSI sequences and control characters removed."""

    text = _CONTROL_RE.sub(" ", _ANSI_RE.sub("", str(value)))
    if len(text) > limit:
        text = text[: max(0, limit - 1)] + "…"
    return text


def _cut(value: Any) -> Any:
    if isinstance(value, str) and len(value) > STRING_MAX:
        return value[: STRING_MAX - 1] + "…"
    return value


# --- Validation (exit 2) -------------------------------------------------------


def _date(value: str, flag: str) -> str:
    text = value
    if _DATE_RE.fullmatch(text):
        try:
            date.fromisoformat(text)
            return text
        except ValueError:
            pass
    raise ReadRefusal("bad_date", f"{flag} must be a date in YYYY-MM-DD form.")


def _range(start: str, end: str) -> tuple[str, str]:
    first, last = _date(start, "--start"), _date(end, "--end")
    if first > last:
        raise ReadRefusal("bad_date", "--start must be on or before --end.")
    return first, last


def _names(raw: list[str]) -> list[str]:
    """Comma-separated or repeated option values, in order, without blanks."""

    found: list[str] = []
    for item in raw:
        found.extend(part.strip() for part in item.split(",") if part.strip())
    return found


def sc_dimensions(raw: list[str]) -> list[str]:
    dimensions = _names(raw)
    for name in dimensions:
        if name not in SC_DIMENSIONS:
            raise ReadRefusal(
                "unknown_dimension",
                "--dimensions accepts only: " + ", ".join(SC_DIMENSIONS) + ".",
            )
    if len(set(dimensions)) != len(dimensions):
        raise ReadRefusal("unknown_dimension", "--dimensions lists a dimension twice.")
    return dimensions


def sc_filters(raw: list[str]) -> list[dict[str, str]]:
    filters: list[dict[str, str]] = []
    for item in raw:
        parts = item.split(":", 2)
        if (
            len(parts) != 3
            or parts[0] not in SC_FILTER_DIMENSIONS
            or parts[1] not in SC_FILTER_OPERATORS
            or not parts[2]
            or len(parts[2]) > SC_FILTER_EXPRESSION_MAX
        ):
            raise ReadRefusal(
                "filter_format",
                "--filter must be dimension:operator:expression, with dimension one of "
                + ", ".join(SC_FILTER_DIMENSIONS)
                + " and operator one of "
                + ", ".join(SC_FILTER_OPERATORS)
                + f" (expression 1-{SC_FILTER_EXPRESSION_MAX} characters).",
            )
        filters.append({"dimension": parts[0], "operator": parts[1], "expression": parts[2]})
    return filters


def _sc_type(value: str) -> str:
    if value not in SC_TYPES:
        raise ReadRefusal("unknown_type", "--type accepts only: " + ", ".join(SC_TYPES) + ".")
    return value


def _sc_rows(row_limit: int, start_row: int) -> None:
    if not 1 <= row_limit <= SC_ROW_LIMIT_MAX:
        raise ReadRefusal("row_limit_range", f"--row-limit must be 1-{SC_ROW_LIMIT_MAX:,}.")
    if start_row < 0:
        raise ReadRefusal("row_limit_range", "--start-row must be 0 or more.")


def ga4_names(raw: list[str], flag: str) -> list[str]:
    names = _names(raw)
    for name in names:
        if not _GA4_NAME_RE.fullmatch(name):
            raise ReadRefusal(
                "name_format",
                f"{flag} names must start with a letter and use only letters, digits, _ and :.",
            )
    if len(set(names)) != len(names):
        raise ReadRefusal("name_format", f"{flag} lists a name twice.")
    return names


def ga4_order_by(value: str, metrics: list[str], dimensions: list[str]) -> dict[str, Any] | None:
    if not value:
        return None
    name, _, direction = value.partition(":")
    if direction not in {"", "desc", "asc"} or not _GA4_NAME_RE.fullmatch(name):
        raise ReadRefusal("name_format", "--order-by must be NAME or NAME:desc (or NAME:asc).")
    desc = direction == "desc"
    if name in metrics:
        return {"metric": {"metricName": name}, "desc": desc}
    if name in dimensions:
        return {"dimension": {"dimensionName": name}, "desc": desc}
    raise ReadRefusal(
        "order_by_unknown", "--order-by must name one of the requested metrics or dimensions."
    )


def _ga4_rows(limit: int, offset: int) -> None:
    if not 1 <= limit <= GA4_LIMIT_MAX:
        raise ReadRefusal("limit_range", f"--limit must be 1-{GA4_LIMIT_MAX:,}.")
    if offset < 0:
        raise ReadRefusal("limit_range", "--offset must be 0 or more.")


def _sitemap_index(value: str) -> str:
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or len(value) > SITEMAP_INDEX_MAX
        or _CONTROL_RE.search(value)
        or " " in value
    ):
        raise ReadRefusal(
            "sitemap_index_format",
            "--sitemap-index must be an http(s) URL of a sitemap index, such as "
            "https://www.example.com/sitemap_index.xml.",
        )
    return value


# --- Request bodies (pure; checked against Google's docs in the tests) -------


def sc_query_request(
    site: str,
    *,
    start: str,
    end: str,
    dimensions: list[str],
    search_type: str,
    filters: list[dict[str, str]],
    row_limit: int,
    start_row: int,
    fresh: bool,
) -> tuple[str, dict[str, Any]]:
    url = SC_QUERY_URL.format(site=urllib.parse.quote(site, safe=""))
    body: dict[str, Any] = {
        "startDate": start,
        "endDate": end,
        "type": search_type,
        "rowLimit": row_limit,
        "startRow": start_row,
        "dataState": "all" if fresh else "final",
    }
    if dimensions:
        body["dimensions"] = dimensions
    if filters:
        body["dimensionFilterGroups"] = [{"groupType": "and", "filters": filters}]
    return url, body


def sc_sitemaps_url(site: str, sitemap_index: str = "") -> str:
    url = SC_SITEMAPS_URL.format(site=urllib.parse.quote(site, safe=""))
    if sitemap_index:
        url += "?" + urllib.parse.urlencode({"sitemapIndex": sitemap_index})
    return url


def ga4_report_request(
    property_id: str,
    *,
    start: str,
    end: str,
    metrics: list[str],
    dimensions: list[str],
    limit: int,
    offset: int,
    order_by: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    url = GA4_RUN_REPORT_URL.format(property=property_id)
    body: dict[str, Any] = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "metrics": [{"name": name} for name in metrics],
        "limit": str(limit),
        "offset": str(offset),
        "returnPropertyQuota": True,
    }
    if dimensions:
        body["dimensions"] = [{"name": name} for name in dimensions]
    if order_by:
        body["orderBys"] = [order_by]
    return url, body


# --- Connection: recorded facts only, token minted in-process ------------------


class ReadFailure(RuntimeError):
    """A credential or provider failure: exit 1 with a stable ``rule``."""

    def __init__(
        self,
        rule: str,
        message: str,
        *,
        state: str = "",
        repair_command: str = "",
        quota: str = "",
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.rule = rule
        self.state = state or rule
        self.repair_command = repair_command
        self.quota = quota
        self.http_status = http_status


def _entry(target: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        config = connect_mod._read_config(target)
        repo_id = str(config.get("repo_id") or connect_mod._repo_identity(target)["repo_id"])
    except ValueError as exc:
        raise ReadRefusal(
            "connect_config_refused",
            "the repo's .mb/connect.yaml could not be used; run `mb connect status google` "
            "for the reason.",
        ) from exc
    entry = config["providers"].get(gc.PROVIDER_ID)
    if isinstance(entry, dict):
        return entry, "repo"
    return connect_mod._user_scope_provider_entry(repo_id, gc.PROVIDER_ID), "user"


def _granted(metadata: dict[str, Any]) -> set[str]:
    raw = str(metadata.get(gc.METADATA_GRANTS) or "")
    return {label.strip() for label in raw.split(",") if label.strip()}


def _recorded(metadata: dict[str, Any], key: str, normalize: Callable[[str], str]) -> str:
    value = str(metadata.get(key) or "").strip()
    if not value:
        return ""
    try:
        return normalize(value)
    except connect_mod.ConnectRefusal:
        return ""


def connect(product: str, repo: str | Path) -> _Connection:
    """Check the recorded facts for ``product``, then mint a token in memory."""

    target = Path(repo).resolve()
    entry, source = _entry(target)
    if not isinstance(entry, dict) or not connect_mod._entry_records_slot(entry, gc.GRANT_SLOT):
        raise ReadFailure(
            "not_connected",
            "this repo has no Google sign-in (mb connect google --oauth); a person signs in "
            "once in a terminal.",
            repair_command="mb connect google --oauth --client-file <Desktop client JSON>",
        )
    raw_metadata = entry.get("metadata")
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
    name = PRODUCT_NAMES[product]
    if product not in _granted(metadata):
        raise ReadFailure(
            "grant_missing",
            f"{name} was not granted at sign-in, so it cannot be read.",
            repair_command=gc.REAUTH_COMMAND,
        )
    site = property_id = ""
    if product == SEARCH_CONSOLE:
        site = _recorded(metadata, gc.METADATA_SITE, gc.normalize_search_console_site)
        if not site:
            raise ReadRefusal(
                "site_not_recorded",
                "no search_console_site is recorded for this repo's Google sign-in.",
                repair_command="mb connect google --metadata search_console_site=<site>",
            )
    else:
        property_id = _recorded(metadata, gc.METADATA_PROPERTY, gc.normalize_ga4_property_id)
        if not property_id:
            raise ReadRefusal(
                "property_not_recorded",
                "no ga4_property_id is recorded for this repo's Google sign-in.",
                repair_command="mb connect google --metadata ga4_property_id=<property-id>",
            )
    minted = gc.read_minted_token(entry, source=source, target=target)
    if not minted.get("ok"):
        state = str(minted.get("state") or go.STATE_UNVALIDATED)
        rule = str(minted.get("rule") or minted.get("backend_state") or state)
        error = str(minted.get("error") or "the Google sign-in could not be read")
        raise ReadFailure(
            gc.STATE_REAUTH_REQUIRED if state == gc.STATE_REAUTH_REQUIRED else rule,
            error + ".",
            state=state,
            repair_command=str(minted.get("repair_command") or ""),
        )
    bearer = _Bearer(str(minted["token"]))
    minted.clear()
    return _Connection(
        product=product, target=target, site=site, property_id=property_id, bearer=bearer
    )


# --- Calling Google ------------------------------------------------------------


def _reasons(payload: Any) -> set[str]:
    """Error reasons in a JSON error body, for allowlist matching only."""

    found: set[str] = set()
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return found
    if isinstance(error.get("status"), str):
        found.add(error["status"])
    for list_key in ("errors", "details"):
        items = error.get(list_key)
        if isinstance(items, list):
            for item in items[:16]:
                if isinstance(item, dict) and isinstance(item.get("reason"), str):
                    found.add(item["reason"])
    return found


def _failure(product: str, status: int, payload: Any) -> ReadFailure:
    prefix = "search_console" if product == SEARCH_CONSOLE else "ga4"
    name = PRODUCT_NAMES[product]
    if 300 <= status < 400:
        # The shared sender never follows a redirect, so the bearer token
        # never reaches a second URL. Not recorded: it says nothing about
        # the sign-in.
        return ReadFailure(
            f"{prefix}_unexpected_redirect",
            f"{name} answered with a redirect, which is never followed; try again later.",
            http_status=status,
        )
    reasons = _reasons(payload)
    quota = next((reason for reason in QUOTA_REASONS if reason in reasons), "")
    if status == 429 or quota:
        return ReadFailure(
            "quota_exhausted",
            f"{name} answered with a quota or rate limit"
            + (f" ({quota})" if quota else "")
            + "; wait, then run the read again with a smaller range or fewer rows.",
            quota=quota,
            http_status=status,
        )
    if status >= 500:
        return ReadFailure(
            f"{prefix}_server_error",
            f"{name} answered with a server error ({status}); it was not retried. Try again later.",
            http_status=status,
        )
    if status == 401:
        return ReadFailure(
            f"{prefix}_auth_rejected",
            f"{name} rejected the access token minted from the sign-in.",
            repair_command=gc.REAUTH_COMMAND,
            http_status=status,
        )
    if status == 403 and reasons & _API_DISABLED_REASONS:
        api = (
            "Google Search Console API"
            if product == SEARCH_CONSOLE
            else "Google Analytics Data API"
        )
        return ReadFailure(
            f"{prefix}_api_disabled",
            f"the {api} is not enabled in the Google Cloud project that owns the OAuth client; "
            "enable it there (APIs & Services > Library).",
            repair_command="mb connect test google",
            http_status=status,
        )
    if status in {403, 404}:
        return ReadFailure(
            f"{prefix}_no_access",
            f"{name} refused the recorded "
            + ("site" if product == SEARCH_CONSOLE else "property")
            + ": the signed-in Google account cannot read it, or it does not exist.",
            repair_command="mb connect test google",
            http_status=status,
        )
    return ReadFailure(
        f"{prefix}_request_rejected",
        f"{name} refused the request ({status}); check the dates, names and filters.",
        http_status=status,
    )


def _call(conn: _Connection, method: str, url: str, body: dict[str, Any] | None) -> dict[str, Any]:
    """One request (retried once only if it never reached Google). Returns the JSON body."""

    prefix = "search_console" if conn.product == SEARCH_CONSOLE else "ga4"
    name = PRODUCT_NAMES[conn.product]
    send = api_sender if api_sender is not None else _default_sender
    assert conn.bearer is not None
    headers = {"Authorization": f"Bearer {conn.bearer.token}", "Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    answer: tuple[int, bytes] | None = None
    for _attempt in range(2):
        try:
            answer = send(method, url, data, headers, REQUEST_TIMEOUT_SECONDS)
            break
        except (OSError, ValueError, http.client.HTTPException):
            continue
    if answer is None:
        raise ReadFailure(
            f"{prefix}_unreachable",
            f"{name} could not be reached (tried twice); try again later.",
        )
    status, raw = int(answer[0]), answer[1]
    payload: Any = None
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, ValueError, RecursionError):
        payload = None
    if 200 <= status < 300:
        if isinstance(payload, dict):
            return payload
        if not raw and conn.product == SEARCH_CONSOLE:
            return {}
        raise ReadFailure(
            f"{prefix}_response_malformed",
            f"{name} returned an unreadable answer; try again later.",
            http_status=status,
        )
    raise _failure(conn.product, status, payload)


# --- Shaping answers -----------------------------------------------------------


def _number(value: Any) -> Any:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def shape_sc_query(
    payload: dict[str, Any], *, site: str, request: dict[str, Any]
) -> dict[str, Any]:
    rows_in = payload.get("rows")
    rows: list[dict[str, Any]] = []
    for row in rows_in if isinstance(rows_in, list) else []:
        if not isinstance(row, dict):
            continue
        keys = row.get("keys")
        rows.append(
            {
                "keys": [str(key) for key in keys] if isinstance(keys, list) else [],
                "clicks": _number(row.get("clicks")),
                "impressions": _number(row.get("impressions")),
                "ctr": _number(row.get("ctr")),
                "position": _number(row.get("position")),
            }
        )
    row_limit = int(request["rowLimit"])
    start_row = int(request["startRow"])
    may_have_more = len(rows) >= row_limit
    result: dict[str, Any] = {
        "ok": True,
        "site": site,
        "range": {
            "start": request["startDate"],
            "end": request["endDate"],
            "timezone": SC_TIMEZONE,
        },
        "type": request["type"],
        "dimensions": list(request.get("dimensions") or []),
        "filters": list((request.get("dimensionFilterGroups") or [{}])[0].get("filters") or []),
        "row_limit": row_limit,
        "start_row": start_row,
        "row_count": len(rows),
        "may_have_more": may_have_more,
        "next_start_row": start_row + len(rows) if may_have_more else None,
        "rows": rows,
        "response_aggregation_type": _cut(str(payload.get("responseAggregationType") or "")),
        "data_state": request["dataState"],
        "safe_to_share": False,
    }
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        result["metadata"] = {
            key: _cut(str(metadata[key]))
            for key in ("first_incomplete_date", "first_incomplete_hour")
            if isinstance(metadata.get(key), str)
        }
    return result


def _sitemap(item: dict[str, Any]) -> dict[str, Any]:
    shaped: dict[str, Any] = {}
    for key in ("path", "lastSubmitted", "lastDownloaded", "type"):
        if isinstance(item.get(key), str):
            shaped[key] = _cut(item[key])
    for key in ("isPending", "isSitemapsIndex"):
        if isinstance(item.get(key), bool):
            shaped[key] = item[key]
    for key in ("warnings", "errors"):
        # `long` fields arrive as JSON strings or numbers.
        value = item.get(key)
        if isinstance(value, str) and value.isdigit():
            shaped[key] = int(value)
        elif _number(value) is not None:
            shaped[key] = value
    contents = item.get("contents")
    if isinstance(contents, list):
        shaped["contents"] = []
        for content in contents[:32]:
            if not isinstance(content, dict):
                continue
            entry: dict[str, Any] = {}
            if isinstance(content.get("type"), str):
                entry["type"] = _cut(content["type"])
            submitted = content.get("submitted")
            if isinstance(submitted, str) and submitted.isdigit():
                entry["submitted"] = int(submitted)
            elif _number(submitted) is not None:
                entry["submitted"] = submitted
            shaped["contents"].append(entry)
    return shaped


def shape_sc_sitemaps(payload: dict[str, Any], *, site: str, sitemap_index: str) -> dict[str, Any]:
    items = payload.get("sitemap")
    sitemaps = (
        [_sitemap(item) for item in items if isinstance(item, dict)]
        if isinstance(items, list)
        else []
    )
    result: dict[str, Any] = {
        "ok": True,
        "site": site,
        "sitemap_count": len(sitemaps),
        "sitemaps": sitemaps,
        "safe_to_share": False,
    }
    if sitemap_index:
        result["sitemap_index"] = sitemap_index
    return result


def _quota_status(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    shaped = {
        key: value[key]
        for key in ("consumed", "remaining")
        if isinstance(value.get(key), int) and not isinstance(value.get(key), bool)
    }
    return shaped or None


GA4_QUOTA_KEYS = (
    "tokensPerDay",
    "tokensPerHour",
    "concurrentRequests",
    "serverErrorsPerProjectPerHour",
    "potentiallyThresholdedRequestsPerHour",
    "tokensPerProjectPerHour",
)


def shape_ga4_report(
    payload: dict[str, Any], *, property_id: str, request: dict[str, Any]
) -> dict[str, Any]:
    dimensions = [item["name"] for item in request.get("dimensions") or []]
    metrics = [item["name"] for item in request["metrics"]]
    rows: list[dict[str, Any]] = []
    rows_in = payload.get("rows")
    for row in rows_in if isinstance(rows_in, list) else []:
        if not isinstance(row, dict):
            continue
        dim_values = row.get("dimensionValues")
        met_values = row.get("metricValues")
        dim_list = dim_values if isinstance(dim_values, list) else []
        met_list = met_values if isinstance(met_values, list) else []
        rows.append(
            {
                "dimensions": {
                    name: _value(dim_list, index) for index, name in enumerate(dimensions)
                },
                "metrics": {name: _value(met_list, index) for index, name in enumerate(metrics)},
            }
        )
    limit = int(request["limit"])
    offset = int(request["offset"])
    total = payload.get("rowCount")
    total_rows = total if isinstance(total, int) and not isinstance(total, bool) else None
    may_have_more = len(rows) >= limit if total_rows is None else offset + len(rows) < total_rows
    result: dict[str, Any] = {
        "ok": True,
        "property_id": property_id,
        "range": {
            "start": request["dateRanges"][0]["startDate"],
            "end": request["dateRanges"][0]["endDate"],
        },
        "dimensions": dimensions,
        "metrics": metrics,
        "limit": limit,
        "offset": offset,
        "row_count": len(rows),
        "total_row_count": total_rows,
        "may_have_more": may_have_more,
        "next_offset": offset + len(rows) if may_have_more else None,
        "rows": rows,
        "safe_to_share": False,
    }
    if request.get("orderBys"):
        result["order_by"] = request["orderBys"][0]
    quota = payload.get("propertyQuota")
    if isinstance(quota, dict):
        shaped_quota = {
            key: status
            for key in GA4_QUOTA_KEYS
            if (status := _quota_status(quota.get(key))) is not None
        }
        result["property_quota"] = shaped_quota
    return result


def _value(values: list[Any], index: int) -> str | None:
    if index >= len(values) or not isinstance(values[index], dict):
        return None
    value = values[index].get("value")
    return value if isinstance(value, str) else None


# --- Commands ------------------------------------------------------------------


def failure_result(exc: ReadRefusal | ReadFailure) -> tuple[dict[str, Any], int]:
    """The not-ok result and exit code. All text is fixed; nothing from Google."""

    extra: dict[str, Any] = {}
    if isinstance(exc, ReadRefusal):
        state, code = "refused", 2
    else:
        state, code = exc.state, 1
        if exc.quota:
            extra["quota"] = exc.quota
        if exc.http_status is not None:
            extra["http_status"] = exc.http_status
    summary = str(exc)
    summary = summary[:1].upper() + summary[1:]
    payload: dict[str, Any] = {
        "ok": False,
        "state": state,
        "rule": exc.rule,
        "summary": summary,
        "repair_command": exc.repair_command,
        "exit_code": code,
        **extra,
        "errors": [{"code": exc.rule, "message": summary}],
        "safe_to_share": True,
    }
    if exc.repair_command:
        payload["actions"] = [{"command": exc.repair_command}]
    return payload, code


def sc_query(
    repo: str | Path,
    *,
    start: str,
    end: str,
    dimensions: list[str],
    search_type: str = "web",
    filters: list[str],
    row_limit: int = SC_ROW_LIMIT_DEFAULT,
    start_row: int = 0,
    fresh: bool = False,
) -> tuple[dict[str, Any], int]:
    try:
        first, last = _range(start, end)
        dims = sc_dimensions(dimensions)
        kind = _sc_type(search_type)
        parsed_filters = sc_filters(filters)
        _sc_rows(row_limit, start_row)
        conn = connect(SEARCH_CONSOLE, repo)
        url, body = sc_query_request(
            conn.site,
            start=first,
            end=last,
            dimensions=dims,
            search_type=kind,
            filters=parsed_filters,
            row_limit=row_limit,
            start_row=start_row,
            fresh=fresh,
        )
        payload = _call(conn, "POST", url, body)
    except (ReadRefusal, ReadFailure) as exc:
        return failure_result(exc)
    return shape_sc_query(payload, site=conn.site, request=body), 0


def sc_sitemaps_list(repo: str | Path, *, sitemap_index: str = "") -> tuple[dict[str, Any], int]:
    try:
        index = _sitemap_index(sitemap_index)
        conn = connect(SEARCH_CONSOLE, repo)
        payload = _call(conn, "GET", sc_sitemaps_url(conn.site, index), None)
    except (ReadRefusal, ReadFailure) as exc:
        return failure_result(exc)
    return shape_sc_sitemaps(payload, site=conn.site, sitemap_index=index), 0


def ga4_report(
    repo: str | Path,
    *,
    start: str,
    end: str,
    metrics: list[str],
    dimensions: list[str],
    limit: int = GA4_LIMIT_DEFAULT,
    offset: int = 0,
    order_by: str = "",
) -> tuple[dict[str, Any], int]:
    try:
        first, last = _range(start, end)
        metric_names = ga4_names(metrics, "--metrics")
        if not metric_names:
            raise ReadRefusal("name_format", "--metrics needs at least one metric name.")
        dimension_names = ga4_names(dimensions, "--dimensions")
        order = ga4_order_by(order_by, metric_names, dimension_names)
        _ga4_rows(limit, offset)
        conn = connect(GA4, repo)
        url, body = ga4_report_request(
            conn.property_id,
            start=first,
            end=last,
            metrics=metric_names,
            dimensions=dimension_names,
            limit=limit,
            offset=offset,
            order_by=order,
        )
        payload = _call(conn, "POST", url, body)
    except (ReadRefusal, ReadFailure) as exc:
        return failure_result(exc)
    return shape_ga4_report(payload, property_id=conn.property_id, request=body), 0


# --- Human output --------------------------------------------------------------


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    cells = [[terminal_safe(cell) if cell is not None else "" for cell in row] for row in rows]
    heads = [terminal_safe(head) for head in headers]
    widths = [
        max([len(head)] + [len(row[index]) for row in cells]) for index, head in enumerate(heads)
    ]
    lines = ["  ".join(head.ljust(widths[i]) for i, head in enumerate(heads)).rstrip()]
    for row in cells:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return lines


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.{digits}f}"
    return str(int(value)) if isinstance(value, float) else str(value)


def render_failure(command: str, result: dict[str, Any], echo: Callable[[str], None]) -> None:
    echo(f"{command}: {result['summary']} ({result['rule']})")
    if result.get("repair_command"):
        echo(f"next: {result['repair_command']}")


def render_sc_query(result: dict[str, Any]) -> list[str]:
    span = result["range"]
    lines = [
        f"Search Console: {terminal_safe(result['site'], STRING_MAX)}",
        f"range: {span['start']} to {span['end']} ({span['timezone']}), type {result['type']}, "
        f"data {result['data_state']}",
        f"rows: {result['row_count']} "
        f"(from row {result['start_row']}, limit {result['row_limit']})",
    ]
    if result["rows"]:
        headers = [*(result["dimensions"] or ["total"]), "clicks", "impressions", "ctr", "position"]
        body = [
            [
                *(row["keys"] or ["all"]),
                _fmt(row["clicks"]),
                _fmt(row["impressions"]),
                _fmt(row["ctr"], 4),
                _fmt(row["position"], 1),
            ]
            for row in result["rows"]
        ]
        lines += _table(headers, body)
    if result["may_have_more"]:
        lines.append(f"more rows may follow: --start-row {result['next_start_row']}")
    return lines


def render_sc_sitemaps(result: dict[str, Any]) -> list[str]:
    lines = [
        f"Search Console: {terminal_safe(result['site'], STRING_MAX)}",
        f"sitemaps: {result['sitemap_count']}",
    ]
    if result["sitemaps"]:
        headers = ["path", "type", "submitted", "downloaded", "pending", "warnings", "errors"]
        body = [
            [
                item.get("path"),
                item.get("type"),
                item.get("lastSubmitted"),
                item.get("lastDownloaded"),
                "yes" if item.get("isPending") else "no",
                item.get("warnings"),
                item.get("errors"),
            ]
            for item in result["sitemaps"]
        ]
        lines += _table(headers, body)
    return lines


def render_ga4_report(result: dict[str, Any]) -> list[str]:
    span = result["range"]
    total = result["total_row_count"]
    lines = [
        f"GA4 property: {result['property_id']}",
        f"range: {span['start']} to {span['end']} (the property's reporting time zone)",
        f"rows: {result['row_count']}"
        + (f" of {total}" if total is not None else "")
        + f" (from row {result['offset']}, limit {result['limit']})",
    ]
    if result["rows"]:
        headers = [*result["dimensions"], *result["metrics"]]
        body = [
            [
                *(row["dimensions"].get(name) for name in result["dimensions"]),
                *(row["metrics"].get(name) for name in result["metrics"]),
            ]
            for row in result["rows"]
        ]
        lines += _table(headers, body)
    if result["may_have_more"]:
        lines.append(f"more rows may follow: --offset {result['next_offset']}")
    quota = result.get("property_quota") or {}
    per_day, per_hour = quota.get("tokensPerDay"), quota.get("tokensPerHour")
    if per_day or per_hour:
        parts = []
        if per_day:
            parts.append(f"{per_day.get('remaining', '?')} tokens left today")
        if per_hour:
            parts.append(f"{per_hour.get('remaining', '?')} this hour")
        consumed = (per_hour or per_day or {}).get("consumed")
        if consumed is not None:
            parts.append(f"this read used {consumed}")
        lines.append("quota: " + ", ".join(parts))
    return lines
