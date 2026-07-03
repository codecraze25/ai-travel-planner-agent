from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.db.models import TripModel, TripPreferencesModel, UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_external_id(self, external_id: str) -> UserModel | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def create(self, external_id: str, email: str) -> UserModel:
        user = UserModel(external_id=external_id, email=email)
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_or_create(self, external_id: str, email: str) -> UserModel:
        user = await self.get_by_external_id(external_id)
        if user is not None:
            return user
        return await self.create(external_id, email)


class TripRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: uuid.UUID) -> list[TripModel]:
        result = await self._session.execute(
            select(TripModel)
            .where(TripModel.user_id == user_id)
            .options(selectinload(TripModel.preferences))
            .order_by(TripModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> TripModel | None:
        result = await self._session.execute(
            select(TripModel)
            .where(TripModel.id == trip_id, TripModel.user_id == user_id)
            .options(selectinload(TripModel.preferences))
        )
        return result.scalar_one_or_none()

    async def create(self, trip: TripModel, preferences: TripPreferencesModel | None) -> TripModel:
        self._session.add(trip)
        await self._session.flush()
        if preferences is not None:
            preferences.trip_id = trip.id
            self._session.add(preferences)
            await self._session.flush()
        await self._session.refresh(trip, attribute_names=["preferences"])
        return trip

    async def save(self, trip: TripModel) -> TripModel:
        await self._session.flush()
        await self._session.refresh(trip, attribute_names=["preferences"])
        return trip
