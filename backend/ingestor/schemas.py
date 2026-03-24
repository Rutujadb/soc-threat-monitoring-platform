from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestPayload(BaseModel):
    """Raw log envelope from clients / simulator."""

    source_type: str
    timestamp: datetime | None = None
    log: dict[str, Any] = Field(default_factory=dict)


class UnifiedEventDTO(BaseModel):
    timestamp: datetime
    source_type: str
    source_ip: str | None = None
    destination_ip: str | None = None
    hostname: str | None = None
    username: str | None = None
    action: str | None = None
    result: str | None = None
    raw: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
