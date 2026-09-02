"""NIGHTHAWK configuration management."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path


class NightHawkConfig(BaseSettings):
    """Strongly-typed configuration with environment/file precedence."""

    # Application identity
    app_name: str = "NIGHTHAWK"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", pattern=r"^(development|staging|production)$")

    # Database
    database_url: str = Field(default="sqlite:///./nighthawk.db")
    db_echo: bool = False
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)

    # API / Network
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_debug: bool = False
    api_workers: int = Field(default=1, ge=1, le=16)

    # Scope / Safety
    default_scope_path: str = "./scope.yaml"
    max_concurrency: int = Field(default=10, ge=1, le=50)
    rate_limit_rps: float = Field(default=5.0, ge=0.1, le=30.0)
    request_timeout: float = Field(default=10.0, ge=1.0, le=120.0)

    # Logging
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: str = "structured"
    structlog_dev_mode: bool = False

    # Security / Redaction
    redact_secrets: bool = True
    redact_reports: bool = True

    # API auth / CORS (Phase 8 hardening). When `api_token` is set, every
    # /api/v1 route requires `Authorization: Bearer <token>`.
    api_token: str | None = None
    cors_origins: str = ""  # comma-separated allowed origins; empty = CORS off

    # Platform
    platform: str = Field(default="linux", pattern=r"^(linux|windows|darwin)$")

    model_config = {
        "env_prefix": "NIGHTHAWK_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @field_validator("database_url")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        allowed = ("sqlite", "postgresql", "postgres", "mysql")
        if not any(scheme in v for scheme in allowed):
            raise ValueError(f"Unsupported database URL scheme in: {v}")
        return v


_CONFIG_INSTANCE: NightHawkConfig | None = None


def get_config() -> NightHawkConfig:
    """Singleton-style access to validated configuration."""
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None:
        _CONFIG_INSTANCE = NightHawkConfig()
    return _CONFIG_INSTANCE
