from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.trip import (
    TripCreateRequest,
    TripListResponse,
    TripResponse,
    TripUpdateRequest,
)
from app.core.auth import get_current_user
from app.domain.trip import TripValidationError
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["trips"])


def get_trip_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TripService:
    return TripService(session)


@router.get("", response_model=TripListResponse)
async def list_trips(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripListResponse:
    items = await service.list_trips(user)
    return TripListResponse(items=items)


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripResponse:
    try:
        return await service.create_trip(user, payload)
    except TripValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripResponse:
    trip = await service.get_trip(trip_id, user)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: uuid.UUID,
    payload: TripUpdateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripResponse:
    try:
        trip = await service.update_trip(trip_id, user, payload)
    except TripValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip
