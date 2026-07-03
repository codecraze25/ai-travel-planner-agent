from datetime import date

import pytest

from app.domain.trip import TripValidationError, validate_trip_fields


def test_validate_trip_fields_accepts_valid_input() -> None:
    validate_trip_fields(
        origin="San Francisco",
        destination="Tokyo",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        travelers=2,
        budget_usd=4000,
        require_future_dates=False,
    )


def test_validate_trip_fields_rejects_end_before_start() -> None:
    with pytest.raises(TripValidationError, match="End date"):
        validate_trip_fields(
            origin="San Francisco",
            destination="Tokyo",
            start_date=date(2026, 10, 15),
            end_date=date(2026, 10, 10),
            travelers=2,
            budget_usd=4000,
            require_future_dates=False,
        )


def test_validate_trip_fields_rejects_empty_origin() -> None:
    with pytest.raises(TripValidationError, match="Origin"):
        validate_trip_fields(
            origin="  ",
            destination="Tokyo",
            start_date=date(2026, 10, 10),
            end_date=date(2026, 10, 15),
            travelers=2,
            budget_usd=4000,
            require_future_dates=False,
        )
