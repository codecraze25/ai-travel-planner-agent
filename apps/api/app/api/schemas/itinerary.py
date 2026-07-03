from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItineraryBlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    day_number: int
    time_block: str
    title: str
    description: str
    location: str | None = None
    est_cost_usd: float
    map_url: str | None = None
    backup_option: str | None = None


class ItineraryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    version: int
    total_est_cost_usd: float
    created_at: datetime
    items: list[ItineraryBlockResponse] = Field(default_factory=list)


class ItineraryGenerateRequest(BaseModel):
    regenerate_day: int | None = None
