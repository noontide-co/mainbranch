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
    helper = payload["repo_boundary"]
    assert helper["schema"] == "mb.repo_boundary_helper.v0"
    assert helper["state"] == "hub_business_repo"
    assert helper["recommended_choice"] == "same_business_repo"
    assert {choice["id"] for choice in helper["choices"]} == {
        "same_business_repo",
        "separate_business_repo",
        "child_lightweight_repo",
    }
    # public-safe payload must not embed any absolute paths
    assert "/Users/" not in json.dumps(payload)


def test_collect_handles_missing_registry(tmp_path: Path) -> None:
    payload = topology.collect(tmp_path)
    assert payload["summary"]["registry_found"] is False
    assert payload["summary"]["registry_ok"] is False
    assert payload["current_repo"]["matched"] is False
    assert payload["restricted_repos"] == []
    assert payload["repo_boundary"]["state"] == "single_business_repo"
    assert payload["repo_boundary"]["recommended_choice"] == "same_business_repo"
    # missing registry alone is informational, not a warning
    assert payload["summary"]["warnings"] == 0


def test_repo_boundary_helper_recognizes_child_descriptor(tmp_path: Path) -> None:
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

    payload = topology.collect(tmp_path)

    helper = payload["repo_boundary"]
    assert helper["state"] == "child_or_execution_repo"
    assert helper["recommended_choice"] == "child_lightweight_repo"
    assert "return to the hub business repo" in helper["next_action"]


def test_repo_boundary_helper_redacts_unsafe_child_parent_handle(tmp_path: Path) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Private client site",
            "github_owner": "client-co",
            "repo_name": "private-site",
            "safe_to_share": False,
            "parent": {
                "github_owner": "example-co",
                "repo_name": "example",
                "remote": "github:example-co/example",
            },
        },
    )

    payload = topology.collect(tmp_path)

    helper = payload["repo_boundary"]
    assert helper["state"] == "child_or_execution_repo"
    assert helper["recommended_choice"] == "child_lightweight_repo"
    assert helper["safe_to_share"] is False
    assert "Hub handle:" not in helper["next_action"]
    assert "example-co/example" not in json.dumps(helper)


# ---------------------------------------------------------------------------
# Repo profiles (MAIN-463)
# ---------------------------------------------------------------------------


def test_role_to_profile_maps_known_roles() -> None:
    assert topology.role_to_profile("business") == "hub"
    assert topology.role_to_profile("site") == "website"
    assert topology.role_to_profile("offer") == "website"
    assert topology.role_to_profile("product") == "product"
    assert topology.role_to_profile("client") == "product"
    assert topology.role_to_profile("finance") == "private"
    assert topology.role_to_profile("legal") == "private"
    assert topology.role_to_profile("ops") == "private"
    assert topology.role_to_profile("integration_sidecar") == "integration"
    assert topology.role_to_profile("archive") == "archive"


def test_role_to_profile_experiment_is_unknown() -> None:
    assert topology.role_to_profile("experiment") == ""
    assert topology.role_to_profile("nonsense") == ""


def test_profile_vocabulary_is_direct() -> None:
    assert {
        "hub",
        "website",
        "product",
        "private",
        "integration",
        "archive",
    } == topology.TOPOLOGY_PROFILES


def test_infer_profile_from_signals_website_via_conversion(tmp_path: Path) -> None:
    (tmp_path / ".mainbranch").mkdir()
    (tmp_path / ".mainbranch" / "conversion.json").write_text("{}", encoding="utf-8")
    assert topology.infer_profile_from_signals(tmp_path) == "website"


def test_infer_profile_from_signals_website_via_product_design(tmp_path: Path) -> None:
    (tmp_path / "PRODUCT.md").write_text("# product", encoding="utf-8")
    (tmp_path / "DESIGN.md").write_text("# design", encoding="utf-8")
    assert topology.infer_profile_from_signals(tmp_path) == "website"


def test_infer_profile_from_signals_hub(tmp_path: Path) -> None:
    (tmp_path / "core").mkdir()
    (tmp_path / ".mb").mkdir()
    assert topology.infer_profile_from_signals(tmp_path) == "hub"


def test_infer_profile_from_signals_unknown(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# nothing", encoding="utf-8")
    assert topology.infer_profile_from_signals(tmp_path) == ""


def test_resolve_profile_explicit_descriptor_wins() -> None:
    # Normalized descriptors set profile_explicit when the owner declared one.
    descriptor = {"found": True, "role": "site", "profile": "archive", "profile_explicit": True}
    out = topology.resolve_profile(descriptor=descriptor, current_view={})
    assert out == {"profile": "archive", "profile_source": "descriptor_explicit"}


def test_resolve_profile_role_derived_descriptor_is_not_explicit() -> None:
    # A role-only descriptor carries a role-derived profile but profile_explicit
    # is False; the source must be "role", not "descriptor_explicit".
    descriptor = {"found": True, "role": "site", "profile": "website", "profile_explicit": False}
    out = topology.resolve_profile(descriptor=descriptor, current_view={})
    assert out == {"profile": "website", "profile_source": "role"}


def test_resolve_profile_falls_back_to_role() -> None:
    descriptor = {"found": True, "role": "finance", "profile": "private", "profile_explicit": False}
    out = topology.resolve_profile(descriptor=descriptor, current_view={})
    assert out == {"profile": "private", "profile_source": "role"}


def test_resolve_profile_role_derived_via_read_child_descriptor(tmp_path: Path) -> None:
    # End-to-end through the normalization layer: a role-only repo.json must
    # report profile_source "role", never "descriptor_explicit".
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "display_name": "Workshop site",
        },
    )
    descriptor = topology.read_child_descriptor(tmp_path)
    assert descriptor["profile"] == "website"
    assert descriptor["profile_explicit"] is False
    out = topology.resolve_profile(descriptor=descriptor, current_view={})
    assert out == {"profile": "website", "profile_source": "role"}


def test_resolve_profile_registry_explicit_requires_flag() -> None:
    # Matched registry entry whose profile is only role-derived must not be
    # labeled registry_explicit.
    derived_view = {"matched": True, "role": "site", "registry_profile": "website"}
    assert topology.resolve_profile(descriptor={"found": False}, current_view=derived_view) == {
        "profile": "website",
        "profile_source": "role",
    }
    explicit_view = {
        "matched": True,
        "role": "site",
        "registry_profile": "archive",
        "registry_profile_explicit": True,
    }
    assert topology.resolve_profile(descriptor={"found": False}, current_view=explicit_view) == {
        "profile": "archive",
        "profile_source": "registry_explicit",
    }


def test_resolve_profile_signal_when_no_descriptor(tmp_path: Path) -> None:
    (tmp_path / ".mainbranch").mkdir()
    (tmp_path / ".mainbranch" / "conversion.json").write_text("{}", encoding="utf-8")
    out = topology.resolve_profile(descriptor={"found": False}, current_view={}, repo_path=tmp_path)
    assert out == {"profile": "website", "profile_source": "signal"}


def test_resolve_profile_unknown() -> None:
    out = topology.resolve_profile(descriptor={"found": False}, current_view={})
    assert out == {"profile": "", "profile_source": "unknown"}


def test_repo_json_reads_explicit_profile(tmp_path: Path) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "product",
            "profile": "archive",
            "display_name": "Old product",
        },
    )
    result = topology.read_child_descriptor(tmp_path)
    assert result["profile"] == "archive"
    assert result["profile_explicit"] is True


def test_repo_json_invalid_profile_ignored(tmp_path: Path) -> None:
    _write_repo_json(
        tmp_path,
        {
            "schema": topology.CHILD_REPO_SCHEMA,
            "role": "site",
            "profile": "lightweight_website",
            "display_name": "Site",
        },
    )
    result = topology.read_child_descriptor(tmp_path)
    # Unrecognized profile falls back to role-derived inference.
    assert result["profile"] == "website"
    assert result["profile_explicit"] is False


def test_legacy_source_infers_website_profile(tmp_path: Path) -> None:
    _write_legacy_source(tmp_path, {"business_repo": "../example"})
    result = topology.read_child_descriptor(tmp_path)
    assert result["role"] == "site"
    assert result["profile"] == "website"


def test_collect_surfaces_profile_for_website(tmp_path: Path) -> None:
    (tmp_path / ".mainbranch").mkdir()
    (tmp_path / ".mainbranch" / "conversion.json").write_text("{}", encoding="utf-8")
    view = topology.collect(tmp_path)
    assert view["current_repo"]["profile"] == "website"
    assert view["current_repo"]["profile_source"] == "signal"
    assert view["summary"]["current_repo_profile"] == "website"


def test_collect_child_profile_counts(tmp_path: Path) -> None:
    _write_registry(tmp_path, _valid_registry())
    view = topology.collect(tmp_path)
    counts = view["child_profile_counts"]
    # workshop-site -> website, finance -> private; hub excluded.
    assert counts.get("website") == 1
    assert counts.get("private") == 1
    assert "hub" not in counts


def test_drift_flags_private_profile_with_public_visibility(tmp_path: Path) -> None:
    _write_registry(
        tmp_path,
        _valid_registry(
            extra_repos=(
                "- slug: books\n"
                "  display_name: Books\n"
                "  role: finance\n"
                "  lifecycle: active\n"
                "  parent: example\n"
                "  github_owner: example-co\n"
                "  repo_name: books\n"
                "  remote: github:example-co/books\n"
                "  visibility: public\n"
            )
        ),
    )
    registry = topology.read_registry(tmp_path)
    findings = topology.drift_findings(
        registry=registry, descriptor=topology._empty_descriptor(), current_view={}
    )
    codes = {f["code"] for f in findings}
    assert "topology_private_profile_public_visibility" in codes


def test_role_to_profile_targets_are_valid() -> None:
    for role, profile in topology.ROLE_TO_PROFILE.items():
        assert role in topology.TOPOLOGY_ROLES
        assert profile in topology.TOPOLOGY_PROFILES


def test_docs_document_every_profile_and_no_fluffy_names() -> None:
    doc = (Path(__file__).resolve().parents[2] / "docs" / "child-repo-descriptors.md").read_text(
        encoding="utf-8"
    )
    for profile in topology.TOPOLOGY_PROFILES:
        assert f"`{profile}`" in doc, f"profile {profile!r} not documented"
    # The retired fluffy names must never become canonical vocabulary.
    for retired in ("lightweight_website", "business_hub", "code_product", "private_source"):
        assert retired not in doc
