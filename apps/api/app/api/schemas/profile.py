from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfilePreferences(BaseModel):
    style: list[str] | None = None
    hotel_prefs: str | None = None
    flight_prefs: str | None = None
    food_prefs: str | None = None
    activity_prefs: str | None = None
    accessibility: str | None = None
    visa_notes: str | None = None
    constraints: str | None = None


class ProfileUpsertRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    nationality: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    passport_number: str | None = Field(default=None, max_length=20)
    clear_passport: bool = False
    passport_expiry: date | None = None
    preferences: ProfilePreferences | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    nationality: str | None = None
    date_of_birth: date | None = None
    passport_masked: str | None = None
    has_passport: bool = False
    passport_expiry: date | None = None
    preferences: ProfilePreferences | None = None
    created_at: datetime
    updated_at: datetime
