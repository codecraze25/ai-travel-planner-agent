from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import ItineraryItemModel, TripModel, UserModel
from app.adapters.db.repositories import (
    FlightRepository,
    HotelRepository,
    ItineraryRepository,
    TripRepository,
)
from app.api.schemas.itinerary import ItineraryBlockResponse, ItineraryResponse
from app.domain.itinerary import build_mock_itinerary, itinerary_to_dict, trip_day_count
from app.domain.trip import TripStatus


class ItineraryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._trips = TripRepository(session)
        self._itineraries = ItineraryRepository(session)
        self._flights = FlightRepository(session)
        self._hotels = HotelRepository(session)

    async def get_itinerary(self, trip_id: uuid.UUID, user: UserModel) -> ItineraryResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        itinerary = await self._itineraries.get_latest_for_trip(trip_id)
        if itinerary is None:
            return None
        return _to_response(itinerary)

    async def generate(
        self,
        trip_id: uuid.UUID,
        user: UserModel,
        *,
        regenerate_day: int | None = None,
    ) -> ItineraryResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        data = await self._build_itinerary_data(trip)
        if regenerate_day is not None:
            data = _filter_day(data, regenerate_day)

        version = await self._itineraries.next_version(trip_id)
        items = _items_from_dict(data)
        itinerary = await self._itineraries.create(
            trip_id=trip_id,
            total_est_cost_usd=float(data["total_est_cost_usd"]),
            items=items,
            version=version,
        )

        if trip.status == TripStatus.PLANNING:
            trip.status = TripStatus.READY
            await self._session.flush()

        await self._session.commit()
        return _to_response(itinerary)

    async def _build_itinerary_data(self, trip: TripModel) -> dict[str, Any]:
        selected_hotel = next(
            (h for h in await self._hotels.list_for_trip(trip.id) if h.selected), None
        )
        docs_check_in: str | None = None
        docs_check_out: str | None = None

        plans = build_mock_itinerary(
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            travelers=trip.travelers,
            hotel_name=selected_hotel.name if selected_hotel else None,
            check_in=docs_check_in,
            check_out=docs_check_out,
        )
        expected_days = trip_day_count(trip.start_date, trip.end_date)
        if len(plans) != expected_days:
            plans = plans[:expected_days]
        return itinerary_to_dict(plans)


def _items_from_dict(data: dict[str, Any]) -> list[ItineraryItemModel]:
    items: list[ItineraryItemModel] = []
    for day in data["days"]:
        backup = day.get("backup_option")
        for block in day["blocks"]:
            items.append(
                ItineraryItemModel(
                    day_number=day["day_number"],
                    time_block=block["time_block"],
                    title=block["title"],
                    description=block["description"],
                    location=block.get("location"),
                    est_cost_usd=float(block["est_cost_usd"]),
                    map_url=block.get("map_url"),
                    backup_option=backup,
                )
            )
    return items


def _filter_day(data: dict[str, Any], day_number: int) -> dict[str, Any]:
    days = [d for d in data["days"] if d["day_number"] == day_number]
    total = sum(d["daily_cost_usd"] for d in days)
    return {**data, "days": days, "total_est_cost_usd": round(total, 2)}


def _to_response(itinerary: Any) -> ItineraryResponse:
    items = [
        ItineraryBlockResponse(
            id=item.id,
            day_number=item.day_number,
            time_block=item.time_block,
            title=item.title,
            description=item.description,
            location=item.location,
            est_cost_usd=item.est_cost_usd,
            map_url=item.map_url,
            backup_option=item.backup_option,
        )
        for item in sorted(itinerary.items, key=lambda i: (i.day_number, i.sort_order))
    ]
    return ItineraryResponse(
        id=itinerary.id,
        trip_id=itinerary.trip_id,
        version=itinerary.version,
        total_est_cost_usd=itinerary.total_est_cost_usd,
        created_at=itinerary.created_at,
        items=items,
    )
