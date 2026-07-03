from __future__ import annotations

from app.adapters.providers.mock_flights import MockFlightProvider
from app.adapters.providers.mock_hotels import MockHotelProvider
from app.core.config import Settings, get_settings


def get_flight_provider(settings: Settings | None = None) -> MockFlightProvider:
    # Real Duffel adapter lands when USE_MOCK_PROVIDERS=false and token is set.
    _ = settings or get_settings()
    return MockFlightProvider()


def get_hotel_provider(settings: Settings | None = None) -> MockHotelProvider:
    # Real Amadeus adapter lands when USE_MOCK_PROVIDERS=false and credentials are set.
    _ = settings or get_settings()
    return MockHotelProvider()
