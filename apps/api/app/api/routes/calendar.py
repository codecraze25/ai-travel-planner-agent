from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.calendar import CalendarResponse
from app.core.auth import get_current_user
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/trips/{trip_id}/calendar", tags=["calendar"])


def get_calendar_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CalendarService:
    return CalendarService(session)


@router.get("", response_model=CalendarResponse)
async def list_calendar_events(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[CalendarService, Depends(get_calendar_service)],
) -> CalendarResponse:
    result = await service.list_events(trip_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result
