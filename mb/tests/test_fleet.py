"""``mb fleet`` read-only fleet status (#984).

Every GitHub and Cloudflare response here is synthetic. No test touches the
network: ``gh`` and the Pages API are replaced by in-memory fakes.
"""

from __future__ import annotations

import json
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import fleet
from mb.cli import app

runner = CliRunner()
# fleet.toml is read with the standard library's tomllib (Python 3.11+).
needs_tomllib = pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib is 3.11+")
NOW = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
MAIN_SITES = "a" * 40
MAIN_WORKSHOP = "b" * 40
MAIN_APP = "c" * 40
OLD_WORKSHOP = "d" * 40
TOKEN = "synthetic-token-value-never-stored"

REGISTRY = textwrap.dedent(
    """\
    ---
    type: repo_topology
    status: active
    schema: mb.repo_topology.v0
    home: github:example-co/example
    business_display_name: Example Business
    repos:
      - slug: example
        role: business
        lifecycle: active
        remote: github:example-co/example
      - slug: acme-sites
        role: site
        lifecycle: active
        parent: example
        remote: github:example-co/acme-sites
      - slug: workshop-site
        role: site
        lifecycle: active
        parent: example
        domain: workshop.example.com
        remote: github:example-co/workshop-site
      - slug: app
        role: product
        lifecycle: active
        parent: example
        remote: github:example-co/app
      - slug: books
        role: finance
        lifecycle: proposed
        parent: example
        remote: github:example-co/books
      - slug: old-site
        role: site
        lifecycle: archived
        parent: example
        remote: github:example-co/old-site
    ---
    """
)

SITES_DESCRIPTOR = {
    "schema": "mb.child_repo.v0",
    "role": "site",
    "github_owner": "example-co",
    "repo_name": "acme-sites",
    "sites": [
        {
            "slug": "alpha",
            "display_name": "Alpha",
            "dir": "clients/alpha",
            "domains": ["alpha.example"],
            "deploy": {"provider": "cloudflare-pages", "project": "alpha-site"},
            "lifecycle": "active",
        },
        {
            "slug": "beta",
            "display_name": "Beta",
            "dir": "clients/beta",
            "deploy": {"provider": "cloudflare-pages", "project": "beta-site"},
        },
    ],
}


def _package(deps: dict[str, str]) -> str:
    return json.dumps({"name": "x", "dependencies": deps})


def _repo(branch: str = "main") -> dict[str, Any]:
    return {"default_branch": branch, "archived": False}


def _branch(sha: str, date: str) -> dict[str, Any]:
    return {"commit": {"sha": sha, "commit": {"committer": {"date": date}}}}


def _runs(*runs: tuple[str, str, str]) -> dict[str, Any]:
    return {
        "check_runs": [
            {"name": name, "status": status, "conclusion": conclusion}
            for name, status, conclusion in runs
        ]
    }


GH: dict[str, tuple[int, Any]] = {
    "repos/example-co/example/contents/core/operations/repo-topology.md": (200, REGISTRY),
    # hub
    "repos/example-co/example": (200, _repo()),
    "repos/example-co/example/branches/main": (200, _branch("e" * 40, "2026-06-14T12:00:00Z")),
    f"repos/example-co/example/commits/{'e' * 40}/check-runs?per_page=100": (200, _runs()),
    "repos/example-co/example/dependabot/alerts?state=open&per_page=100": (200, []),
    "repos/example-co/example/pulls?state=open&per_page=100": (200, []),
    # multi-site repo: alpha has its own package.json, beta falls back to root
    "repos/example-co/acme-sites": (200, _repo()),
    "repos/example-co/acme-sites/branches/main": (200, _branch(MAIN_SITES, "2026-06-05T12:00:00Z")),
    f"repos/example-co/acme-sites/commits/{MAIN_SITES}/check-runs?per_page=100": (
        200,
        _runs(("build", "completed", "success"), ("lint", "completed", "failure")),
    ),
    "repos/example-co/acme-sites/contents/.mainbranch/repo.json": (
        200,
        json.dumps(SITES_DESCRIPTOR),
    ),
    "repos/example-co/acme-sites/contents/package.json": (
        200,
        _package({"astro": "^4.16.18", "@acme/engine": "github:example-co/engine#v1.2.0"}),
    ),
    "repos/example-co/acme-sites/contents/clients/alpha/package.json": (
        200,
        _package({"astro": "^5.1.0", "@acme/engine": "github:example-co/engine#v1.3.0"}),
    ),
    "repos/example-co/acme-sites/dependabot/alerts?state=open&per_page=100": (
        200,
        [
            {"security_vulnerability": {"severity": "high"}},
            {"security_vulnerability": {"severity": "high"}},
            {"security_advisory": {"severity": "critical"}},
            {"security_vulnerability": {"severity": "low"}},
        ],
    ),
    "repos/example-co/acme-sites/pulls?state=open&per_page=100": (
        200,
        [
            {"user": {"login": "dependabot[bot]"}, "created_at": "2026-06-01T12:00:00Z"},
            {"user": {"login": "dependabot[bot]"}, "created_at": "2026-06-10T12:00:00Z"},
            {"user": {"login": "someone"}, "created_at": "2026-05-01T12:00:00Z"},
        ],
    ),
    "repos/example-co/engine/tags?per_page=100": (
        200,
        [{"name": "v1.3.0"}, {"name": "v1.2.0"}, {"name": "v1.10.0-rc"}, {"name": "nightly"}],
    ),
    # single-site repo, no descriptor; deploy found by project name, behind main
    "repos/example-co/workshop-site": (200, _repo()),
    "repos/example-co/workshop-site/branches/main": (
        200,
        _branch(MAIN_WORKSHOP, "2026-06-15T06:00:00Z"),
    ),
    f"repos/example-co/workshop-site/commits/{MAIN_WORKSHOP}/check-runs?per_page=100": (
        200,
        _runs(("build", "in_progress", "")),
    ),
    "repos/example-co/workshop-site/contents/package.json": (
        200,
        _package({"next": "14.2.3", "@acme/engine": "file:../engine"}),
    ),
    f"repos/example-co/workshop-site/compare/{OLD_WORKSHOP}...{MAIN_WORKSHOP}": (
        200,
        {"status": "ahead", "ahead_by": 3, "behind_by": 0},
    ),
    # Dependabot alerts need a security-alerts scope; 403 must not fail refresh.
    "repos/example-co/workshop-site/dependabot/alerts?state=open&per_page=100": (403, None),
    "repos/example-co/workshop-site/pulls?state=open&per_page=100": (200, []),
    # product repo, no package.json, alerts endpoint 404 (disabled)
    "repos/example-co/app": (200, _repo("trunk")),
    "repos/example-co/app/branches/trunk": (200, _branch(MAIN_APP, "2026-05-16T12:00:00Z")),
    f"repos/example-co/app/commits/{MAIN_APP}/check-runs?per_page=100": (
        200,
        _runs(("test", "completed", "success")),
    ),
    "repos/example-co/app/dependabot/alerts?state=open&per_page=100": (404, None),
    "repos/example-co/app/pulls?state=open&per_page=100": (200, []),
}

PAGES = {
    "success": True,
    "result_info": {"page": 1, "total_pages": 1},
    "result": [
        {
            "name": "alpha-site",
            "domains": ["alpha.example"],
            "production_branch": "main",
            "canonical_deployment": {
                "short_id": "abc123",
                "created_on": "2026-06-14T10:00:00Z",
                "env_vars": {"SECRET_THING": {"value": "must-not-be-cached"}},
                "deployment_trigger": {
                    "type": "ad_hoc",
                    "metadata": {
                        "branch": "main",
                        "commit_hash": MAIN_SITES,
                        "commit_dirty": True,
                        "commit_message": "deploy",
                    },
                },
            },
        },
        {"name": "beta-site", "domains": [], "canonical_deployment": None},
        {
            "name": "workshop-site",
            "domains": ["workshop.example.com"],
            "canonical_deployment": {
                "short_id": "def456",
                "created_on": "2026-06-10T10:00:00Z",
                "deployment_trigger": {
                    "type": "ad_hoc",
                    "metadata": {
                        "branch": "main",
                        "commit_hash": OLD_WORKSHOP,
                        "commit_dirty": False,
                    },
                },
            },
        },
    ],
}


class Pages(list[tuple[int, Any]]):
    """Several pages of one paginated endpoint: (status, body) per page."""


class FakeGh:
    def __init__(self, responses: dict[str, tuple[int, Any]]) -> None:
        self.responses = responses
        self.seen: list[list[str]] = []

    def __call__(self, args: list[str]) -> tuple[int, str, str]:
        self.seen.append(args)
        assert args[:3] == ["api", "--method", "GET"], "fleet must only GET"
        path = args[-1]
        status, body = self.responses.get(path, (404, None))
        if isinstance(body, Pages):
            # gh api --paginate fails as a whole when any page fails.
            failed = [page_status for page_status, _ in body if page_status != 200]
            if failed:
                return 1, "", f"gh: Server Error (HTTP {failed[0]})"
            pages = [page for _, page in body]
            return 0, json.dumps(pages if "--slurp" in args else pages[0]), ""
        if status != 200:
            return 1, "", f"gh: Not Found (HTTP {status})"
        if "--slurp" in args:
            body = [body]
        text = body if isinstance(body, str) else json.dumps(body)
        return 0, text, ""


def _write_config(tmp_path: Path, *, cloudflare: bool = True) -> Path:
    checkout = tmp_path / "checkouts" / "example"
    checkout.mkdir(parents=True)
    path = tmp_path / "config" / "mainbranch" / "fleet.toml"
    path.parent.mkdir(parents=True)
    lines = [
        "[[hubs]]",
        'name = "example-co"',
        'remote = "github:example-co/example"',
        f'checkout = "{checkout}"',
    ]
    if cloudflare:
        lines.append('cloudflare = "cloudflare-read"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def cloudflare_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        fleet, "_cloudflare_credentials", lambda connection, checkout: (TOKEN, "acct-1", "")
    )


def _refresh(
    tmp_path: Path,
    gh: FakeGh | None = None,
    pages: list[tuple[int, Any]] | None = None,
) -> tuple[dict[str, Any], Path, FakeGh]:
    fake = gh or FakeGh(GH)
    seen_headers: list[dict[str, str]] = []
    page_responses = list(pages or [(200, PAGES)])

    def http_get(url: str, headers: dict[str, str]) -> tuple[int, Any]:
        seen_headers.append(headers)
        assert url.startswith(f"{fleet.CLOUDFLARE_API}/accounts/acct-1/pages/projects")
        page = int(url.rsplit("page=", 1)[1])
        return page_responses[min(page, len(page_responses)) - 1]

    cache = tmp_path / "state" / "fleet.db"
    result = fleet.refresh(
        config=_write_config(tmp_path),
        cache=cache,
        github=fleet.GitHub(runner=fake),
        cloudflare=fleet.Cloudflare(http_get=http_get),
        now=NOW,
    )
    assert all(h == {"Authorization": f"Bearer {TOKEN}"} for h in seen_headers)
    return result, cache, fake


def _rows(cache: Path) -> dict[str, dict[str, Any]]:
    status = fleet.status(cache=cache, now=NOW)
    return {f"{row['repo']}:{row['site']}": row for row in status["sites"]}


@needs_tomllib
def test_refresh_builds_one_row_per_site(tmp_path: Path, cloudflare_creds: None) -> None:
    result, cache, _ = _refresh(tmp_path)

    assert result["ok"], result["errors"]
    rows = _rows(cache)
    assert sorted(rows) == [
        "example-co/acme-sites:alpha",
        "example-co/acme-sites:beta",
        "example-co/app:",
        "example-co/example:",
        "example-co/workshop-site:",
    ]
    status = fleet.status(cache=cache, now=NOW)
    assert status["hubs"][0]["skipped"] == [
        {"slug": "books", "reason": "proposed, not readable yet"},
        {"slug": "old-site", "reason": "archived"},
    ]
    assert "example-co/books" not in [repo["repo"] for repo in status["repos"]]
    assert status["summary"]["sites"] == 5


@needs_tomllib
def test_multi_site_reads_dir_package_then_repo_root(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    _, cache, _ = _refresh(tmp_path)
    rows = _rows(cache)

    alpha = rows["example-co/acme-sites:alpha"]
    beta = rows["example-co/acme-sites:beta"]
    assert alpha["framework"] == {
        "name": "astro",
        "spec": "^5.1.0",
        "version": "5.1.0",
        "state": "ok",
    }
    assert alpha["engine_pin"]["ref"] == "v1.3.0"
    assert alpha["engine_pin"]["on_latest"] is True
    assert beta["framework"]["version"] == "4.16.18"
    assert beta["engine_pin"]["ref"] == "v1.2.0"
    assert beta["engine_pin"]["latest_tag"] == "v1.3.0"
    assert "engine_behind_latest" in beta["flags"]
    assert alpha["ci"] == {"state": "failure", "total": 2, "failing": ["lint"]}
    assert "ci_failing" in alpha["flags"]
    assert alpha["days_since_commit"] == 10


@needs_tomllib
def test_denied_site_package_is_unavailable_not_root_facts(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    responses = dict(GH)
    responses["repos/example-co/acme-sites/contents/clients/alpha/package.json"] = (403, None)

    result, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert not result["ok"]
    assert any(
        "example-co/acme-sites: clients/alpha/package.json not readable (HTTP 403)" in error
        for error in result["errors"]
    )
    rows = _rows(cache)
    alpha = rows["example-co/acme-sites:alpha"]
    assert alpha["framework"]["state"] == "unavailable"
    assert alpha["framework"]["version"] == ""
    assert alpha["engine_pin"]["state"] == "unavailable"
    assert alpha["engine_pin"]["http_status"] == 403
    assert alpha["package"] == {
        "path": "clients/alpha/package.json",
        "state": "unavailable",
        "http_status": 403,
    }
    assert "facts_unavailable" in alpha["flags"]
    # beta's own package.json is a confirmed 404, so the root is still used.
    beta = rows["example-co/acme-sites:beta"]
    assert beta["framework"]["version"] == "4.16.18"
    assert beta["package"]["path"] == "package.json"


@needs_tomllib
def test_rate_limited_descriptor_reports_unknown_sites(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    responses = dict(GH)
    responses["repos/example-co/acme-sites/contents/.mainbranch/repo.json"] = (429, None)

    result, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert not result["ok"]
    assert any(
        "example-co/acme-sites: .mainbranch/repo.json not readable (HTTP 429)" in error
        for error in result["errors"]
    )
    rows = _rows(cache)
    assert "example-co/acme-sites:alpha" not in rows
    row = rows["example-co/acme-sites:"]
    assert row["sites_state"] == "unavailable"
    assert row["framework"]["state"] == "unavailable"
    assert row["framework"]["version"] == ""
    assert row["engine_pin"]["state"] == "unavailable"
    assert row["deploy"]["state"] == "descriptor_unavailable"
    repo = {r["repo"]: r for r in fleet.status(cache=cache, now=NOW)["repos"]}
    assert repo["example-co/acme-sites"]["descriptor"]["read_state"] == "unavailable"
    assert repo["example-co/acme-sites"]["descriptor"]["http_status"] == 429


@needs_tomllib
def test_malformed_package_and_descriptor_are_errors(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    responses = dict(GH)
    responses["repos/example-co/workshop-site/contents/package.json"] = (200, "{not json")
    responses["repos/example-co/app/contents/.mainbranch/repo.json"] = (200, "[1]")

    result, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert not result["ok"]
    assert any("package.json is not a valid JSON object" in e for e in result["errors"])
    assert any("example-co/app: .mainbranch/repo.json" in e for e in result["errors"])
    rows = _rows(cache)
    assert rows["example-co/workshop-site:"]["framework"]["state"] == "malformed"
    assert rows["example-co/app:"]["sites_state"] == "malformed"


def _check_run_pages(*pages: tuple[int, Any]) -> dict[str, tuple[int, Any]]:
    responses = dict(GH)
    responses[f"repos/example-co/app/commits/{MAIN_APP}/check-runs?per_page=100"] = (
        200,
        Pages(pages),
    )
    return responses


FIRST_RUNS_PAGE = {
    "total_count": 101,
    "check_runs": [
        {"name": f"job-{index}", "status": "completed", "conclusion": "success"}
        for index in range(100)
    ],
}


@needs_tomllib
def test_ci_reads_every_check_run_page(tmp_path: Path, cloudflare_creds: None) -> None:
    second = {
        "total_count": 101,
        "check_runs": [{"name": "deploy", "status": "completed", "conclusion": "failure"}],
    }
    responses = _check_run_pages((200, FIRST_RUNS_PAGE), (200, second))

    _, cache, fake = _refresh(tmp_path, FakeGh(responses))

    ci = _rows(cache)["example-co/app:"]["ci"]
    assert ci == {"state": "failure", "total": 101, "failing": ["deploy"]}
    check_args = [args for args in fake.seen if "check-runs" in args[-1] and "/app/" in args[-1]]
    assert check_args and "--paginate" in check_args[0]


@needs_tomllib
def test_ci_is_unknown_when_a_check_run_page_fails(tmp_path: Path, cloudflare_creds: None) -> None:
    responses = _check_run_pages((200, FIRST_RUNS_PAGE), (502, None))

    result, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert _rows(cache)["example-co/app:"]["ci"]["state"] == "unknown"
    assert not result["ok"]
    assert any(
        "example-co/app: check runs on the default branch not fully readable" in error
        for error in result["errors"]
    )


@needs_tomllib
def test_ci_is_unknown_when_pages_are_missing(tmp_path: Path, cloudflare_creds: None) -> None:
    responses = _check_run_pages((200, FIRST_RUNS_PAGE))

    _, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert _rows(cache)["example-co/app:"]["ci"]["state"] == "unknown"


@needs_tomllib
def test_deploy_facts_dirty_and_behind_main(tmp_path: Path, cloudflare_creds: None) -> None:
    _, cache, _ = _refresh(tmp_path)
    rows = _rows(cache)

    alpha = rows["example-co/acme-sites:alpha"]["deploy"]
    assert alpha["project_source"] == "declared"
    assert alpha["deployed_sha"] == MAIN_SITES
    assert alpha["dirty"] is True
    assert alpha["matches_main"] is True
    assert "deploy_dirty" in rows["example-co/acme-sites:alpha"]["flags"]

    assert rows["example-co/acme-sites:beta"]["deploy"]["state"] == "no_production_deployment"

    workshop = rows["example-co/workshop-site:"]
    assert workshop["deploy"]["project_source"] == "project_name_match"
    assert workshop["deploy"]["dirty"] is False
    assert workshop["deploy"]["compare"] == "ahead"
    assert workshop["deploy"]["behind_by"] == 3
    assert "deploy_behind_main" in workshop["flags"]
    assert workshop["engine_pin"]["kind"] == "path"
    assert "engine_unpinned" in workshop["flags"]
    assert workshop["ci"]["state"] == "pending"

    assert rows["example-co/app:"]["deploy"]["state"] == "undeclared"


@needs_tomllib
def test_dependabot_counts_per_repo_and_unavailable_states(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    result, cache, _ = _refresh(tmp_path)
    repos = {repo["repo"]: repo for repo in fleet.status(cache=cache, now=NOW)["repos"]}

    sites = repos["example-co/acme-sites"]
    assert sites["dependabot_alerts"] == {
        "state": "ok",
        "http_status": 200,
        "open": 4,
        "by_severity": {"critical": 1, "high": 2, "medium": 0, "low": 1},
    }
    assert sites["dependabot_prs"] == {
        "state": "ok",
        "http_status": 200,
        "open": 2,
        "oldest_days": 14,
    }
    assert repos["example-co/workshop-site"]["dependabot_alerts"]["state"] == "unavailable"
    assert repos["example-co/workshop-site"]["dependabot_alerts"]["http_status"] == 403
    assert repos["example-co/app"]["dependabot_alerts"]["http_status"] == 404
    # Unavailable alerts never fail the refresh.
    assert result["ok"]
    assert result["summary"]["dependabot_alerts"]["high"] == 2
    assert result["summary"]["dependabot_alerts_unavailable"] == 2
    assert result["summary"]["dependabot_prs"] == 2
    # Dependabot is per repo, not per site.
    assert "dependabot_alerts" not in _rows(cache)["example-co/acme-sites:alpha"]


@needs_tomllib
def test_cache_never_holds_tokens_or_build_env(tmp_path: Path, cloudflare_creds: None) -> None:
    result, cache, _ = _refresh(tmp_path)

    raw = cache.read_bytes()
    assert TOKEN.encode() not in raw
    assert b"must-not-be-cached" not in raw
    assert b"SECRET_THING" not in raw
    assert TOKEN not in json.dumps(result)


@needs_tomllib
def test_refresh_reads_registry_from_local_checkout_first(
    tmp_path: Path, cloudflare_creds: None
) -> None:
    config = _write_config(tmp_path, cloudflare=False)
    checkout = tmp_path / "checkouts" / "example"
    registry = checkout / "core" / "operations" / "repo-topology.md"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        REGISTRY.split("  - slug: acme-sites")[0] + "---\n",
        encoding="utf-8",
    )
    fake = FakeGh(GH)

    fleet.refresh(
        config=config,
        cache=tmp_path / "fleet.db",
        github=fleet.GitHub(runner=fake),
        cloudflare=fleet.Cloudflare(http_get=lambda url, headers: (500, None)),
        now=NOW,
    )

    paths = [args[-1] for args in fake.seen]
    assert "repos/example-co/example/contents/core/operations/repo-topology.md" not in paths
    rows = _rows(tmp_path / "fleet.db")
    assert list(rows) == ["example-co/example:"]
    assert rows["example-co/example:"]["deploy"]["state"] == "no_connection"


@needs_tomllib
def test_refresh_reports_unreadable_repo_and_cloudflare_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        fleet,
        "_cloudflare_credentials",
        lambda connection, checkout: ("", "", "cloudflare connection 'cloudflare-read': missing"),
    )
    responses = dict(GH)
    responses["repos/example-co/app"] = (404, None)

    result, cache, _ = _refresh(tmp_path, FakeGh(responses))

    assert not result["ok"]
    assert any("example-co/app" in error for error in result["errors"])
    assert any("cloudflare" in error for error in result["errors"])
    rows = _rows(cache)
    assert "example-co/app:" not in rows
    assert rows["example-co/acme-sites:alpha"]["deploy"]["state"] == "provider_error"
    status = fleet.status(cache=cache, now=NOW)
    assert status["ok"]
    assert status["warnings"]


UNSUCCESSFUL = {"success": False, "errors": [{"code": 10000, "message": "x"}], "result": []}


@needs_tomllib
@pytest.mark.parametrize(
    ("pages", "expected"),
    [
        ([(200, UNSUCCESSFUL)], "unsuccessful response, codes 10000 (HTTP 200)"),
        ([(200, {"result": []})], "unsuccessful response (HTTP 200)"),
        ([(200, {"success": True, "result": None})], "malformed response (HTTP 200)"),
        ([(200, ["not", "an", "object"])], "malformed response (HTTP 200)"),
        (
            [(200, {"success": True, "result": [], "result_info": {"total_pages": "x"}})],
            "malformed response (HTTP 200)",
        ),
        # A good first page and a failing second one: nothing is kept.
        (
            [(200, {**PAGES, "result_info": {"page": 1, "total_pages": 2}}), (200, UNSUCCESSFUL)],
            "unsuccessful response, codes 10000 (HTTP 200)",
        ),
    ],
)
def test_unsuccessful_cloudflare_envelope_is_a_provider_error(
    tmp_path: Path, cloudflare_creds: None, pages: list[tuple[int, Any]], expected: str
) -> None:
    result, cache, _ = _refresh(tmp_path, pages=pages)

    assert not result["ok"]
    assert f"example-co: cloudflare pages read failed: {expected}" in result["errors"]
    rows = _rows(cache)
    assert rows["example-co/acme-sites:alpha"]["deploy"]["state"] == "provider_error"
    assert rows["example-co/workshop-site:"]["deploy"]["state"] == "provider_error"
    hub = fleet.status(cache=cache, now=NOW)["hubs"][0]
    assert hub["cloudflare"]["state"] == "error"
    assert "x" not in hub["cloudflare"]["error"].split()


@needs_tomllib
def test_cloudflare_http_error_is_a_provider_error(tmp_path: Path, cloudflare_creds: None) -> None:
    result, cache, _ = _refresh(tmp_path, pages=[(429, None)])

    assert "example-co: cloudflare pages read failed (HTTP 429)" in result["errors"]
    assert _rows(cache)["example-co/acme-sites:alpha"]["deploy"]["state"] == "provider_error"


def test_status_without_cache_asks_for_refresh(tmp_path: Path) -> None:
    result = fleet.status(cache=tmp_path / "missing.db", now=NOW)

    assert not result["ok"]
    assert result["actions"] == ["mb fleet refresh"]


@needs_tomllib
def test_status_reports_snapshot_age(tmp_path: Path, cloudflare_creds: None) -> None:
    _, cache, _ = _refresh(tmp_path)

    later = datetime(2026, 6, 17, 12, 0, tzinfo=timezone.utc)
    result = fleet.status(cache=cache, now=later)

    assert result["refreshed_at"] == "2026-06-15T12:00:00Z"
    assert result["age_seconds"] == 2 * 86400
    assert result["actions"] == ["mb fleet refresh"]


@needs_tomllib
def test_load_config_validation(tmp_path: Path) -> None:
    path = tmp_path / "fleet.toml"
    with pytest.raises(fleet.FleetConfigError, match="no hub list"):
        fleet.load_config(path)
    path.write_text("hubs = [", encoding="utf-8")
    with pytest.raises(fleet.FleetConfigError, match="not valid TOML"):
        fleet.load_config(path)
    path.write_text('[[hubs]]\nremote = "not a remote"\n', encoding="utf-8")
    with pytest.raises(fleet.FleetConfigError, match="owner/repo"):
        fleet.load_config(path)
    path.write_text('[[hubs]]\nremote = "example-co/hub"\ncloudflare = "cf"\n', encoding="utf-8")
    with pytest.raises(fleet.FleetConfigError, match="needs a checkout"):
        fleet.load_config(path)
    path.write_text(
        '[[hubs]]\nremote = "example-co/hub"\ncheckout = "/tmp/a"\n'
        'cloudflare = "cf"\nconnect_checkout = "/tmp/b"\n',
        encoding="utf-8",
    )
    hub = fleet.load_config(path)["hubs"][0]
    assert hub["checkout"] == Path("/tmp/a")
    assert hub["connect_checkout"] == Path("/tmp/b")


def test_config_and_cache_paths_follow_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    assert fleet.config_path() == tmp_path / "cfg" / "mainbranch" / "fleet.toml"
    assert fleet.cache_path() == tmp_path / "state" / "mainbranch" / "fleet.db"


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("github:example-co/engine#v1.2.3", {"kind": "tag", "ref": "v1.2.3"}),
        (
            "git+https://github.com/example-co/engine.git#abc1234",
            {"kind": "commit", "ref": "abc1234"},
        ),
        ("github:example-co/engine#main", {"kind": "branch", "ref": "main"}),
        ("github:example-co/engine", {"kind": "none", "ref": ""}),
        ("file:../engine", {"kind": "path", "ref": "../engine"}),
    ],
)
def test_parse_pin(spec: str, expected: dict[str, str]) -> None:
    pin = fleet.parse_pin(spec)
    assert {"kind": pin["kind"], "ref": pin["ref"]} == expected


@needs_tomllib
def test_cli_status_json_envelope_and_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cloudflare_creds: None
) -> None:
    _, cache, _ = _refresh(tmp_path)
    monkeypatch.setattr(fleet, "cache_path", lambda: cache)

    as_json = runner.invoke(app, ["fleet", "status", "--json"])
    as_text = runner.invoke(app, ["fleet", "status"])

    assert as_json.exit_code == 0
    payload = json.loads(as_json.stdout)
    assert payload["mb_command"] == "mb fleet status"
    assert payload["result_schema"]["name"] == "mainbranch.fleet_status"
    assert payload["result_status"] == "ok"
    assert as_text.exit_code == 0
    assert "alpha" in as_text.stdout
    assert "unavailable (403)" in as_text.stdout
    assert "1/2/0/1" in as_text.stdout


def test_cli_missing_config_exits_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "nothing"))

    result = runner.invoke(app, ["fleet", "refresh", "--json"])
    hubs = runner.invoke(app, ["fleet", "hubs", "list"])

    assert result.exit_code == 2
    assert json.loads(result.stdout)["ok"] is False
    assert hubs.exit_code == 2


@needs_tomllib
def test_cli_hubs_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = _write_config(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config.parent.parent))

    result = runner.invoke(app, ["fleet", "hubs", "list", "--json"])

    payload = json.loads(result.stdout)
    assert result.exit_code == 0
    assert payload["hubs"][0]["remote_full_name"] == "example-co/example"
    assert payload["hubs"][0]["checkout_present"] is True
    assert payload["hubs"][0]["cloudflare"] == "cloudflare-read"


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="Python 3.10 only")
def test_load_config_on_python_310_says_311_is_needed(tmp_path: Path) -> None:
    path = tmp_path / "fleet.toml"
    path.write_text('[[hubs]]\nremote = "example-co/hub"\n', encoding="utf-8")
    with pytest.raises(fleet.FleetConfigError, match="Python 3.11"):
        fleet.load_config(path)
