"""Mission generator for dynamic bounty mission creation."""

import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from nighthawk.game.bounty import (
    BountyMission, ClientProfile, ClientType, MissionDifficulty, 
    MissionStatus, ClientReputation
)


class MissionGenerator:
    """Generate dynamic bounty missions."""
    
    # Mission templates for different difficulties and types
    MISSION_TEMPLATES = {
        MissionDifficulty.EASY: {
            "titles": [
                "Basic Network Reconnaissance",
                "Simple Web Application Scan",
                "Port Enumeration Exercise",
                "DNS Investigation",
                "Passive Information Gathering",
            ],
            "descriptions": [
                "Perform basic reconnaissance on the target",
                "Scan and identify open ports",
                "Gather DNS records and subdomains",
                "Identify web technologies",
                "Map out the network perimeter",
            ],
            "base_reward_range": (500, 1500),
            "xp_reward_range": (50, 150),
            "time_limit_hours_range": (12, 24),
            "required_skills": ["reconnaissance", "scanning"],
        },
        MissionDifficulty.MEDIUM: {
            "titles": [
                "Web Application Vulnerability Assessment",
                "Intermediate Penetration Test",
                "Social Engineering Campaign",
                "Network Intrusion Detection",
                "Active Directory Reconnaissance",
            ],
            "descriptions": [
                "Identify web vulnerabilities (OWASP Top 10)",
                "Perform full penetration test",
                "Execute targeted phishing campaign",
                "Detect network intrusions",
                "Enumerate Active Directory users and groups",
            ],
            "base_reward_range": (2000, 5000),
            "xp_reward_range": (150, 300),
            "time_limit_hours_range": (24, 72),
            "required_skills": ["exploitation", "social_engineering", "network_security"],
        },
        MissionDifficulty.HARD: {
            "titles": [
                "Advanced Penetration Test",
                "Zero-Day Exploitation",
                "Multi-Stage Attack Chain",
                "Enterprise Network Breach",
                "APT-Style Campaign",
            ],
            "descriptions": [
                "Execute a full-chain exploitation attack",
                "Discover and exploit a zero-day vulnerability",
                "Chain multiple exploits together",
                "Breach enterprise network perimeter",
                "Conduct advanced persistent threat operation",
            ],
            "base_reward_range": (8000, 15000),
            "xp_reward_range": (300, 600),
            "time_limit_hours_range": (48, 120),
            "required_skills": ["exploitation", "post_exploitation", "stealth", "evasion"],
        },
        MissionDifficulty.EXPERT: {
            "titles": [
                "Nation-State Level Attack",
                "Secure Facility Infiltration",
                "Military-Grade Defense Bypass",
                "Cryptographic Algorithm Break",
                "Maximum Security System Compromise",
            ],
            "descriptions": [
                "Conduct nation-state caliber cyber operation",
                "Infiltrate heavily defended facility",
                "Bypass military-grade security",
                "Break advanced cryptographic systems",
                "Compromise maximum security infrastructure",
            ],
            "base_reward_range": (20000, 50000),
            "xp_reward_range": (600, 1200),
            "time_limit_hours_range": (72, 168),
            "required_skills": ["exploitation", "cryptography", "reverse_engineering", "post_exploitation"],
        },
        MissionDifficulty.LEGENDARY: {
            "titles": [
                "Save the World",
                "Quantum Computer Hack",
                "Satellite Network Infiltration",
                "Global Banking System Breach",
                "AI Security System Override",
            ],
            "descriptions": [
                "Save the world from cyber catastrophe",
                "Break quantum encryption",
                "Infiltrate satellite command centers",
                "Breach global banking networks",
                "Override AI-powered security systems",
            ],
            "base_reward_range": (100000, 500000),
            "xp_reward_range": (2000, 5000),
            "time_limit_hours_range": (168, 336),
            "required_skills": ["exploitation", "cryptography", "reverse_engineering", "ai", "aerospace"],
        },
    }
    
    RED_TEAM_OBJECTIVES = [
        "Gain initial access to the target system",
        "Escalate privileges to administrator level",
        "Establish persistent backdoor access",
        "Extract sensitive data from the target",
        "Maintain stealth throughout the operation",
        "Exfiltrate data without detection",
        "Deploy custom malware payload",
        "Compromise the target's credentials",
        "Disable security controls silently",
        "Map the internal network topology",
    ]
    
    BLUE_TEAM_OBJECTIVES = [
        "Detect all intrusion attempts",
        "Block malicious traffic",
        "Identify compromised accounts",
        "Investigate and respond to alerts",
        "Restore systems to known-good state",
        "Recover exfiltrated data evidence",
        "Strengthen defensive posture",
        "Hunt for indicators of compromise",
        "Conduct forensic analysis",
        "Implement security patches",
    ]
    
    CONSTRAINTS = [
        "Must avoid IDS/IPS detection",
        "Cannot modify system files",
        "Must maintain operational security",
        "Cannot trigger security alerts",
        "Time limit is strict - no extensions",
        "Must use only provided tools",
        "Cannot use external resources",
        "Detection results in mission failure",
    ]
    
    TARGET_INFO_TEMPLATES = {
        "organization": [
            "TechCorp Industries",
            "SecureBank Ltd",
            "MediHealth Systems",
            "GovNet Agency",
            "DefenseContractors Inc",
        ],
        "location": [
            "New York, USA",
            "London, UK",
            "Singapore",
            "Frankfurt, Germany",
            "Tokyo, Japan",
        ],
        "industry": [
            "Financial Services",
            "Healthcare",
            "Government",
            "Technology",
            "Defense",
        ],
    }
    
    def __init__(self):
        """Initialize mission generator."""
        self.generated_missions: Dict[str, BountyMission] = {}
    
    def generate_mission(self, 
                        difficulty: MissionDifficulty,
                        client_type: Optional[ClientType] = None,
                        player_level: int = 1,
                        is_red_team: bool = True) -> BountyMission:
        """
        Generate a dynamic bounty mission.
        
        Args:
            difficulty: Mission difficulty level
            client_type: Client type (random if None)
            player_level: Player's current level
            is_red_team: True for red team, False for blue team
        
        Returns:
            Generated BountyMission
        """
        # Select random client if not specified
        if client_type is None:
            client_type = random.choice(list(ClientType))
        
        client = ClientProfile(client_type=client_type)
        
        # Get template for difficulty
        template = self.MISSION_TEMPLATES.get(difficulty)
        if not template:
            template = self.MISSION_TEMPLATES[MissionDifficulty.MEDIUM]
        
        # Generate mission components
        title = random.choice(template["titles"])
        description = random.choice(template["descriptions"])
        
        base_reward_min, base_reward_max = template["base_reward_range"]
        base_reward = random.randint(base_reward_min, base_reward_max)
        
        xp_reward_min, xp_reward_max = template["xp_reward_range"]
        xp_reward = random.randint(xp_reward_min, xp_reward_max)
        
        time_min, time_max = template["time_limit_hours_range"]
        time_limit = random.randint(time_min, time_max)
        
        # Select objectives
        objectives_list = self.RED_TEAM_OBJECTIVES if is_red_team else self.BLUE_TEAM_OBJECTIVES
        num_objectives = random.randint(2, 4)
        objectives = random.sample(objectives_list, min(num_objectives, len(objectives_list)))
        
        # Generate target info
        target_org = random.choice(self.TARGET_INFO_TEMPLATES["organization"])
        target_location = random.choice(self.TARGET_INFO_TEMPLATES["location"])
        target_industry = random.choice(self.TARGET_INFO_TEMPLATES["industry"])
        
        target_info = {
            "organization": target_org,
            "location": target_location,
            "industry": target_industry,
            "primary_system": f"target-{random.randint(1, 100)}.com",
            "network_range": f"192.168.{random.randint(1, 255)}.0/24",
        }
        
        # Select constraints
        num_constraints = random.randint(1, 3)
        constraints = random.sample(self.CONSTRAINTS, min(num_constraints, len(self.CONSTRAINTS)))
        
        # Create mission
        mission = BountyMission(
            client=client,
            title=title,
            description=description,
            detailed_brief=f"{description}\n\nTarget: {target_org} ({target_industry} industry)\nLocation: {target_location}",
            difficulty=difficulty,
            status=MissionStatus.AVAILABLE,
            required_level=max(1, player_level - 2),
            required_skills=template["required_skills"],
            base_reward=base_reward,
            bonus_reward=int(base_reward * 0.1),  # 10% bonus
            xp_reward=xp_reward,
            reputation_reward=random.randint(5, 20),
            time_limit_hours=time_limit,
            objectives=objectives,
            target_info=target_info,
            constraints=constraints,
            tools_available=[
                "scanner", "exploit_framework", "payload_generator",
                "credential_manager", "network_monitor", "log_analyzer"
            ],
        )
        
        return mission
    
    def generate_batch(self, 
                       count: int,
                       difficulty: Optional[MissionDifficulty] = None,
                       player_level: int = 1) -> List[BountyMission]:
        """
        Generate a batch of missions.
        
        Args:
            count: Number of missions to generate
            difficulty: Specific difficulty or random if None
            player_level: Player's current level
        
        Returns:
            List of generated missions
        """
        missions = []
        
        for _ in range(count):
            if difficulty is None:
                # Random difficulty weighted towards player level
                diff_choice = random.choices(
                    list(MissionDifficulty),
                    weights=[1, 3, 2, 1, 0.5],  # Medium most common
                )[0]
            else:
                diff_choice = difficulty
            
            is_red_team = random.choice([True, False])
            mission = self.generate_mission(
                difficulty=diff_choice,
                player_level=player_level,
                is_red_team=is_red_team
            )
            missions.append(mission)
        
        return missions
    
    def generate_daily_missions(self, count: int = 10, player_level: int = 1) -> List[BountyMission]:
        """
        Generate daily mission refresh.
        
        Args:
            count: Number of daily missions
            player_level: Player's current level
        
        Returns:
            List of daily missions
        """
        return self.generate_batch(count, player_level=player_level)
    
    def generate_mission_for_client(self, 
                                   client_type: ClientType,
                                   player_level: int = 1) -> BountyMission:
        """
        Generate a mission from a specific client type.
        
        Args:
            client_type: Type of client requesting mission
            player_level: Player's current level
        
        Returns:
            Generated mission from specified client
        """
        # Client types have specialty difficulties
        difficulty_map = {
            ClientType.SHADOW_BROKER: MissionDifficulty.LEGENDARY,
            ClientType.CORPORATE_GUARDIAN: MissionDifficulty.MEDIUM,
            ClientType.GRAY_HAT_COLLECTIVE: MissionDifficulty.HARD,
            ClientType.DARK_NET_TRADER: MissionDifficulty.EXPERT,
            ClientType.WHITE_KNIGHT_SEC: MissionDifficulty.HARD,
        }
        
        difficulty = difficulty_map.get(client_type, MissionDifficulty.MEDIUM)
        
        # Add some randomness
        if random.random() < 0.3:
            difficulties = list(MissionDifficulty)
            difficulty = random.choice(difficulties)
        
        is_red_team = client_type in [
            ClientType.SHADOW_BROKER, 
            ClientType.DARK_NET_TRADER
        ]
        
        return self.generate_mission(
            difficulty=difficulty,
            client_type=client_type,
            player_level=player_level,
            is_red_team=is_red_team
        )
