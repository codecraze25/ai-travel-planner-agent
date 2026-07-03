from __future__ import annotations

from typing import Protocol

from app.domain.travel import FlightOption, FlightSearchQuery, HotelOption, HotelSearchQuery


class FlightProvider(Protocol):
    async def search_flights(self, query: FlightSearchQuery) -> list[FlightOption]: ...


class HotelProvider(Protocol):
    async def search_hotels(self, query: HotelSearchQuery) -> list[HotelOption]: ...
