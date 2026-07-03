from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.repositories import TripRepository
from app.api.schemas.calendar import CalendarEventResponse, CalendarResponse
from app.core.config import get_settings
from app.domain.calendar import build_stub_calendar_events


class CalendarService:
    def __init__(self, session: AsyncSession) -> None:
        self._trips = TripRepository(session)

    async def list_events(
        self, trip_id: uuid.UUID, user: UserModel
    ) -> CalendarResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        settings = get_settings()
        if settings.use_mock_calendar or not settings.google_client_id:
            events = build_stub_calendar_events(
                origin=trip.origin,
                destination=trip.destination,
                start_date=trip.start_date,
                end_date=trip.end_date,
            )
            return CalendarResponse(
                source="stub",
                items=[
                    CalendarEventResponse(
                        title=e.title,
                        start=e.start,
                        end=e.end,
                        location=e.location,
                        source=e.source,
                    )
                    for e in events
                ],
            )

        # Google Calendar OAuth read is scaffolded for a later iteration.
        return CalendarResponse(
            source="unavailable",
            items=[],
            note="Google Calendar OAuth is not connected. Set USE_MOCK_CALENDAR=true.",
        )
