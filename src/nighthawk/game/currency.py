"""CryptoCreds currency system."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class TransactionType(str, Enum):
    """Transaction types."""
    EARN = "earn"
    SPEND = "spend"
    REWARD = "reward"
    BONUS = "bonus"
    REFUND = "refund"
    PURCHASE = "purchase"


class TransactionCategory(str, Enum):
    """Transaction categories."""
    MISSION = "mission"
    BOUNTY = "bounty"
    CTF = "ctf"
    ACHIEVEMENT = "achievement"
    DAILY_BONUS = "daily_bonus"
    TOOL_PURCHASE = "tool_purchase"
    VM_UPGRADE = "vm_upgrade"
    INTEL = "intel"
    COSMETIC = "cosmetic"
    OTHER = "other"


@dataclass
class Transaction:
    """Individual currency transaction."""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: TransactionType = TransactionType.EARN
    category: TransactionCategory = TransactionCategory.OTHER
    amount: int = 0
    balance_after: int = 0
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["type"] = self.type.value
        data["category"] = self.category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Create from dictionary."""
        if "type" in data and isinstance(data["type"], str):
            data["type"] = TransactionType(data["type"])
        if "category" in data and isinstance(data["category"], str):
            data["category"] = TransactionCategory(data["category"])
        return cls(**data)


class CryptoCreds:
    """CryptoCreds (₡) currency management system."""
    
    # Currency symbol
    SYMBOL = "₡"
    
    # Starting balance for new players
    STARTING_BALANCE = 1000
    
    # Daily login bonus
    DAILY_BONUS = 100
    
    # Reward amounts by category
    REWARDS = {
        "mission_easy": 500,
        "mission_medium": 2000,
        "mission_hard": 5000,
        "mission_expert": 10000,
        "mission_legendary": 25000,
        "bounty_small": 1000,
        "bounty_medium": 5000,
        "bounty_large": 15000,
        "bounty_elite": 50000,
        "ctf_participation": 500,
        "ctf_top10": 5000,
        "ctf_top3": 20000,
        "ctf_winner": 100000,
        "achievement_common": 50,
        "achievement_rare": 500,
        "achievement_epic": 2000,
        "achievement_legendary": 5000,
        "vulnerability_found": 200,
        "exploit_success": 500,
        "defense_success": 300,
    }
    
    # Item costs
    COSTS = {
        "tool_basic": 1000,
        "tool_advanced": 5000,
        "tool_elite": 15000,
        "tool_legendary": 50000,
        "exploit_common": 2000,
        "exploit_rare": 8000,
        "exploit_epic": 25000,
        "vm_upgrade_basic": 5000,
        "vm_upgrade_advanced": 15000,
        "vm_upgrade_elite": 50000,
        "intel_hint": 100,
        "intel_target_info": 500,
        "intel_vulnerability": 2000,
        "theme_basic": 500,
        "theme_premium": 2000,
        "theme_elite": 5000,
    }
    
    def __init__(self, initial_balance: int = STARTING_BALANCE):
        """Initialize currency system."""
        self.balance = initial_balance
        self.transaction_history: List[Transaction] = []
    
    def get_balance(self) -> int:
        """Get current balance."""
        return self.balance
    
    def format_amount(self, amount: int) -> str:
        """Format amount with currency symbol."""
        return f"{self.SYMBOL}{amount:,}"
    
    def add(
        self,
        amount: int,
        transaction_type: TransactionType = TransactionType.EARN,
        category: TransactionCategory = TransactionCategory.OTHER,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Transaction:
        """
        Add currency.
        
        Args:
            amount: Amount to add
            transaction_type: Type of transaction
            category: Category of transaction
            description: Transaction description
            metadata: Additional metadata
        
        Returns:
            Transaction record
        """
        self.balance += amount
        
        transaction = Transaction(
            type=transaction_type,
            category=category,
            amount=amount,
            balance_after=self.balance,
            description=description,
            metadata=metadata or {},
        )
        
        self.transaction_history.append(transaction)
        return transaction
    
    def spend(
        self,
        amount: int,
        category: TransactionCategory = TransactionCategory.OTHER,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Transaction]:
        """
        Spend currency.
        
        Args:
            amount: Amount to spend
            category: Category of transaction
            description: Transaction description
            metadata: Additional metadata
        
        Returns:
            Transaction record if successful, None if insufficient funds
        """
        if self.balance < amount:
            return None
        
        self.balance -= amount
        
        transaction = Transaction(
            type=TransactionType.SPEND,
            category=category,
            amount=amount,
            balance_after=self.balance,
            description=description,
            metadata=metadata or {},
        )
        
        self.transaction_history.append(transaction)
        return transaction
    
    def can_afford(self, amount: int) -> bool:
        """Check if can afford amount."""
        return self.balance >= amount
    
    def reward_mission(self, difficulty: str, bonus_multiplier: float = 1.0) -> Transaction:
        """Reward for completing mission."""
        base_amount = self.REWARDS.get(f"mission_{difficulty.lower()}", 1000)
        amount = int(base_amount * bonus_multiplier)
        
        return self.add(
            amount=amount,
            transaction_type=TransactionType.REWARD,
            category=TransactionCategory.MISSION,
            description=f"Mission completed ({difficulty})",
            metadata={"difficulty": difficulty, "bonus_multiplier": bonus_multiplier},
        )
    
    def reward_bounty(self, size: str) -> Transaction:
        """Reward for completing bounty."""
        amount = self.REWARDS.get(f"bounty_{size.lower()}", 1000)
        
        return self.add(
            amount=amount,
            transaction_type=TransactionType.REWARD,
            category=TransactionCategory.BOUNTY,
            description=f"Bounty completed ({size})",
            metadata={"size": size},
        )
    
    def reward_ctf(self, placement: int, total_participants: int) -> Transaction:
        """Reward for CTF event based on placement."""
        if placement == 1:
            amount = self.REWARDS["ctf_winner"]
            desc = "CTF Winner! 🏆"
        elif placement <= 3:
            amount = self.REWARDS["ctf_top3"]
            desc = f"CTF Top 3 (#{placement}) 🥉"
        elif placement <= 10:
            amount = self.REWARDS["ctf_top10"]
            desc = f"CTF Top 10 (#{placement})"
        else:
            amount = self.REWARDS["ctf_participation"]
            desc = f"CTF Participation (#{placement})"
        
        return self.add(
            amount=amount,
            transaction_type=TransactionType.REWARD,
            category=TransactionCategory.CTF,
            description=desc,
            metadata={"placement": placement, "total_participants": total_participants},
        )
    
    def reward_achievement(self, rarity: str) -> Transaction:
        """Reward for unlocking achievement."""
        amount = self.REWARDS.get(f"achievement_{rarity.lower()}", 50)
        
        return self.add(
            amount=amount,
            transaction_type=TransactionType.REWARD,
            category=TransactionCategory.ACHIEVEMENT,
            description=f"Achievement unlocked ({rarity})",
            metadata={"rarity": rarity},
        )
    
    def daily_bonus(self, streak_days: int = 0) -> Transaction:
        """Award daily login bonus."""
        # Bonus increases with streak (max 5x)
        multiplier = min(1 + (streak_days * 0.1), 5.0)
        amount = int(self.DAILY_BONUS * multiplier)
        
        return self.add(
            amount=amount,
            transaction_type=TransactionType.BONUS,
            category=TransactionCategory.DAILY_BONUS,
            description=f"Daily login bonus (streak: {streak_days} days)",
            metadata={"streak_days": streak_days, "multiplier": multiplier},
        )
    
    def purchase_tool(self, tool_tier: str, tool_name: str) -> Optional[Transaction]:
        """Purchase a tool."""
        cost = self.COSTS.get(f"tool_{tool_tier.lower()}", 1000)
        
        return self.spend(
            amount=cost,
            category=TransactionCategory.TOOL_PURCHASE,
            description=f"Purchased tool: {tool_name}",
            metadata={"tool_name": tool_name, "tier": tool_tier},
        )
    
    def purchase_vm_upgrade(self, upgrade_tier: str) -> Optional[Transaction]:
        """Purchase VM upgrade."""
        cost = self.COSTS.get(f"vm_upgrade_{upgrade_tier.lower()}", 5000)
        
        return self.spend(
            amount=cost,
            category=TransactionCategory.VM_UPGRADE,
            description=f"VM upgrade ({upgrade_tier})",
            metadata={"tier": upgrade_tier},
        )
    
    def purchase_intel(self, intel_type: str, target: str = "") -> Optional[Transaction]:
        """Purchase intelligence/hints."""
        cost = self.COSTS.get(f"intel_{intel_type.lower()}", 100)
        
        return self.spend(
            amount=cost,
            category=TransactionCategory.INTEL,
            description=f"Intel purchased: {intel_type}",
            metadata={"intel_type": intel_type, "target": target},
        )
    
    def get_transaction_history(
        self,
        limit: Optional[int] = None,
        category: Optional[TransactionCategory] = None,
    ) -> List[Transaction]:
        """
        Get transaction history.
        
        Args:
            limit: Maximum number of transactions to return
            category: Filter by category
        
        Returns:
            List of transactions (most recent first)
        """
        transactions = self.transaction_history[::-1]  # Reverse for most recent first
        
        if category:
            transactions = [t for t in transactions if t.category == category]
        
        if limit:
            transactions = transactions[:limit]
        
        return transactions
    
    def get_total_earned(self, category: Optional[TransactionCategory] = None) -> int:
        """Get total amount earned."""
        transactions = self.transaction_history
        
        if category:
            transactions = [t for t in transactions if t.category == category]
        
        return sum(
            t.amount
            for t in transactions
            if t.type in [TransactionType.EARN, TransactionType.REWARD, TransactionType.BONUS]
        )
    
    def get_total_spent(self, category: Optional[TransactionCategory] = None) -> int:
        """Get total amount spent."""
        transactions = self.transaction_history
        
        if category:
            transactions = [t for t in transactions if t.category == category]
        
        return sum(
            t.amount
            for t in transactions
            if t.type in [TransactionType.SPEND, TransactionType.PURCHASE]
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get currency statistics."""
        return {
            "current_balance": self.balance,
            "total_earned": self.get_total_earned(),
            "total_spent": self.get_total_spent(),
            "transaction_count": len(self.transaction_history),
            "most_earned_category": self._get_most_earned_category(),
            "most_spent_category": self._get_most_spent_category(),
        }
    
    def _get_most_earned_category(self) -> str:
        """Get category with most earnings."""
        category_totals: Dict[TransactionCategory, int] = {}
        
        for t in self.transaction_history:
            if t.type in [TransactionType.EARN, TransactionType.REWARD, TransactionType.BONUS]:
                category_totals[t.category] = category_totals.get(t.category, 0) + t.amount
        
        if not category_totals:
            return "none"
        
        return max(category_totals, key=category_totals.get).value  # type: ignore
    
    def _get_most_spent_category(self) -> str:
        """Get category with most spending."""
        category_totals: Dict[TransactionCategory, int] = {}
        
        for t in self.transaction_history:
            if t.type in [TransactionType.SPEND, TransactionType.PURCHASE]:
                category_totals[t.category] = category_totals.get(t.category, 0) + t.amount
        
        if not category_totals:
            return "none"
        
        return max(category_totals, key=category_totals.get).value  # type: ignore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "balance": self.balance,
            "transaction_history": [t.to_dict() for t in self.transaction_history],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CryptoCreds":
        """Create from dictionary."""
        currency = cls(initial_balance=0)
        currency.balance = data.get("balance", cls.STARTING_BALANCE)
        
        transaction_data = data.get("transaction_history", [])
        currency.transaction_history = [
            Transaction.from_dict(t) for t in transaction_data
        ]
        
        return currency
