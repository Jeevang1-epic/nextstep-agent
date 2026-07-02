from mcp_server.server import deadline_calculator


def test_absolute_deadline_date() -> None:
    result = deadline_calculator("Payment due by July 12, 2026.", "2026-07-02")

    assert result["due_date"] == "2026-07-12"
    assert result["days_remaining"] == 10
    assert result["status"] == "upcoming"


def test_next_weekday_deadline() -> None:
    result = deadline_calculator("Bring the form next Friday.", "2026-07-02")

    assert result["due_date"] == "2026-07-03"
    assert result["days_remaining"] == 1
    assert result["status"] == "due_soon"


def test_business_day_window() -> None:
    result = deadline_calculator("Call within 5 business days.", "2026-07-02")

    assert result["due_date"] == "2026-07-09"
    assert result["days_remaining"] == 7
    assert result["status"] == "due_soon"


def test_overdue_deadline() -> None:
    result = deadline_calculator("Submit by July 1, 2026.", "2026-07-02")

    assert result["due_date"] == "2026-07-01"
    assert result["days_remaining"] == -1
    assert result["status"] == "overdue"
