from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import TripModel, UserModel
from app.adapters.db.repositories import TripRepository
from app.adapters.db.session import get_db_session
from app.agent.runner import AgentRunner
from app.agent.tools import AgentTools
from app.api.schemas.trip import TripCreateRequest, TripUpdateRequest
from app.core.auth import get_current_user
from app.domain.chat_parse import default_trip_dates, parse_trip_intent
from app.domain.trip import TripStatus
from app.services.trip_service import TripService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    trip_id: uuid.UUID | None = None


def _correlation_id(request: Request) -> str | None:
    return request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID")


async def _stream_events(events: AsyncIterator[dict[str, object]]) -> AsyncIterator[str]:
    async for event in events:
        yield f"data: {json.dumps(event, default=str)}\n\n"


@router.post("")
async def chat(
    payload: ChatRequest,
    request: Request,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    trips = TripRepository(session)
    trip_service = TripService(session)
    intent = parse_trip_intent(payload.message)

    trip: TripModel | None = None
    if payload.trip_id is not None:
        trip = await trips.get_for_user(payload.trip_id, user.id)

    if trip is None:
        listed = await trips.list_for_user(user.id)
        active = [t for t in listed if t.status != TripStatus.ARCHIVED]
        trip = active[0] if active else None

    if trip is None:
        start, end = default_trip_dates()
        created = await trip_service.create_trip(
            user,
            TripCreateRequest(
                origin=intent.origin or "San Francisco",
                destination=intent.destination or "Tokyo",
                start_date=intent.start_date or start,
                end_date=intent.end_date or end,
                travelers=intent.travelers or 1,
                budget_usd=intent.budget_usd or 4000.0,
            ),
        )
        trip = await trips.get_for_user(created.id, user.id)
        assert trip is not None
    elif any(
        [
            intent.origin,
            intent.destination,
            intent.start_date,
            intent.end_date,
            intent.travelers,
            intent.budget_usd,
        ]
    ):
        await trip_service.update_trip(
            trip.id,
            user,
            TripUpdateRequest(
                origin=intent.origin,
                destination=intent.destination,
                start_date=intent.start_date,
                end_date=intent.end_date,
                travelers=intent.travelers,
                budget_usd=intent.budget_usd,
            ),
        )
        trip = await trips.get_for_user(trip.id, user.id)
        assert trip is not None

    tools = AgentTools(
        session,
        trip.id,
        user,
        correlation_id=_correlation_id(request),
    )
    runner = AgentRunner(tools, destination=trip.destination, origin=trip.origin)

    trip_summary = {
        "id": str(trip.id),
        "origin": trip.origin,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat()
        if isinstance(trip.start_date, date)
        else str(trip.start_date),
        "end_date": trip.end_date.isoformat()
        if isinstance(trip.end_date, date)
        else str(trip.end_date),
        "travelers": trip.travelers,
        "budget_usd": trip.budget_usd,
    }

    async def generate() -> AsyncIterator[str]:
        yield f"data: {json.dumps({'type': 'trip', 'data': trip_summary})}\n\n"
        async for chunk in _stream_events(runner.run(payload.message)):
            yield chunk
        await session.commit()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
