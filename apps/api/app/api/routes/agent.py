from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.repositories import TripRepository
from app.adapters.db.session import get_db_session
from app.agent.runner import AgentRunner
from app.agent.tools import AgentTools
from app.api.schemas.agent import AgentChatRequest
from app.core.auth import get_current_user

router = APIRouter(prefix="/trips/{trip_id}/agent", tags=["agent"])


def _correlation_id(request: Request) -> str | None:
    return request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID")


async def _stream_events(events: AsyncIterator[dict[str, object]]) -> AsyncIterator[str]:
    async for event in events:
        yield f"data: {json.dumps(event, default=str)}\n\n"


@router.post("/chat")
async def agent_chat(
    trip_id: uuid.UUID,
    payload: AgentChatRequest,
    request: Request,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    trips = TripRepository(session)
    trip = await trips.get_for_user(trip_id, user.id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    tools = AgentTools(
        session,
        trip_id,
        user,
        correlation_id=_correlation_id(request),
    )
    runner = AgentRunner(tools, destination=trip.destination, origin=trip.origin)

    async def generate() -> AsyncIterator[str]:
        async for chunk in _stream_events(runner.run(payload.message)):
            yield chunk
        await session.commit()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
