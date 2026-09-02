"""Main game engine coordinating all systems."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime, timedelta

from nighthawk.game.player import Player, PlayerProfile, Team
from nighthawk.game.currency import CryptoCreds, TransactionCategory
from nighthawk.game.progression import XPSystem, LevelSystem, SkillTree
from nighthawk.game.reputation import ReputationSystem, ReputationType


class GameEngine:
    """Main game engine managing all game systems."""
    
    VERSION = "1.0.0"
    SAVE_DIR = Path.home() / ".nighthawk" / "saves"
    
    def __init__(self):
        """Initialize game engine."""
        self.player: Optional[Player] = None
        self.currency: Optional[CryptoCreds] = None
        self.xp_system = XPSystem()
        self.reputation: Optional[ReputationSystem] = None
        self.skill_tree: Optional[SkillTree] = None
        
        self.is_initialized = False
        self.current_save_slot = 1
        
        # Ensure save directory exists
        self.SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    def initialize_new_game(self, username: str) -> bool:
        """
        Initialize a new game.
        
        Args:
            username: Player username
        
        Returns:
            True if successful
        """
        try:
            # Create new player profile
            self.player = Player()
            self.player.create_new_profile(username)
            
            # Initialize systems
            self.currency = CryptoCreds()
            self.reputation = ReputationSystem()
            
            # Note: skill_tree will be initialized after team selection
            self.skill_tree = None
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing new game: {e}")
            return False
    
    def load_game(self, slot: int = 1) -> bool:
        """
        Load game from save slot.
        
        Args:
            slot: Save slot number (1-3)
        
        Returns:
            True if successful
        """
        save_file = self.SAVE_DIR / f"save_slot_{slot}.json"
        
        if not save_file.exists():
            return False
        
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load player profile
            profile = PlayerProfile.from_dict(data["player"])
            self.player = Player(profile)
            self.player.get_profile().update_last_login()
            
            # Load currency
            self.currency = CryptoCreds.from_dict(data["currency"])
            
            # Load reputation
            self.reputation = ReputationSystem.from_dict(data["reputation"])
            
            # Load skill tree
            if "skill_tree" in data and self.player.is_team_selected():
                self.skill_tree = SkillTree.from_dict(data["skill_tree"])
            
            self.current_save_slot = slot
            self.is_initialized = True
            
            # Check for daily bonus
            self._check_daily_bonus()
            
            return True
        
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def save_game(self, slot: Optional[int] = None) -> bool:
        """
        Save game to slot.
        
        Args:
            slot: Save slot number (1-3), uses current slot if None
        
        Returns:
            True if successful
        """
        if not self.is_initialized or not self.player:
            return False
        
        slot = slot or self.current_save_slot
        save_file = self.SAVE_DIR / f"save_slot_{slot}.json"
        
        try:
            # Update last save timestamp
            self.player.get_profile().update_last_save()
            
            # Prepare save data
            save_data = {
                "version": self.VERSION,
                "player": self.player.get_profile().to_dict(),
                "currency": self.currency.to_dict() if self.currency else {},
                "reputation": self.reputation.to_dict() if self.reputation else {},
                "skill_tree": self.skill_tree.to_dict() if self.skill_tree else {},
                "saved_at": datetime.utcnow().isoformat(),
            }
            
            # Write to file
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            
            self.current_save_slot = slot
            return True
        
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def auto_save(self) -> bool:
        """Auto-save to current slot."""
        return self.save_game()
    
    def get_save_slots(self) -> Dict[int, Optional[Dict[str, Any]]]:
        """
        Get information about all save slots.
        
        Returns:
            Dict mapping slot numbers to save info (None if empty)
        """
        slots = {}
        
        for slot in [1, 2, 3]:
            save_file = self.SAVE_DIR / f"save_slot_{slot}.json"
            
            if save_file.exists():
                try:
                    with open(save_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    player_data = data.get("player", {})
                    slots[slot] = {
                        "username": player_data.get("username", "Unknown"),
                        "team": player_data.get("team", "neutral"),
                        "level": player_data.get("level", 1),
                        "saved_at": data.get("saved_at", "Unknown"),
                    }
                except:
                    slots[slot] = None
            else:
                slots[slot] = None
        
        return slots
    
    def delete_save(self, slot: int) -> bool:
        """Delete save slot."""
        save_file = self.SAVE_DIR / f"save_slot_{slot}.json"
        
        try:
            if save_file.exists():
                save_file.unlink()
            return True
        except:
            return False
    
    def select_team(self, team: str) -> bool:
        """
        Select player team (Red or Blue).
        
        Args:
            team: "red" or "blue"
        
        Returns:
            True if successful
        """
        if not self.player:
            return False
        
        if self.player.is_team_selected():
            return False  # Already selected
        
        # Validate team
        if team.lower() == "red":
            team_enum = Team.RED
        elif team.lower() == "blue":
            team_enum = Team.BLUE
        else:
            return False
        
        # Select team
        self.player.get_profile().select_team(team_enum)
        
        # Initialize skill tree for team
        self.skill_tree = SkillTree(team=team.lower())
        
        # Award initial skill point
        self.skill_tree.add_skill_points(1)
        
        # Award team selection bonus
        if self.currency:
            self.currency.add(
                amount=500,
                description=f"Team selection bonus ({team.upper()} Team)",
            )
        
        return True
    
    def award_xp(
        self,
        amount: int,
        source: str = "generic",
        show_notification: bool = True,
    ) -> Dict[str, Any]:
        """
        Award XP to player.
        
        Args:
            amount: XP amount
            source: XP source description
            show_notification: Whether to show level-up notification
        
        Returns:
            Dict with level_up info
        """
        if not self.player:
            return {"level_up": False}
        
        profile = self.player.get_profile()
        old_level = profile.level
        
        # Add XP
        new_level = profile.add_xp(amount)
        
        result = {
            "xp_gained": amount,
            "total_xp": profile.xp,
            "level_up": new_level > 0,
            "old_level": old_level,
            "new_level": profile.level if new_level > 0 else old_level,
        }
        
        # Handle level up
        if new_level > 0:
            levels_gained = new_level - old_level
            
            # Award skill points (1 per level)
            if self.skill_tree:
                self.skill_tree.add_skill_points(levels_gained)
                result["skill_points_gained"] = levels_gained
            
            # Award currency bonus (100 * new level)
            if self.currency:
                bonus = 100 * new_level
                self.currency.add(
                    amount=bonus,
                    description=f"Level up bonus (Level {new_level})",
                )
                result["currency_bonus"] = bonus
        
        return result
    
    def award_currency(
        self,
        amount: int,
        category: TransactionCategory = TransactionCategory.OTHER,
        description: str = "",
    ) -> bool:
        """Award currency to player."""
        if not self.currency:
            return False
        
        self.currency.add(amount=amount, category=category, description=description)
        return True
    
    def spend_currency(
        self,
        amount: int,
        category: TransactionCategory = TransactionCategory.OTHER,
        description: str = "",
    ) -> bool:
        """Spend player currency."""
        if not self.currency:
            return False
        
        transaction = self.currency.spend(
            amount=amount,
            category=category,
            description=description,
        )
        
        return transaction is not None
    
    def award_reputation(
        self,
        faction: str,
        amount: int,
        reason: str = "",
    ) -> bool:
        """Award reputation to faction."""
        if not self.reputation:
            return False
        
        try:
            faction_type = ReputationType(faction)
            self.reputation.add_reputation(faction_type, amount, reason)
            return True
        except:
            return False
    
    def upgrade_skill(self, skill_id: str) -> Dict[str, Any]:
        """
        Upgrade a skill.
        
        Returns:
            Dict with success status and info
        """
        if not self.skill_tree:
            return {"success": False, "error": "Skill tree not initialized"}
        
        if not self.player:
            return {"success": False, "error": "Player not initialized"}
        
        # Attempt upgrade
        success = self.skill_tree.upgrade_skill(skill_id)
        
        if success:
            skill = self.skill_tree.get_skill(skill_id)
            return {
                "success": True,
                "skill_id": skill_id,
                "new_level": skill.current_level if skill else 0,
                "remaining_points": self.skill_tree.skill_points,
            }
        else:
            return {
                "success": False,
                "error": "Cannot upgrade skill (check requirements)",
            }
    
    def unlock_achievement(self, achievement_id: str) -> Dict[str, Any]:
        """
        Unlock an achievement.
        
        Returns:
            Dict with success status and rewards
        """
        if not self.player:
            return {"success": False}
        
        profile = self.player.get_profile()
        
        # Check if already unlocked
        if achievement_id in profile.achievements:
            return {"success": False, "already_unlocked": True}
        
        # Unlock achievement
        success = profile.unlock_achievement(achievement_id)
        
        if success:
            # Award XP and currency (example amounts)
            xp_reward = 100
            currency_reward = 500
            
            self.award_xp(xp_reward, f"Achievement: {achievement_id}")
            if self.currency:
                self.currency.reward_achievement("common")
            
            return {
                "success": True,
                "achievement_id": achievement_id,
                "xp_reward": xp_reward,
                "currency_reward": currency_reward,
            }
        
        return {"success": False}
    
    def _check_daily_bonus(self) -> None:
        """Check and award daily login bonus."""
        if not self.player or not self.currency:
            return
        
        profile = self.player.get_profile()
        
        try:
            last_login = datetime.fromisoformat(profile.last_login)
            now = datetime.utcnow()
            
            # Check if more than 24 hours since last login
            if (now - last_login) >= timedelta(hours=24):
                # Award daily bonus
                streak = profile.stats.login_streak_days
                self.currency.daily_bonus(streak)
                
                # Update streak
                if (now - last_login) < timedelta(hours=48):
                    profile.stats.login_streak_days += 1
                else:
                    profile.stats.login_streak_days = 1
        except:
            pass
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state summary."""
        if not self.is_initialized or not self.player:
            return {"initialized": False}
        
        profile = self.player.get_profile()
        
        return {
            "initialized": True,
            "player": {
                "username": profile.username,
                "team": profile.team.value,
                "level": profile.level,
                "rank": profile.get_rank_title(),
                "xp": profile.xp,
                "xp_to_next": profile.xp_to_next_level(),
            },
            "currency": {
                "balance": self.currency.get_balance() if self.currency else 0,
                "formatted": self.currency.format_amount(self.currency.get_balance()) if self.currency else "₡0",
            },
            "reputation": self.reputation.get_reputation_summary() if self.reputation else {},
            "skills": self.skill_tree.get_skill_summary() if self.skill_tree else {},
            "stats": profile.stats.to_dict(),
        }
    
    def get_player_summary(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive player summary."""
        if not self.player:
            return None
        
        return self.player.get_profile_summary()
