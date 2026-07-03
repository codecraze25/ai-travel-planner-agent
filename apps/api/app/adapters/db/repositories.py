from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.db.models import (
    AgentActionModel,
    AuditLogModel,
    DocumentChunkModel,
    DocumentModel,
    EmailModel,
    FlightModel,
    HotelModel,
    ItineraryItemModel,
    ItineraryModel,
    TripModel,
    TripPreferencesModel,
    UserModel,
)
from app.domain.documents import DocumentStatus


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


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, document: DocumentModel) -> DocumentModel:
        self._session.add(document)
        await self._session.flush()
        return document

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[DocumentModel]:
        result = await self._session.execute(
            select(DocumentModel)
            .where(DocumentModel.trip_id == trip_id)
            .order_by(DocumentModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_trip(
        self, document_id: uuid.UUID, trip_id: uuid.UUID
    ) -> DocumentModel | None:
        result = await self._session.execute(
            select(DocumentModel)
            .where(DocumentModel.id == document_id, DocumentModel.trip_id == trip_id)
            .options(selectinload(DocumentModel.chunks))
        )
        return result.scalar_one_or_none()

    async def delete(self, document: DocumentModel) -> None:
        await self._session.delete(document)
        await self._session.flush()

    async def replace_chunks(
        self, document_id: uuid.UUID, chunks: list[DocumentChunkModel]
    ) -> None:
        existing = await self._session.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        for row in existing.scalars().all():
            await self._session.delete(row)
        await self._session.flush()
        for chunk in chunks:
            chunk.document_id = document_id
            self._session.add(chunk)
        await self._session.flush()

    async def list_chunks_for_trip(self, trip_id: uuid.UUID) -> list[DocumentChunkModel]:
        result = await self._session.execute(
            select(DocumentChunkModel)
            .join(DocumentModel, DocumentChunkModel.document_id == DocumentModel.id)
            .where(
                DocumentModel.trip_id == trip_id,
                DocumentModel.status == DocumentStatus.READY,
            )
            .options(selectinload(DocumentChunkModel.document))
        )
        return list(result.scalars().all())


class ItineraryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_for_trip(self, trip_id: uuid.UUID) -> ItineraryModel | None:
        result = await self._session.execute(
            select(ItineraryModel)
            .where(ItineraryModel.trip_id == trip_id)
            .options(selectinload(ItineraryModel.items))
            .order_by(ItineraryModel.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        trip_id: uuid.UUID,
        total_est_cost_usd: float,
        items: list[ItineraryItemModel],
        version: int = 1,
    ) -> ItineraryModel:
        itinerary = ItineraryModel(
            trip_id=trip_id,
            version=version,
            total_est_cost_usd=total_est_cost_usd,
        )
        self._session.add(itinerary)
        await self._session.flush()
        for idx, item in enumerate(items):
            item.itinerary_id = itinerary.id
            item.sort_order = idx
            self._session.add(item)
        await self._session.flush()
        await self._session.refresh(itinerary, attribute_names=["items"])
        return itinerary

    async def next_version(self, trip_id: uuid.UUID) -> int:
        latest = await self.get_latest_for_trip(trip_id)
        return 1 if latest is None else latest.version + 1


class AgentActionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        *,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        tool_name: str,
        input_json: dict[str, object] | None,
        output_json: dict[str, object] | None,
        success: bool,
        error_message: str | None = None,
        correlation_id: str | None = None,
    ) -> AgentActionModel:
        action = AgentActionModel(
            trip_id=trip_id,
            user_id=user_id,
            tool_name=tool_name,
            input_json=input_json,
            output_json=output_json,
            success=success,
            error_message=error_message,
            correlation_id=correlation_id,
        )
        self._session.add(action)
        await self._session.flush()
        return action

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[AgentActionModel]:
        result = await self._session.execute(
            select(AgentActionModel)
            .where(AgentActionModel.trip_id == trip_id)
            .order_by(AgentActionModel.created_at.desc())
        )
        return list(result.scalars().all())


class EmailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, email: EmailModel) -> EmailModel:
        self._session.add(email)
        await self._session.flush()
        return email

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[EmailModel]:
        result = await self._session.execute(
            select(EmailModel)
            .where(EmailModel.trip_id == trip_id)
            .order_by(EmailModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_trip(self, email_id: uuid.UUID, trip_id: uuid.UUID) -> EmailModel | None:
        result = await self._session.execute(
            select(EmailModel).where(EmailModel.id == email_id, EmailModel.trip_id == trip_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_trip(self, trip_id: uuid.UUID) -> EmailModel | None:
        result = await self._session.execute(
            select(EmailModel)
            .where(EmailModel.trip_id == trip_id)
            .order_by(EmailModel.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save(self, email: EmailModel) -> EmailModel:
        await self._session.flush()
        return email


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        *,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        details: dict[str, object] | None = None,
    ) -> AuditLogModel:
        entry = AuditLogModel(
            trip_id=trip_id,
            user_id=user_id,
            action=action,
            details=details,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def list_for_trip(self, trip_id: uuid.UUID) -> list[AuditLogModel]:
        result = await self._session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.trip_id == trip_id)
            .order_by(AuditLogModel.created_at.desc())
        )
        return list(result.scalars().all())
