"""Reputation system for different factions."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ReputationType(str, Enum):
    """Reputation faction types."""
    UNDERGROUND = "underground"  # Underground hacker forums
    CORPORATE = "corporate"  # Corporate security firms
    GOVERNMENT = "government"  # Government agencies
    BLACKMARKET = "blackmarket"  # Black market contacts


class ReputationTier(str, Enum):
    """Reputation tier levels."""
    UNKNOWN = "unknown"  # 0-99
    NOTICED = "noticed"  # 100-299
    RECOGNIZED = "recognized"  # 300-499
    RESPECTED = "respected"  # 500-699
    RENOWNED = "renowned"  # 700-899
    LEGENDARY = "legendary"  # 900-1000


@dataclass
class ReputationChange:
    """Record of reputation change."""
    rep_type: ReputationType
    amount: int
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    new_total: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rep_type": self.rep_type.value,
            "amount": self.amount,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "new_total": self.new_total,
        }


class Faction:
    """Individual faction reputation tracking."""
    
    # Reputation tier thresholds
    TIER_THRESHOLDS = {
        ReputationTier.UNKNOWN: 0,
        ReputationTier.NOTICED: 100,
        ReputationTier.RECOGNIZED: 300,
        ReputationTier.RESPECTED: 500,
        ReputationTier.RENOWNED: 700,
        ReputationTier.LEGENDARY: 900,
    }
    
    # Benefits unlocked at each tier
    TIER_BENEFITS = {
        ReputationTier.UNKNOWN: [],
        ReputationTier.NOTICED: ["basic_missions", "faction_contact"],
        ReputationTier.RECOGNIZED: ["advanced_missions", "discount_5"],
        ReputationTier.RESPECTED: ["elite_missions", "discount_10", "exclusive_tools"],
        ReputationTier.RENOWNED: ["legendary_missions", "discount_15", "rare_tools", "faction_backup"],
        ReputationTier.LEGENDARY: ["impossible_missions", "discount_25", "legendary_tools", "faction_alliance"],
    }
    
    def __init__(self, faction_type: ReputationType, reputation: int = 0):
        """Initialize faction."""
        self.faction_type = faction_type
        self.reputation = min(1000, max(0, reputation))
        self.history: List[ReputationChange] = []
    
    def add_reputation(self, amount: int, reason: str = "") -> ReputationChange:
        """
        Add reputation (positive or negative).
        
        Args:
            amount: Amount to add (can be negative)
            reason: Reason for change
        
        Returns:
            ReputationChange record
        """
        old_rep = self.reputation
        self.reputation = min(1000, max(0, self.reputation + amount))
        actual_change = self.reputation - old_rep
        
        change = ReputationChange(
            rep_type=self.faction_type,
            amount=actual_change,
            reason=reason,
            new_total=self.reputation,
        )
        
        self.history.append(change)
        return change
    
    def get_tier(self) -> ReputationTier:
        """Get current reputation tier."""
        for tier in reversed(ReputationTier):
            if self.reputation >= self.TIER_THRESHOLDS[tier]:
                return tier
        return ReputationTier.UNKNOWN
    
    def get_tier_progress(self) -> float:
        """Get progress to next tier (0.0 to 1.0)."""
        current_tier = self.get_tier()
        
        # If legendary, return 1.0
        if current_tier == ReputationTier.LEGENDARY:
            return 1.0
        
        # Get next tier threshold
        tier_list = list(ReputationTier)
        current_index = tier_list.index(current_tier)
        next_tier = tier_list[current_index + 1]
        
        current_threshold = self.TIER_THRESHOLDS[current_tier]
        next_threshold = self.TIER_THRESHOLDS[next_tier]
        
        tier_range = next_threshold - current_threshold
        progress_in_tier = self.reputation - current_threshold
        
        return progress_in_tier / tier_range if tier_range > 0 else 1.0
    
    def reputation_to_next_tier(self) -> int:
        """Get reputation needed for next tier."""
        current_tier = self.get_tier()
        
        if current_tier == ReputationTier.LEGENDARY:
            return 0
        
        tier_list = list(ReputationTier)
        current_index = tier_list.index(current_tier)
        next_tier = tier_list[current_index + 1]
        
        next_threshold = self.TIER_THRESHOLDS[next_tier]
        return max(0, next_threshold - self.reputation)
    
    def get_benefits(self) -> List[str]:
        """Get unlocked benefits for current tier."""
        tier = self.get_tier()
        benefits = []
        
        # Accumulate all benefits up to current tier
        for t in ReputationTier:
            benefits.extend(self.TIER_BENEFITS[t])
            if t == tier:
                break
        
        return benefits
    
    def has_benefit(self, benefit: str) -> bool:
        """Check if specific benefit is unlocked."""
        return benefit in self.get_benefits()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "faction_type": self.faction_type.value,
            "reputation": self.reputation,
            "tier": self.get_tier().value,
            "history": [h.to_dict() for h in self.history],
        }


class ReputationSystem:
    """Manage reputation across all factions."""
    
    # Reputation rewards by action
    REWARDS = {
        # Underground faction (hacker community)
        "underground": {
            "complete_bounty": 25,
            "win_ctf": 50,
            "discover_zeroday": 100,
            "share_exploit": 30,
            "help_community": 10,
            "leak_corporate_data": 75,  # For red team
            "fail_mission": -10,
        },
        # Corporate faction (security firms)
        "corporate": {
            "complete_security_audit": 30,
            "find_vulnerability": 20,
            "protect_assets": 40,
            "professional_report": 25,
            "get_certification": 50,
            "data_breach": -100,  # Major penalty
            "unethical_behavior": -50,
        },
        # Government faction (agencies)
        "government": {
            "complete_official_mission": 40,
            "report_threat": 30,
            "defend_infrastructure": 60,
            "assist_investigation": 35,
            "get_security_clearance": 100,
            "illegal_activity": -150,
            "leak_classified": -200,
        },
        # Black market faction (underground contacts)
        "blackmarket": {
            "sell_exploit": 30,
            "trade_intel": 20,
            "complete_gray_mission": 40,
            "steal_data": 50,
            "rat_to_authorities": -200,  # Ultimate betrayal
            "fail_delivery": -30,
        },
    }
    
    def __init__(self):
        """Initialize reputation system."""
        self.factions: Dict[ReputationType, Faction] = {
            ReputationType.UNDERGROUND: Faction(ReputationType.UNDERGROUND),
            ReputationType.CORPORATE: Faction(ReputationType.CORPORATE),
            ReputationType.GOVERNMENT: Faction(ReputationType.GOVERNMENT),
            ReputationType.BLACKMARKET: Faction(ReputationType.BLACKMARKET),
        }
    
    def get_faction(self, faction_type: ReputationType) -> Faction:
        """Get faction by type."""
        return self.factions[faction_type]
    
    def add_reputation(
        self,
        faction_type: ReputationType,
        amount: int,
        reason: str = "",
    ) -> ReputationChange:
        """
        Add reputation to faction.
        
        Args:
            faction_type: Which faction
            amount: Amount to add (can be negative)
            reason: Reason for change
        
        Returns:
            ReputationChange record
        """
        faction = self.get_faction(faction_type)
        return faction.add_reputation(amount, reason)
    
    def add_reputation_all(
        self,
        amounts: Dict[ReputationType, int],
        reason: str = "",
    ) -> List[ReputationChange]:
        """
        Add reputation to multiple factions.
        
        Args:
            amounts: Dict of faction types to amounts
            reason: Reason for changes
        
        Returns:
            List of ReputationChange records
        """
        changes = []
        for faction_type, amount in amounts.items():
            change = self.add_reputation(faction_type, amount, reason)
            changes.append(change)
        return changes
    
    def reward_action(
        self,
        action: str,
        faction_type: ReputationType,
    ) -> Optional[ReputationChange]:
        """
        Reward reputation for specific action.
        
        Args:
            action: Action key (e.g., "complete_bounty")
            faction_type: Which faction
        
        Returns:
            ReputationChange if action exists, None otherwise
        """
        faction_key = faction_type.value
        if faction_key not in self.REWARDS:
            return None
        
        amount = self.REWARDS[faction_key].get(action)
        if amount is None:
            return None
        
        return self.add_reputation(
            faction_type,
            amount,
            reason=f"Action: {action}",
        )
    
    def get_total_reputation(self) -> int:
        """Get total reputation across all factions."""
        return sum(f.reputation for f in self.factions.values())
    
    def get_highest_faction(self) -> Tuple[ReputationType, int]:
        """Get faction with highest reputation."""
        highest = max(
            self.factions.items(),
            key=lambda x: x[1].reputation,
        )
        return (highest[0], highest[1].reputation)
    
    def get_dominant_alignment(self) -> str:
        """
        Get dominant alignment based on faction reputation.
        
        Returns:
            "underground", "legitimate", "government", or "gray"
        """
        highest_faction, highest_rep = self.get_highest_faction()
        
        if highest_rep < 300:
            return "neutral"
        
        if highest_faction == ReputationType.UNDERGROUND:
            return "underground"
        elif highest_faction == ReputationType.CORPORATE:
            return "legitimate"
        elif highest_faction == ReputationType.GOVERNMENT:
            return "government"
        else:  # BLACKMARKET
            return "gray"
    
    def has_faction_requirement(
        self,
        faction_type: ReputationType,
        required_rep: int,
    ) -> bool:
        """Check if meets faction reputation requirement."""
        faction = self.get_faction(faction_type)
        return faction.reputation >= required_rep
    
    def has_tier_requirement(
        self,
        faction_type: ReputationType,
        required_tier: ReputationTier,
    ) -> bool:
        """Check if meets faction tier requirement."""
        faction = self.get_faction(faction_type)
        current_tier = faction.get_tier()
        
        tier_list = list(ReputationTier)
        return tier_list.index(current_tier) >= tier_list.index(required_tier)
    
    def get_all_benefits(self) -> Dict[str, List[str]]:
        """Get all unlocked benefits across factions."""
        return {
            faction_type.value: faction.get_benefits()
            for faction_type, faction in self.factions.items()
        }
    
    def get_reputation_summary(self) -> Dict[str, Any]:
        """Get summary of all reputations."""
        return {
            "total": self.get_total_reputation(),
            "dominant_alignment": self.get_dominant_alignment(),
            "factions": {
                faction_type.value: {
                    "reputation": faction.reputation,
                    "tier": faction.get_tier().value,
                    "progress": faction.get_tier_progress(),
                }
                for faction_type, faction in self.factions.items()
            },
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "factions": {
                faction_type.value: faction.to_dict()
                for faction_type, faction in self.factions.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReputationSystem":
        """Create from dictionary."""
        system = cls()
        
        factions_data = data.get("factions", {})
        for faction_type_str, faction_data in factions_data.items():
            faction_type = ReputationType(faction_type_str)
            faction = system.get_faction(faction_type)
            faction.reputation = faction_data.get("reputation", 0)
            
            # Restore history
            history_data = faction_data.get("history", [])
            faction.history = [
                ReputationChange(
                    rep_type=ReputationType(h["rep_type"]),
                    amount=h["amount"],
                    reason=h["reason"],
                    timestamp=h["timestamp"],
                    new_total=h["new_total"],
                )
                for h in history_data
            ]
        
        return system
