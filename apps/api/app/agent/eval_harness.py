"""Agent eval harness for golden-path and guardrail regression tests."""

from __future__ import annotations

from datetime import date

from app.domain.guardrails import is_tool_allowed
from app.domain.itinerary import build_mock_itinerary, trip_day_count


def eval_guardrails_no_send_without_approval() -> None:
    allowed, _ = is_tool_allowed("send_email", user_approved=False)
    assert not allowed, "send_email must be blocked without approval"


def eval_guardrails_no_book_in_mvp() -> None:
    allowed, _ = is_tool_allowed("book_hotel", user_approved=True)
    assert not allowed, "book_hotel must be blocked in MVP"


def eval_golden_tokyo_itinerary() -> None:
    """Tokyo Oct 10–15 scenario produces 5 full days."""
    plans = build_mock_itinerary(
        destination="Tokyo",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        travelers=2,
        hotel_name="Hotel Gracery Shinjuku",
        check_in="Oct 10, 3 PM",
        check_out="Oct 15, 11 AM",
    )
    assert len(plans) == trip_day_count(date(2026, 10, 10), date(2026, 10, 15))
    assert plans[0].blocks[0].title == "Arrival & hotel check-in"
    assert "Senso-ji" in plans[0].blocks[1].title or "Tsukiji" in plans[1].blocks[0].title
    total_cost = sum(p.daily_cost_usd for p in plans)
    assert total_cost > 0


def run_eval_suite() -> None:
    eval_guardrails_no_send_without_approval()
    eval_guardrails_no_book_in_mvp()
    eval_golden_tokyo_itinerary()
