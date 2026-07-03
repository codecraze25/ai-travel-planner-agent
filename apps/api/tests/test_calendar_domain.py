from datetime import date

from app.domain.calendar import build_stub_calendar_events


def test_stub_calendar_has_departure_and_return() -> None:
    events = build_stub_calendar_events(
        origin="SFO",
        destination="Tokyo",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
    )
    assert len(events) == 3
    assert "SFO" in events[0].title
    assert "Tokyo" in events[1].title
    assert events[0].source == "stub"
