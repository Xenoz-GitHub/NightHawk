"""Team selection system with role-specific content."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TeamRole(str, Enum):
    """Team role types."""
    RED = "red"
    BLUE = "blue"


@dataclass
class TeamInfo:
    """Information about a team."""
    role: TeamRole
    name: str
    tagline: str
    description: str
    focus_areas: List[str]
    starting_tools: List[str]
    starting_skills: Dict[str, int]
    starting_bonus_currency: int
    starting_bonus_xp: int
    color_scheme: str
    icon: str
    motto: str


class TeamDatabase:
    """Database of team information and content."""

    RED_TEAM = TeamInfo(
        role=TeamRole.RED,
        name="Red Team - Offensive Security",
        tagline="Attack is the Best Defense",
        description="""
Join the elite Red Team and become a master of offensive security.
Your mission: Find vulnerabilities before the enemy does.

As a Red Team operator, you'll:
• Penetrate secure systems using advanced exploitation techniques
• Craft custom payloads and zero-day exploits
• Deploy social engineering campaigns
• Maintain persistent access to compromised networks
• Evade detection systems and cover your tracks

This path is for those who think like an attacker to defend better.
You'll learn real-world hacking techniques in a safe, simulated environment.
        """.strip(),
        focus_areas=[
            "Exploitation & Payload Development",
            "Network Penetration Testing",
            "Social Engineering & Phishing",
            "Post-Exploitation & Persistence",
            "Stealth & Evasion Techniques",
            "Vulnerability Research",
        ],
        starting_tools=[
            "basic_scanner",
            "port_scanner",
            "web_crawler",
            "password_dictionary",
        ],
        starting_skills={
            "exploitation": 1,
            "stealth": 1,
            "social_engineering": 0,
            "post_exploitation": 0,
        },
        starting_bonus_currency=500,
        starting_bonus_xp=100,
        color_scheme="red",
        icon="",
        motto="We break in so you can keep them out",
    )

    BLUE_TEAM = TeamInfo(
        role=TeamRole.BLUE,
        name="Blue Team - Defensive Security",
        tagline="The Last Line of Defense",
        description="""
Join the Blue Team and become a guardian of the digital realm.
Your mission: Detect, respond, and neutralize threats before damage occurs.

As a Blue Team defender, you'll:
• Monitor networks for suspicious activity in real-time
• Analyze security logs and hunt for threats proactively
• Respond to incidents with precision and speed
• Conduct digital forensics investigations
• Harden systems against advanced persistent threats

This path is for those who protect, detect, and defend.
You'll master the art of cybersecurity defense and incident response.
        """.strip(),
        focus_areas=[
            "Threat Detection & Monitoring",
            "Incident Response & Containment",
            "Digital Forensics & Investigation",
            "System Hardening & Defense",
            "Security Operations (SOC)",
            "Threat Intelligence & Hunting",
        ],
        starting_tools=[
            "log_analyzer",
            "network_monitor",
            "firewall_manager",
            "backup_tool",
        ],
        starting_skills={
            "detection": 1,
            "response": 1,
            "forensics": 0,
            "hardening": 0,
        },
        starting_bonus_currency=500,
        starting_bonus_xp=100,
        color_scheme="blue",
        icon="",
        motto="We stand watch while others sleep",
    )

    @classmethod
    def get_team_info(cls, role: TeamRole) -> TeamInfo:
        """Get team information by role."""
        if role == TeamRole.RED:
            return cls.RED_TEAM
        else:
            return cls.BLUE_TEAM

    @classmethod
    def get_all_teams(cls) -> List[TeamInfo]:
        """Get information for all teams."""
        return [cls.RED_TEAM, cls.BLUE_TEAM]


@dataclass
class MissionTemplate:
    """Template for role-specific missions."""
    mission_id: str
    title: str
    description: str
    difficulty: str
    team_role: TeamRole
    objectives: List[str]
    rewards: Dict[str, int]
    required_level: int
    required_tools: List[str]
    duration_minutes: int
    category: str


class MissionLibrary:
    """Library of role-specific mission templates."""

    # Red Team Missions
    RED_TEAM_MISSIONS = [
        MissionTemplate(
            mission_id="red_intro_1",
            title="First Steps: Reconnaissance",
            description="Your first target awaits. Perform basic reconnaissance on a web server.",
            difficulty="easy",
            team_role=TeamRole.RED,
            objectives=[
                "Scan the target for open ports",
                "Identify running services",
                "Map the attack surface",
            ],
            rewards={"xp": 100, "currency": 500, "reputation_underground": 10},
            required_level=1,
            required_tools=["basic_scanner"],
            duration_minutes=10,
            category="reconnaissance",
        ),
        MissionTemplate(
            mission_id="red_intro_2",
            title="Exploitation 101",
            description="Exploit a known vulnerability in an unpatched web application.",
            difficulty="easy",
            team_role=TeamRole.RED,
            objectives=[
                "Identify the vulnerability",
                "Select appropriate exploit",
                "Gain initial access",
            ],
            rewards={"xp": 200, "currency": 1000, "reputation_underground": 20},
            required_level=1,
            required_tools=["basic_scanner"],
            duration_minutes=15,
            category="exploitation",
        ),
        MissionTemplate(
            mission_id="red_intermediate_1",
            title="Corporate Infiltration",
            description="Penetrate the perimeter defenses of a mid-sized corporation.",
            difficulty="medium",
            team_role=TeamRole.RED,
            objectives=[
                "Bypass the firewall",
                "Compromise an employee workstation",
                "Escalate privileges to domain admin",
                "Exfiltrate sensitive documents",
            ],
            rewards={"xp": 500, "currency": 2500, "reputation_underground": 40},
            required_level=5,
            required_tools=["port_scanner", "password_cracker"],
            duration_minutes=30,
            category="penetration",
        ),
        MissionTemplate(
            mission_id="red_advanced_1",
            title="APT Campaign Simulation",
            description="Execute a sophisticated Advanced Persistent Threat campaign.",
            difficulty="hard",
            team_role=TeamRole.RED,
            objectives=[
                "Establish initial foothold via spear-phishing",
                "Deploy custom backdoor",
                "Move laterally across the network",
                "Maintain persistence for 7 days",
                "Exfiltrate crown jewels without detection",
            ],
            rewards={"xp": 1500, "currency": 7500, "reputation_underground": 100},
            required_level=15,
            required_tools=["advanced_exploit_kit", "stealth_toolkit"],
            duration_minutes=60,
            category="apt_simulation",
        ),
        MissionTemplate(
            mission_id="red_expert_1",
            title="Zero-Day Hunt",
            description="Discover and weaponize a zero-day vulnerability in enterprise software.",
            difficulty="expert",
            team_role=TeamRole.RED,
            objectives=[
                "Reverse engineer the target application",
                "Identify memory corruption vulnerability",
                "Develop working exploit",
                "Create reliable payload",
                "Demonstrate remote code execution",
            ],
            rewards={"xp": 3000, "currency": 15000, "reputation_underground": 200},
            required_level=25,
            required_tools=["debugger", "disassembler", "exploit_framework"],
            duration_minutes=90,
            category="vulnerability_research",
        ),
    ]

    # Blue Team Missions
    BLUE_TEAM_MISSIONS = [
        MissionTemplate(
            mission_id="blue_intro_1",
            title="First Watch: Log Analysis",
            description="Your first shift as a SOC analyst. Review security logs for threats.",
            difficulty="easy",
            team_role=TeamRole.BLUE,
            objectives=[
                "Review system logs for anomalies",
                "Identify suspicious login attempts",
                "Document findings",
            ],
            rewards={"xp": 100, "currency": 500, "reputation_corporate": 10},
            required_level=1,
            required_tools=["log_analyzer"],
            duration_minutes=10,
            category="monitoring",
        ),
        MissionTemplate(
            mission_id="blue_intro_2",
            title="Incident Response: Malware Alert",
            description="A workstation has been flagged for suspicious activity. Investigate and contain.",
            difficulty="easy",
            team_role=TeamRole.BLUE,
            objectives=[
                "Isolate the infected system",
                "Identify the malware strain",
                "Remove the infection",
            ],
            rewards={"xp": 200, "currency": 1000, "reputation_corporate": 20},
            required_level=1,
            required_tools=["network_monitor"],
            duration_minutes=15,
            category="incident_response",
        ),
        MissionTemplate(
            mission_id="blue_intermediate_1",
            title="Threat Hunt: APT Detection",
            description="Intelligence suggests an APT group is targeting your organization. Hunt them down.",
            difficulty="medium",
            team_role=TeamRole.BLUE,
            objectives=[
                "Analyze network traffic for IOCs",
                "Identify compromised systems",
                "Trace lateral movement",
                "Contain the threat",
            ],
            rewards={"xp": 500, "currency": 2500, "reputation_corporate": 40},
            required_level=5,
            required_tools=["network_monitor", "threat_intel_feed"],
            duration_minutes=30,
            category="threat_hunting",
        ),
        MissionTemplate(
            mission_id="blue_advanced_1",
            title="Live Fire: Active Breach",
            description="Red Team is actively attacking your network. Defend in real-time.",
            difficulty="hard",
            team_role=TeamRole.BLUE,
            objectives=[
                "Detect the initial intrusion",
                "Block attack vectors in real-time",
                "Prevent data exfiltration",
                "Identify all compromised assets",
                "Eradicate attacker presence",
            ],
            rewards={"xp": 1500, "currency": 7500, "reputation_corporate": 100},
            required_level=15,
            required_tools=["siem", "edr", "firewall_manager"],
            duration_minutes=60,
            category="active_defense",
        ),
        MissionTemplate(
            mission_id="blue_expert_1",
            title="Forensics: Nation-State Attack",
            description="Conduct full forensics investigation of a nation-state cyber attack.",
            difficulty="expert",
            team_role=TeamRole.BLUE,
            objectives=[
                "Acquire forensic images of all systems",
                "Reconstruct the attack timeline",
                "Identify attribution indicators",
                "Document TTPs used by attacker",
                "Prepare comprehensive incident report",
            ],
            rewards={"xp": 3000, "currency": 15000, "reputation_government": 200},
            required_level=25,
            required_tools=["forensics_suite", "memory_analyzer", "timeline_tool"],
            duration_minutes=90,
            category="forensics",
        ),
    ]

    @classmethod
    def get_missions_for_team(cls, team_role: TeamRole, level: int = 1) -> List[MissionTemplate]:
        """Get available missions for team and level."""
        if team_role == TeamRole.RED:
            missions = cls.RED_TEAM_MISSIONS
        else:
            missions = cls.BLUE_TEAM_MISSIONS

        # Filter by level requirement
        return [m for m in missions if m.required_level <= level]

    @classmethod
    def get_mission_by_id(cls, mission_id: str) -> Optional[MissionTemplate]:
        """Get mission by ID."""
        all_missions = cls.RED_TEAM_MISSIONS + cls.BLUE_TEAM_MISSIONS
        for mission in all_missions:
            if mission.mission_id == mission_id:
                return mission
        return None

    @classmethod
    def get_starter_missions(cls, team_role: TeamRole) -> List[MissionTemplate]:
        """Get starter missions for new players."""
        missions = cls.get_missions_for_team(team_role, level=1)
        return [m for m in missions if m.difficulty == "easy"]


class TeamSelectionValidator:
    """Validate team selection and requirements."""

    @staticmethod
    def can_select_team(has_existing_team: bool) -> bool:
        """Check if player can select a team."""
        # Can only select team once
        return not has_existing_team

    @staticmethod
    def validate_team_choice(choice: str) -> Optional[TeamRole]:
        """Validate team choice input."""
        choice = choice.lower().strip()

        if choice in ["red", "r", "1", "offensive", "attack"]:
            return TeamRole.RED
        elif choice in ["blue", "b", "2", "defensive", "defend"]:
            return TeamRole.BLUE
        else:
            return None

    @staticmethod
    def get_team_requirements(team_role: TeamRole) -> Dict[str, Any]:
        """Get requirements for joining a team."""
        # No requirements for initial selection
        return {
            "min_level": 1,
            "prerequisites": [],
            "one_time_choice": True,
        }


class TeamBenefits:
    """Team-specific benefits and bonuses."""

    RED_TEAM_BENEFITS = {
        "level_5": {
            "unlocks": ["advanced_scanner", "exploit_database"],
            "bonus": "10% bonus damage to targets",
        },
        "level_10": {
            "unlocks": ["custom_payload_generator", "obfuscation_tool"],
            "bonus": "Reduced detection chance by 15%",
        },
        "level_15": {
            "unlocks": ["zero_day_research_lab", "apt_toolkit"],
            "bonus": "Access to black market exploits",
        },
        "level_20": {
            "unlocks": ["nation_state_arsenal"],
            "bonus": "Elite Red Team status - 25% XP bonus",
        },
    }

    BLUE_TEAM_BENEFITS = {
        "level_5": {
            "unlocks": ["advanced_ids", "correlation_engine"],
            "bonus": "10% faster threat detection",
        },
        "level_10": {
            "unlocks": ["ml_threat_detector", "automated_response"],
            "bonus": "15% reduction in incident response time",
        },
        "level_15": {
            "unlocks": ["threat_intel_platform", "proactive_hunting"],
            "bonus": "Access to government threat feeds",
        },
        "level_20": {
            "unlocks": ["security_operations_center"],
            "bonus": "Elite Blue Team status - 25% XP bonus",
        },
    }

    @classmethod
    def get_benefits_at_level(cls, team_role: TeamRole, level: int) -> List[Dict[str, Any]]:
        """Get all benefits unlocked up to this level."""
        if team_role == TeamRole.RED:
            benefits_db = cls.RED_TEAM_BENEFITS
        else:
            benefits_db = cls.BLUE_TEAM_BENEFITS

        unlocked = []
        for req_level, benefits in benefits_db.items():
            req_level_int = int(req_level.split("_")[1])
            if level >= req_level_int:
                unlocked.append({
                    "level": req_level_int,
                    "unlocks": benefits["unlocks"],
                    "bonus": benefits["bonus"],
                })

        return unlocked

    @classmethod
    def get_next_benefit(cls, team_role: TeamRole, current_level: int) -> Optional[Dict[str, Any]]:
        """Get next benefit to be unlocked."""
        if team_role == TeamRole.RED:
            benefits_db = cls.RED_TEAM_BENEFITS
        else:
            benefits_db = cls.BLUE_TEAM_BENEFITS

        for req_level, benefits in sorted(benefits_db.items()):
            req_level_int = int(req_level.split("_")[1])
            if current_level < req_level_int:
                return {
                    "level": req_level_int,
                    "unlocks": benefits["unlocks"],
                    "bonus": benefits["bonus"],
                }

        return None


class TeamComparison:
    """Compare teams for player decision-making."""

    @staticmethod
    def get_comparison_matrix() -> Dict[str, Dict[str, str]]:
        """Get side-by-side comparison of teams."""
        return {
            "focus": {
                "red": "Offensive Security - Breaking In",
                "blue": "Defensive Security - Keeping Out",
            },
            "playstyle": {
                "red": "Aggressive, Creative, Exploit-focused",
                "blue": "Analytical, Methodical, Defense-focused",
            },
            "primary_activities": {
                "red": "Hacking, Exploitation, Penetration Testing",
                "blue": "Monitoring, Detection, Incident Response",
            },
            "difficulty": {
                "red": "High - Requires creative problem solving",
                "blue": "Medium - Requires attention to detail",
            },
            "reputation_focus": {
                "red": "Underground hackers, Black market",
                "blue": "Corporate security, Government agencies",
            },
            "best_for": {
                "red": "Those who love breaking things to understand them",
                "blue": "Those who love protecting and defending systems",
            },
        }

    @staticmethod
    def get_decision_helper(player_preferences: Dict[str, str]) -> TeamRole:
        """Help player decide based on preferences."""
        red_score = 0
        blue_score = 0

        # Analyze preferences
        if player_preferences.get("prefer_offense", False):
            red_score += 2
        if player_preferences.get("prefer_defense", False):
            blue_score += 2

        if player_preferences.get("creative_thinker", False):
            red_score += 1
        if player_preferences.get("analytical_thinker", False):
            blue_score += 1

        if player_preferences.get("like_puzzles", False):
            red_score += 1
        if player_preferences.get("like_monitoring", False):
            blue_score += 1

        # Return recommendation
        if red_score > blue_score:
            return TeamRole.RED
        elif blue_score > red_score:
            return TeamRole.BLUE
        else:
            return TeamRole.RED  # Default to Red if tied
