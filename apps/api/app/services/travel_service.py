from __future__ import annotations

import uuid
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import FlightModel, HotelModel, UserModel
from app.adapters.db.repositories import FlightRepository, HotelRepository, TripRepository
from app.adapters.providers.factory import get_flight_provider, get_hotel_provider
from app.api.schemas.travel import (
    BudgetResponse,
    FlightResponse,
    FlightSearchRequest,
    FlightSearchResponse,
    FlightTradeoffsResponse,
    HotelResponse,
    HotelSearchRequest,
    HotelSearchResponse,
    SelectResponse,
)
from app.domain.travel import (
    FlightOption,
    FlightSearchQuery,
    HotelOption,
    HotelSearchQuery,
    calculate_budget,
    rank_flight_tradeoffs,
)
from app.domain.trip import TripStatus


class TravelService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._trips = TripRepository(session)
        self._flights = FlightRepository(session)
        self._hotels = HotelRepository(session)

    async def search_flights(
        self, trip_id: uuid.UUID, user: UserModel, payload: FlightSearchRequest
    ) -> FlightSearchResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        query = FlightSearchQuery(
            origin=trip.origin,
            destination=trip.destination,
            departure_date=trip.start_date,
            return_date=trip.end_date,
            passengers=trip.travelers,
            cabin_class=payload.cabin_class,
            max_price=payload.max_price,
            nonstop_only=payload.nonstop_only,
        )
        provider = get_flight_provider()
        options = await provider.search_flights(query)
        models = [_flight_to_model(opt) for opt in options]
        saved = await self._flights.replace_for_trip(trip_id, models)

        if trip.status == TripStatus.DRAFT:
            trip.status = TripStatus.PLANNING
            await self._session.flush()

        await self._session.commit()

        tradeoffs = rank_flight_tradeoffs(options)
        id_by_external = {f.external_id: f.id for f in saved}
        return FlightSearchResponse(
            items=[FlightResponse.model_validate(f) for f in saved],
            tradeoffs=FlightTradeoffsResponse(
                best_value_id=_map_id(tradeoffs.best_value, id_by_external),
                fastest_id=_map_id(tradeoffs.fastest, id_by_external),
                cheapest_id=_map_id(tradeoffs.cheapest, id_by_external),
                explanations=tradeoffs.explanations,
            ),
        )

    async def list_flights(
        self, trip_id: uuid.UUID, user: UserModel
    ) -> list[FlightResponse] | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        flights = await self._flights.list_for_trip(trip_id)
        return [FlightResponse.model_validate(f) for f in flights]

    async def select_flight(
        self, trip_id: uuid.UUID, flight_id: uuid.UUID, user: UserModel
    ) -> SelectResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        selected = await self._flights.select(trip_id, flight_id)
        if selected is None:
            return None
        await self._session.commit()
        budget = await self._budget_for_trip(trip_id, trip.budget_usd)
        return SelectResponse(flight=FlightResponse.model_validate(selected), budget=budget)

    async def search_hotels(
        self, trip_id: uuid.UUID, user: UserModel, payload: HotelSearchRequest
    ) -> HotelSearchResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        query = HotelSearchQuery(
            destination=trip.destination,
            check_in=trip.start_date,
            check_out=trip.end_date,
            guests=trip.travelers,
            rooms=payload.rooms,
            max_price_per_night=payload.max_price_per_night,
            min_rating=payload.min_rating,
        )
        provider = get_hotel_provider()
        options = await provider.search_hotels(query)
        models = [_hotel_to_model(opt) for opt in options]
        saved = await self._hotels.replace_for_trip(trip_id, models)

        if trip.status == TripStatus.DRAFT:
            trip.status = TripStatus.PLANNING
            await self._session.flush()

        await self._session.commit()
        return HotelSearchResponse(items=[HotelResponse.model_validate(h) for h in saved])

    async def list_hotels(self, trip_id: uuid.UUID, user: UserModel) -> list[HotelResponse] | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        hotels = await self._hotels.list_for_trip(trip_id)
        return [HotelResponse.model_validate(h) for h in hotels]

    async def select_hotel(
        self, trip_id: uuid.UUID, hotel_id: uuid.UUID, user: UserModel
    ) -> SelectResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        selected = await self._hotels.select(trip_id, hotel_id)
        if selected is None:
            return None
        await self._session.commit()
        budget = await self._budget_for_trip(trip_id, trip.budget_usd)
        return SelectResponse(hotel=HotelResponse.model_validate(selected), budget=budget)

    async def get_budget(self, trip_id: uuid.UUID, user: UserModel) -> BudgetResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        return await self._budget_for_trip(trip_id, trip.budget_usd)

    async def _budget_for_trip(self, trip_id: uuid.UUID, trip_budget: float) -> BudgetResponse:
        flights = await self._flights.list_for_trip(trip_id)
        hotels = await self._hotels.list_for_trip(trip_id)
        flight_cost = next((f.price_usd for f in flights if f.selected), 0.0)
        hotel_cost = next((h.total_price_usd for h in hotels if h.selected), 0.0)
        summary = calculate_budget(trip_budget, flight_cost, hotel_cost)
        return BudgetResponse(
            trip_budget_usd=summary.trip_budget_usd,
            flight_cost_usd=summary.flight_cost_usd,
            hotel_cost_usd=summary.hotel_cost_usd,
            other_cost_usd=summary.other_cost_usd,
            committed_usd=summary.committed_usd,
            remaining_usd=summary.remaining_usd,
            utilization_pct=summary.utilization_pct,
            warning=summary.warning,
        )


def _flight_to_model(opt: FlightOption) -> FlightModel:
    return FlightModel(
        external_id=opt.external_id,
        airline=opt.airline,
        flight_number=opt.flight_number,
        departure_time=opt.departure_time,
        arrival_time=opt.arrival_time,
        duration_minutes=opt.duration_minutes,
        stops=opt.stops,
        price_usd=opt.price_usd,
        baggage_info=opt.baggage_info,
        booking_link=opt.booking_link,
        cancellation_policy=opt.cancellation_policy,
        selected=False,
        raw_json=asdict(opt),
    )


def _hotel_to_model(opt: HotelOption) -> HotelModel:
    return HotelModel(
        external_id=opt.external_id,
        name=opt.name,
        price_per_night_usd=opt.price_per_night_usd,
        total_price_usd=opt.total_price_usd,
        rating=opt.rating,
        location=opt.location,
        amenities=opt.amenities,
        cancellation_policy=opt.cancellation_policy,
        photo_urls=opt.photo_urls,
        booking_link=opt.booking_link,
        selected=False,
        raw_json=asdict(opt),
    )


def _map_id(option: FlightOption | None, id_by_external: dict[str, uuid.UUID]) -> uuid.UUID | None:
    if option is None:
        return None
    return id_by_external.get(option.external_id)
