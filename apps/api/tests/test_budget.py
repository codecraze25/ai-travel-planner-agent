from app.domain.travel import calculate_budget


def test_budget_under_threshold() -> None:
    summary = calculate_budget(4000, flight_cost_usd=845, hotel_cost_usd=900)
    assert summary.committed_usd == 1745
    assert summary.remaining_usd == 2255
    assert summary.warning is None


def test_budget_warning_at_80_percent() -> None:
    summary = calculate_budget(4000, flight_cost_usd=2000, hotel_cost_usd=1300)
    assert summary.utilization_pct == 82.5
    assert summary.warning is not None
    assert "Budget warning" in summary.warning


def test_budget_over_budget() -> None:
    summary = calculate_budget(1000, flight_cost_usd=800, hotel_cost_usd=300)
    assert summary.remaining_usd == -100
    assert summary.warning is not None
    assert "Over budget" in summary.warning
