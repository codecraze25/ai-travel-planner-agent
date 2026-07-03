"""Agent tool schemas (wired in Phase 4)."""

from __future__ import annotations

SEARCH_FLIGHTS_TOOL = {
    "name": "search_flights",
    "description": "Search flights for a trip using origin, destination, and dates.",
    "parameters": {
        "type": "object",
        "properties": {
            "trip_id": {"type": "string"},
            "cabin_class": {"type": "string"},
            "max_price": {"type": "number"},
            "nonstop_only": {"type": "boolean"},
        },
        "required": ["trip_id"],
    },
}

SEARCH_HOTELS_TOOL = {
    "name": "search_hotels",
    "description": "Search hotels for a trip destination and dates.",
    "parameters": {
        "type": "object",
        "properties": {
            "trip_id": {"type": "string"},
            "rooms": {"type": "integer"},
            "max_price_per_night": {"type": "number"},
            "min_rating": {"type": "number"},
        },
        "required": ["trip_id"],
    },
}
