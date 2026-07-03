from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.itinerary import ItineraryGenerateRequest, ItineraryResponse
from app.core.auth import get_current_user
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/trips/{trip_id}/itinerary", tags=["itinerary"])


def get_itinerary_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItineraryService:
    return ItineraryService(session)


@router.get("", response_model=ItineraryResponse)
async def get_itinerary(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ItineraryService, Depends(get_itinerary_service)],
) -> ItineraryResponse:
    itinerary = await service.get_itinerary(trip_id, user)
    if itinerary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found")
    return itinerary


@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(
    trip_id: uuid.UUID,
    payload: ItineraryGenerateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ItineraryService, Depends(get_itinerary_service)],
) -> ItineraryResponse:
    itinerary = await service.generate(trip_id, user, regenerate_day=payload.regenerate_day)
    if itinerary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return itinerary
