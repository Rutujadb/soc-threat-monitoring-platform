import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Severity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AlertStatus(str, enum.Enum):
    new = "new"
    investigating = "investigating"
    escalated = "escalated"
    resolved = "resolved"
    false_positive = "false_positive"


class CaseStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    escalated = "escalated"
    resolved = "resolved"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    action: Mapped[str | None] = mapped_column(String(512), nullable=True)
    result: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSON, default=dict)

    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="event")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, default=utcnow)
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(256), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=AlertStatus.new.value, index=True)
    mitre_techniques: Mapped[list] = mapped_column(JSON, default=list)
    affected_host: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_ip: Mapped[str | None] = mapped_column(String(128), nullable=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    assigned_to: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    playbook_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    event: Mapped["Event"] = relationship("Event", back_populates="alerts")
    notes: Mapped[list["AlertNote"]] = relationship("AlertNote", back_populates="alert", cascade="all, delete-orphan")
    cases: Mapped[list["Case"]] = relationship("Case", secondary="case_alerts", back_populates="alerts")


class AlertNote(Base):
    __tablename__ = "alert_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    author: Mapped[str] = mapped_column(String(128), nullable=False, default="analyst")
    content: Mapped[str] = mapped_column(Text, nullable=False)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="notes")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default=Severity.medium.value)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=CaseStatus.open.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    alerts: Mapped[list["Alert"]] = relationship("Alert", secondary="case_alerts", back_populates="cases")


class CaseAlert(Base):
    __tablename__ = "case_alerts"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id"), primary_key=True)
