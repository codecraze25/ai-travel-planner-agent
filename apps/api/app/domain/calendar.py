"""Calendar domain — stub events for trip dates (Phase 6)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class CalendarEvent:
    title: str
    start: str
    end: str
    location: str
    source: str


def build_stub_calendar_events(
    *,
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
) -> list[CalendarEvent]:
    """Deterministic calendar events for local/CI without Google Calendar OAuth."""
    return [
        CalendarEvent(
            title=f"Depart {origin}",
            start=f"{start_date.isoformat()}T08:00:00",
            end=f"{start_date.isoformat()}T11:00:00",
            location=origin,
            source="stub",
        ),
        CalendarEvent(
            title=f"In {destination}",
            start=f"{start_date.isoformat()}T18:00:00",
            end=f"{(end_date - timedelta(days=1)).isoformat()}T18:00:00",
            location=destination,
            source="stub",
        ),
        CalendarEvent(
            title=f"Return to {origin}",
            start=f"{end_date.isoformat()}T10:00:00",
            end=f"{end_date.isoformat()}T14:00:00",
            location=origin,
            source="stub",
        ),
    ]
