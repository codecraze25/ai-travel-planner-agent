from datetime import date

from app.domain.email import (
    EmailTemplate,
    build_email_draft,
    build_eml,
    format_itinerary_summary,
)
from app.domain.guardrails import can_send_email, is_tool_allowed


def test_format_itinerary_summary() -> None:
    summary = format_itinerary_summary(
        [
            {"day_number": 1, "time_block": "morning", "title": "Arrive", "est_cost_usd": 0},
            {"day_number": 1, "time_block": "evening", "title": "Dinner", "est_cost_usd": 40},
        ]
    )
    assert "Day 1" in summary
    assert "Arrive" in summary


def test_build_itinerary_summary_draft() -> None:
    draft = build_email_draft(
        template=EmailTemplate.ITINERARY_SUMMARY,
        origin="SFO",
        destination="Tokyo",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        travelers=2,
        itinerary_summary="Day 1:\n  - morning: Arrive ($0)",
        recipient="demo@example.com",
    )
    assert "Tokyo" in draft.subject
    assert "Nothing has been sent" in draft.body_text


def test_build_eml_contains_headers() -> None:
    eml = build_eml(
        from_addr="me@example.com",
        to_addr="you@example.com",
        subject="Trip",
        body_text="Hello",
        body_html="<p>Hello</p>",
    )
    assert "To: you@example.com" in eml
    assert "Subject: Trip" in eml


def test_export_blocked_without_approval() -> None:
    assert not can_send_email(user_approved=False)
    allowed, reason = is_tool_allowed("send_email", user_approved=False)
    assert not allowed
    assert reason is not None


def test_export_allowed_after_approval() -> None:
    assert can_send_email(user_approved=True)
    allowed, _ = is_tool_allowed("send_email", user_approved=True)
    assert allowed


def test_send_blocked_without_approval() -> None:
    allowed, reason = is_tool_allowed("send_email", user_approved=False)
    assert not allowed
    assert reason is not None
