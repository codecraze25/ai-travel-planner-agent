from datetime import date

from app.domain.guardrails import can_book_hotel, can_send_email, is_tool_allowed
from app.domain.itinerary import build_mock_itinerary, trip_day_count


def test_send_email_blocked_without_approval() -> None:
    assert not can_send_email(user_approved=False)
    allowed, reason = is_tool_allowed("send_email", user_approved=False)
    assert not allowed
    assert reason is not None


def test_send_email_allowed_with_approval() -> None:
    assert can_send_email(user_approved=True)
    allowed, _ = is_tool_allowed("send_email", user_approved=True)
    assert allowed


def test_book_hotel_blocked_in_mvp() -> None:
    assert not can_book_hotel(mvp_mode=True)
    allowed, reason = is_tool_allowed("book_hotel")
    assert not allowed
    assert "MVP" in (reason or "")


def test_search_flights_allowed() -> None:
    allowed, reason = is_tool_allowed("search_flights")
    assert allowed
    assert reason is None


def test_tokyo_itinerary_day_count() -> None:
    start = date(2026, 10, 10)
    end = date(2026, 10, 15)
    plans = build_mock_itinerary(
        destination="Tokyo",
        start_date=start,
        end_date=end,
        travelers=2,
    )
    assert len(plans) == trip_day_count(start, end)
    assert plans[0].blocks[0].time_block.value == "morning"


def test_itinerary_has_positive_costs() -> None:
    plans = build_mock_itinerary(
        destination="Paris",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 4),
        travelers=1,
    )
    assert sum(p.daily_cost_usd for p in plans) >= 0
