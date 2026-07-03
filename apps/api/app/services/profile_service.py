from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import TravelerProfileModel, UserModel
from app.adapters.db.repositories import TravelerProfileRepository
from app.api.schemas.profile import ProfilePreferences, ProfileResponse, ProfileUpsertRequest
from app.core.config import get_settings
from app.domain.crypto import (
    EncryptionError,
    decrypt_text,
    encrypt_text,
    mask_passport,
    validate_passport_number,
)
from app.domain.profile import ProfileValidationError, validate_profile_fields


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._profiles = TravelerProfileRepository(session)

    async def get_profile(self, user: UserModel) -> ProfileResponse | None:
        profile = await self._profiles.get_for_user(user.id)
        if profile is None:
            return None
        return self._to_response(profile)

    async def upsert_profile(
        self, user: UserModel, payload: ProfileUpsertRequest
    ) -> ProfileResponse:
        validate_profile_fields(
            full_name=payload.full_name,
            nationality=payload.nationality,
            date_of_birth=payload.date_of_birth,
            passport_expiry=payload.passport_expiry,
        )

        settings = get_settings()
        profile = await self._profiles.get_for_user(user.id)
        now = datetime.now(UTC)
        prefs = payload.preferences.model_dump(exclude_none=True) if payload.preferences else None

        if profile is None:
            profile = TravelerProfileModel(
                user_id=user.id,
                full_name=payload.full_name.strip(),
                nationality=_optional_str(payload.nationality),
                date_of_birth=payload.date_of_birth,
                passport_expiry=payload.passport_expiry,
                preferences_json=prefs,
                created_at=now,
                updated_at=now,
            )
            self._apply_passport(profile, payload, settings.profile_encryption_key)
            await self._profiles.create(profile)
        else:
            profile.full_name = payload.full_name.strip()
            profile.nationality = _optional_str(payload.nationality)
            profile.date_of_birth = payload.date_of_birth
            profile.passport_expiry = payload.passport_expiry
            profile.preferences_json = prefs
            profile.updated_at = now
            self._apply_passport(profile, payload, settings.profile_encryption_key)
            await self._profiles.save(profile)

        response = self._to_response(profile)
        await self._session.commit()
        return response

    def _apply_passport(
        self,
        profile: TravelerProfileModel,
        payload: ProfileUpsertRequest,
        secret: str,
    ) -> None:
        if payload.clear_passport:
            profile.passport_number_enc = None
            return
        if payload.passport_number is None or not payload.passport_number.strip():
            return
        number = validate_passport_number(payload.passport_number)
        try:
            profile.passport_number_enc = encrypt_text(number, secret)
        except EncryptionError as exc:
            raise ProfileValidationError(str(exc)) from exc

    def _to_response(self, profile: TravelerProfileModel) -> ProfileResponse:
        settings = get_settings()
        passport_masked: str | None = None
        has_passport = bool(profile.passport_number_enc)
        if has_passport and profile.passport_number_enc:
            try:
                plaintext = decrypt_text(
                    profile.passport_number_enc, settings.profile_encryption_key
                )
                passport_masked = mask_passport(plaintext)
            except EncryptionError:
                passport_masked = "****"

        prefs = None
        if profile.preferences_json:
            prefs = ProfilePreferences.model_validate(profile.preferences_json)

        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            full_name=profile.full_name,
            nationality=profile.nationality,
            date_of_birth=profile.date_of_birth,
            passport_masked=passport_masked,
            has_passport=has_passport,
            passport_expiry=profile.passport_expiry,
            preferences=prefs,
            created_at=profile.created_at or datetime.now(UTC),
            updated_at=profile.updated_at or datetime.now(UTC),
        )


def _optional_str(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
