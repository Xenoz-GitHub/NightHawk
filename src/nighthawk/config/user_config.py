"""ENCRYPTED CREW - User configuration management."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import os

from pydantic import BaseModel, Field


class ThemeConfig(BaseModel):
    """Theme and color configuration."""
    primary_color: str = Field(default="cyan", description="Primary UI color")
    success_color: str = Field(default="green", description="Success message color")
    error_color: str = Field(default="red", description="Error message color")
    warning_color: str = Field(default="yellow", description="Warning message color")
    info_color: str = Field(default="cyan", description="Info message color")
    show_banner: bool = Field(default=True, description="Show ASCII banner on commands")
    use_emoji: bool = Field(default=True, description="Use emoji icons in output")


class ScanConfig(BaseModel):
    """Default scan configuration."""
    default_timeout: int = Field(default=30, description="Default timeout in seconds")
    max_threads: int = Field(default=10, description="Maximum concurrent threads")
    rate_limit: int = Field(default=10, description="Requests per second limit")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    user_agent: str = Field(
        default="ENCRYPTED-CREW-NIGHTHAWK/2.0.0",
        description="User agent string"
    )


class ReportConfig(BaseModel):
    """Report generation configuration."""
    default_format: str = Field(default="html", description="Default report format")
    include_raw_data: bool = Field(default=False, description="Include raw scan data")
    redact_secrets: bool = Field(default=True, description="Redact sensitive information")
    timestamp_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="Timestamp format")


class UserConfig(BaseModel):
    """User configuration for ENCRYPTED CREW NIGHTHAWK."""
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    scan: ScanConfig = Field(default_factory=ScanConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)
    
    # Global settings
    auto_create_scope: bool = Field(
        default=False,
        description="Automatically create scope.yaml if missing"
    )
    strict_scope: bool = Field(
        default=True,
        description="Enforce strict scope validation"
    )
    verbose: bool = Field(default=False, description="Enable verbose output")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Paths
    default_scope_file: str = Field(default="scope.yaml", description="Default scope file")
    output_directory: str = Field(default="./nighthawk-output", description="Output directory")


class ConfigManager:
    """Manage user configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager."""
        if config_path is None:
            # Try user home directory first, fall back to current directory
            home_config = Path.home() / ".nighthawk" / "config.json"
            local_config = Path(".nighthawk") / "config.json"
            
            if home_config.exists():
                config_path = home_config
            elif local_config.exists():
                config_path = local_config
            else:
                # Create in user home by default
                config_path = home_config
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> UserConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserConfig(**data)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
                return UserConfig()
        else:
            return UserConfig()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config.model_dump(), f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key."""
        keys = key.split('.')
        obj = self.config
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                raise AttributeError(f"Invalid config key: {key}")
        setattr(obj, keys[-1], value)
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config = UserConfig()
    
    def export_example(self, path: Path) -> None:
        """Export example configuration file."""
        example_config = UserConfig()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(example_config.model_dump(), f, indent=2)


# Global config instance
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


def reload_config() -> None:
    """Reload configuration from file."""
    global _global_config
    _global_config = ConfigManager()
