from __future__ import annotations

from pydantic import BaseModel, Field


class CalendarEventResponse(BaseModel):
    title: str
    start: str
    end: str
    location: str
    source: str


class CalendarResponse(BaseModel):
    source: str
    items: list[CalendarEventResponse] = Field(default_factory=list)
    note: str | None = None
