"""SQLAlchemy ORM models for persistence."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, Float, DateTime, JSON, ForeignKey, Integer, Text,
    Boolean, Enum as SQLAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from nighthawk.database.engine import Base
from nighthawk.models.core import Severity, ConfidenceLevel


class CampaignDB(Base):
    __tablename__ = "campaigns"

    id = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(128), nullable=False)
    scope_path = mapped_column(String(512), nullable=True)
    started_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    status = mapped_column(String(32), default="running")

    findings = relationship("FindingDB", back_populates="campaign", cascade="all, delete-orphan")


class FindingDB(Base):
    __tablename__ = "findings"

    id = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = mapped_column(Uuid(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    title = mapped_column(String(256), nullable=False)
    description = mapped_column(Text, nullable=False)
    severity = mapped_column(SQLAEnum(Severity, native_enum=False), nullable=False)
    confidence = mapped_column(Float, nullable=False, default=0.0)
    category = mapped_column(String(128), nullable=False)
    asset_id = mapped_column(String(64), nullable=True)
    remediation = mapped_column(Text, nullable=False)
    references = mapped_column(JSON, default=list)
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    campaign = relationship("CampaignDB", back_populates="findings")


class AssetDB(Base):
    __tablename__ = "assets"

    id = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = mapped_column(String(256), nullable=True)
    ip_addresses = mapped_column(JSON, default=list)
    platform = mapped_column(String(32), default="unknown")
    os_name = mapped_column(String(128), nullable=True)
    os_version = mapped_column(String(128), nullable=True)
    services = mapped_column(JSON, default=list)
    technologies = mapped_column(JSON, default=list)
    metadata = mapped_column(JSON, default=dict)
    first_seen = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ScanResultDB(Base):
    __tablename__ = "scan_results"

    id = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = mapped_column(Uuid(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    module = mapped_column(String(64), nullable=False)
    target = mapped_column(String(512), nullable=False)
    result_json = mapped_column(JSON, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
