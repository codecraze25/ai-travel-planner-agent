from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ActivityItem(BaseModel):
    id: str
    kind: str  # agent_action | audit
    action: str
    success: bool | None = None
    details: dict[str, object] | None = None
    error_message: str | None = None
    created_at: datetime


class ActivityListResponse(BaseModel):
    items: list[ActivityItem] = Field(default_factory=list)
