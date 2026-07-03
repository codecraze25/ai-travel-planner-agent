from datetime import date

import pytest

from app.adapters.providers.mock_flights import MockFlightProvider
from app.adapters.providers.mock_hotels import MockHotelProvider
from app.domain.travel import (
    FlightOption,
    FlightSearchQuery,
    HotelSearchQuery,
    rank_flight_tradeoffs,
)


@pytest.mark.asyncio
async def test_mock_flight_search_returns_options() -> None:
    provider = MockFlightProvider()
    results = await provider.search_flights(
        FlightSearchQuery(
            origin="San Francisco",
            destination="Tokyo",
            departure_date=date(2026, 10, 10),
            return_date=date(2026, 10, 15),
            passengers=2,
        )
    )
    assert len(results) >= 3
    assert all(r.price_usd > 0 for r in results)
    assert all(r.booking_link for r in results)


@pytest.mark.asyncio
async def test_mock_flight_nonstop_filter() -> None:
    provider = MockFlightProvider()
    results = await provider.search_flights(
        FlightSearchQuery(
            origin="SFO",
            destination="NRT",
            departure_date=date(2026, 10, 10),
            return_date=date(2026, 10, 15),
            passengers=1,
            nonstop_only=True,
        )
    )
    assert results
    assert all(r.stops == 0 for r in results)


@pytest.mark.asyncio
async def test_mock_hotel_search_returns_options() -> None:
    provider = MockHotelProvider()
    results = await provider.search_hotels(
        HotelSearchQuery(
            destination="Tokyo",
            check_in=date(2026, 10, 10),
            check_out=date(2026, 10, 15),
            guests=2,
        )
    )
    assert len(results) >= 3
    assert all(r.total_price_usd == r.price_per_night_usd * 5 for r in results)
    assert all(r.booking_link for r in results)


def test_flight_tradeoffs_explanations() -> None:
    flights = [
        FlightOption("a", "UA", "UA1", "t", "t", 960, 1, 845),
        FlightOption("b", "JL", "JL1", "t", "t", 660, 0, 1120),
        FlightOption("c", "NH", "NH1", "t", "t", 1320, 2, 720),
    ]
    tradeoffs = rank_flight_tradeoffs(flights)
    assert tradeoffs.cheapest is not None and tradeoffs.cheapest.price_usd == 720
    assert tradeoffs.fastest is not None and tradeoffs.fastest.duration_minutes == 660
    assert len(tradeoffs.explanations) == 3
    assert "Best value" in tradeoffs.explanations[0]
