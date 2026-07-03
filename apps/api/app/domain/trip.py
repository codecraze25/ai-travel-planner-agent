from __future__ import annotations

from datetime import date
from enum import StrEnum


class TripStatus(StrEnum):
    DRAFT = "draft"
    PLANNING = "planning"
    READY = "ready"
    ARCHIVED = "archived"


class TripValidationError(ValueError):
    """Raised when trip input fails domain validation."""


def validate_trip_fields(
    *,
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
    travelers: int,
    budget_usd: float,
    require_future_dates: bool = True,
) -> None:
    if not origin.strip():
        raise TripValidationError("Origin city is required.")
    if not destination.strip():
        raise TripValidationError("Destination is required.")
    if end_date < start_date:
        raise TripValidationError("End date must be on or after start date.")
    if require_future_dates and start_date < date.today():
        raise TripValidationError("Start date must be in the future for new trips.")
    if travelers < 1:
        raise TripValidationError("Travelers must be at least 1.")
    if budget_usd <= 0:
        raise TripValidationError("Budget must be greater than zero.")
