from datetime import date, timedelta

import pytest

from app.domain.profile import ProfileValidationError, validate_profile_fields


def test_validate_profile_ok() -> None:
    validate_profile_fields(
        full_name="Ada Lovelace",
        nationality="UK",
        date_of_birth=date(1815, 12, 10),
        passport_expiry=date.today() + timedelta(days=365),
    )


def test_validate_profile_requires_name() -> None:
    with pytest.raises(ProfileValidationError):
        validate_profile_fields(full_name="  ")
