from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.db.models import (
    FlightModel,
    HotelModel,
    TripModel,
    TripPreferencesModel,
    UserModel,
)


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


class FlightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_for_trip(
        self, trip_id: uuid.UUID, flights: list[FlightModel]
    ) -> list[FlightModel]:
        existing = await self._session.execute(
            select(FlightModel).where(FlightModel.trip_id == trip_id)
        )
        for row in existing.scalars().all():
            await self._session.delete(row)
        await self._session.flush()
        for flight in flights:
            flight.trip_id = trip_id
            self._session.add(flight)
        await self._session.flush()
        return await self.list_for_trip(trip_id)

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[FlightModel]:
        result = await self._session.execute(
            select(FlightModel)
            .where(FlightModel.trip_id == trip_id)
            .order_by(FlightModel.price_usd.asc())
        )
        return list(result.scalars().all())

    async def get_for_trip(self, flight_id: uuid.UUID, trip_id: uuid.UUID) -> FlightModel | None:
        result = await self._session.execute(
            select(FlightModel).where(FlightModel.id == flight_id, FlightModel.trip_id == trip_id)
        )
        return result.scalar_one_or_none()

    async def select(self, trip_id: uuid.UUID, flight_id: uuid.UUID) -> FlightModel | None:
        flights = await self.list_for_trip(trip_id)
        selected: FlightModel | None = None
        for flight in flights:
            flight.selected = flight.id == flight_id
            if flight.selected:
                selected = flight
        await self._session.flush()
        return selected


class HotelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_for_trip(
        self, trip_id: uuid.UUID, hotels: list[HotelModel]
    ) -> list[HotelModel]:
        existing = await self._session.execute(
            select(HotelModel).where(HotelModel.trip_id == trip_id)
        )
        for row in existing.scalars().all():
            await self._session.delete(row)
        await self._session.flush()
        for hotel in hotels:
            hotel.trip_id = trip_id
            self._session.add(hotel)
        await self._session.flush()
        return await self.list_for_trip(trip_id)

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[HotelModel]:
        result = await self._session.execute(
            select(HotelModel)
            .where(HotelModel.trip_id == trip_id)
            .order_by(HotelModel.total_price_usd.asc())
        )
        return list(result.scalars().all())

    async def get_for_trip(self, hotel_id: uuid.UUID, trip_id: uuid.UUID) -> HotelModel | None:
        result = await self._session.execute(
            select(HotelModel).where(HotelModel.id == hotel_id, HotelModel.trip_id == trip_id)
        )
        return result.scalar_one_or_none()

    async def select(self, trip_id: uuid.UUID, hotel_id: uuid.UUID) -> HotelModel | None:
        hotels = await self.list_for_trip(trip_id)
        selected: HotelModel | None = None
        for hotel in hotels:
            hotel.selected = hotel.id == hotel_id
            if hotel.selected:
                selected = hotel
        await self._session.flush()
        return selected
