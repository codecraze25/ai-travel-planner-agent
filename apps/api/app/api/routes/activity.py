from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.activity import ActivityListResponse
from app.core.auth import get_current_user
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/trips/{trip_id}/activity", tags=["activity"])


def get_activity_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActivityService:
    return ActivityService(session)


@router.get("", response_model=ActivityListResponse)
async def list_activity(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ActivityService, Depends(get_activity_service)],
) -> ActivityListResponse:
    result = await service.list_activity(trip_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result
