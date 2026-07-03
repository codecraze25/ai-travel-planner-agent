from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FlightSearchRequest(BaseModel):
    cabin_class: str = "economy"
    max_price: float | None = None
    nonstop_only: bool = False


class HotelSearchRequest(BaseModel):
    rooms: int = Field(default=1, ge=1)
    max_price_per_night: float | None = None
    min_rating: float | None = None


class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    external_id: str
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int
    price_usd: float
    baggage_info: str | None = None
    booking_link: str | None = None
    cancellation_policy: str | None = None
    selected: bool = False


class HotelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    external_id: str
    name: str
    price_per_night_usd: float
    total_price_usd: float
    rating: float | None = None
    location: str | None = None
    amenities: list[str] | None = None
    cancellation_policy: str | None = None
    photo_urls: list[str] | None = None
    booking_link: str | None = None
    selected: bool = False


class FlightTradeoffsResponse(BaseModel):
    best_value_id: UUID | None = None
    fastest_id: UUID | None = None
    cheapest_id: UUID | None = None
    explanations: list[str]


class FlightSearchResponse(BaseModel):
    items: list[FlightResponse]
    tradeoffs: FlightTradeoffsResponse


class HotelSearchResponse(BaseModel):
    items: list[HotelResponse]


class BudgetResponse(BaseModel):
    trip_budget_usd: float
    flight_cost_usd: float
    hotel_cost_usd: float
    other_cost_usd: float
    committed_usd: float
    remaining_usd: float
    utilization_pct: float
    warning: str | None = None


class SelectResponse(BaseModel):
    flight: FlightResponse | None = None
    hotel: HotelResponse | None = None
    budget: BudgetResponse
