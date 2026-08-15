"""期限ユーティリティのテスト."""

from datetime import date

from petatto_kanban.display.ui_theme import UiTheme, palette_for_theme
from petatto_kanban.due_date import (
    CALENDAR_DAY_CELL_BD,
    CALENDAR_DAY_CELL_HIGHLIGHTTHICKNESS,
    CALENDAR_DAY_CELL_WIDTH,
    CALENDAR_TODAY_BUTTON_BG,
    CALENDAR_TODAY_BUTTON_HOVER_BG,
    DUE_DATE_NONE_LABEL,
    calendar_day_button_style,
    calendar_day_cell_geometry,
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


def test_calendar_day_button_style_today_is_green() -> None:
    today = date(2026, 8, 12)
    style = calendar_day_button_style(
        today,
        selected=None,
        default_bg="#ffffff",
        today=today,
    )
    assert style.bg == CALENDAR_TODAY_BUTTON_BG
    assert style.fg == "#ffffff"
    assert style.hover_bg == CALENDAR_TODAY_BUTTON_HOVER_BG
    assert style.hover_fg == "#ffffff"
    assert style.relief == "flat"


def test_calendar_day_button_style_selected_uses_sunken() -> None:
    picked = date(2026, 8, 15)
    style = calendar_day_button_style(
        picked,
        selected=picked,
        default_bg="#ffffff",
        today=date(2026, 8, 12),
    )
    assert style.relief == "sunken"


def test_calendar_day_button_style_normal_hover_follows_theme() -> None:
    today = date(2026, 8, 12)
    day = date(2026, 8, 20)
    default_palette = palette_for_theme(UiTheme.DEFAULT)
    dark_palette = palette_for_theme(UiTheme.DARK)
    default_style = calendar_day_button_style(
        day,
        selected=None,
        default_bg=default_palette.due_picker_bg,
        default_fg=default_palette.due_picker_fg,
        today=today,
        palette=default_palette,
    )
    dark_style = calendar_day_button_style(
        day,
        selected=None,
        default_bg=dark_palette.due_picker_bg,
        default_fg=dark_palette.due_picker_fg,
        today=today,
        palette=dark_palette,
    )
    assert default_style.hover_bg == default_palette.due_picker_day_hover_bg
    assert default_style.hover_fg == default_palette.due_picker_day_hover_fg
    assert default_style.hover_bg != default_style.bg
    assert dark_style.hover_bg == dark_palette.due_picker_day_hover_bg
    assert dark_style.hover_bg != default_style.hover_bg


def test_calendar_day_button_style_today_hover_ignores_theme() -> None:
    today = date(2026, 8, 12)
    palette = palette_for_theme(UiTheme.DARK)
    style = calendar_day_button_style(
        today,
        selected=None,
        default_bg=palette.due_picker_bg,
        default_fg=palette.due_picker_fg,
        today=today,
        palette=palette,
    )
    assert style.bg == CALENDAR_TODAY_BUTTON_BG
    assert style.hover_bg == CALENDAR_TODAY_BUTTON_HOVER_BG
    assert style.hover_bg != palette.due_picker_day_hover_bg


def test_calendar_day_cell_geometry_is_fixed() -> None:
    geometry = calendar_day_cell_geometry()
    assert geometry["width"] == CALENDAR_DAY_CELL_WIDTH
    assert geometry["bd"] == CALENDAR_DAY_CELL_BD
    assert geometry["highlightthickness"] == CALENDAR_DAY_CELL_HIGHLIGHTTHICKNESS
    assert calendar_day_cell_geometry() == geometry
