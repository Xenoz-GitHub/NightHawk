"""Tests for game engine."""

import pytest
from pathlib import Path
import json

from nighthawk.game.engine import GameEngine
from nighthawk.game.player import Team
from nighthawk.game.currency import TransactionCategory
from nighthawk.game.reputation import ReputationType


class TestGameEngine:
    """Test game engine functionality."""
    
    def test_initialize_new_game(self):
        """Test creating a new game."""
        engine = GameEngine()
        
        success = engine.initialize_new_game("TestPlayer")
        
        assert success is True
        assert engine.is_initialized is True
        assert engine.player is not None
        assert engine.player.get_profile().username == "TestPlayer"
        assert engine.currency is not None
        assert engine.reputation is not None
    
    def test_team_selection(self):
        """Test team selection."""
        engine = GameEngine()
        engine.initialize_new_game("RedTeamPlayer")
        
        # Select red team
        success = engine.select_team("red")
        
        assert success is True
        assert engine.player.get_profile().team == Team.RED
        assert engine.skill_tree is not None
        assert engine.skill_tree.team == "red"
    
    def test_award_xp(self):
        """Test XP awarding."""
        engine = GameEngine()
        engine.initialize_new_game("XPPlayer")
        engine.select_team("blue")
        
        # Award XP
        result = engine.award_xp(1000, "test")
        
        assert result["xp_gained"] == 1000
        assert engine.player.get_profile().xp == 1000
    
    def test_level_up(self):
        """Test leveling up."""
        engine = GameEngine()
        engine.initialize_new_game("LevelUpPlayer")
        engine.select_team("red")
        
        # Award enough XP to level up
        result = engine.award_xp(5000, "level up test")
        
        assert result["level_up"] is True
        assert result["new_level"] > 1
        assert "skill_points_gained" in result
    
    def test_currency_operations(self):
        """Test currency operations."""
        engine = GameEngine()
        engine.initialize_new_game("MoneyPlayer")
        
        initial_balance = engine.currency.get_balance()
        
        # Award currency
        engine.award_currency(1000, TransactionCategory.MISSION, "Test mission")
        assert engine.currency.get_balance() == initial_balance + 1000
        
        # Spend currency
        success = engine.spend_currency(500, TransactionCategory.TOOL_PURCHASE, "Test tool")
        assert success is True
        assert engine.currency.get_balance() == initial_balance + 500
    
    def test_reputation_award(self):
        """Test reputation awarding."""
        engine = GameEngine()
        engine.initialize_new_game("ReputationPlayer")
        
        # Award reputation
        success = engine.award_reputation("underground", 50, "Test action")
        
        assert success is True
        faction = engine.reputation.get_faction(ReputationType.UNDERGROUND)
        assert faction.reputation == 50
    
    def test_save_and_load(self, tmp_path):
        """Test save and load functionality."""
        # Override save directory for testing
        GameEngine.SAVE_DIR = tmp_path
        
        # Create and save game
        engine1 = GameEngine()
        engine1.initialize_new_game("SaveTestPlayer")
        engine1.select_team("red")
        engine1.award_xp(2000, "test")
        engine1.award_currency(5000, TransactionCategory.BOUNTY)
        
        save_success = engine1.save_game(slot=1)
        assert save_success is True
        
        # Load game
        engine2 = GameEngine()
        load_success = engine2.load_game(slot=1)
        
        assert load_success is True
        assert engine2.player.get_profile().username == "SaveTestPlayer"
        assert engine2.player.get_profile().team == Team.RED
        assert engine2.player.get_profile().xp == 2000
    
    def test_skill_upgrade(self):
        """Test skill upgrading."""
        engine = GameEngine()
        engine.initialize_new_game("SkillPlayer")
        engine.select_team("red")
        
        # Get first skill
        first_skill_id = None
        if engine.skill_tree and engine.skill_tree.skills:
            for category in engine.skill_tree.skills.values():
                if category:
                    first_skill_id = category[0].node_id
                    break
        
        if first_skill_id:
            # Upgrade skill
            result = engine.upgrade_skill(first_skill_id)
            
            assert result["success"] is True
            assert result["new_level"] > 0
    
    def test_achievement_unlock(self):
        """Test achievement unlocking."""
        engine = GameEngine()
        engine.initialize_new_game("AchievementPlayer")
        
        # Unlock achievement
        result = engine.unlock_achievement("first_mission")
        
        assert result["success"] is True
        assert "first_mission" in engine.player.get_profile().achievements
    
    def test_game_state(self):
        """Test getting game state."""
        engine = GameEngine()
        engine.initialize_new_game("StatePlayer")
        engine.select_team("blue")
        
        state = engine.get_game_state()
        
        assert state["initialized"] is True
        assert state["player"]["username"] == "StatePlayer"
        assert state["player"]["team"] == "blue"
        assert "currency" in state
        assert "reputation" in state
        assert "skills" in state


class TestPlayerProfile:
    """Test player profile functionality."""
    
    def test_profile_creation(self):
        """Test creating player profile."""
        from nighthawk.game.player import PlayerProfile
        
        profile = PlayerProfile(username="TestUser")
        
        assert profile.username == "TestUser"
        assert profile.team == Team.NEUTRAL
        assert profile.level == 1
        assert profile.xp == 0
        assert profile.currency == 0
    
    def test_xp_progression(self):
        """Test XP and leveling."""
        from nighthawk.game.player import PlayerProfile
        
        profile = PlayerProfile(username="XPTest")
        
        # Add XP
        new_level = profile.add_xp(5000)
        
        assert profile.xp == 5000
        assert profile.level > 1
        assert new_level > 1
    
    def test_currency_operations(self):
        """Test currency operations."""
        from nighthawk.game.player import PlayerProfile
        
        profile = PlayerProfile(username="MoneyTest")
        
        # Add currency
        profile.add_currency(1000)
        assert profile.currency == 1000
        
        # Spend currency
        success = profile.spend_currency(500)
        assert success is True
        assert profile.currency == 500
        
        # Try to overspend
        success = profile.spend_currency(1000)
        assert success is False
        assert profile.currency == 500


class TestCryptoCreds:
    """Test currency system."""
    
    def test_currency_creation(self):
        """Test creating currency system."""
        from nighthawk.game.currency import CryptoCreds
        
        currency = CryptoCreds()
        
        assert currency.get_balance() == CryptoCreds.STARTING_BALANCE
    
    def test_add_currency(self):
        """Test adding currency."""
        from nighthawk.game.currency import CryptoCreds
        
        currency = CryptoCreds(initial_balance=0)
        
        transaction = currency.add(1000, description="Test add")
        
        assert currency.get_balance() == 1000
        assert transaction.amount == 1000
        assert len(currency.transaction_history) == 1
    
    def test_spend_currency(self):
        """Test spending currency."""
        from nighthawk.game.currency import CryptoCreds
        
        currency = CryptoCreds(initial_balance=1000)
        
        transaction = currency.spend(500, description="Test spend")
        
        assert transaction is not None
        assert currency.get_balance() == 500
    
    def test_insufficient_funds(self):
        """Test spending with insufficient funds."""
        from nighthawk.game.currency import CryptoCreds
        
        currency = CryptoCreds(initial_balance=100)
        
        transaction = currency.spend(500, description="Test overspend")
        
        assert transaction is None
        assert currency.get_balance() == 100


class TestSkillTree:
    """Test skill tree system."""
    
    def test_red_team_skills(self):
        """Test red team skill tree."""
        from nighthawk.game.progression import SkillTree
        
        tree = SkillTree(team="red")
        
        assert tree.team == "red"
        assert len(tree.skills) > 0
        assert "exploitation" in tree.skills
    
    def test_blue_team_skills(self):
        """Test blue team skill tree."""
        from nighthawk.game.progression import SkillTree
        
        tree = SkillTree(team="blue")
        
        assert tree.team == "blue"
        assert len(tree.skills) > 0
        assert "detection" in tree.skills
    
    def test_skill_upgrade(self):
        """Test upgrading skills."""
        from nighthawk.game.progression import SkillTree
        
        tree = SkillTree(team="red")
        tree.add_skill_points(5)
        
        # Get first skill
        first_skill = None
        for category in tree.skills.values():
            if category:
                first_skill = category[0]
                break
        
        if first_skill:
            success = tree.upgrade_skill(first_skill.node_id)
            assert success is True
            assert first_skill.current_level > 0


class TestReputationSystem:
    """Test reputation system."""
    
    def test_reputation_creation(self):
        """Test creating reputation system."""
        from nighthawk.game.reputation import ReputationSystem
        
        system = ReputationSystem()
        
        assert len(system.factions) == 4
    
    def test_add_reputation(self):
        """Test adding reputation."""
        from nighthawk.game.reputation import ReputationSystem, ReputationType
        
        system = ReputationSystem()
        
        change = system.add_reputation(
            ReputationType.UNDERGROUND,
            50,
            "Test action"
        )
        
        assert change.amount == 50
        faction = system.get_faction(ReputationType.UNDERGROUND)
        assert faction.reputation == 50
    
    def test_reputation_tiers(self):
        """Test reputation tier progression."""
        from nighthawk.game.reputation import ReputationSystem, ReputationType, ReputationTier
        
        system = ReputationSystem()
        faction = system.get_faction(ReputationType.UNDERGROUND)
        
        # Unknown tier
        assert faction.get_tier() == ReputationTier.UNKNOWN
        
        # Add reputation to reach Noticed
        faction.add_reputation(100, "Progress test")
        assert faction.get_tier() == ReputationTier.NOTICED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
