"""CLI for authorized red-team planning and mission definitions."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from nighthawk.redteam import (
    ExecutionMode,
    RedTeamMission,
    RedTeamObjective,
    build_attack_path,
)

console = Console()
redteam_app = typer.Typer(
    name="redteam",
    help="Authorized red-team planning, validation, and evidence workflows.",
    invoke_without_command=True,
)


@redteam_app.callback()
def redteam_menu(ctx: typer.Context) -> None:
    """Show the red-team menu when no action was selected."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


def _objective(value: str) -> RedTeamObjective:
    try:
        return RedTeamObjective(value.strip().lower())
    except ValueError as exc:
        choices = ", ".join(item.value for item in RedTeamObjective)
        raise typer.BadParameter(f"Choose one of: {choices}") from exc


def _mode(value: str) -> ExecutionMode:
    try:
        return ExecutionMode(value.strip().lower())
    except ValueError as exc:
        choices = ", ".join(item.value for item in ExecutionMode)
        raise typer.BadParameter(f"Choose one of: {choices}") from exc


@redteam_app.command("plan")
def show_plan(
    objective: str = typer.Argument(..., help="Red-team objective to plan."),
) -> None:
    """Show a deterministic, non-executing attack-path plan."""
    selected = _objective(objective)
    table = Table(title=f"Attack path: {selected.value}", show_header=True)
    table.add_column("Step", style="cyan")
    table.add_column("Phase", style="magenta")
    table.add_column("Technique", style="yellow")
    table.add_column("Safe action", style="green")
    for step in build_attack_path(selected):
        table.add_row(step.id, step.phase, step.technique, step.safe_action)
    console.print(table)
    console.print("[dim]Planning only: no network or target actions were performed.[/dim]")


@redteam_app.command("mission-create")
def create_mission(
    title: str = typer.Argument(..., help="Mission title."),
    objective: str = typer.Option("recon", "--objective", "-o"),
    mode: str = typer.Option("simulation", "--mode", help="simulation, validate, or authorized-active"),
    target: list[str] = typer.Option([], "--target", help="Approved target; repeat for multiple targets."),
    authorization_ref: str | None = typer.Option(None, "--authorization-ref", help="Approval or ticket reference."),
    notes: str = typer.Option("", "--notes"),
    output: Path = typer.Option(Path(".nighthawk/missions/mission.json"), "--output", "-f"),
) -> None:
    """Create a validated, auditable red-team mission plan."""
    mission = RedTeamMission(
        title=title,
        objective=_objective(objective),
        mode=_mode(mode),
        targets=target,
        authorization_ref=authorization_ref,
        notes=notes,
    )
    try:
        payload = mission.to_dict()
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Mission written:[/green] {output}")
    console.print(f"[cyan]Objective:[/cyan] {mission.objective.value}")
    console.print(f"[cyan]Mode:[/cyan] {mission.mode.value}")
    console.print(f"[cyan]Steps:[/cyan] {len(build_attack_path(mission.objective))}")


@redteam_app.command("objectives")
def list_objectives() -> None:
    """List supported red-team objectives."""
    for objective in RedTeamObjective:
        console.print(objective.value)
