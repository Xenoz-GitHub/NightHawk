"""Bounty board UI for terminal display."""

from typing import List, Optional
from datetime import datetime, timedelta

from nighthawk.game.bounty import (
    BountyMission, BountyBoard, MissionDifficulty, MissionStatus, 
    ClientType, ClientReputation
)


class BountyBoardUI:
    """Terminal UI for bounty board display."""
    
    # Color codes for terminal
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    
    # Difficulty colors
    DIFFICULTY_COLORS = {
        MissionDifficulty.EASY: COLORS["green"],
        MissionDifficulty.MEDIUM: COLORS["yellow"],
        MissionDifficulty.HARD: COLORS["red"],
        MissionDifficulty.EXPERT: COLORS["magenta"],
        MissionDifficulty.LEGENDARY: COLORS["cyan"],
    }
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")
    
    @staticmethod
    def print_header(title: str):
        """Print colored header."""
        print(f"\n{BountyBoardUI.COLORS['bold']}{BountyBoardUI.COLORS['cyan']}")
        print("=" * 80)
        print(f"  {title}")
        print("=" * 80)
        print(BountyBoardUI.COLORS['reset'])
    
    @staticmethod
    def print_mission_list(missions: List[BountyMission], show_numbers: bool = True):
        """
        Print a formatted list of missions.
        
        Args:
            missions: List of missions to display
            show_numbers: Show mission numbers
        """
        if not missions:
            print(f"{BountyBoardUI.COLORS['dim']}No missions available.{BountyBoardUI.COLORS['reset']}")
            return
        
        print()
        for i, mission in enumerate(missions, 1):
            BountyBoardUI.print_mission_summary(mission, show_number=show_numbers, number=i)
            print()
    
    @staticmethod
    def print_mission_summary(mission: BountyMission, show_number: bool = False, number: int = 0):
        """
        Print a mission summary in compact form.
        
        Args:
            mission: Mission to display
            show_number: Show mission number
            number: Mission number to display
        """
        # Mission header with difficulty
        diff_color = BountyBoardUI.DIFFICULTY_COLORS.get(mission.difficulty, BountyBoardUI.COLORS["reset"])
        number_str = f"[{number:2d}] " if show_number else ""
        
        print(f"{number_str}{diff_color}{mission.difficulty.value.upper():10}{BountyBoardUI.COLORS['reset']} "
              f"{mission.title}")
        
        # Client info
        print(f"     {BountyBoardUI.COLORS['dim']}Client: {mission.client.name} "
              f"({mission.client.client_type.value}){BountyBoardUI.COLORS['reset']}")
        
        # Brief description
        print(f"     {mission.description}")
        
        # Requirements and rewards
        print(f"     {BountyBoardUI.COLORS['blue']}Required Level: {mission.required_level}"
              f"{BountyBoardUI.COLORS['reset']} | "
              f"{BountyBoardUI.COLORS['green']}Reward: ₡{mission.base_reward:,} + {mission.xp_reward} XP"
              f"{BountyBoardUI.COLORS['reset']}")
        
        # Time limit
        time_remaining = mission.time_remaining()
        if time_remaining:
            hours = int(time_remaining.total_seconds() / 3600)
            print(f"     {BountyBoardUI.COLORS['yellow']}Time Remaining: {hours}h{BountyBoardUI.COLORS['reset']} | "
                  f"Status: {mission.status.value}")
        else:
            print(f"     {BountyBoardUI.COLORS['red']}EXPIRED{BountyBoardUI.COLORS['reset']}")
    
    @staticmethod
    def print_mission_detail(mission: BountyMission):
        """
        Print detailed mission information.
        
        Args:
            mission: Mission to display in detail
        """
        BountyBoardUI.print_header(f"MISSION DETAILS: {mission.title}")
        
        # Client information
        print(f"\n{BountyBoardUI.COLORS['bold']}CLIENT INFORMATION{BountyBoardUI.COLORS['reset']}")
        print(f"  Name: {mission.client.name}")
        print(f"  Type: {mission.client.client_type.value}")
        print(f"  Contact: {mission.client.contact_method}")
        print(f"  Reputation: {mission.client.reputation_tier.value}")
        print(f"  Track Record: {mission.client.successful_completion_rate * 100:.1f}% success rate")
        
        # Mission details
        print(f"\n{BountyBoardUI.COLORS['bold']}MISSION DETAILS{BountyBoardUI.COLORS['reset']}")
        diff_color = BountyBoardUI.DIFFICULTY_COLORS.get(mission.difficulty, BountyBoardUI.COLORS["reset"])
        print(f"  Difficulty: {diff_color}{mission.difficulty.value.upper()}{BountyBoardUI.COLORS['reset']}")
        print(f"  Status: {mission.status.value}")
        print(f"  Required Level: {mission.required_level}")
        
        # Brief
        print(f"\n{BountyBoardUI.COLORS['bold']}BRIEF{BountyBoardUI.COLORS['reset']}")
        print(f"  {mission.detailed_brief}")
        
        # Objectives
        print(f"\n{BountyBoardUI.COLORS['bold']}OBJECTIVES{BountyBoardUI.COLORS['reset']}")
        for i, obj in enumerate(mission.objectives, 1):
            print(f"  {i}. {obj}")
        
        # Target info
        print(f"\n{BountyBoardUI.COLORS['bold']}TARGET INFORMATION{BountyBoardUI.COLORS['reset']}")
        for key, value in mission.target_info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Constraints
        if mission.constraints:
            print(f"\n{BountyBoardUI.COLORS['bold']}CONSTRAINTS{BountyBoardUI.COLORS['reset']}")
            for constraint in mission.constraints:
                print(f"  - {constraint}")
        
        # Rewards
        print(f"\n{BountyBoardUI.COLORS['bold']}REWARDS{BountyBoardUI.COLORS['reset']}")
        print(f"  {BountyBoardUI.COLORS['green']}Base Reward: ₡{mission.base_reward:,}{BountyBoardUI.COLORS['reset']}")
        print(f"  {BountyBoardUI.COLORS['green']}Bonus (Quick Completion): ₡{mission.bonus_reward:,}{BountyBoardUI.COLORS['reset']}")
        print(f"  {BountyBoardUI.COLORS['blue']}XP Reward: {mission.xp_reward}{BountyBoardUI.COLORS['reset']}")
        print(f"  {BountyBoardUI.COLORS['magenta']}Reputation: +{mission.reputation_reward}{BountyBoardUI.COLORS['reset']}")
        
        # Time limit
        print(f"\n{BountyBoardUI.COLORS['bold']}TIME LIMIT{BountyBoardUI.COLORS['reset']}")
        print(f"  Total: {mission.time_limit_hours} hours")
        time_remaining = mission.time_remaining()
        if time_remaining:
            hours = int(time_remaining.total_seconds() / 3600)
            minutes = int((time_remaining.total_seconds() % 3600) / 60)
            print(f"  {BountyBoardUI.COLORS['yellow']}Remaining: {hours}h {minutes}m{BountyBoardUI.COLORS['reset']}")
        else:
            print(f"  {BountyBoardUI.COLORS['red']}EXPIRED{BountyBoardUI.COLORS['reset']}")
        
        # Available tools
        print(f"\n{BountyBoardUI.COLORS['bold']}AVAILABLE TOOLS{BountyBoardUI.COLORS['reset']}")
        for tool in mission.tools_available:
            print(f"  - {tool}")
        
        print()
    
    @staticmethod
    def print_bounty_board(board: BountyBoard, player_level: int = 1):
        """
        Print the main bounty board.
        
        Args:
            board: BountyBoard instance
            player_level: Player's current level
        """
        BountyBoardUI.print_header("NIGHTHAWK BOUNTY BOARD")
        
        # Board statistics
        stats = board.get_mission_stats()
        print(f"\n{BountyBoardUI.COLORS['cyan']}Available: {stats['available_missions']} | "
              f"Active: {stats['active_missions']} | "
              f"Completed: {stats['completed_missions']} | "
              f"Clients: {stats['total_clients']}{BountyBoardUI.COLORS['reset']}\n")
        
        # Display available missions
        available_missions = board.get_available_missions(player_level)
        
        if available_missions:
            print(f"{BountyBoardUI.COLORS['bold']}AVAILABLE MISSIONS ({len(available_missions)}):"
                  f"{BountyBoardUI.COLORS['reset']}\n")
            BountyBoardUI.print_mission_list(available_missions, show_numbers=True)
        else:
            print(f"{BountyBoardUI.COLORS['dim']}No missions available at your level.{BountyBoardUI.COLORS['reset']}\n")
    
    @staticmethod
    def print_active_missions(missions: List[BountyMission]):
        """
        Print player's active missions.
        
        Args:
            missions: List of active missions
        """
        BountyBoardUI.print_header("YOUR ACTIVE MISSIONS")
        
        if not missions:
            print(f"{BountyBoardUI.COLORS['dim']}No active missions.{BountyBoardUI.COLORS['reset']}\n")
            return
        
        print(f"\n{BountyBoardUI.COLORS['bold']}You have {len(missions)} active mission(s):{BountyBoardUI.COLORS['reset']}\n")
        BountyBoardUI.print_mission_list(missions, show_numbers=True)
    
    @staticmethod
    def print_mission_accepted(mission: BountyMission):
        """
        Print mission acceptance confirmation.
        
        Args:
            mission: Accepted mission
        """
        print(f"\n{BountyBoardUI.COLORS['green']}{BountyBoardUI.COLORS['bold']} MISSION ACCEPTED{BountyBoardUI.COLORS['reset']}")
        print(f"{BountyBoardUI.COLORS['green']}Mission ID: {mission.mission_id}{BountyBoardUI.COLORS['reset']}\n")
    
    @staticmethod
    def print_mission_completed(mission: BountyMission, crypto_reward: int, xp_reward: int):
        """
        Print mission completion confirmation.
        
        Args:
            mission: Completed mission
            crypto_reward: Cryptocurrency reward earned
            xp_reward: XP reward earned
        """
        print(f"\n{BountyBoardUI.COLORS['green']}{BountyBoardUI.COLORS['bold']}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + f" MISSION COMPLETE: {mission.title}".ljust(79) + "║")
        print("║" + " " * 78 + "║")
        print("║" + f" Reward: {BountyBoardUI.COLORS['yellow']}₡{crypto_reward:,}{BountyBoardUI.COLORS['green']} + {BountyBoardUI.COLORS['cyan']}{xp_reward} XP{BountyBoardUI.COLORS['green']}".ljust(79) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(BountyBoardUI.COLORS['reset'])
    
    @staticmethod
    def print_client_reputation(client_name: str, reputation_tier: str, change: int):
        """
        Print client reputation change.
        
        Args:
            client_name: Name of the client
            reputation_tier: New reputation tier
            change: Reputation change amount
        """
        symbol = "up" if change > 0 else "down"
        color = BountyBoardUI.COLORS['green'] if change > 0 else BountyBoardUI.COLORS['red']
        
        print(f"\n{color}{symbol} {client_name} Reputation: {reputation_tier.upper()}{BountyBoardUI.COLORS['reset']}")
