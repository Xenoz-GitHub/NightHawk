"""Experience points and progression system."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


class XPSource(str, Enum):
    """XP earning sources."""
    MISSION = "mission"
    BOUNTY = "bounty"
    CTF = "ctf"
    VULNERABILITY = "vulnerability"
    EXPLOIT = "exploit"
    DEFENSE = "defense"
    TRAINING = "training"
    ACHIEVEMENT = "achievement"
    DISCOVERY = "discovery"
    CHALLENGE = "challenge"


@dataclass
class XPReward:
    """XP reward definition."""
    source: XPSource
    base_amount: int
    multiplier: float = 1.0
    bonus: int = 0
    description: str = ""
    
    def calculate(self) -> int:
        """Calculate total XP."""
        return int((self.base_amount * self.multiplier) + self.bonus)


class XPSystem:
    """Experience points management system."""
    
    # Base XP amounts by source
    BASE_XP = {
        "mission_easy": 100,
        "mission_medium": 500,
        "mission_hard": 1500,
        "mission_expert": 3000,
        "mission_legendary": 5000,
        "bounty_small": 200,
        "bounty_medium": 1000,
        "bounty_large": 3000,
        "bounty_elite": 5000,
        "ctf_challenge": 500,
        "ctf_win": 10000,
        "ctf_top3": 5000,
        "ctf_participation": 1000,
        "vulnerability_low": 50,
        "vulnerability_medium": 150,
        "vulnerability_high": 300,
        "vulnerability_critical": 500,
        "exploit_success": 200,
        "exploit_stealth": 400,
        "defense_block": 100,
        "defense_detect": 200,
        "defense_respond": 300,
        "training_exercise": 10,
        "training_advanced": 50,
        "achievement_unlock": 100,
        "discovery_service": 25,
        "discovery_secret": 100,
        "challenge_complete": 150,
    }
    
    def calculate_xp(
        self,
        source_key: str,
        multiplier: float = 1.0,
        bonus: int = 0,
    ) -> int:
        """
        Calculate XP reward.
        
        Args:
            source_key: Key for base XP amount
            multiplier: XP multiplier (e.g., 1.5 for bonus events)
            bonus: Flat bonus XP
        
        Returns:
            Total XP amount
        """
        base = self.BASE_XP.get(source_key, 0)
        return int((base * multiplier) + bonus)
    
    def calculate_mission_xp(
        self,
        difficulty: str,
        time_bonus: bool = False,
        stealth_bonus: bool = False,
        perfect_bonus: bool = False,
    ) -> int:
        """
        Calculate mission XP with bonuses.
        
        Args:
            difficulty: Mission difficulty (easy/medium/hard/expert/legendary)
            time_bonus: Completed quickly
            stealth_bonus: Completed stealthily
            perfect_bonus: Perfect completion (no mistakes)
        
        Returns:
            Total XP
        """
        base = self.BASE_XP.get(f"mission_{difficulty.lower()}", 100)
        multiplier = 1.0
        
        if time_bonus:
            multiplier += 0.25
        if stealth_bonus:
            multiplier += 0.5
        if perfect_bonus:
            multiplier += 0.75
        
        return int(base * multiplier)
    
    def calculate_ctf_xp(
        self,
        challenges_solved: int,
        placement: int,
        total_participants: int,
    ) -> int:
        """
        Calculate CTF event XP.
        
        Args:
            challenges_solved: Number of challenges completed
            placement: Final placement
            total_participants: Total number of participants
        
        Returns:
            Total XP
        """
        # Base XP from challenges
        challenge_xp = challenges_solved * self.BASE_XP["ctf_challenge"]
        
        # Placement bonus
        if placement == 1:
            placement_xp = self.BASE_XP["ctf_win"]
        elif placement <= 3:
            placement_xp = self.BASE_XP["ctf_top3"]
        else:
            placement_xp = self.BASE_XP["ctf_participation"]
        
        return challenge_xp + placement_xp


class LevelSystem:
    """Level progression system."""
    
    # Level tier thresholds
    TIERS = {
        "script_kiddie": (1, 10),
        "security_analyst": (11, 20),
        "penetration_tester": (21, 30),
        "security_engineer": (31, 40),
        "elite_hacker": (41, 50),
        "security_architect": (51, 75),
        "legendary_ghost": (76, 99),
    }
    
    # Level tier names
    TIER_NAMES = {
        "script_kiddie": "Script Kiddie",
        "security_analyst": "Security Analyst",
        "penetration_tester": "Penetration Tester",
        "security_engineer": "Security Engineer",
        "elite_hacker": "Elite Hacker",
        "security_architect": "Security Architect",
        "legendary_ghost": "Legendary Ghost",
    }
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """
        Calculate total XP required to reach a level.
        
        Uses exponential formula for smooth progression:
        XP = base * (level ^ exponent) * tier_multiplier
        """
        if level <= 1:
            return 0
        elif level <= 10:
            return int(1000 * math.pow(level - 1, 1.25))
        elif level <= 20:
            return int(10000 + 5000 * math.pow(level - 10, 1.33))
        elif level <= 30:
            return int(50000 + 10000 * math.pow(level - 20, 1.43))
        elif level <= 40:
            return int(150000 + 20000 * math.pow(level - 30, 1.54))
        elif level <= 50:
            return int(350000 + 40000 * math.pow(level - 40, 1.67))
        elif level <= 75:
            return int(750000 + 80000 * math.pow(level - 50, 1.82))
        else:
            return int(2000000 + 200000 * math.pow(level - 75, 2.0))
    
    @staticmethod
    def level_from_xp(xp: int) -> int:
        """Calculate level from total XP."""
        level = 1
        while level < 99:
            if xp < LevelSystem.xp_for_level(level + 1):
                return level
            level += 1
        return 99
    
    @staticmethod
    def xp_to_next_level(current_xp: int, current_level: int) -> int:
        """Calculate XP needed for next level."""
        next_level_xp = LevelSystem.xp_for_level(current_level + 1)
        return max(0, next_level_xp - current_xp)
    
    @staticmethod
    def progress_to_next_level(current_xp: int, current_level: int) -> float:
        """Calculate progress to next level (0.0 to 1.0)."""
        if current_level >= 99:
            return 1.0
        
        current_level_xp = LevelSystem.xp_for_level(current_level)
        next_level_xp = LevelSystem.xp_for_level(current_level + 1)
        
        level_xp_range = next_level_xp - current_level_xp
        xp_in_level = current_xp - current_level_xp
        
        return min(1.0, max(0.0, xp_in_level / level_xp_range))
    
    @staticmethod
    def get_tier(level: int) -> str:
        """Get tier name for level."""
        for tier, (min_level, max_level) in LevelSystem.TIERS.items():
            if min_level <= level <= max_level:
                return LevelSystem.TIER_NAMES[tier]
        return "Unknown"
    
    @staticmethod
    def get_tier_range(level: int) -> Tuple[int, int]:
        """Get level range for current tier."""
        for tier, (min_level, max_level) in LevelSystem.TIERS.items():
            if min_level <= level <= max_level:
                return (min_level, max_level)
        return (1, 99)


@dataclass
class SkillNode:
    """Individual skill in skill tree."""
    node_id: str
    name: str
    description: str
    max_level: int = 10
    current_level: int = 0
    cost_per_level: int = 1  # Skill points needed per level
    prerequisites: List[str] = field(default_factory=list)  # Required node_ids
    unlocks: List[str] = field(default_factory=list)  # Unlocked abilities/tools
    
    def can_upgrade(self, available_points: int, unlocked_nodes: List[str]) -> bool:
        """Check if skill can be upgraded."""
        # Check max level
        if self.current_level >= self.max_level:
            return False
        
        # Check skill points
        if available_points < self.cost_per_level:
            return False
        
        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in unlocked_nodes:
                return False
        
        return True
    
    def upgrade(self) -> bool:
        """Upgrade skill by one level."""
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False
    
    def is_unlocked(self) -> bool:
        """Check if skill is unlocked."""
        return self.current_level > 0
    
    def get_progress(self) -> float:
        """Get upgrade progress (0.0 to 1.0)."""
        if self.max_level == 0:
            return 1.0
        return self.current_level / self.max_level


class SkillTree:
    """Skill tree management system."""
    
    # Red Team skill trees
    RED_TEAM_SKILLS = {
        "exploitation": [
            SkillNode(
                "exploit_basic",
                "Basic Exploitation",
                "Learn fundamental exploitation techniques",
                max_level=5,
                unlocks=["basic_exploits", "payload_generator"],
            ),
            SkillNode(
                "exploit_advanced",
                "Advanced Exploitation",
                "Master complex exploitation methods",
                max_level=5,
                prerequisites=["exploit_basic"],
                unlocks=["advanced_exploits", "custom_payloads"],
            ),
            SkillNode(
                "exploit_zeroday",
                "Zero-Day Research",
                "Discover and weaponize zero-day vulnerabilities",
                max_level=10,
                prerequisites=["exploit_advanced"],
                unlocks=["zeroday_exploits", "exploit_framework"],
            ),
        ],
        "stealth": [
            SkillNode(
                "stealth_basic",
                "Basic Evasion",
                "Learn to avoid basic detection systems",
                max_level=5,
                unlocks=["traffic_obfuscation", "log_cleaning"],
            ),
            SkillNode(
                "stealth_advanced",
                "Advanced Obfuscation",
                "Evade advanced security systems",
                max_level=5,
                prerequisites=["stealth_basic"],
                unlocks=["av_bypass", "edr_evasion"],
            ),
            SkillNode(
                "stealth_ghost",
                "Ghost Mode",
                "Become virtually undetectable",
                max_level=10,
                prerequisites=["stealth_advanced"],
                unlocks=["ghost_protocol", "anti_forensics"],
            ),
        ],
        "social_engineering": [
            SkillNode(
                "social_phishing",
                "Phishing",
                "Create convincing phishing campaigns",
                max_level=5,
                unlocks=["email_spoofing", "credential_harvesting"],
            ),
            SkillNode(
                "social_vishing",
                "Vishing",
                "Voice phishing and social manipulation",
                max_level=5,
                prerequisites=["social_phishing"],
                unlocks=["voice_spoofing", "pretexting"],
            ),
            SkillNode(
                "social_physical",
                "Physical Security",
                "Bypass physical security measures",
                max_level=10,
                prerequisites=["social_vishing"],
                unlocks=["tailgating", "lockpicking", "badge_cloning"],
            ),
        ],
        "post_exploitation": [
            SkillNode(
                "post_basic",
                "Basic Persistence",
                "Maintain access to compromised systems",
                max_level=5,
                unlocks=["backdoors", "scheduled_tasks"],
            ),
            SkillNode(
                "post_advanced",
                "Advanced Rootkits",
                "Deploy sophisticated persistence mechanisms",
                max_level=5,
                prerequisites=["post_basic"],
                unlocks=["kernel_rootkits", "bootkit"],
            ),
            SkillNode(
                "post_apt",
                "APT Tactics",
                "Nation-state level techniques",
                max_level=10,
                prerequisites=["post_advanced"],
                unlocks=["apt_framework", "c2_infrastructure", "lateral_movement"],
            ),
        ],
    }
    
    # Blue Team skill trees
    BLUE_TEAM_SKILLS = {
        "detection": [
            SkillNode(
                "detect_basic",
                "Log Analysis",
                "Analyze security logs for threats",
                max_level=5,
                unlocks=["log_parser", "basic_queries"],
            ),
            SkillNode(
                "detect_anomaly",
                "Anomaly Detection",
                "Identify unusual patterns and behaviors",
                max_level=5,
                prerequisites=["detect_basic"],
                unlocks=["anomaly_detection", "baseline_analysis"],
            ),
            SkillNode(
                "detect_ai",
                "AI-Powered SIEM",
                "Use AI/ML for threat detection",
                max_level=10,
                prerequisites=["detect_anomaly"],
                unlocks=["ml_detection", "correlation_engine", "predictive_analysis"],
            ),
        ],
        "response": [
            SkillNode(
                "response_triage",
                "Basic Triage",
                "Initial incident assessment",
                max_level=5,
                unlocks=["incident_response", "basic_containment"],
            ),
            SkillNode(
                "response_advanced",
                "Advanced IR",
                "Complex incident response procedures",
                max_level=5,
                prerequisites=["response_triage"],
                unlocks=["advanced_containment", "eradication", "recovery"],
            ),
            SkillNode(
                "response_hunting",
                "Proactive Hunting",
                "Hunt threats before they strike",
                max_level=10,
                prerequisites=["response_advanced"],
                unlocks=["threat_hunting", "ioc_tracking", "apt_detection"],
            ),
        ],
        "forensics": [
            SkillNode(
                "forensics_file",
                "File Analysis",
                "Analyze files and file systems",
                max_level=5,
                unlocks=["file_carving", "metadata_analysis"],
            ),
            SkillNode(
                "forensics_memory",
                "Memory Forensics",
                "Analyze system memory dumps",
                max_level=5,
                prerequisites=["forensics_file"],
                unlocks=["memory_dump", "process_analysis", "malware_extraction"],
            ),
            SkillNode(
                "forensics_network",
                "Network Forensics",
                "Analyze network traffic and packets",
                max_level=10,
                prerequisites=["forensics_memory"],
                unlocks=["packet_analysis", "traffic_reconstruction", "protocol_analysis"],
            ),
        ],
        "hardening": [
            SkillNode(
                "harden_basic",
                "Basic Security",
                "Implement fundamental security controls",
                max_level=5,
                unlocks=["firewall_rules", "access_control"],
            ),
            SkillNode(
                "harden_defense",
                "Defense in Depth",
                "Layered security architecture",
                max_level=5,
                prerequisites=["harden_basic"],
                unlocks=["network_segmentation", "security_layers"],
            ),
            SkillNode(
                "harden_zerotrust",
                "Zero Trust",
                "Implement zero trust architecture",
                max_level=10,
                prerequisites=["harden_defense"],
                unlocks=["zero_trust", "microsegmentation", "continuous_verification"],
            ),
        ],
    }
    
    def __init__(self, team: str = "red"):
        """Initialize skill tree for team."""
        self.team = team
        self.skills: Dict[str, List[SkillNode]] = {}
        self.skill_points = 0
        self.unlocked_abilities: List[str] = []
        
        # Load appropriate skill tree
        if team == "red":
            self.skills = self._load_skills(self.RED_TEAM_SKILLS)
        elif team == "blue":
            self.skills = self._load_skills(self.BLUE_TEAM_SKILLS)
    
    def _load_skills(self, skill_data: Dict[str, List[SkillNode]]) -> Dict[str, List[SkillNode]]:
        """Load skill data (creates deep copies)."""
        loaded = {}
        for category, nodes in skill_data.items():
            loaded[category] = [
                SkillNode(
                    node_id=n.node_id,
                    name=n.name,
                    description=n.description,
                    max_level=n.max_level,
                    current_level=n.current_level,
                    cost_per_level=n.cost_per_level,
                    prerequisites=n.prerequisites.copy(),
                    unlocks=n.unlocks.copy(),
                )
                for n in nodes
            ]
        return loaded
    
    def add_skill_points(self, amount: int) -> None:
        """Add skill points."""
        self.skill_points += amount
    
    def get_skill(self, node_id: str) -> Optional[SkillNode]:
        """Get skill node by ID."""
        for category in self.skills.values():
            for node in category:
                if node.node_id == node_id:
                    return node
        return None
    
    def upgrade_skill(self, node_id: str) -> bool:
        """
        Upgrade a skill.
        
        Returns:
            True if successful, False otherwise
        """
        node = self.get_skill(node_id)
        if not node:
            return False
        
        # Check if can upgrade
        unlocked_ids = self._get_unlocked_node_ids()
        if not node.can_upgrade(self.skill_points, unlocked_ids):
            return False
        
        # Perform upgrade
        if node.upgrade():
            self.skill_points -= node.cost_per_level
            
            # Unlock abilities if first level
            if node.current_level == 1:
                for ability in node.unlocks:
                    if ability not in self.unlocked_abilities:
                        self.unlocked_abilities.append(ability)
            
            return True
        
        return False
    
    def _get_unlocked_node_ids(self) -> List[str]:
        """Get list of unlocked node IDs."""
        unlocked = []
        for category in self.skills.values():
            for node in category:
                if node.is_unlocked():
                    unlocked.append(node.node_id)
        return unlocked
    
    def has_ability(self, ability_id: str) -> bool:
        """Check if ability is unlocked."""
        return ability_id in self.unlocked_abilities
    
    def get_available_upgrades(self) -> List[SkillNode]:
        """Get list of skills that can be upgraded."""
        unlocked_ids = self._get_unlocked_node_ids()
        available = []
        
        for category in self.skills.values():
            for node in category:
                if node.can_upgrade(self.skill_points, unlocked_ids):
                    available.append(node)
        
        return available
    
    def get_skill_summary(self) -> Dict[str, Any]:
        """Get summary of skill tree."""
        total_nodes = sum(len(nodes) for nodes in self.skills.values())
        unlocked_nodes = len(self._get_unlocked_node_ids())
        
        return {
            "team": self.team,
            "skill_points": self.skill_points,
            "unlocked_abilities": len(self.unlocked_abilities),
            "total_nodes": total_nodes,
            "unlocked_nodes": unlocked_nodes,
            "progress": unlocked_nodes / total_nodes if total_nodes > 0 else 0,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        skills_data = {}
        for category, nodes in self.skills.items():
            skills_data[category] = [
                {
                    "node_id": n.node_id,
                    "current_level": n.current_level,
                }
                for n in nodes
            ]
        
        return {
            "team": self.team,
            "skill_points": self.skill_points,
            "unlocked_abilities": self.unlocked_abilities,
            "skills": skills_data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillTree":
        """Create from dictionary."""
        tree = cls(team=data.get("team", "red"))
        tree.skill_points = data.get("skill_points", 0)
        tree.unlocked_abilities = data.get("unlocked_abilities", [])
        
        # Restore skill levels
        skills_data = data.get("skills", {})
        for category, nodes_data in skills_data.items():
            if category in tree.skills:
                for node_data in nodes_data:
                    node = tree.get_skill(node_data["node_id"])
                    if node:
                        node.current_level = node_data["current_level"]
        
        return tree
