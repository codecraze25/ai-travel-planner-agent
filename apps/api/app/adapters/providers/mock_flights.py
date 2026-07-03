from __future__ import annotations

from app.domain.travel import FlightOption, FlightSearchQuery


class MockFlightProvider:
    """Deterministic flight results for local/CI (no API keys)."""

    async def search_flights(self, query: FlightSearchQuery) -> list[FlightOption]:
        origin = query.origin[:3].upper()
        dest = query.destination[:3].upper()
        date = query.departure_date.isoformat()

        options = [
            FlightOption(
                external_id=f"mock-fast-{origin}-{dest}",
                airline="Japan Airlines",
                flight_number="JL001",
                departure_time=f"{date}T10:00:00",
                arrival_time=f"{date}T14:00:00",
                duration_minutes=660,
                stops=0,
                price_usd=1120.0 * query.passengers,
                baggage_info="1 checked bag included",
                booking_link="https://example.com/book/jl001",
                cancellation_policy="Refundable with fee up to 24h before departure",
            ),
            FlightOption(
                external_id=f"mock-value-{origin}-{dest}",
                airline="United Airlines",
                flight_number="UA837",
                departure_time=f"{date}T08:30:00",
                arrival_time=f"{date}T16:45:00",
                duration_minutes=960,
                stops=1,
                price_usd=845.0 * query.passengers,
                baggage_info="Carry-on only; checked bag $60",
                booking_link="https://example.com/book/ua837",
                cancellation_policy="Non-refundable; change fee $200",
            ),
            FlightOption(
                external_id=f"mock-cheap-{origin}-{dest}",
                airline="ANA",
                flight_number="NH008",
                departure_time=f"{date}T06:00:00",
                arrival_time=f"{date}T22:30:00",
                duration_minutes=1320,
                stops=2,
                price_usd=720.0 * query.passengers,
                baggage_info="No bags included",
                booking_link="https://example.com/book/nh008",
                cancellation_policy="Non-refundable",
            ),
            FlightOption(
                external_id=f"mock-mid-{origin}-{dest}",
                airline="Delta",
                flight_number="DL295",
                departure_time=f"{date}T12:15:00",
                arrival_time=f"{date}T18:40:00",
                duration_minutes=780,
                stops=1,
                price_usd=980.0 * query.passengers,
                baggage_info="1 checked bag included",
                booking_link="https://example.com/book/dl295",
                cancellation_policy="Partially refundable",
            ),
        ]

        if query.nonstop_only:
            options = [f for f in options if f.stops == 0]
        if query.max_price is not None:
            options = [f for f in options if f.price_usd <= query.max_price]
        return options
