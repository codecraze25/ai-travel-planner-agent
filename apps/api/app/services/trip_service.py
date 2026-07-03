from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import TripModel, TripPreferencesModel, UserModel
from app.adapters.db.repositories import TripRepository, UserRepository
from app.api.schemas.trip import (
    TripCreateRequest,
    TripPreferencesInput,
    TripResponse,
    TripUpdateRequest,
    trip_model_to_response,
)
from app.domain.trip import TripStatus, validate_trip_fields


class TripService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._trips = TripRepository(session)
        self._users = UserRepository(session)

    async def list_trips(self, user: UserModel) -> list[TripResponse]:
        trips = await self._trips.list_for_user(user.id)
        return [trip_model_to_response(t) for t in trips]

    async def get_trip(self, trip_id: uuid.UUID, user: UserModel) -> TripResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        return trip_model_to_response(trip)

    async def create_trip(self, user: UserModel, payload: TripCreateRequest) -> TripResponse:
        validate_trip_fields(
            origin=payload.origin,
            destination=payload.destination,
            start_date=payload.start_date,
            end_date=payload.end_date,
            travelers=payload.travelers,
            budget_usd=payload.budget_usd,
        )
        trip = TripModel(
            user_id=user.id,
            origin=payload.origin.strip(),
            destination=payload.destination.strip(),
            start_date=payload.start_date,
            end_date=payload.end_date,
            travelers=payload.travelers,
            budget_usd=payload.budget_usd,
            status=TripStatus.DRAFT,
        )
        preferences = _preferences_from_input(payload.preferences)
        created = await self._trips.create(trip, preferences)
        await self._session.commit()
        return trip_model_to_response(created)

    async def update_trip(
        self, trip_id: uuid.UUID, user: UserModel, payload: TripUpdateRequest
    ) -> TripResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        if payload.origin is not None:
            trip.origin = payload.origin.strip()
        if payload.destination is not None:
            trip.destination = payload.destination.strip()
        if payload.start_date is not None:
            trip.start_date = payload.start_date
        if payload.end_date is not None:
            trip.end_date = payload.end_date
        if payload.travelers is not None:
            trip.travelers = payload.travelers
        if payload.budget_usd is not None:
            trip.budget_usd = payload.budget_usd
        if payload.status is not None:
            trip.status = payload.status

        validate_trip_fields(
            origin=trip.origin,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            travelers=trip.travelers,
            budget_usd=trip.budget_usd,
            require_future_dates=False,
        )

        if payload.preferences is not None:
            if trip.preferences is None:
                trip.preferences = TripPreferencesModel(trip_id=trip.id)
            _apply_preferences(trip.preferences, payload.preferences)

        updated = await self._trips.save(trip)
        await self._session.commit()
        return trip_model_to_response(updated)


def _preferences_from_input(data: TripPreferencesInput | None) -> TripPreferencesModel | None:
    if data is None:
        return None
    return TripPreferencesModel(**data.model_dump(exclude_none=True))


def _apply_preferences(model: TripPreferencesModel, data: TripPreferencesInput) -> None:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
