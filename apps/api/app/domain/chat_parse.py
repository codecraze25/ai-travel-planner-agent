"""Lightweight natural-language trip field extraction for chat-first UX."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ParsedTripIntent:
    origin: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    travelers: int | None = None
    budget_usd: float | None = None
    wants_plan: bool = False


_ROUTE = re.compile(
    r"\b([A-Za-z][A-Za-z\s]{1,40}?)\s*(?:to|->|→)\s*([A-Za-z][A-Za-z\s]{1,40}?)\b",
    re.IGNORECASE,
)
_DATES = re.compile(
    r"\b(\d{4}-\d{2}-\d{2})\s*(?:to|-|–|—)\s*(\d{4}-\d{2}-\d{2})\b",
)
_TRAVELERS = re.compile(r"\b(\d+)\s*(?:travelers?|people|passengers?)\b", re.IGNORECASE)
_BUDGET = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)", re.IGNORECASE)


_LEADING_VERBS = re.compile(
    r"^(?:please\s+)?(?:plan|book|arrange|schedule)\s+",
    re.IGNORECASE,
)


def parse_trip_intent(message: str) -> ParsedTripIntent:
    original = message.strip()
    text = _LEADING_VERBS.sub("", original)
    origin = destination = None
    route = _ROUTE.search(text)
    if route:
        origin = route.group(1).strip(" ,.")
        destination = route.group(2).strip(" ,.")
        # Trim trailing date-like tokens from destination
        destination = re.split(r"\s+\d", destination, maxsplit=1)[0].strip()

    start_date = end_date = None
    dates = _DATES.search(text)
    if dates:
        start_date = date.fromisoformat(dates.group(1))
        end_date = date.fromisoformat(dates.group(2))

    travelers = None
    tmatch = _TRAVELERS.search(text)
    if tmatch:
        travelers = int(tmatch.group(1))

    budget_usd = None
    bmatch = _BUDGET.search(text)
    if bmatch:
        budget_usd = float(bmatch.group(1).replace(",", ""))

    wants_plan = bool(
        re.search(r"\b(plan|book|itinerary|trip|flight|hotel)\b", original, re.IGNORECASE)
    )

    return ParsedTripIntent(
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travelers=travelers,
        budget_usd=budget_usd,
        wants_plan=wants_plan,
    )


def default_trip_dates() -> tuple[date, date]:
    start = date.today() + timedelta(days=30)
    end = start + timedelta(days=5)
    return start, end
