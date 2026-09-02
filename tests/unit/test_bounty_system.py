"""Unit tests for bounty system."""

import pytest
from datetime import datetime, timedelta

from nighthawk.game.bounty import (
    BountyBoard, BountyMission, ClientProfile, ClientType, 
    MissionDifficulty, MissionStatus, ClientReputation
)
from nighthawk.game.mission_generator import MissionGenerator


class TestClientProfile:
    """Test ClientProfile class."""
    
    def test_create_client(self):
        """Test creating a client profile."""
        client = ClientProfile(
            client_type=ClientType.SHADOW_BROKER,
            name="ShadowBroker",
            description="High-risk missions"
        )
        
        assert client.name == "ShadowBroker"
        assert client.client_type == ClientType.SHADOW_BROKER
        assert client.reputation_tier == ClientReputation.UNKNOWN
    
    def test_client_id_generated(self):
        """Test that client ID is auto-generated."""
        client1 = ClientProfile()
        client2 = ClientProfile()
        
        assert client1.client_id != client2.client_id
        assert len(client1.client_id) > 0


class TestBountyMission:
    """Test BountyMission class."""
    
    def test_create_mission(self):
        """Test creating a bounty mission."""
        client = ClientProfile(client_type=ClientType.CORPORATE_GUARDIAN)
        mission = BountyMission(
            client=client,
            title="Test Mission",
            description="Test description",
            difficulty=MissionDifficulty.MEDIUM,
            base_reward=2000,
        )
        
        assert mission.title == "Test Mission"
        assert mission.status == MissionStatus.AVAILABLE
        assert mission.base_reward == 2000
    
    def test_mission_expiration(self):
        """Test mission expiration check."""
        mission = BountyMission(
            title="Test",
            time_limit_hours=0,  # Already expired
        )
        
        # Set deadline to past
        mission.deadline = datetime.now() - timedelta(hours=1)
        
        assert mission.is_expired()
    
    def test_mission_not_expired(self):
        """Test mission not expired."""
        mission = BountyMission(
            title="Test",
            time_limit_hours=24,
        )
        
        assert not mission.is_expired()
    
    def test_time_remaining(self):
        """Test time remaining calculation."""
        mission = BountyMission(
            title="Test",
            time_limit_hours=24,
        )
        
        remaining = mission.time_remaining()
        assert remaining is not None
        assert remaining.total_seconds() > 0
    
    def test_dynamic_reward_calculation(self):
        """Test dynamic reward calculation."""
        mission = BountyMission(
            title="Test",
            base_reward=1000,
            xp_reward=100,
            difficulty=MissionDifficulty.MEDIUM,
            required_level=10,
        )
        
        # Same level as required
        crypto, xp = mission.calculate_dynamic_reward(player_level=10)
        assert crypto == 1000
        assert xp == 100
        
        # Higher level
        crypto, xp = mission.calculate_dynamic_reward(player_level=20)
        assert crypto > 1000
        assert xp > 100
    
    def test_difficulty_multipliers(self):
        """Test difficulty multipliers on rewards."""
        mission_easy = BountyMission(
            title="Easy",
            base_reward=1000,
            difficulty=MissionDifficulty.EASY,
            required_level=1,
        )
        
        mission_hard = BountyMission(
            title="Hard",
            base_reward=1000,
            difficulty=MissionDifficulty.HARD,
            required_level=1,
        )
        
        easy_crypto, _ = mission_easy.calculate_dynamic_reward(player_level=1)
        hard_crypto, _ = mission_hard.calculate_dynamic_reward(player_level=1)
        
        assert hard_crypto > easy_crypto


class TestBountyBoard:
    """Test BountyBoard class."""
    
    def test_board_initialization(self):
        """Test bounty board initialization."""
        board = BountyBoard()
        
        assert board.max_visible_missions == 20
        assert len(board.clients) == 5  # 5 default clients
    
    def test_get_client_by_type(self):
        """Test getting client by type."""
        board = BountyBoard()
        
        client = board.get_client_by_type(ClientType.SHADOW_BROKER)
        assert client is not None
        assert client.client_type == ClientType.SHADOW_BROKER
    
    def test_post_mission(self):
        """Test posting a mission."""
        board = BountyBoard()
        mission = BountyMission(title="Test Mission")
        
        mission_id = board.post_mission(mission)
        
        assert mission_id == mission.mission_id
        assert mission_id in board.missions
    
    def test_get_available_missions(self):
        """Test getting available missions."""
        board = BountyBoard()
        
        # Post some missions
        for i in range(5):
            mission = BountyMission(
                title=f"Mission {i}",
                status=MissionStatus.AVAILABLE if i < 3 else MissionStatus.COMPLETED
            )
            board.post_mission(mission)
        
        available = board.get_available_missions()
        
        assert len(available) == 3
        assert all(m.status == MissionStatus.AVAILABLE for m in available)
    
    def test_accept_mission(self):
        """Test accepting a mission."""
        board = BountyBoard()
        mission = BountyMission(title="Test")
        board.post_mission(mission)
        
        success = board.accept_mission(mission.mission_id, "player1")
        
        assert success
        assert mission.status == MissionStatus.ACCEPTED
        assert mission.acceptance_count == 1
    
    def test_accept_expired_mission_fails(self):
        """Test that accepting expired mission fails."""
        board = BountyBoard()
        mission = BountyMission(
            title="Expired",
            time_limit_hours=0,
        )
        mission.deadline = datetime.now() - timedelta(hours=1)
        board.post_mission(mission)
        
        success = board.accept_mission(mission.mission_id, "player1")
        
        assert not success
        assert mission.status == MissionStatus.EXPIRED
    
    def test_complete_mission(self):
        """Test completing a mission."""
        board = BountyBoard()
        mission = BountyMission(
            title="Test",
            base_reward=1000,
            xp_reward=100,
        )
        board.post_mission(mission)
        board.accept_mission(mission.mission_id, "player1")
        
        crypto, xp, success = board.complete_mission(mission.mission_id, player_level=1)
        
        assert success
        assert crypto >= 1000  # At least base reward
        assert xp >= 100
        assert mission.status == MissionStatus.COMPLETED
        assert mission.completion_count == 1
    
    def test_fail_mission(self):
        """Test failing a mission."""
        board = BountyBoard()
        mission = BountyMission(title="Test")
        board.post_mission(mission)
        board.accept_mission(mission.mission_id, "player1")
        
        success = board.fail_mission(mission.mission_id)
        
        assert success
        assert mission.status == MissionStatus.FAILED
        assert mission.failure_count == 1
    
    def test_player_active_missions(self):
        """Test getting player's active missions."""
        board = BountyBoard()
        mission1 = BountyMission(title="Mission 1")
        mission2 = BountyMission(title="Mission 2")
        
        board.post_mission(mission1)
        board.post_mission(mission2)
        
        board.accept_mission(mission1.mission_id, "player1")
        board.accept_mission(mission2.mission_id, "player1")
        
        active = board.get_player_active_missions()
        
        assert len(active) == 2
    
    def test_player_mission_history(self):
        """Test getting player's mission history."""
        board = BountyBoard()
        mission1 = BountyMission(title="Mission 1", base_reward=1000)
        mission2 = BountyMission(title="Mission 2", base_reward=2000)
        
        board.post_mission(mission1)
        board.post_mission(mission2)
        
        board.accept_mission(mission1.mission_id, "player1")
        board.accept_mission(mission2.mission_id, "player1")
        
        board.complete_mission(mission1.mission_id, player_level=1)
        board.complete_mission(mission2.mission_id, player_level=1)
        
        history = board.get_player_mission_history()
        
        assert len(history) == 2
        assert all(m.status == MissionStatus.COMPLETED for m in history)
    
    def test_mission_stats(self):
        """Test getting mission statistics."""
        board = BountyBoard()
        
        mission = BountyMission(title="Test")
        board.post_mission(mission)
        board.accept_mission(mission.mission_id, "player1")
        
        stats = board.get_mission_stats()
        
        assert stats['total_missions_posted'] == 1
        assert stats['available_missions'] == 0  # Was accepted
        assert stats['active_missions'] == 1
        assert stats['completed_missions'] == 0
    
    def test_update_client_reputation(self):
        """Test updating client reputation."""
        board = BountyBoard()
        client = list(board.clients.values())[0]
        tier_order = list(ClientReputation)
        original_index = tier_order.index(client.reputation_tier)

        board.update_client_reputation(client.client_id, 1)

        # Reputation should improve or stay same (tier order, not str ordering)
        assert tier_order.index(client.reputation_tier) >= original_index


class TestMissionGenerator:
    """Test MissionGenerator class."""
    
    def test_generate_mission(self):
        """Test generating a single mission."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission(
            difficulty=MissionDifficulty.MEDIUM,
            player_level=10
        )
        
        assert mission.title
        assert mission.description
        assert mission.difficulty == MissionDifficulty.MEDIUM
        assert mission.base_reward > 0
        assert mission.xp_reward > 0
    
    def test_generate_easy_mission(self):
        """Test generating an easy mission."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission(
            difficulty=MissionDifficulty.EASY,
            player_level=1
        )
        
        assert mission.difficulty == MissionDifficulty.EASY
        # Easy missions should have lower rewards
        assert mission.base_reward < 2000
    
    def test_generate_legendary_mission(self):
        """Test generating a legendary mission."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission(
            difficulty=MissionDifficulty.LEGENDARY,
            player_level=50
        )
        
        assert mission.difficulty == MissionDifficulty.LEGENDARY
        # Legendary missions should have high rewards
        assert mission.base_reward >= 100000
    
    def test_generate_batch(self):
        """Test generating batch of missions."""
        generator = MissionGenerator()
        
        missions = generator.generate_batch(count=5, player_level=10)
        
        assert len(missions) == 5
        assert all(m.title for m in missions)
    
    def test_generate_daily_missions(self):
        """Test generating daily mission refresh."""
        generator = MissionGenerator()
        
        missions = generator.generate_daily_missions(count=10, player_level=5)
        
        assert len(missions) == 10
        assert all(m.status == MissionStatus.AVAILABLE for m in missions)
    
    def test_generate_mission_for_client(self):
        """Test generating mission for specific client."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission_for_client(
            client_type=ClientType.SHADOW_BROKER,
            player_level=20
        )
        
        assert mission.client.client_type == ClientType.SHADOW_BROKER
    
    def test_mission_objectives(self):
        """Test that missions have objectives."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission(
            difficulty=MissionDifficulty.MEDIUM,
            player_level=10
        )
        
        assert len(mission.objectives) > 0
    
    def test_mission_has_target_info(self):
        """Test that missions have target information."""
        generator = MissionGenerator()
        
        mission = generator.generate_mission(
            difficulty=MissionDifficulty.MEDIUM,
            player_level=10
        )
        
        assert len(mission.target_info) > 0
        assert 'organization' in mission.target_info
        assert 'location' in mission.target_info


class TestBountySystemIntegration:
    """Integration tests for bounty system."""
    
    def test_full_mission_lifecycle(self):
        """Test complete mission lifecycle."""
        board = BountyBoard()
        generator = MissionGenerator()
        
        # Generate and post missions
        missions = generator.generate_batch(count=5, player_level=10)
        for mission in missions:
            board.post_mission(mission)
        
        # Get available missions
        available = board.get_available_missions(player_level=10)
        assert len(available) > 0
        
        # Accept a mission
        mission = available[0]
        board.accept_mission(mission.mission_id, "player1")
        
        # Check active missions
        active = board.get_player_active_missions()
        assert len(active) == 1
        
        # Complete the mission
        crypto, xp, success = board.complete_mission(mission.mission_id, player_level=10)
        assert success
        assert crypto > 0
        
        # Check history
        history = board.get_player_mission_history()
        assert len(history) == 1
    
    def test_multiple_missions_handling(self):
        """Test handling multiple concurrent missions."""
        board = BountyBoard()
        generator = MissionGenerator()
        
        # Generate multiple missions
        missions = generator.generate_batch(count=3, player_level=10)
        for mission in missions:
            board.post_mission(mission)
        
        # Accept all missions
        available = board.get_available_missions(player_level=10)
        for mission in available:
            board.accept_mission(mission.mission_id, "player1")
        
        active = board.get_player_active_missions()
        assert len(active) == 3
        
        # Complete one mission
        board.complete_mission(active[0].mission_id, player_level=10)
        
        # Should have 2 active, 1 completed
        active = board.get_player_active_missions()
        history = board.get_player_mission_history()
        
        assert len(active) == 2
        assert len(history) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
