from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.trip import TripStatus


class TripPreferencesInput(BaseModel):
    style: list[str] | None = None
    hotel_prefs: str | None = None
    flight_prefs: str | None = None
    food_prefs: str | None = None
    activity_prefs: str | None = None
    accessibility: str | None = None
    visa_notes: str | None = None
    constraints: str | None = None


class TripPreferencesResponse(TripPreferencesInput):
    model_config = ConfigDict(from_attributes=True)


class TripCreateRequest(BaseModel):
    origin: str
    destination: str
    start_date: date
    end_date: date
    travelers: int = Field(ge=1)
    budget_usd: float = Field(gt=0)
    preferences: TripPreferencesInput | None = None


class TripUpdateRequest(BaseModel):
    origin: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    travelers: int | None = Field(default=None, ge=1)
    budget_usd: float | None = Field(default=None, gt=0)
    status: TripStatus | None = None
    preferences: TripPreferencesInput | None = None


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    origin: str
    destination: str
    start_date: date
    end_date: date
    travelers: int
    budget_usd: float
    status: TripStatus
    preferences: TripPreferencesResponse | None = None
    created_at: datetime
    updated_at: datetime


class TripListResponse(BaseModel):
    items: list[TripResponse]


def trip_model_to_response(trip: Any) -> TripResponse:
    prefs = None
    if trip.preferences is not None:
        prefs = TripPreferencesResponse.model_validate(trip.preferences)
    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        origin=trip.origin,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        travelers=trip.travelers,
        budget_usd=trip.budget_usd,
        status=trip.status,
        preferences=prefs,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )
