"""Traveler profile domain validation."""

from __future__ import annotations

from datetime import date


class ProfileValidationError(ValueError):
    """Raised when traveler profile input is invalid."""


def validate_profile_fields(
    *,
    full_name: str,
    nationality: str | None = None,
    date_of_birth: date | None = None,
    passport_expiry: date | None = None,
) -> None:
    if not full_name.strip():
        raise ProfileValidationError("Full name is required.")
    if len(full_name.strip()) > 200:
        raise ProfileValidationError("Full name is too long.")
    if nationality is not None and len(nationality.strip()) > 100:
        raise ProfileValidationError("Nationality is too long.")
    if date_of_birth is not None and date_of_birth >= date.today():
        raise ProfileValidationError("Date of birth must be in the past.")
    if passport_expiry is not None and passport_expiry < date.today():
        raise ProfileValidationError("Passport expiry must be today or in the future.")
