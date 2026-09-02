"""Save game management system."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import shutil
from datetime import datetime


class SaveManager:
    """Manage game save files."""
    
    SAVE_DIR = Path.home() / ".nighthawk" / "saves"
    BACKUP_DIR = Path.home() / ".nighthawk" / "backups"
    MAX_BACKUPS = 5
    
    def __init__(self):
        """Initialize save manager."""
        self.SAVE_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_save_path(self, slot: int) -> Path:
        """Get path for save slot."""
        return self.SAVE_DIR / f"save_slot_{slot}.json"
    
    def save_exists(self, slot: int) -> bool:
        """Check if save exists."""
        return self.get_save_path(slot).exists()
    
    def load_save(self, slot: int) -> Optional[Dict[str, Any]]:
        """Load save data from slot."""
        save_file = self.get_save_path(slot)
        
        if not save_file.exists():
            return None
        
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading save: {e}")
            return None
    
    def write_save(self, slot: int, data: Dict[str, Any]) -> bool:
        """Write save data to slot."""
        save_file = self.get_save_path(slot)
        
        try:
            # Create backup if save exists
            if save_file.exists():
                self._create_backup(slot)
            
            # Write save
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error writing save: {e}")
            return False
    
    def delete_save(self, slot: int) -> bool:
        """Delete save slot."""
        save_file = self.get_save_path(slot)
        
        try:
            if save_file.exists():
                # Create final backup before deletion
                self._create_backup(slot)
                save_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """Get metadata about save slot."""
        save_file = self.get_save_path(slot)
        
        if not save_file.exists():
            return None
        
        try:
            data = self.load_save(slot)
            if not data:
                return None
            
            player_data = data.get("player", {})
            
            return {
                "slot": slot,
                "username": player_data.get("username", "Unknown"),
                "team": player_data.get("team", "neutral"),
                "level": player_data.get("level", 1),
                "xp": player_data.get("xp", 0),
                "currency": data.get("currency", {}).get("balance", 0),
                "missions_completed": player_data.get("stats", {}).get("missions_completed", 0),
                "playtime": player_data.get("stats", {}).get("playtime_minutes", 0),
                "created_at": player_data.get("created_at", "Unknown"),
                "saved_at": data.get("saved_at", "Unknown"),
                "file_size": save_file.stat().st_size,
            }
        except Exception as e:
            print(f"Error getting save info: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save slots with info."""
        saves = []
        
        for slot in [1, 2, 3]:
            info = self.get_save_info(slot)
            if info:
                saves.append(info)
            else:
                saves.append({"slot": slot, "empty": True})
        
        return saves
    
    def _create_backup(self, slot: int) -> bool:
        """Create backup of save slot."""
        save_file = self.get_save_path(slot)
        
        if not save_file.exists():
            return False
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.BACKUP_DIR / f"save_slot_{slot}_backup_{timestamp}.json"
            
            # Copy save to backup
            shutil.copy2(save_file, backup_file)
            
            # Clean old backups
            self._cleanup_backups(slot)
            
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def _cleanup_backups(self, slot: int) -> None:
        """Clean old backups, keeping only MAX_BACKUPS."""
        try:
            # Find all backups for this slot
            backups = sorted(
                self.BACKUP_DIR.glob(f"save_slot_{slot}_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            
            # Delete old backups
            for backup in backups[self.MAX_BACKUPS:]:
                backup.unlink()
        except Exception as e:
            print(f"Error cleaning backups: {e}")
    
    def restore_backup(self, slot: int, backup_index: int = 0) -> bool:
        """
        Restore a backup.
        
        Args:
            slot: Save slot number
            backup_index: Index of backup (0 = most recent)
        
        Returns:
            True if successful
        """
        try:
            # Find backups for slot
            backups = sorted(
                self.BACKUP_DIR.glob(f"save_slot_{slot}_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            
            if backup_index >= len(backups):
                return False
            
            backup_file = backups[backup_index]
            save_file = self.get_save_path(slot)
            
            # Copy backup to save slot
            shutil.copy2(backup_file, save_file)
            
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self, slot: int) -> List[Dict[str, Any]]:
        """List all backups for slot."""
        try:
            backups = sorted(
                self.BACKUP_DIR.glob(f"save_slot_{slot}_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            
            return [
                {
                    "slot": slot,
                    "index": i,
                    "filename": backup.name,
                    "created_at": datetime.fromtimestamp(backup.stat().st_mtime).isoformat(),
                    "size": backup.stat().st_size,
                }
                for i, backup in enumerate(backups)
            ]
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def export_save(self, slot: int, export_path: Path) -> bool:
        """Export save to external file."""
        save_file = self.get_save_path(slot)
        
        if not save_file.exists():
            return False
        
        try:
            shutil.copy2(save_file, export_path)
            return True
        except Exception as e:
            print(f"Error exporting save: {e}")
            return False
    
    def import_save(self, import_path: Path, slot: int) -> bool:
        """Import save from external file."""
        if not import_path.exists():
            return False
        
        try:
            # Validate JSON
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if valid save format
            if "player" not in data or "currency" not in data:
                return False
            
            # Copy to save slot
            save_file = self.get_save_path(slot)
            shutil.copy2(import_path, save_file)
            
            return True
        except Exception as e:
            print(f"Error importing save: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        try:
            total_size = sum(
                f.stat().st_size
                for f in self.SAVE_DIR.glob("*.json")
            )
            
            backup_size = sum(
                f.stat().st_size
                for f in self.BACKUP_DIR.glob("*.json")
            )
            
            save_count = len(list(self.SAVE_DIR.glob("*.json")))
            backup_count = len(list(self.BACKUP_DIR.glob("*.json")))
            
            return {
                "save_directory": str(self.SAVE_DIR),
                "backup_directory": str(self.BACKUP_DIR),
                "total_save_size": total_size,
                "total_backup_size": backup_size,
                "save_count": save_count,
                "backup_count": backup_count,
            }
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {}
