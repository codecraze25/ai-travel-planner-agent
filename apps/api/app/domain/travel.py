from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class FlightOption:
    external_id: str
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int
    price_usd: float
    baggage_info: str = ""
    booking_link: str = ""
    cancellation_policy: str = ""


@dataclass(frozen=True)
class HotelOption:
    external_id: str
    name: str
    price_per_night_usd: float
    total_price_usd: float
    rating: float = 0.0
    location: str = ""
    amenities: list[str] = field(default_factory=list)
    cancellation_policy: str = ""
    photo_urls: list[str] = field(default_factory=list)
    booking_link: str = ""


@dataclass(frozen=True)
class FlightSearchQuery:
    origin: str
    destination: str
    departure_date: date
    return_date: date
    passengers: int
    cabin_class: str = "economy"
    max_price: float | None = None
    nonstop_only: bool = False


@dataclass(frozen=True)
class HotelSearchQuery:
    destination: str
    check_in: date
    check_out: date
    guests: int
    rooms: int = 1
    max_price_per_night: float | None = None
    min_rating: float | None = None


@dataclass(frozen=True)
class FlightTradeoffs:
    best_value: FlightOption | None
    fastest: FlightOption | None
    cheapest: FlightOption | None
    explanations: list[str]


@dataclass(frozen=True)
class BudgetSummary:
    trip_budget_usd: float
    flight_cost_usd: float
    hotel_cost_usd: float
    other_cost_usd: float
    committed_usd: float
    remaining_usd: float
    utilization_pct: float
    warning: str | None


def calculate_budget(
    trip_budget_usd: float,
    flight_cost_usd: float = 0.0,
    hotel_cost_usd: float = 0.0,
    other_cost_usd: float = 0.0,
    warning_threshold: float = 0.8,
) -> BudgetSummary:
    committed = flight_cost_usd + hotel_cost_usd + other_cost_usd
    remaining = trip_budget_usd - committed
    utilization = (committed / trip_budget_usd) if trip_budget_usd > 0 else 0.0
    warning: str | None = None
    if utilization >= 1.0:
        warning = "Over budget: committed spend exceeds trip budget."
    elif utilization >= warning_threshold:
        warning = (
            f"Budget warning: committed spend is {utilization:.0%} of trip budget "
            f"(threshold {warning_threshold:.0%})."
        )
    return BudgetSummary(
        trip_budget_usd=trip_budget_usd,
        flight_cost_usd=flight_cost_usd,
        hotel_cost_usd=hotel_cost_usd,
        other_cost_usd=other_cost_usd,
        committed_usd=committed,
        remaining_usd=remaining,
        utilization_pct=round(utilization * 100, 1),
        warning=warning,
    )


def rank_flight_tradeoffs(flights: list[FlightOption]) -> FlightTradeoffs:
    if not flights:
        return FlightTradeoffs(None, None, None, ["No flights found."])

    cheapest = min(flights, key=lambda f: f.price_usd)
    fastest = min(flights, key=lambda f: (f.duration_minutes, f.price_usd))
    # Best value: balance price and duration (lower score is better)
    best_value = min(
        flights,
        key=lambda f: (f.price_usd / 100.0) + (f.duration_minutes / 60.0) + (f.stops * 2),
    )

    explanations = [
        (
            f"Best value: ${best_value.price_usd:.0f}, "
            f"{best_value.stops} stop(s), "
            f"{best_value.duration_minutes // 60}h "
            f"{best_value.duration_minutes % 60}m "
            f"({best_value.airline} {best_value.flight_number})."
        ),
        (
            f"Fastest: ${fastest.price_usd:.0f}, "
            f"{fastest.stops} stop(s), {fastest.duration_minutes // 60}h "
            f"{fastest.duration_minutes % 60}m ({fastest.airline} {fastest.flight_number})."
        ),
        (
            f"Cheapest: ${cheapest.price_usd:.0f}, "
            f"{cheapest.stops} stop(s), {cheapest.duration_minutes // 60}h "
            f"{cheapest.duration_minutes % 60}m ({cheapest.airline} {cheapest.flight_number})."
        ),
    ]
    return FlightTradeoffs(best_value, fastest, cheapest, explanations)
