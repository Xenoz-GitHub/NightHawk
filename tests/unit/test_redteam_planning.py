"""Tests for authorized red-team planning models and CLI."""

import json

import pytest
from typer.testing import CliRunner

from nighthawk.cli.main import app
from nighthawk.redteam import (
    ExecutionMode,
    RedTeamMission,
    RedTeamObjective,
    build_attack_path,
)


class TestRedTeamMission:
    def test_simulation_needs_no_authorization(self):
        mission = RedTeamMission("Practice", RedTeamObjective.RECON)
        mission.validate()
        assert mission.to_dict()["mode"] == "simulation"

    def test_validate_mode_requires_authorization(self):
        mission = RedTeamMission(
            "Review", RedTeamObjective.RECON, ExecutionMode.VALIDATE
        )
        with pytest.raises(ValueError, match="authorization"):
            mission.validate()

    def test_blank_authorization_reference_is_rejected(self):
        mission = RedTeamMission(
            "Review", RedTeamObjective.RECON,
            ExecutionMode.VALIDATE, authorization_ref="   ",
        )
        with pytest.raises(ValueError, match="authorization"):
            mission.validate()

    def test_active_mode_requires_targets(self):
        mission = RedTeamMission(
            "Live review", RedTeamObjective.RECON,
            ExecutionMode.AUTHORIZED_ACTIVE, authorization_ref="ROE-42",
        )
        with pytest.raises(ValueError, match="target"):
            mission.validate()

    def test_plans_have_ordered_dependencies(self):
        steps = build_attack_path(RedTeamObjective.INITIAL_ACCESS)
        assert steps[1].requires == (steps[0].id,)
        assert steps[2].requires == (steps[1].id,)
        assert all(not step.destructive for step in steps)


def test_redteam_cli_creates_simulation_mission(tmp_path):
    output = tmp_path / "mission.json"
    result = CliRunner().invoke(app, [
        "redteam", "mission-create", "Lab review",
        "--objective", "detection-validation",
        "--output", str(output),
    ])
    assert result.exit_code == 0, result.output
    payload = json.loads(output.read_text())
    assert payload["objective"] == "detection-validation"
    assert payload["mode"] == "simulation"


def test_redteam_cli_rejects_active_mission_without_approval(tmp_path):
    result = CliRunner().invoke(app, [
        "redteam", "mission-create", "Live review",
        "--mode", "authorized-active",
        "--target", "approved.example",
        "--output", str(tmp_path / "mission.json"),
    ])
    assert result.exit_code != 0
    assert "authorization" in result.output.lower()


def test_game_commands_are_not_root_commands():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "│ game " in result.output
    assert " bounties " not in result.output
    assert " mission-list " not in result.output
    assert " game-start" not in result.output
