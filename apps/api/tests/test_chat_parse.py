from datetime import date

from app.domain.chat_parse import parse_trip_intent


def test_parse_route_dates_budget() -> None:
    intent = parse_trip_intent(
        "Plan San Francisco to Tokyo 2026-10-10 to 2026-10-15 for 2 travelers $4000"
    )
    assert intent.origin == "San Francisco"
    assert intent.destination == "Tokyo"
    assert intent.start_date == date(2026, 10, 10)
    assert intent.end_date == date(2026, 10, 15)
    assert intent.travelers == 2
    assert intent.budget_usd == 4000.0
    assert intent.wants_plan is True
