"""Tests for ``mb.topology`` reader (issue #418)."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from mb import topology


def _write_registry(repo: Path, body: str) -> Path:
    path = repo / "core" / "operations" / "repo-topology.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _valid_registry(extra_repos: str = "") -> str:
    base = textwrap.dedent(
        """\
        ---
        type: repo_topology
        status: active
        schema: mb.repo_topology.v0
        home: github:example-co/example
        business_display_name: Example Business
        repos:
          - slug: example
            display_name: Example Business
            role: business
            lifecycle: active
            github_owner: example-co
            repo_name: example
            remote: github:example-co/example
            visibility: team_private
            relationship: hub_for
            purpose: Hub repo for company strategy and decisions.
          - slug: workshop-site
            display_name: Workshop site
            role: site
            lifecycle: active
            relationship: execution_vehicle_for
            parent: example
            github_owner: example-co
            repo_name: workshop-site
            remote: github:example-co/workshop-site
            visibility: public
            domain: workshop.example.com
            linked_offers:
              - core/offers/workshop/offer.md
            linked_pushes:
              - pushes/2026-05-20-workshop-launch/push.md
            linked_playbook_runs:
              - pushes/2026-05-20-workshop-launch/playbooks/launch.md
          - slug: finance
            display_name: Finance source
            role: finance
            lifecycle: active
            relationship: reports_to
            parent: example
            visibility: restricted
            purpose: Private bookkeeping; hub stores approved summaries only.
        """
    )
    if extra_repos:
        # Ensure the extra block sits at the same indent as the existing
        # ``repos:`` list (2 spaces).
        indented = "\n".join(
            ("  " + line) if line.strip() else line for line in extra_repos.splitlines()
        )
        base = base.rstrip() + "\n" + indented + "\n"
    return base + "---\n# Topology\n"


# ---------------------------------------------------------------------------
# normalize_remote
# ---------------------------------------------------------------------------


def test_normalize_remote_accepts_common_handle_forms() -> None:
    assert topology.normalize_remote("github:example-co/example") == "example-co/example"
    assert (
        topology.normalize_remote("https://github.com/example-co/example.git")
        == "example-co/example"
    )
    assert (
        topology.normalize_remote("git@github.com:example-co/example.git") == "example-co/example"
    )
    assert topology.normalize_remote("example-co/example") == "example-co/example"
    assert topology.normalize_remote("") == ""
    assert topology.normalize_remote("not a remote") == ""


# ---------------------------------------------------------------------------
# read_registry
# ---------------------------------------------------------------------------


def test_read_registry_missing(tmp_path: Path) -> None:
    result = topology.read_registry(tmp_path)
    assert result["found"] is False
    assert result["ok"] is False
    assert result["error"] == "missing"
    assert result["repos"] == []


def test_read_registry_valid(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    result = topology.read_registry(tmp_path)
    assert result["found"] is True
    assert result["ok"] is True
    assert result["business_display_name"] == "Example Business"
    assert result["home_full_name"] == "example-co/example"
    slugs = [entry["slug"] for entry in result["repos"]]
    assert slugs == ["example", "workshop-site", "finance"]
    hub = result["repos"][0]
    assert hub["is_hub"] is True
    assert hub["remote_full_name"] == "example-co/example"
    site = result["repos"][1]
    assert "execution_vehicle_for" in site["relationships"]
    assert site["linked_offers"] == ["core/offers/workshop/offer.md"]
    assert site["linked_playbook_runs"] == ["pushes/2026-05-20-workshop-launch/playbooks/launch.md"]


def test_read_registry_unparsable(tmp_path: Path) -> None:
    _write_registry(tmp_path, "---\ntype: not_topology\n---\n# noop\n")
    result = topology.read_registry(tmp_path)
    assert result["found"] is True
    assert result["ok"] is False
    assert "type" in result["error"]


# ---------------------------------------------------------------------------
# read_child_descriptor
# ---------------------------------------------------------------------------


def _write_repo_json(repo: Path, payload: dict[str, object]) -> Path:
    target = repo / ".mainbranch" / "repo.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def _write_legacy_source(repo: Path, payload: dict[str, object]) -> Path:
    target = repo / ".mainbranch" / "source.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def test_read_child_descriptor_repo_json(tmp_path: Path) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "display_name": "Example Business",
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
                "local_checkout": "../example",
            },
            "linked": {"offers": ["core/offers/workshop/offer.md"]},
        },
    )
    result = topology.read_child_descriptor(tmp_path)
    assert result["found"] is True
    assert result["kind"] == "repo_json"
    assert result["ok"] is True
    assert result["role"] == "site"
    assert result["parent"]["remote_full_name"] == "example-co/example"
    assert result["parent"]["local_checkout_relative"] == "../example"
    assert result["legacy_business_repo_present"] is False


def test_read_child_descriptor_repo_json_drops_absolute_local_checkout(
    tmp_path: Path,
) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "local_checkout": "/Users/someone/Documents/GitHub/example-co/example",
            },
        },
    )
    result = topology.read_child_descriptor(tmp_path)
    assert result["parent"]["local_checkout_relative"] == ""


def test_read_child_descriptor_legacy_source_flags_absolute_business_repo(
    tmp_path: Path,
) -> None:
    _write_legacy_source(
        tmp_path,
        {
            "business_repo": "/Users/someone/Documents/GitHub/example-co/example",
            "offer_path": "core/offers/workshop/offer.md",
            "campaign_path": "pushes/2026-05-20-workshop-launch/push.md",
        },
    )
    result = topology.read_child_descriptor(tmp_path)
    assert result["found"] is True
    assert result["kind"] == "legacy_source"
    assert result["legacy_business_repo_present"] is True
    # absolute path is never copied into the public payload
    assert "/Users/" not in json.dumps(result)


def test_read_child_descriptor_missing(tmp_path: Path) -> None:
    result = topology.read_child_descriptor(tmp_path)
    assert result["found"] is False
    assert result["ok"] is False


def test_read_child_descriptor_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / ".mainbranch" / "repo.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    result = topology.read_child_descriptor(tmp_path)
    assert result["found"] is True
    assert result["ok"] is False
    assert result["error"].startswith("invalid JSON")


# ---------------------------------------------------------------------------
# current_repo_view + counts + boundary notes
# ---------------------------------------------------------------------------


def test_current_repo_view_matches_by_remote(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(
        registry=registry,
        descriptor=descriptor,
        git_remote="git@github.com:example-co/example.git",
    )
    assert view["matched"] is True
    assert view["match_source"] == "registry_remote"
    assert view["slug"] == "example"
    assert view["is_hub"] is True


def test_current_repo_view_does_not_false_match_across_github_orgs(
    tmp_path: Path,
) -> None:
    """Descriptor without its own github_owner must not borrow the parent's
    owner to compose a registry handle — a child in a different org would
    otherwise silently match an unrelated registry entry.
    """
    _write_registry(tmp_path, _valid_registry())
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Cross-org site",
            "repo_name": "workshop-site",
            # descriptor's own github_owner deliberately omitted; the child
            # really lives under a different GitHub org.
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    assert view["matched"] is False
    assert view["match_source"] == "descriptor"


def test_current_repo_view_falls_back_to_descriptor(tmp_path: Path) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(
        registry=registry,
        descriptor=descriptor,
        git_remote="",
    )
    assert view["matched"] is False
    assert view["match_source"] == "descriptor"
    assert view["role"] == "site"


def test_child_role_counts_excludes_hub(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    registry = topology.read_registry(tmp_path)
    counts = topology.child_role_counts(registry, exclude_slug="example")
    assert counts["total"] == 2
    assert counts["by_role"]["site"]["active"] == 1
    assert counts["by_role"]["finance"]["active"] == 1
    assert counts["by_lifecycle"]["active"] == 2


def test_restricted_repo_summary_excludes_public(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    registry = topology.read_registry(tmp_path)
    notes = topology.restricted_repo_summary(registry)
    visibilities = sorted(note["visibility"] for note in notes)
    assert "public" not in visibilities
    assert "team_private" in visibilities
    assert "restricted" in visibilities
    # boundary notes must not leak unsafe metadata
    payload = json.dumps(notes)
    assert "/Users/" not in payload


# ---------------------------------------------------------------------------
# drift_findings
# ---------------------------------------------------------------------------


def test_drift_findings_missing_registry_is_info_when_no_descriptor(
    tmp_path: Path,
) -> None:
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    assert len(findings) == 1
    assert findings[0]["code"] == "topology_registry_missing"
    assert findings[0]["severity"] == "info"


def test_drift_findings_missing_registry_with_descriptor_warns(
    tmp_path: Path,
) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"] for f in findings}
    assert "topology_descriptor_orphan" in codes


def test_drift_findings_descriptor_parent_unmatched(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "github_owner": "other-org",
                "repo_name": "other-hub",
                "remote": "github:other-org/other-hub",
            },
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"] for f in findings}
    assert "topology_descriptor_parent_unmatched" in codes


def test_drift_findings_descriptor_role_mismatch(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "product",
            "display_name": "Workshop site",
            "github_owner": "example-co",
            "repo_name": "workshop-site",
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(
        registry=registry,
        descriptor=descriptor,
        git_remote="git@github.com:example-co/workshop-site.git",
    )
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"] for f in findings}
    assert "topology_descriptor_role_mismatch" in codes


def test_drift_findings_unsafe_keys_warn(tmp_path: Path) -> None:
    extra = textwrap.dedent(
        """\
        - slug: legal
          display_name: Legal source
          role: legal
          lifecycle: active
          visibility: restricted
          relationship: reports_to
          parent: example
          ledger_path: /private/legal/ledger
          api_key: should-not-be-here
        """
    )
    _write_registry(tmp_path, _valid_registry(extra_repos=extra))
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"] for f in findings}
    assert "topology_repo_unsafe_keys" in codes


def test_drift_findings_restricted_with_safe_metadata_does_not_warn(
    tmp_path: Path,
) -> None:
    _write_registry(tmp_path, _valid_registry())
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    # finance entry is restricted but has only safe fields, so no warning
    codes = {f["code"] for f in findings}
    assert "topology_repo_unsafe_keys" not in codes
    assert "topology_repo_absolute_path" not in codes


def test_drift_findings_legacy_source_absolute_path(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    _write_legacy_source(
        tmp_path,
        {
            "business_repo": "/Users/someone/Documents/GitHub/example-co/example",
            "offer_path": "core/offers/workshop/offer.md",
            "campaign_path": "pushes/2026-05-20-workshop-launch/push.md",
        },
    )
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"] for f in findings}
    assert "topology_legacy_source_local_path" in codes


def test_drift_findings_blueprint_reference_is_info(tmp_path: Path) -> None:
    extra = textwrap.dedent(
        """\
        - slug: docs-site
          display_name: Docs site
          role: site
          lifecycle: active
          relationship: execution_vehicle_for
          parent: example
          github_owner: example-co
          repo_name: docs-site
          remote: github:example-co/docs-site
          visibility: public
          linked_playbooks:
            - .claude/playbooks/launch/launch.md
        """
    )
    _write_registry(tmp_path, _valid_registry(extra_repos=extra))
    registry = topology.read_registry(tmp_path)
    descriptor = topology.read_child_descriptor(tmp_path)
    view = topology.current_repo_view(registry=registry, descriptor=descriptor, git_remote="")
    findings = topology.drift_findings(registry=registry, descriptor=descriptor, current_view=view)
    codes = {f["code"]: f for f in findings}
    assert "topology_playbook_blueprint_reference" in codes
    assert codes["topology_playbook_blueprint_reference"]["severity"] == "info"


# ---------------------------------------------------------------------------
# collect (top-level)
# ---------------------------------------------------------------------------


def test_collect_returns_safe_payload(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    payload = topology.collect(tmp_path, git_remote="git@github.com:example-co/example.git")
    assert payload["schema"] == "mb.topology.view.v0"
    assert payload["safe_to_share"] is True
    assert payload["summary"]["registry_ok"] is True
    assert payload["summary"]["current_repo_matched"] is True
    assert payload["summary"]["child_repo_count"] == 2
    assert payload["current_repo"]["slug"] == "example"
    # public-safe payload must not embed any absolute paths
    assert "/Users/" not in json.dumps(payload)


def test_collect_handles_missing_registry(tmp_path: Path) -> None:
    payload = topology.collect(tmp_path)
    assert payload["summary"]["registry_found"] is False
    assert payload["summary"]["registry_ok"] is False
    assert payload["current_repo"]["matched"] is False
    assert payload["restricted_repos"] == []
    # missing registry alone is informational, not a warning
    assert payload["summary"]["warnings"] == 0
