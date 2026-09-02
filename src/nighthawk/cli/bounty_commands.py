"""CLI commands for bounty system."""

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
import time

from nighthawk.game.bounty import BountyBoard, MissionDifficulty, MissionStatus
from nighthawk.game.mission_generator import MissionGenerator
from nighthawk.ui.bounty_board import BountyBoardUI
from nighthawk.cli.banner import (
    print_success,
    print_error,
    print_warning,
    print_info,
    create_header_panel,
)

console = Console()
bounty_app = typer.Typer(
    name="bounties",
    help="💰 Bounty System - Accept missions for fame and fortune",
)

# Global bounty board and generator instances
_bounty_board: BountyBoard = None
_mission_generator: MissionGenerator = None


def get_bounty_board() -> BountyBoard:
    """Get or create bounty board instance."""
    global _bounty_board
    if _bounty_board is None:
        _bounty_board = BountyBoard()
    return _bounty_board


def get_mission_generator() -> MissionGenerator:
    """Get or create mission generator instance."""
    global _mission_generator
    if _mission_generator is None:
        _mission_generator = MissionGenerator()
    return _mission_generator


def initialize_bounty_board(player_level: int = 1):
    """Initialize bounty board with daily missions."""
    board = get_bounty_board()
    generator = get_mission_generator()
    
    # Generate daily missions if board is empty
    if len(board.get_available_missions(player_level)) == 0:
        daily_missions = generator.generate_daily_missions(count=10, player_level=player_level)
        for mission in daily_missions:
            board.post_mission(mission)


@bounty_app.command("board")
def show_bounty_board(
    player_level: int = typer.Option(1, "--level", "-l", help="Player level for mission filtering")
) -> None:
    """💰 Display the bounty board with available missions."""
    console.clear()
    
    board = get_bounty_board()
    initialize_bounty_board(player_level)
    
    BountyBoardUI.print_bounty_board(board, player_level)


@bounty_app.command("list")
def list_missions(
    difficulty: str = typer.Option(None, "--difficulty", "-d", 
                                   help="Filter by difficulty (easy, medium, hard, expert, legendary)"),
    player_level: int = typer.Option(1, "--level", "-l", help="Player level for mission filtering"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum missions to show"),
) -> None:
    """📋 List available missions with filtering."""
    console.clear()
    BountyBoardUI.print_header("MISSION LIST")
    
    board = get_bounty_board()
    initialize_bounty_board(player_level)
    
    missions = board.get_available_missions(player_level, max_results=limit)
    
    # Filter by difficulty if specified
    if difficulty:
        try:
            diff_enum = MissionDifficulty[difficulty.upper()]
            missions = [m for m in missions if m.difficulty == diff_enum]
        except KeyError:
            print_error(console, f"Invalid difficulty: {difficulty}")
            return
    
    BountyBoardUI.print_mission_list(missions, show_numbers=True)


@bounty_app.command("info")
def mission_info(
    mission_number: int = typer.Argument(..., help="Mission number to view details"),
    player_level: int = typer.Option(1, "--level", "-l", help="Player level"),
) -> None:
    """🔍 View detailed information about a specific mission."""
    console.clear()
    
    board = get_bounty_board()
    initialize_bounty_board(player_level)
    
    missions = board.get_available_missions(player_level)
    
    if mission_number < 1 or mission_number > len(missions):
        print_error(console, f"Invalid mission number: {mission_number}")
        return
    
    mission = missions[mission_number - 1]
    BountyBoardUI.print_mission_detail(mission)


@bounty_app.command("accept")
def accept_mission(
    mission_number: int = typer.Argument(..., help="Mission number to accept"),
    player_id: str = typer.Option("player", "--player-id", "-p", help="Player ID"),
    player_level: int = typer.Option(1, "--level", "-l", help="Player level"),
) -> None:
    """✅ Accept a mission from the bounty board."""
    board = get_bounty_board()
    initialize_bounty_board(player_level)
    
    missions = board.get_available_missions(player_level)
    
    if mission_number < 1 or mission_number > len(missions):
        print_error(console, f"Invalid mission number: {mission_number}")
        return
    
    mission = missions[mission_number - 1]
    
    # Show mission summary and ask for confirmation
    console.print()
    BountyBoardUI.print_mission_summary(mission)
    console.print()
    
    if Confirm.ask("[yellow]Accept this mission?[/yellow]"):
        success = board.accept_mission(mission.mission_id, player_id)
        
        if success:
            BountyBoardUI.print_mission_accepted(mission)
            print_success(console, f"✓ Mission '{mission.title}' accepted!")
            print_info(console, f"Deadline: {mission.deadline.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print_error(console, "Failed to accept mission!")
    else:
        print_warning(console, "Mission not accepted.")


@bounty_app.command("active")
def show_active_missions(
    player_id: str = typer.Option("player", "--player-id", "-p", help="Player ID"),
) -> None:
    """🎯 Show your active missions."""
    console.clear()
    
    board = get_bounty_board()
    active_missions = board.get_player_active_missions()
    
    BountyBoardUI.print_active_missions(active_missions)


@bounty_app.command("complete")
def complete_mission(
    mission_number: int = typer.Argument(..., help="Mission number (from active list) to complete"),
    player_level: int = typer.Option(1, "--level", "-l", help="Player level"),
) -> None:
    """✨ Complete an active mission."""
    board = get_bounty_board()
    active_missions = board.get_player_active_missions()
    
    if mission_number < 1 or mission_number > len(active_missions):
        print_error(console, f"Invalid mission number: {mission_number}")
        return
    
    mission = active_missions[mission_number - 1]
    
    # Simulate mission completion with time delay
    console.print(f"\n[cyan]Completing mission: {mission.title}[/cyan]")
    
    with console.status("[bold green]Processing...") as status:
        time.sleep(1)
    
    # Complete mission and get rewards
    crypto_reward, xp_reward, success = board.complete_mission(mission.mission_id, player_level)
    
    if success:
        BountyBoardUI.print_mission_completed(mission, crypto_reward, xp_reward)
        print_success(console, "✓ Mission completed successfully!")
        console.print()
    else:
        print_error(console, "Failed to complete mission!")


@bounty_app.command("history")
def show_mission_history(
    player_id: str = typer.Option("player", "--player-id", "-p", help="Player ID"),
) -> None:
    """📜 Show your completed mission history."""
    console.clear()
    BountyBoardUI.print_header("MISSION HISTORY")
    
    board = get_bounty_board()
    history = board.get_player_mission_history()
    
    if not history:
        print_info(console, "No completed missions yet.")
        console.print()
        return
    
    # Create table
    table = Table(title=f"Completed Missions ({len(history)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Mission", style="green")
    table.add_column("Difficulty", justify="center")
    table.add_column("Client")
    table.add_column("Reward", style="yellow")
    table.add_column("Completed", style="dim")
    
    for i, mission in enumerate(history, 1):
        reward = f"₡{mission.base_reward:,}"
        completed_time = mission.completed_at.strftime("%Y-%m-%d %H:%M") if mission.completed_at else "N/A"
        
        table.add_row(
            str(i),
            mission.title,
            mission.difficulty.value.upper(),
            mission.client.name,
            reward,
            completed_time,
        )
    
    console.print(table)
    console.print()


@bounty_app.command("stats")
def show_bounty_stats() -> None:
    """📊 Display bounty system statistics."""
    console.clear()
    BountyBoardUI.print_header("BOUNTY STATISTICS")
    
    board = get_bounty_board()
    stats = board.get_mission_stats()
    
    # Create stats table
    table = Table(show_header=False, show_border=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    
    table.add_row("Total Missions Posted", str(stats['total_missions_posted']))
    table.add_row("Available Missions", str(stats['available_missions']))
    table.add_row("Your Active Missions", str(stats['active_missions']))
    table.add_row("Completed Missions", str(stats['completed_missions']))
    table.add_row("Registered Clients", str(stats['total_clients']))
    
    console.print()
    console.print(table)
    console.print()


@bounty_app.command("refresh")
def refresh_bounty_board(
    player_level: int = typer.Option(1, "--level", "-l", help="Player level"),
) -> None:
    """🔄 Refresh bounty board with new missions."""
    global _bounty_board
    
    generator = get_mission_generator()
    
    console.print("[cyan]Refreshing bounty board...[/cyan]")
    
    with console.status("[bold green]Generating new missions..."):
        time.sleep(0.5)
        
        # Reset board
        _bounty_board = BountyBoard()
        
        # Generate new missions
        new_missions = generator.generate_daily_missions(count=10, player_level=player_level)
        for mission in new_missions:
            get_bounty_board().post_mission(mission)
    
    print_success(console, "✓ Bounty board refreshed with 10 new missions!")
    console.print()


@bounty_app.command("clients")
def list_clients() -> None:
    """👥 Display information about all bounty clients."""
    console.clear()
    BountyBoardUI.print_header("BOUNTY CLIENTS")
    
    board = get_bounty_board()
    
    console.print()
    
    # Create clients table
    table = Table(title="Registered Clients", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Specialization")
    table.add_column("Reputation", justify="center")
    table.add_column("Success Rate", justify="center")
    table.add_column("Contact", style="dim")
    
    for client in board.clients.values():
        icon = BountyBoardUI.CLIENT_ICONS.get(client.client_type, "🔹")
        success_rate = f"{client.successful_completion_rate * 100:.1f}%" if client.total_missions_posted > 0 else "N/A"
        
        table.add_row(
            f"{icon} {client.name}",
            client.client_type.value,
            client.specialization,
            client.reputation_tier.value.upper(),
            success_rate,
            client.contact_method,
        )
    
    console.print(table)
    console.print()
