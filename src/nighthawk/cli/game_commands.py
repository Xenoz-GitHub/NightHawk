"""CLI commands for game functionality."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from pathlib import Path
import time

from nighthawk.game.engine import GameEngine
from nighthawk.game.team_selection import (
    TeamDatabase,
    TeamRole,
    MissionLibrary,
    TeamSelectionValidator,
    TeamBenefits,
    TeamComparison,
)
from nighthawk.cli.banner import (
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_info,
    create_header_panel,
)

console = Console()
game_app = typer.Typer(
    name="game",
    help=" Hacking Simulation Game - Red Team vs Blue Team",
)

# Global game engine instance
_game_engine: GameEngine = None


def get_game_engine() -> GameEngine:
    """Get or create game engine instance."""
    global _game_engine
    if _game_engine is None:
        _game_engine = GameEngine()
    return _game_engine


def print_typing_effect(text: str, delay: float = 0.03) -> None:
    """Print text with typing effect."""
    for char in text:
        console.print(char, end="", style="bold green")
        time.sleep(delay)
    console.print()


def print_glitch_text(text: str) -> None:
    """Print text with glitch effect."""
    console.print(f"[red blink]{text}[/red blink]")
    time.sleep(0.1)
    console.print(f"\r{text}", style="bold green")


@game_app.command("start")
def start_game() -> None:
    """ Start a new game or continue existing save."""
    console.clear()
    print_banner(console, "2.0.0")
    console.print()

    engine = get_game_engine()

    # Check for existing saves
    save_slots = engine.get_save_slots()
    existing_saves = [slot for slot, info in save_slots.items() if info is not None]

    if existing_saves:
        console.print(create_header_panel(
            " Welcome Back, Operative",
            "Continue Your Mission or Start Fresh"
        ))
        console.print()

        # Show existing saves
        table = Table(title=" Save Slots", show_header=True, header_style="bold cyan")
        table.add_column("Slot", style="cyan", justify="center")
        table.add_column("Username", style="green")
        table.add_column("Team", style="magenta")
        table.add_column("Level", justify="center")
        table.add_column("Last Saved", style="dim")

        for slot, info in save_slots.items():
            if info:
                team_icon = "" if info["team"] == "red" else ""
                table.add_row(
                    str(slot),
                    info["username"],
                    f"{team_icon} {info['team'].upper()}",
                    str(info["level"]),
                    info["saved_at"][:19].replace("T", " "),
                )
            else:
                table.add_row(
                    str(slot),
                    "[dim]Empty[/dim]",
                    "",
                    "",
                    "",
                )

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "[cyan]Choose option[/cyan]",
            choices=["new", "load", "exit"],
            default="load"
        )

        if choice == "exit":
            return
        elif choice == "load":
            slot = int(Prompt.ask("[cyan]Select save slot[/cyan]", choices=["1", "2", "3"]))

            if save_slots[slot] is None:
                print_error(console, f"Slot {slot} is empty!")
                return

            success = engine.load_game(slot)
            if success:
                print_success(console, f" Loaded save: {save_slots[slot]['username']}")
                console.print()
                show_game_dashboard()
            else:
                print_error(console, "Failed to load save!")
            return

    # New game
    console.print(create_header_panel(
        " New Game",
        "Begin Your Journey Into the Shadows"
    ))
    console.print()

    print_typing_effect(" INITIALIZING NIGHTHAWK SYSTEM...")
    time.sleep(0.5)
    print_typing_effect(" ESTABLISHING SECURE CONNECTION...")
    time.sleep(0.5)
    print_typing_effect(" LOADING NEURAL NETWORK...")
    time.sleep(0.5)
    print_glitch_text(" SYSTEM READY")
    console.print()

    # Get username
    username = Prompt.ask("[cyan]Enter your hacker alias[/cyan]", default="Anonymous")

    # Initialize game
    success = engine.initialize_new_game(username)

    if not success:
        print_error(console, "Failed to initialize game!")
        return

    print_success(console, f" Profile created: {username}")
    console.print()

    # Proceed to team selection
    select_team_interactive()


@game_app.command("select-team")
def select_team_interactive() -> None:
    """ Select your team (Red Team or Blue Team)."""
    engine = get_game_engine()

    if not engine.is_initialized:
        print_error(console, "No game in progress! Use 'nighthawk game start' first.")
        return

    if engine.player.is_team_selected():
        profile = engine.player.get_profile()
        team_icon = "" if profile.team.value == "red" else ""
        print_warning(console, f"Team already selected: {team_icon} {profile.team.value.upper()} TEAM")
        return

    console.clear()
    console.print()

    # ASCII Art for Team Selection
    console.print("""
[red bold]
    ██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗
    ██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
    ██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║
    ██╔══██╗██╔══╝  ██║  ██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
    ██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
    ╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
[/red bold]
                                      [red]VS[/red]
[cyan bold]
    ██████╗ ██╗     ██╗   ██╗███████╗    ████████╗███████╗ █████╗ ███╗   ███╗
    ██╔══██╗██║     ██║   ██║██╔════╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
    ██████╔╝██║     ██║   ██║█████╗         ██║   █████╗  ███████║██╔████╔██║
    ██╔══██╗██║     ██║   ██║██╔══╝         ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
    ██████╔╝███████╗╚██████╔╝███████╗       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
    ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
[/cyan bold]
    """, justify="center")

    console.print()
    console.print(Panel.fit(
        "[yellow bold]  THIS CHOICE IS PERMANENT  [/yellow bold]\n"
        "Choose wisely - your team determines your path, skills, and missions.",
        border_style="yellow",
    ))
    console.print()

    # Show team comparison
    show_team_comparison()
    console.print()

    # Get team choice
    choice = Prompt.ask(
        "[bold cyan]Select your team[/bold cyan]",
        choices=["red", "blue", "compare", "help"],
        default="red"
    )

    if choice == "compare":
        show_detailed_comparison()
        return select_team_interactive()
    elif choice == "help":
        show_team_help()
        return select_team_interactive()

    # Confirm choice
    team_name = "Red Team (Offensive)" if choice == "red" else "Blue Team (Defensive)"
    confirm = Confirm.ask(f"[yellow]Confirm selection: {team_name}?[/yellow]")

    if not confirm:
        console.print()
        print_info(console, "Selection cancelled. Think it over...")
        return

    # Select team
    success = engine.select_team(choice)

    if success:
        console.print()
        print_glitch_text(" INITIALIZING TEAM PROTOCOLS...")
        time.sleep(0.5)

        team_info = TeamDatabase.get_team_info(TeamRole(choice))

        if choice == "red":
            console.print(Panel.fit(
                f"[red bold]  WELCOME TO RED TEAM  [/red bold]\n\n"
                f"[white]{team_info.motto}[/white]\n\n"
                f"[green]Starting Tools Unlocked:[/green]\n" +
                "\n".join(f"   {tool}" for tool in team_info.starting_tools) +
                f"\n\n[yellow]Bonus: {team_info.starting_bonus_currency} ₡ + {team_info.starting_bonus_xp} XP[/yellow]",
                border_style="red",
                title="[red bold]OFFENSIVE SECURITY[/red bold]",
            ))
        else:
            console.print(Panel.fit(
                f"[cyan bold]  WELCOME TO BLUE TEAM  [/cyan bold]\n\n"
                f"[white]{team_info.motto}[/white]\n\n"
                f"[green]Starting Tools Unlocked:[/green]\n" +
                "\n".join(f"   {tool}" for tool in team_info.starting_tools) +
                f"\n\n[yellow]Bonus: {team_info.starting_bonus_currency} ₡ + {team_info.starting_bonus_xp} XP[/yellow]",
                border_style="cyan",
                title="[cyan bold]DEFENSIVE SECURITY[/cyan bold]",
            ))

        console.print()
        print_success(console, " Team selection complete!")

        # Save game
        engine.save_game(slot=1)

        console.print()
        print_typing_effect(" Your first missions are now available...")
        console.print()

        # Show starter missions
        show_starter_missions(TeamRole(choice))

    else:
        print_error(console, "Failed to select team!")


def show_team_comparison() -> None:
    """Show side-by-side team comparison."""
    comparison = TeamComparison.get_comparison_matrix()

    table = Table(title=" Team Comparison ", show_header=True, header_style="bold magenta")
    table.add_column("Aspect", style="yellow", justify="left")
    table.add_column("Red Team ", style="red", justify="left")
    table.add_column("Blue Team ", style="cyan", justify="left")

    for aspect, values in comparison.items():
        table.add_row(
            aspect.replace("_", " ").title(),
            values["red"],
            values["blue"],
        )

    console.print(table)


def show_detailed_comparison() -> None:
    """Show detailed team information."""
    console.clear()
    console.print()

    red_team = TeamDatabase.get_team_info(TeamRole.RED)
    blue_team = TeamDatabase.get_team_info(TeamRole.BLUE)

    # Red Team Panel
    red_panel = Panel(
        f"[bold]{red_team.tagline}[/bold]\n\n"
        f"{red_team.description}\n\n"
        f"[yellow]Focus Areas:[/yellow]\n" +
        "\n".join(f"  - {area}" for area in red_team.focus_areas),
        title="[red bold] RED TEAM - Offensive Security[/red bold]",
        border_style="red",
    )

    # Blue Team Panel
    blue_panel = Panel(
        f"[bold]{blue_team.tagline}[/bold]\n\n"
        f"{blue_team.description}\n\n"
        f"[yellow]Focus Areas:[/yellow]\n" +
        "\n".join(f"  - {area}" for area in blue_team.focus_areas),
        title="[cyan bold] BLUE TEAM - Defensive Security[/cyan bold]",
        border_style="cyan",
    )

    console.print(red_panel)
    console.print()
    console.print(blue_panel)
    console.print()

    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_team_help() -> None:
    """Show team selection help."""
    console.clear()
    console.print()

    help_panel = Panel(
        "[bold cyan] Which Team Should You Choose?[/bold cyan]\n\n"
        "[yellow]Choose RED TEAM if you:[/yellow]\n"
        "  - Love offensive security and penetration testing\n"
        "  - Enjoy finding vulnerabilities and exploiting them\n"
        "  - Think creatively and like breaking things\n"
        "  - Want to learn hacking techniques\n"
        "  - Prefer aggressive, attack-focused gameplay\n\n"
        "[cyan]Choose BLUE TEAM if you:[/cyan]\n"
        "  - Love defensive security and system hardening\n"
        "  - Enjoy analyzing logs and detecting threats\n"
        "  - Think analytically and like solving puzzles\n"
        "  - Want to learn incident response\n"
        "  - Prefer strategic, defense-focused gameplay\n\n"
        "[green]Both teams are equally challenging and rewarding![/green]\n"
        "The choice comes down to personal playstyle preference.",
        title="[bold magenta] Team Selection Guide[/bold magenta]",
        border_style="magenta",
    )

    console.print(help_panel)
    console.print()

    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def show_starter_missions(team_role: TeamRole) -> None:
    """Show starter missions for selected team."""
    missions = MissionLibrary.get_starter_missions(team_role)

    if not missions:
        return

    table = Table(
        title=f" Your First Missions",
        show_header=True,
        header_style="bold green"
    )
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Mission", style="yellow")
    table.add_column("Difficulty", style="magenta", justify="center")
    table.add_column("Rewards", style="green", justify="right")

    for mission in missions[:3]:  # Show first 3
        rewards_str = f"{mission.rewards['xp']} XP, ₡{mission.rewards['currency']}"
        table.add_row(
            mission.mission_id.split("_")[-1],
            mission.title,
            mission.difficulty.upper(),
            rewards_str,
        )

    console.print(table)
    console.print()
    print_info(console, "Use 'nighthawk game missions' to view all available missions")


@game_app.command("dashboard")
def show_game_dashboard() -> None:
    """ Show your game progress dashboard."""
    engine = get_game_engine()

    if not engine.is_initialized:
        print_error(console, "No game in progress! Use 'nighthawk game start' first.")
        return

    state = engine.get_game_state()
    profile = engine.player.get_profile()

    console.clear()
    console.print()

    # Header
    team_icon = "" if profile.team.value == "red" else ""
    team_color = "red" if profile.team.value == "red" else "cyan"

    console.print(Panel.fit(
        f"[{team_color} bold]{team_icon} {profile.username} - {profile.get_rank_title()} {team_icon}[/{team_color} bold]\n"
        f"[white]Level {profile.level} {profile.team.value.upper()} Team Operative[/white]",
        border_style=team_color,
        title="[bold] OPERATIVE DASHBOARD[/bold]",
    ))
    console.print()

    # Stats Grid
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column(style="cyan")
    stats_table.add_column(style="yellow bold")
    stats_table.add_column(style="cyan")
    stats_table.add_column(style="yellow bold")

    stats_table.add_row(
        " Balance:", f"₡{state['currency']['balance']:,}",
        "Total XP:", f"{state['player']['xp']:,}",
    )
    stats_table.add_row(
        " Next Level:", f"{state['player']['xp_to_next']:,} XP",
        " Missions:", f"{profile.stats.missions_completed}",
    )
    stats_table.add_row(
        " Achievements:", f"{len(profile.achievements)}",
        "Playtime:", f"{profile.stats.playtime_minutes} min",
    )

    console.print(stats_table)
    console.print()

    # Reputation
    if engine.reputation:
        rep_summary = engine.reputation.get_reputation_summary()

        rep_table = Table(title=" Reputation", show_header=True, header_style="bold magenta")
        rep_table.add_column("Faction", style="cyan")
        rep_table.add_column("Level", style="yellow", justify="center")
        rep_table.add_column("Progress", style="green")

        for faction, data in rep_summary["factions"].items():
            progress_bar = "█" * int(data["progress"] * 20)
            rep_table.add_row(
                faction.title(),
                f"{data['reputation']}/1000",
                f"[green]{progress_bar}[/green] {data['tier'].title()}",
            )

        console.print(rep_table)

    console.print()
    print_info(console, "Use 'nighthawk game missions' to start your next mission!")


@game_app.command("missions")
def show_missions() -> None:
    """ View available missions."""
    engine = get_game_engine()

    if not engine.is_initialized:
        print_error(console, "No game in progress! Use 'nighthawk game start' first.")
        return

    if not engine.player.is_team_selected():
        print_warning(console, "Select a team first! Use 'nighthawk game select-team'")
        return

    profile = engine.player.get_profile()
    team_role = TeamRole(profile.team.value)
    missions = MissionLibrary.get_missions_for_team(team_role, profile.level)

    console.clear()
    console.print()

    team_color = "red" if team_role == TeamRole.RED else "cyan"
    console.print(Panel.fit(
        f"[{team_color} bold]Available Missions for Level {profile.level}[/{team_color} bold]",
        border_style=team_color,
        title=" MISSION BOARD",
    ))
    console.print()

    if not missions:
        print_warning(console, "No missions available at your level yet!")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", justify="center", width=12)
    table.add_column("Title", style="yellow", width=30)
    table.add_column("Difficulty", justify="center", width=10)
    table.add_column("Category", style="magenta", width=15)
    table.add_column("Duration", justify="center", width=10)
    table.add_column("Rewards", style="green", justify="right", width=20)

    for mission in missions:
        # Color code difficulty
        diff_color = {
            "easy": "green",
            "medium": "yellow",
            "hard": "red",
            "expert": "magenta",
            "legendary": "bold red",
        }.get(mission.difficulty, "white")

        rewards = f"{mission.rewards['xp']} XP\n₡{mission.rewards['currency']}"

        table.add_row(
            mission.mission_id,
            mission.title,
            f"[{diff_color}]{mission.difficulty.upper()}[/{diff_color}]",
            mission.category.replace("_", " ").title(),
            f"{mission.duration_minutes}m",
            rewards,
        )

    console.print(table)
    console.print()
    print_info(console, "Use 'nighthawk game start-mission <id>' to begin a mission")


@game_app.command("save")
def save_game_command(
    slot: int = typer.Option(1, "--slot", "-s", help="Save slot (1-3)")
) -> None:
    """ Save your game progress."""
    engine = get_game_engine()

    if not engine.is_initialized:
        print_error(console, "No game in progress!")
        return

    success = engine.save_game(slot)

    if success:
        print_success(console, f" Game saved to slot {slot}")
    else:
        print_error(console, "Failed to save game!")


@game_app.command("stats")
def show_stats() -> None:
    """ View detailed statistics."""
    engine = get_game_engine()

    if not engine.is_initialized:
        print_error(console, "No game in progress!")
        return

    profile = engine.player.get_profile()
    stats = profile.stats

    console.clear()
    console.print()

    console.print(Panel.fit(
        f"[bold cyan]Detailed Statistics for {profile.username}[/bold cyan]",
        border_style="cyan",
        title=" STATISTICS",
    ))
    console.print()

    # Combat Stats
    combat_table = Table(title=" Combat Statistics", show_header=False)
    combat_table.add_column(style="cyan", width=30)
    combat_table.add_column(style="yellow bold", justify="right")

    if profile.team.value == "red":
        combat_table.add_row("Systems Compromised:", str(stats.systems_compromised))
        combat_table.add_row("Total Damage Dealt:", str(stats.total_damage_dealt))
        combat_table.add_row("Secrets Found:", str(stats.secrets_found))
        combat_table.add_row("Vulnerabilities Discovered:", str(stats.vulnerabilities_discovered))
    else:
        combat_table.add_row("Attacks Blocked:", str(stats.attacks_blocked))
        combat_table.add_row("Total Damage Prevented:", str(stats.total_damage_prevented))
        combat_table.add_row("Threats Detected:", str(stats.secrets_found))
        combat_table.add_row("Incidents Resolved:", str(stats.vulnerabilities_discovered))

    console.print(combat_table)
    console.print()

    # Mission Stats
    mission_table = Table(title=" Mission Statistics", show_header=False)
    mission_table.add_column(style="cyan", width=30)
    mission_table.add_column(style="yellow bold", justify="right")

    mission_table.add_row("Missions Completed:", str(stats.missions_completed))
    mission_table.add_row("Missions Failed:", str(stats.missions_failed))
    mission_table.add_row("Bounties Completed:", str(stats.bounties_completed))

    success_rate = (stats.missions_completed / (stats.missions_completed + stats.missions_failed) * 100) if (stats.missions_completed + stats.missions_failed) > 0 else 0
    mission_table.add_row("Success Rate:", f"{success_rate:.1f}%")

    console.print(mission_table)
    console.print()

    # CTF Stats
    ctf_table = Table(title=" CTF Statistics", show_header=False)
    ctf_table.add_column(style="cyan", width=30)
    ctf_table.add_column(style="yellow bold", justify="right")

    ctf_table.add_row("CTF Wins:", str(stats.ctf_wins))
    ctf_table.add_row("CTF Losses:", str(stats.ctf_losses))

    win_rate = (stats.ctf_wins / (stats.ctf_wins + stats.ctf_losses) * 100) if (stats.ctf_wins + stats.ctf_losses) > 0 else 0
    ctf_table.add_row("Win Rate:", f"{win_rate:.1f}%")

    console.print(ctf_table)


if __name__ == "__main__":
    game_app()
