"""カード期限の表示・状態判定."""

from __future__ import annotations

from datetime import date

from petatto_kanban.display.ui_theme import UiThemePalette, resolved_palette

DUE_DATE_NONE_LABEL = "期限なし"


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


def due_date_panel_style(
    value: date | None,
    today: date | None = None,
    *,
    palette: UiThemePalette | None = None,
) -> tuple[str, str]:
    """期限パネルの背景色・文字色を返す."""
    colors = resolved_palette(palette)
    status = due_date_status(value, today)
    if status == "overdue":
        return colors.due_overdue_bg, colors.due_overdue_fg
    if status == "today":
        return colors.due_today_bg, colors.due_today_fg
    if status == "future":
        return colors.due_future_bg, colors.due_future_fg
    return colors.due_none_bg, colors.due_none_fg
