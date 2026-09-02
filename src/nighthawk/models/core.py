"""Core Pydantic v2 models for NIGHTHAWK."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceLevel(str, Enum):
    CONFIRMED = "confirmed"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    """Evidence supporting a finding."""

    description: str
    source: str
    value: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("value")
    @classmethod
    def redact_value(cls, v: str | None) -> str | None:
        if v is None:
            return None
        # Basic redaction for potential secrets
        if any(keyword in v.lower() for keyword in ("secret", "token", "password", "key", "credential")):
            if len(v) > 12:
                return v[:6] + "*" * (len(v) - 10) + v[-4:]
        return v


class Finding(BaseModel):
    """Standardized security finding."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    description: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    category: str
    asset_id: uuid.UUID | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    remediation: str
    references: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict_redacted(self) -> dict[str, Any]:
        """Serialize with redacted evidence values."""
        d = self.model_dump(mode="json")
        for ev in d.get("evidence", []):
            val = ev.get("value")
            if val is not None and len(val) > 8:
                ev["value"] = val[:4] + "*" * (len(val) - 8) + val[-4:]
        return d


class Asset(BaseModel):
    """Discovered asset representation."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    hostname: str | None = None
    ip_addresses: list[str] = Field(default_factory=list)
    platform: str = "unknown"
    os_name: str | None = None
    os_version: str | None = None
    services: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceInfo(BaseModel):
    """Observable service descriptor."""

    port: int
    protocol: str = "tcp"
    state: str = "unknown"
    service_name: str | None = None
    banner: str | None = None
    version: str | None = None


class TechnologyMatch(BaseModel):
    """Detected technology with evidence."""

    name: str
    category: str
    confidence_level: ConfidenceLevel = ConfidenceLevel.POSSIBLE
    evidence: list[str] = Field(default_factory=list)
    version: str | None = None
    version_confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class NetworkScanResult(BaseModel):
    """Result of a network scan operation."""

    target: str
    scan_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ScopeConfig(BaseModel):
    """Authorized assessment scope."""

    model_config = ConfigDict(extra="ignore")

    VALID_MODULES: ClassVar[set[str]] = {
        "web",
        "network",
        "secrets",
        "tech",
        "technology",
        "dns",
        "http",
        "tls",
        "service_enumeration",
        "secret_scanning",
    }

    name: str = "default_scope"
    domains: list[str] = Field(default_factory=list)
    ips: list[str] = Field(default_factory=list)
    cidrs: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    repositories: list[str] = Field(default_factory=list)
    allowed_modules: list[str] = Field(default_factory=list)
    rate_limits: dict[str, Any] = Field(default_factory=dict)

    @field_validator("allowed_modules")
    @classmethod
    def validate_allowed_modules(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            module_name = str(item).strip().lower()
            if not module_name:
                continue
            canonical = {
                "http": "web",
                "https": "web",
                "tls": "web",
                "technology": "tech",
                "technologies": "tech",
                "secret_scanning": "secrets",
                "service_enumeration": "network",
            }.get(module_name, module_name)
            if canonical not in cls.VALID_MODULES:
                valid = ", ".join(sorted(cls.VALID_MODULES))
                raise ValueError(f"Unsupported module '{item}'. Allowed modules: {valid}")
            normalized.append(canonical)
        return list(dict.fromkeys(normalized))
