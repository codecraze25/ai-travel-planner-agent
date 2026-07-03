from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.travel import (
    BudgetResponse,
    FlightResponse,
    FlightSearchRequest,
    FlightSearchResponse,
    HotelResponse,
    HotelSearchRequest,
    HotelSearchResponse,
    SelectResponse,
)
from app.core.auth import get_current_user
from app.services.travel_service import TravelService

router = APIRouter(prefix="/trips/{trip_id}", tags=["travel"])


def get_travel_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TravelService:
    return TravelService(session)


@router.post("/flights/search", response_model=FlightSearchResponse)
async def search_flights(
    trip_id: uuid.UUID,
    payload: FlightSearchRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> FlightSearchResponse:
    result = await service.search_flights(trip_id, user, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.get("/flights", response_model=list[FlightResponse])
async def list_flights(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> list[FlightResponse]:
    result = await service.list_flights(trip_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.post("/flights/{flight_id}/select", response_model=SelectResponse)
async def select_flight(
    trip_id: uuid.UUID,
    flight_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> SelectResponse:
    result = await service.select_flight(trip_id, flight_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
    return result


@router.post("/hotels/search", response_model=HotelSearchResponse)
async def search_hotels(
    trip_id: uuid.UUID,
    payload: HotelSearchRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> HotelSearchResponse:
    result = await service.search_hotels(trip_id, user, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.get("/hotels", response_model=list[HotelResponse])
async def list_hotels(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> list[HotelResponse]:
    result = await service.list_hotels(trip_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.post("/hotels/{hotel_id}/select", response_model=SelectResponse)
async def select_hotel(
    trip_id: uuid.UUID,
    hotel_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> SelectResponse:
    result = await service.select_hotel(trip_id, hotel_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return result


@router.get("/budget", response_model=BudgetResponse)
async def get_budget(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[TravelService, Depends(get_travel_service)],
) -> BudgetResponse:
    result = await service.get_budget(trip_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result
