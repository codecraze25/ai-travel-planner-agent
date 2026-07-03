"""Itinerary domain entities and mock generation for offline dev."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any
from urllib.parse import quote


class TimeBlock(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


@dataclass(frozen=True)
class ItineraryBlock:
    time_block: TimeBlock
    title: str
    description: str
    location: str
    est_cost_usd: float
    map_url: str


@dataclass(frozen=True)
class ItineraryDayPlan:
    day_number: int
    date_label: str
    blocks: tuple[ItineraryBlock, ...]
    daily_cost_usd: float
    backup_option: str


def trip_day_count(start_date: date, end_date: date) -> int:
    """Number of full days between start (inclusive) and end (exclusive checkout)."""
    return max(1, (end_date - start_date).days)


def _map_url(location: str, destination: str) -> str:
    query = quote(f"{location}, {destination}")
    return f"https://maps.google.com/?q={query}"


_TOKYO_ACTIVITIES: list[tuple[str, str, str, float]] = [
    (
        "Senso-ji Temple",
        "Explore Asakusa's historic temple and Nakamise shopping street.",
        "Asakusa",
        0.0,
    ),
    ("Tsukiji Outer Market", "Sample fresh sushi and street food.", "Tsukiji", 35.0),
    ("teamLab Planets", "Immersive digital art experience.", "Toyosu", 32.0),
    ("Meiji Shrine", "Quiet forest walk and Shinto shrine visit.", "Shibuya", 0.0),
    ("Shinjuku Gyoen", "Stroll through Japanese and French gardens.", "Shinjuku", 5.0),
    ("Tokyo National Museum", "Japan's largest collection of cultural artifacts.", "Ueno", 12.0),
    ("Shibuya Crossing & Hachiko", "Iconic scramble crossing and photo stop.", "Shibuya", 0.0),
    ("Akihabara", "Electronics, anime culture, and retro arcades.", "Akihabara", 20.0),
    ("Odaiba waterfront", "Bay views, shopping, and Rainbow Bridge at dusk.", "Odaiba", 15.0),
    ("Harajuku & Takeshita Street", "Youth fashion, crepes, and pop culture.", "Harajuku", 25.0),
]

_GENERIC_ACTIVITIES: list[tuple[str, str, str, float]] = [
    ("City walking tour", "Self-guided orientation walk near your hotel.", "City center", 0.0),
    ("Local market", "Browse regional food and crafts.", "Downtown", 20.0),
    ("Museum visit", "Half-day at the main city museum.", "Cultural district", 15.0),
    ("Neighborhood food crawl", "Sample local specialties for lunch and snacks.", "Old town", 40.0),
    ("Park and viewpoints", "Relax outdoors with city skyline views.", "Central park", 0.0),
]


def build_mock_itinerary(
    *,
    destination: str,
    start_date: date,
    end_date: date,
    travelers: int,
    hotel_name: str | None = None,
    check_in: str | None = None,
    check_out: str | None = None,
) -> list[ItineraryDayPlan]:
    """Deterministic itinerary for mock LLM / CI golden-path tests."""
    days = trip_day_count(start_date, end_date)
    activities = _TOKYO_ACTIVITIES if "tokyo" in destination.lower() else _GENERIC_ACTIVITIES
    hotel_label = hotel_name or f"Hotel in {destination}"
    plans: list[ItineraryDayPlan] = []

    for day_idx in range(days):
        day_number = day_idx + 1
        day_date = start_date + timedelta(days=day_idx)
        date_label = day_date.isoformat()
        act = activities[day_idx % len(activities)]

        blocks: list[ItineraryBlock] = []
        if day_idx == 0:
            arrival_note = f"Check in at {hotel_label}"
            if check_in:
                arrival_note += f" (confirmation: {check_in})"
            blocks.append(
                ItineraryBlock(
                    time_block=TimeBlock.MORNING,
                    title="Arrival & hotel check-in",
                    description=arrival_note + ". Drop bags and acclimate.",
                    location=hotel_label,
                    est_cost_usd=0.0,
                    map_url=_map_url(hotel_label, destination),
                )
            )
            blocks.append(
                ItineraryBlock(
                    time_block=TimeBlock.AFTERNOON,
                    title=act[0],
                    description=act[1],
                    location=act[2],
                    est_cost_usd=act[3] * travelers,
                    map_url=_map_url(act[2], destination),
                )
            )
            blocks.append(
                ItineraryBlock(
                    time_block=TimeBlock.EVENING,
                    title="Dinner near hotel",
                    description="Casual izakaya or hotel restaurant — budget ~$25/person.",
                    location="Near hotel",
                    est_cost_usd=25.0 * travelers,
                    map_url=_map_url(destination, destination),
                )
            )
        elif day_idx == days - 1:
            checkout_note = f"Check out from {hotel_label}"
            if check_out:
                checkout_note += f" by {check_out}"
            blocks.append(
                ItineraryBlock(
                    time_block=TimeBlock.MORNING,
                    title="Departure prep",
                    description=checkout_note + ". Last-minute shopping if time allows.",
                    location=hotel_label,
                    est_cost_usd=0.0,
                    map_url=_map_url(hotel_label, destination),
                )
            )
            blocks.append(
                ItineraryBlock(
                    time_block=TimeBlock.AFTERNOON,
                    title="Transfer to airport",
                    description="Allow 3+ hours before international departure.",
                    location="Airport",
                    est_cost_usd=30.0 * travelers,
                    map_url=_map_url("airport", destination),
                )
            )
        else:
            blocks.extend(
                [
                    ItineraryBlock(
                        time_block=TimeBlock.MORNING,
                        title=act[0],
                        description=act[1],
                        location=act[2],
                        est_cost_usd=act[3] * travelers,
                        map_url=_map_url(act[2], destination),
                    ),
                    ItineraryBlock(
                        time_block=TimeBlock.AFTERNOON,
                        title="Local lunch & explore",
                        description="Flexible time for cafes, shops, or a short museum visit.",
                        location=act[2],
                        est_cost_usd=30.0 * travelers,
                        map_url=_map_url(act[2], destination),
                    ),
                    ItineraryBlock(
                        time_block=TimeBlock.EVENING,
                        title="Evening activity",
                        description="Neighborhood stroll or reserved restaurant if desired.",
                        location=destination,
                        est_cost_usd=40.0 * travelers,
                        map_url=_map_url(destination, destination),
                    ),
                ]
            )

        daily_cost = sum(b.est_cost_usd for b in blocks)
        backup = f"Rainy-day alternative: indoor mall or onsen near {destination}."
        plans.append(
            ItineraryDayPlan(
                day_number=day_number,
                date_label=date_label,
                blocks=tuple(blocks),
                daily_cost_usd=round(daily_cost, 2),
                backup_option=backup,
            )
        )

    return plans


def itinerary_to_dict(plans: list[ItineraryDayPlan]) -> dict[str, Any]:
    total = sum(p.daily_cost_usd for p in plans)
    return {
        "days": [
            {
                "day_number": p.day_number,
                "date_label": p.date_label,
                "daily_cost_usd": p.daily_cost_usd,
                "backup_option": p.backup_option,
                "blocks": [
                    {
                        "time_block": b.time_block.value,
                        "title": b.title,
                        "description": b.description,
                        "location": b.location,
                        "est_cost_usd": b.est_cost_usd,
                        "map_url": b.map_url,
                    }
                    for b in p.blocks
                ],
            }
            for p in plans
        ],
        "total_est_cost_usd": round(total, 2),
    }
