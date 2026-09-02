"""Player profile and management system."""

import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class Team(str, Enum):
    """Player team selection."""
    RED = "red"  # Offensive Security
    BLUE = "blue"  # Defensive Security
    NEUTRAL = "neutral"  # Not yet selected


@dataclass
class PlayerStats:
    """Player statistics tracking."""
    missions_completed: int = 0
    missions_failed: int = 0
    bounties_completed: int = 0
    ctf_wins: int = 0
    ctf_losses: int = 0
    systems_compromised: int = 0
    attacks_blocked: int = 0
    secrets_found: int = 0
    vulnerabilities_discovered: int = 0
    total_damage_dealt: int = 0
    total_damage_prevented: int = 0
    playtime_minutes: int = 0
    login_streak_days: int = 0
    achievements_unlocked: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerStats":
        """Create stats from dictionary."""
        return cls(**data)


@dataclass
class PlayerInventory:
    """Player inventory management."""
    items: Dict[str, int] = field(default_factory=dict)  # item_id: quantity
    tools: List[str] = field(default_factory=list)  # unlocked tools
    exploits: List[str] = field(default_factory=list)  # unlocked exploits
    
    def add_item(self, item_id: str, quantity: int = 1) -> None:
        """Add item to inventory."""
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        if item_id not in self.items:
            return False
        
        if self.items[item_id] < quantity:
            return False
        
        self.items[item_id] -= quantity
        if self.items[item_id] == 0:
            del self.items[item_id]
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if player has item."""
        return self.items.get(item_id, 0) >= quantity
    
    def unlock_tool(self, tool_id: str) -> bool:
        """Unlock a tool. Returns True if newly unlocked."""
        if tool_id not in self.tools:
            self.tools.append(tool_id)
            return True
        return False
    
    def unlock_exploit(self, exploit_id: str) -> bool:
        """Unlock an exploit. Returns True if newly unlocked."""
        if exploit_id not in self.exploits:
            self.exploits.append(exploit_id)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerInventory":
        """Create inventory from dictionary."""
        return cls(**data)


@dataclass
class PlayerProfile:
    """Complete player profile."""
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = "Anonymous"
    team: Team = Team.NEUTRAL
    level: int = 1
    xp: int = 0
    currency: int = 0  # CryptoCreds
    
    # Reputation (0-1000 each)
    reputation_underground: int = 0
    reputation_corporate: int = 0
    reputation_government: int = 0
    reputation_blackmarket: int = 0
    
    # Skills (0-10 levels each)
    skills: Dict[str, int] = field(default_factory=dict)
    
    # Collections
    achievements: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)
    active_missions: List[str] = field(default_factory=list)
    
    # Stats
    stats: PlayerStats = field(default_factory=PlayerStats)
    inventory: PlayerInventory = field(default_factory=PlayerInventory)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_save: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Settings
    tutorial_completed: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default skills if not set."""
        if not self.skills:
            self.skills = self._get_default_skills()
    
    def _get_default_skills(self) -> Dict[str, int]:
        """Get default skill levels based on team."""
        if self.team == Team.RED:
            return {
                "exploitation": 1,
                "stealth": 1,
                "social_engineering": 0,
                "post_exploitation": 0,
            }
        elif self.team == Team.BLUE:
            return {
                "detection": 1,
                "response": 1,
                "forensics": 0,
                "hardening": 0,
            }
        else:
            return {}
    
    def select_team(self, team: Team) -> None:
        """Select player team (can only be done once)."""
        if self.team == Team.NEUTRAL:
            self.team = team
            self.skills = self._get_default_skills()
    
    def add_xp(self, amount: int) -> int:
        """Add XP and return new level if leveled up, else 0."""
        old_level = self.level
        self.xp += amount
        
        # Calculate new level
        new_level = self._calculate_level(self.xp)
        
        if new_level > old_level:
            self.level = new_level
            return new_level
        
        return 0
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        # Level thresholds (exponential growth)
        if xp < 1000:
            return 1
        elif xp < 10000:
            return min(10, int((xp / 1000) ** 0.8) + 1)
        elif xp < 50000:
            return min(20, int((xp / 5000) ** 0.75) + 10)
        elif xp < 150000:
            return min(30, int((xp / 10000) ** 0.7) + 20)
        elif xp < 350000:
            return min(40, int((xp / 20000) ** 0.65) + 30)
        elif xp < 750000:
            return min(50, int((xp / 40000) ** 0.6) + 40)
        elif xp < 2000000:
            return min(75, int((xp / 80000) ** 0.55) + 50)
        else:
            return min(99, int((xp / 200000) ** 0.5) + 75)
    
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level."""
        # Estimate based on current level
        if self.level < 10:
            next_xp = ((self.level + 1) - 1) ** 1.25 * 1000
        elif self.level < 20:
            next_xp = ((self.level + 1) - 10) ** 1.33 * 5000
        elif self.level < 30:
            next_xp = ((self.level + 1) - 20) ** 1.43 * 10000
        elif self.level < 40:
            next_xp = ((self.level + 1) - 30) ** 1.54 * 20000
        elif self.level < 50:
            next_xp = ((self.level + 1) - 40) ** 1.67 * 40000
        elif self.level < 75:
            next_xp = ((self.level + 1) - 50) ** 1.82 * 80000
        else:
            next_xp = ((self.level + 1) - 75) ** 2.0 * 200000
        
        return max(0, int(next_xp - self.xp))
    
    def add_currency(self, amount: int) -> None:
        """Add CryptoCreds."""
        self.currency += amount
    
    def spend_currency(self, amount: int) -> bool:
        """Spend CryptoCreds. Returns True if successful."""
        if self.currency >= amount:
            self.currency -= amount
            return True
        return False
    
    def add_reputation(self, rep_type: str, amount: int) -> None:
        """Add reputation (capped at 1000)."""
        if rep_type == "underground":
            self.reputation_underground = min(1000, self.reputation_underground + amount)
        elif rep_type == "corporate":
            self.reputation_corporate = min(1000, self.reputation_corporate + amount)
        elif rep_type == "government":
            self.reputation_government = min(1000, self.reputation_government + amount)
        elif rep_type == "blackmarket":
            self.reputation_blackmarket = min(1000, self.reputation_blackmarket + amount)
    
    def upgrade_skill(self, skill_name: str) -> bool:
        """Upgrade skill level. Returns True if successful."""
        if skill_name not in self.skills:
            return False
        
        if self.skills[skill_name] >= 10:
            return False  # Max level
        
        self.skills[skill_name] += 1
        return True
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock achievement. Returns True if newly unlocked."""
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            self.stats.achievements_unlocked += 1
            return True
        return False
    
    def start_mission(self, mission_id: str) -> None:
        """Start a mission."""
        if mission_id not in self.active_missions:
            self.active_missions.append(mission_id)
    
    def complete_mission(self, mission_id: str, success: bool = True) -> None:
        """Complete a mission."""
        if mission_id in self.active_missions:
            self.active_missions.remove(mission_id)
        
        if success:
            if mission_id not in self.completed_missions:
                self.completed_missions.append(mission_id)
            self.stats.missions_completed += 1
        else:
            self.stats.missions_failed += 1
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow().isoformat()
    
    def update_last_save(self) -> None:
        """Update last save timestamp."""
        self.last_save = datetime.utcnow().isoformat()
    
    def get_rank_title(self) -> str:
        """Get player rank title based on level."""
        if self.level < 10:
            return "Script Kiddie"
        elif self.level < 20:
            return "Security Analyst"
        elif self.level < 30:
            return "Penetration Tester"
        elif self.level < 40:
            return "Security Engineer"
        elif self.level < 50:
            return "Elite Hacker"
        elif self.level < 75:
            return "Security Architect"
        else:
            return "Legendary Ghost"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        data = asdict(self)
        data["team"] = self.team.value
        return data
    
    def to_json(self) -> str:
        """Convert profile to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerProfile":
        """Create profile from dictionary."""
        # Convert nested objects
        if "stats" in data and isinstance(data["stats"], dict):
            data["stats"] = PlayerStats.from_dict(data["stats"])
        
        if "inventory" in data and isinstance(data["inventory"], dict):
            data["inventory"] = PlayerInventory.from_dict(data["inventory"])
        
        if "team" in data and isinstance(data["team"], str):
            data["team"] = Team(data["team"])
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "PlayerProfile":
        """Create profile from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class Player:
    """Player controller class."""
    
    def __init__(self, profile: Optional[PlayerProfile] = None):
        """Initialize player with profile."""
        self.profile = profile or PlayerProfile()
    
    def create_new_profile(self, username: str) -> None:
        """Create a new player profile."""
        self.profile = PlayerProfile(username=username)
    
    def load_profile(self, profile: PlayerProfile) -> None:
        """Load existing profile."""
        self.profile = profile
        self.profile.update_last_login()
    
    def get_profile(self) -> PlayerProfile:
        """Get current profile."""
        return self.profile
    
    def is_team_selected(self) -> bool:
        """Check if team has been selected."""
        return self.profile.team != Team.NEUTRAL
    
    def can_afford(self, cost: int) -> bool:
        """Check if player can afford something."""
        return self.profile.currency >= cost
    
    def has_level_requirement(self, required_level: int) -> bool:
        """Check if player meets level requirement."""
        return self.profile.level >= required_level
    
    def has_reputation_requirement(self, rep_type: str, required_amount: int) -> bool:
        """Check if player meets reputation requirement."""
        rep_map = {
            "underground": self.profile.reputation_underground,
            "corporate": self.profile.reputation_corporate,
            "government": self.profile.reputation_government,
            "blackmarket": self.profile.reputation_blackmarket,
        }
        return rep_map.get(rep_type, 0) >= required_amount
    
    def get_total_reputation(self) -> int:
        """Get total reputation across all types."""
        return (
            self.profile.reputation_underground +
            self.profile.reputation_corporate +
            self.profile.reputation_government +
            self.profile.reputation_blackmarket
        )
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get summary of player profile."""
        return {
            "username": self.profile.username,
            "team": self.profile.team.value,
            "level": self.profile.level,
            "rank": self.profile.get_rank_title(),
            "xp": self.profile.xp,
            "xp_to_next": self.profile.xp_to_next_level(),
            "currency": self.profile.currency,
            "total_reputation": self.get_total_reputation(),
            "missions_completed": self.profile.stats.missions_completed,
            "achievements": len(self.profile.achievements),
        }
