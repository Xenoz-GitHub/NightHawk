"""Bounty system for NIGHTHAWK game."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid


class ClientType(str, Enum):
    """Anonymous client types for bounty missions."""
    SHADOW_BROKER = "shadow_broker"
    CORPORATE_GUARDIAN = "corporate_guardian"
    GRAY_HAT_COLLECTIVE = "grayhat_collective"
    DARK_NET_TRADER = "darknet_trader"
    WHITE_KNIGHT_SEC = "whiteknight_sec"


class MissionDifficulty(str, Enum):
    """Mission difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    LEGENDARY = "legendary"


class MissionStatus(str, Enum):
    """Mission status states."""
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ClientReputation(str, Enum):
    """Client reputation tiers."""
    UNKNOWN = "unknown"
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    SKILLED = "skilled"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class ClientProfile:
    """Profile of an anonymous bounty client."""
    client_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_type: ClientType = ClientType.SHADOW_BROKER
    name: str = ""
    description: str = ""
    reputation_tier: ClientReputation = ClientReputation.UNKNOWN
    total_missions_posted: int = 0
    successful_completion_rate: float = 0.0
    average_reward: int = 0
    specialization: str = ""
    contact_method: str = ""
    personality_trait: str = ""
    
    def __post_init__(self):
        """Initialize client profile with default values."""
        if not self.client_id or self.client_id == "":
            self.client_id = str(uuid.uuid4())


@dataclass
class BountyMission:
    """A bounty mission offered to the player."""
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client: ClientProfile = field(default_factory=ClientProfile)
    title: str = ""
    description: str = ""
    detailed_brief: str = ""
    difficulty: MissionDifficulty = MissionDifficulty.MEDIUM
    status: MissionStatus = MissionStatus.AVAILABLE
    required_level: int = 1
    required_skills: List[str] = field(default_factory=list)
    
    # Rewards
    base_reward: int = 1000  # Base CryptoCreds reward
    bonus_reward: int = 0     # Bonus if completed quickly/perfectly
    xp_reward: int = 100
    reputation_reward: int = 10
    
    # Time constraints
    time_limit_hours: int = 24
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Mission specifics
    objectives: List[str] = field(default_factory=list)
    target_info: Dict[str, str] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    tools_available: List[str] = field(default_factory=list)
    
    # Tracking
    acceptance_count: int = 0
    completion_count: int = 0
    failure_count: int = 0
    
    def __post_init__(self):
        """Initialize mission with default values."""
        if not self.mission_id or self.mission_id == "":
            self.mission_id = str(uuid.uuid4())
        if self.deadline is None:
            self.deadline = datetime.now() + timedelta(hours=self.time_limit_hours)
    
    def is_expired(self) -> bool:
        """Check if mission has expired."""
        return datetime.now() > self.deadline
    
    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining for mission."""
        if self.deadline:
            remaining = self.deadline - datetime.now()
            return remaining if remaining.total_seconds() > 0 else None
        return None
    
    def calculate_dynamic_reward(self, player_level: int) -> Tuple[int, int]:
        """
        Calculate reward based on player level and difficulty.
        
        Returns:
            Tuple of (crypto_reward, xp_reward)
        """
        level_multiplier = max(0.5, player_level / (self.required_level or 1))
        difficulty_multiplier = {
            MissionDifficulty.EASY: 0.5,
            MissionDifficulty.MEDIUM: 1.0,
            MissionDifficulty.HARD: 1.5,
            MissionDifficulty.EXPERT: 2.0,
            MissionDifficulty.LEGENDARY: 3.0,
        }.get(self.difficulty, 1.0)
        
        crypto_reward = int(self.base_reward * level_multiplier * difficulty_multiplier)
        xp = int(self.xp_reward * level_multiplier * difficulty_multiplier)
        
        return crypto_reward, xp


class BountyBoard:
    """Main bounty board managing all available missions."""
    
    def __init__(self, max_visible_missions: int = 20):
        """Initialize bounty board."""
        self.missions: Dict[str, BountyMission] = {}
        self.clients: Dict[str, ClientProfile] = {}
        self.player_accepted_missions: Dict[str, BountyMission] = {}
        self.player_completed_missions: List[str] = []
        self.max_visible_missions = max_visible_missions
        self._initialize_default_clients()
    
    def _initialize_default_clients(self):
        """Initialize default client profiles."""
        clients_data = [
            {
                "client_type": ClientType.SHADOW_BROKER,
                "name": "ShadowBroker",
                "description": "High-risk, high-reward missions from the dark underground",
                "specialization": "Zero-day Exploits",
                "contact_method": "Encrypted IRC",
                "personality_trait": "Ruthless",
            },
            {
                "client_type": ClientType.CORPORATE_GUARDIAN,
                "name": "CorporateGuardian",
                "description": "Legitimate corporate security contracts for penetration testing",
                "specialization": "Corporate Infiltration",
                "contact_method": "Secure Email",
                "personality_trait": "Professional",
            },
            {
                "client_type": ClientType.GRAY_HAT_COLLECTIVE,
                "name": "GrayHat_Collective",
                "description": "Ethical hacking contracts in gray areas",
                "specialization": "Vulnerability Disclosure",
                "contact_method": "Signal App",
                "personality_trait": "Pragmatic",
            },
            {
                "client_type": ClientType.DARK_NET_TRADER,
                "name": "DarkNet_Trader",
                "description": "Black market contracts with high risk and rewards",
                "specialization": "Data Exfiltration",
                "contact_method": "Tor Network",
                "personality_trait": "Aggressive",
            },
            {
                "client_type": ClientType.WHITE_KNIGHT_SEC,
                "name": "WhiteKnight_Sec",
                "description": "Defensive security contracts protecting against threats",
                "specialization": "Threat Defense",
                "contact_method": "Secure VPN",
                "personality_trait": "Protective",
            },
        ]
        
        for client_data in clients_data:
            client = ClientProfile(
                client_type=client_data["client_type"],
                name=client_data["name"],
                description=client_data["description"],
                specialization=client_data["specialization"],
                contact_method=client_data["contact_method"],
                personality_trait=client_data["personality_trait"],
                reputation_tier=ClientReputation.UNKNOWN,
            )
            self.clients[client.client_id] = client
    
    def get_client_by_type(self, client_type: ClientType) -> Optional[ClientProfile]:
        """Get a client profile by type."""
        for client in self.clients.values():
            if client.client_type == client_type:
                return client
        return None
    
    def post_mission(self, mission: BountyMission) -> str:
        """
        Post a new mission to the board.
        
        Returns:
            Mission ID
        """
        self.missions[mission.mission_id] = mission
        return mission.mission_id
    
    def get_available_missions(self, player_level: int = 1, 
                               max_results: Optional[int] = None) -> List[BountyMission]:
        """
        Get available missions sorted by relevance and reward.
        
        Args:
            player_level: Player's current level
            max_results: Maximum number of missions to return
        
        Returns:
            List of available missions
        """
        available = [
            m for m in self.missions.values()
            if m.status == MissionStatus.AVAILABLE and not m.is_expired()
        ]
        
        # Sort by relevance (level requirement close to player level)
        available.sort(key=lambda m: abs(m.required_level - player_level) + m.base_reward)
        
        if max_results:
            available = available[:max_results]
        else:
            available = available[:self.max_visible_missions]
        
        return available
    
    def accept_mission(self, mission_id: str, player_id: str) -> bool:
        """
        Accept a mission.
        
        Returns:
            True if successful
        """
        mission = self.missions.get(mission_id)
        if not mission:
            return False
        
        if mission.status != MissionStatus.AVAILABLE:
            return False
        
        if mission.is_expired():
            mission.status = MissionStatus.EXPIRED
            return False
        
        mission.status = MissionStatus.ACCEPTED
        mission.accepted_at = datetime.now()
        mission.acceptance_count += 1
        
        self.player_accepted_missions[mission_id] = mission
        return True
    
    def complete_mission(self, mission_id: str, player_level: int) -> Tuple[int, int, bool]:
        """
        Complete a mission.
        
        Returns:
            Tuple of (crypto_reward, xp_reward, success)
        """
        mission = self.missions.get(mission_id)
        if not mission:
            return 0, 0, False
        
        if mission.status not in [MissionStatus.ACCEPTED, MissionStatus.IN_PROGRESS]:
            return 0, 0, False
        
        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now()
        mission.completion_count += 1
        
        crypto_reward, xp_reward = mission.calculate_dynamic_reward(player_level)
        
        # Bonus for quick completion
        if mission.time_remaining() and mission.time_remaining().total_seconds() > 0:
            bonus = int(mission.bonus_reward * (mission.time_remaining().total_seconds() / 
                                                (mission.time_limit_hours * 3600)))
            crypto_reward += bonus
        
        # Update client reputation
        if mission.client:
            mission.client.total_missions_posted += 1
            mission.client.successful_completion_rate = (
                (mission.client.successful_completion_rate * 
                 (mission.client.total_missions_posted - 1) + 1.0) /
                mission.client.total_missions_posted
            )
        
        self.player_completed_missions.append(mission_id)
        if mission_id in self.player_accepted_missions:
            del self.player_accepted_missions[mission_id]
        
        return crypto_reward, xp_reward, True
    
    def fail_mission(self, mission_id: str) -> bool:
        """
        Mark a mission as failed.
        
        Returns:
            True if successful
        """
        mission = self.missions.get(mission_id)
        if not mission:
            return False
        
        if mission.status not in [MissionStatus.ACCEPTED, MissionStatus.IN_PROGRESS]:
            return False
        
        mission.status = MissionStatus.FAILED
        mission.failure_count += 1
        
        # Update client reputation (negative)
        if mission.client:
            mission.client.total_missions_posted += 1
            mission.client.successful_completion_rate = (
                (mission.client.successful_completion_rate * 
                 (mission.client.total_missions_posted - 1)) /
                mission.client.total_missions_posted
            )
        
        if mission_id in self.player_accepted_missions:
            del self.player_accepted_missions[mission_id]
        
        return True
    
    def get_player_active_missions(self) -> List[BountyMission]:
        """Get player's currently active missions."""
        return list(self.player_accepted_missions.values())
    
    def get_player_mission_history(self) -> List[BountyMission]:
        """Get player's completed missions."""
        return [self.missions[mid] for mid in self.player_completed_missions]
    
    def get_mission_stats(self) -> Dict[str, int]:
        """Get statistics about missions."""
        return {
            "total_missions_posted": len(self.missions),
            "available_missions": len([m for m in self.missions.values() 
                                      if m.status == MissionStatus.AVAILABLE]),
            "completed_missions": len(self.player_completed_missions),
            "active_missions": len(self.player_accepted_missions),
            "total_clients": len(self.clients),
        }
    
    def update_client_reputation(self, client_id: str, reputation_change: int):
        """Update a client's reputation."""
        client = self.clients.get(client_id)
        if not client:
            return
        
        # Simple reputation tier progression
        current_tier_index = {
            ClientReputation.UNKNOWN: 0,
            ClientReputation.NOVICE: 1,
            ClientReputation.APPRENTICE: 2,
            ClientReputation.SKILLED: 3,
            ClientReputation.EXPERT: 4,
            ClientReputation.MASTER: 5,
        }
        
        tiers = [
            ClientReputation.UNKNOWN,
            ClientReputation.NOVICE,
            ClientReputation.APPRENTICE,
            ClientReputation.SKILLED,
            ClientReputation.EXPERT,
            ClientReputation.MASTER,
        ]
        
        current_index = current_tier_index.get(client.reputation_tier, 0)
        new_index = max(0, min(5, current_index + reputation_change))
        client.reputation_tier = tiers[new_index]
