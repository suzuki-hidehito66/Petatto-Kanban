"""カード期限の表示・状態判定."""

from __future__ import annotations

from datetime import date

DUE_DATE_NONE_LABEL = "期限なし"
DUE_PANEL_OVERDUE_BG = "#ffcdd2"
DUE_PANEL_OVERDUE_FG = "#b71c1c"
DUE_PANEL_TODAY_BG = "#fff9c4"
DUE_PANEL_TODAY_FG = "#f57f17"
DUE_PANEL_FUTURE_BG = "#f5f5f0"
DUE_PANEL_FUTURE_FG = "#444444"
DUE_PANEL_NONE_BG = "#f5f5f0"
DUE_PANEL_NONE_FG = "#666666"


def format_due_date(value: date | None) -> str:
    """期限の表示文字列を返す."""
    if value is None:
        return DUE_DATE_NONE_LABEL
    return value.strftime("%Y/%m/%d")


def due_date_status(value: date | None, today: date | None = None) -> str:
    """期限状態: none / overdue / today / future."""
    if value is None:
        return "none"
    reference = today or date.today()
    if value < reference:
        return "overdue"
    if value == reference:
        return "today"
    return "future"


def due_date_panel_style(value: date | None, today: date | None = None) -> tuple[str, str]:
    """期限パネルの背景色・文字色を返す."""
    status = due_date_status(value, today)
    if status == "overdue":
        return DUE_PANEL_OVERDUE_BG, DUE_PANEL_OVERDUE_FG
    if status == "today":
        return DUE_PANEL_TODAY_BG, DUE_PANEL_TODAY_FG
    if status == "future":
        return DUE_PANEL_FUTURE_BG, DUE_PANEL_FUTURE_FG
    return DUE_PANEL_NONE_BG, DUE_PANEL_NONE_FG
