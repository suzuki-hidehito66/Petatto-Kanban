"""期限ユーティリティのテスト."""

from datetime import date

from petatto_kanban.due_date import (
    DUE_DATE_NONE_LABEL,
    due_date_panel_style,
    due_date_status,
    format_due_date,
)


def test_format_due_date_none() -> None:
    assert format_due_date(None) == DUE_DATE_NONE_LABEL


def test_format_due_date_value() -> None:
    assert format_due_date(date(2026, 8, 12)) == "2026/08/12"


def test_due_date_status_colors() -> None:
    today = date(2026, 8, 12)
    assert due_date_status(None, today) == "none"
    assert due_date_status(date(2026, 8, 11), today) == "overdue"
    assert due_date_status(date(2026, 8, 12), today) == "today"
    assert due_date_status(date(2026, 8, 13), today) == "future"

    overdue_bg, _ = due_date_panel_style(date(2026, 8, 11), today)
    today_bg, _ = due_date_panel_style(date(2026, 8, 12), today)
    assert overdue_bg != today_bg
