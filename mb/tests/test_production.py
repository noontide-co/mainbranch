"""`mb production plan` — money-taking branch-protection posture (#835)."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from mb import production as production_mod
from mb.cli import app

runner = CliRunner()

# A fully-armed money-taking protection object.
_ARMED = {
    "required_pull_request_reviews": {"required_approving_review_count": 1},
    "required_status_checks": {"strict": True, "contexts": ["mb checks", "money-path canary"]},
    "allow_force_pushes": {"enabled": False},
    "allow_deletions": {"enabled": False},
}


def test_plan_flags_every_gap_when_unprotected() -> None:
    result = production_mod.plan("owner/repo", current_protection=None)
    assert result["ok"] is False
    assert len(result["missing"]) == 4
    assert result["present"] == []
    # Names the provider-mutation contract and emits operator-applies commands.
    assert "provider-mutation-contract.md" in result["summary"]
    assert result["apply_commands"]
    assert any("gh api -X PUT" in c for c in result["apply_commands"])
    assert "owner/repo" in result["apply_commands"][0]


def test_plan_clean_when_fully_armed() -> None:
    result = production_mod.plan("owner/repo", current_protection=_ARMED)
    assert result["ok"] is True
    assert result["missing"] == []
    assert len(result["present"]) == 4
    assert result["apply_commands"] == []


def test_plan_requires_canary_in_status_checks() -> None:
    # A status-check gate WITHOUT the canary still leaves the checks item open.
    no_canary = dict(_ARMED)
    no_canary["required_status_checks"] = {"strict": True, "contexts": ["mb checks"]}
    result = production_mod.plan("owner/repo", current_protection=no_canary)
    assert result["ok"] is False
    assert any("canary" in m for m in result["missing"])


def test_plan_solo_on_main_is_a_deliberate_skip_not_a_gap() -> None:
    result = production_mod.plan("owner/repo", solo=True)
    assert result["ok"] is True
    assert result["solo_on_main"] is True
    assert result["missing"] == []
    assert result["apply_commands"] == []
    assert "deliberate skip" in result["summary"]


def test_plan_partial_posture_lists_present_and_missing() -> None:
    partial = {
        "required_pull_request_reviews": {"required_approving_review_count": 1},
        "allow_force_pushes": {"enabled": True},  # force-push still allowed = gap
        "allow_deletions": {"enabled": False},
    }
    result = production_mod.plan("owner/repo", current_protection=partial)
    assert "require a pull request before merge" in result["present"]
    assert "block force-push to the default branch" in result["missing"]
    assert any("status checks" in m for m in result["missing"])


def test_production_plan_cli_solo_json() -> None:
    result = runner.invoke(app, ["production", "plan", "--solo", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["solo_on_main"] is True
    assert payload["safe_to_share"] is True
