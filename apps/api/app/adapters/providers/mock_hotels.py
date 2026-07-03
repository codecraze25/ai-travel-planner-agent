from __future__ import annotations

from app.domain.travel import HotelOption, HotelSearchQuery


class MockHotelProvider:
    """Deterministic hotel results for local/CI (no API keys)."""

    async def search_hotels(self, query: HotelSearchQuery) -> list[HotelOption]:
        nights = max((query.check_out - query.check_in).days, 1)
        dest = query.destination

        options = [
            HotelOption(
                external_id=f"mock-hotel-shinjuku-{dest}",
                name="Shinjuku Station Hotel",
                price_per_night_usd=180.0,
                total_price_usd=180.0 * nights,
                rating=4.5,
                location="Shinjuku, near train station",
                amenities=["WiFi", "Breakfast", "Gym"],
                cancellation_policy="Free cancellation until 48h before check-in",
                photo_urls=["https://example.com/photos/shinjuku.jpg"],
                booking_link="https://example.com/book/shinjuku-hotel",
            ),
            HotelOption(
                external_id=f"mock-hotel-shibuya-{dest}",
                name="Shibuya Skyline Inn",
                price_per_night_usd=145.0,
                total_price_usd=145.0 * nights,
                rating=4.2,
                location="Shibuya",
                amenities=["WiFi", "Restaurant"],
                cancellation_policy="Non-refundable rate available",
                photo_urls=["https://example.com/photos/shibuya.jpg"],
                booking_link="https://example.com/book/shibuya-inn",
            ),
            HotelOption(
                external_id=f"mock-hotel-ginza-{dest}",
                name="Ginza Grand Hotel",
                price_per_night_usd=260.0,
                total_price_usd=260.0 * nights,
                rating=4.8,
                location="Ginza",
                amenities=["WiFi", "Spa", "Pool", "Breakfast"],
                cancellation_policy="Free cancellation until 24h before check-in",
                photo_urls=["https://example.com/photos/ginza.jpg"],
                booking_link="https://example.com/book/ginza-grand",
            ),
            HotelOption(
                external_id=f"mock-hotel-budget-{dest}",
                name="Asakusa Budget Stay",
                price_per_night_usd=95.0,
                total_price_usd=95.0 * nights,
                rating=3.9,
                location="Asakusa",
                amenities=["WiFi"],
                cancellation_policy="Non-refundable",
                photo_urls=["https://example.com/photos/asakusa.jpg"],
                booking_link="https://example.com/book/asakusa-budget",
            ),
        ]

        if query.max_price_per_night is not None:
            options = [h for h in options if h.price_per_night_usd <= query.max_price_per_night]
        if query.min_rating is not None:
            options = [h for h in options if h.rating >= query.min_rating]
        return options
