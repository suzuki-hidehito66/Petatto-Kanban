"""カレンダー日付セルの配色・枠ジオメトリ（FR-014 / UC-008）。tkinter 非依存."""

from __future__ import annotations

from datetime import date
from typing import NamedTuple

from petatto_kanban.display.ui_theme import UiThemePalette, resolved_palette

CALENDAR_DAY_CELL_WIDTH = 3
CALENDAR_DAY_CELL_BD = 1
CALENDAR_DAY_CELL_HIGHLIGHTTHICKNESS = 0
CALENDAR_DAY_CELL_PADX = 1
CALENDAR_DAY_CELL_PADY = 1
CALENDAR_COLUMNS = 7


class CalendarDayButtonStyle(NamedTuple):
    """カレンダー日付ボタンの通常色・ホバー色・ relief."""

    bg: str
    fg: str
    hover_bg: str
    hover_fg: str
    relief: str


def calendar_day_cell_geometry() -> dict[str, int]:
    """日付ボタンと空セルで共通の枠ジオメトリ（ホバーで外寸が変わらない）."""
    return {
        "width": CALENDAR_DAY_CELL_WIDTH,
        "bd": CALENDAR_DAY_CELL_BD,
        "highlightthickness": CALENDAR_DAY_CELL_HIGHLIGHTTHICKNESS,
    }


def calendar_day_button_style(
    day: date,
    *,
    selected: date | None,
    default_bg: str,
    default_fg: str = "#222222",
    today: date | None = None,
    palette: UiThemePalette | None = None,
) -> CalendarDayButtonStyle:
    """カレンダー日付ボタンの背景色・文字色・ホバー色・ relief を返す."""
    colors = resolved_palette(palette)
    reference = today or date.today()
    if day == reference:
        bg = colors.calendar_today_bg
        fg = colors.calendar_today_fg
        hover_bg = colors.calendar_today_hover_bg
        hover_fg = colors.calendar_today_hover_fg
    else:
        bg = default_bg
        fg = default_fg
        hover_bg = colors.due_picker_day_hover_bg
        hover_fg = colors.due_picker_day_hover_fg
    relief = "sunken" if selected == day else "flat"
    return CalendarDayButtonStyle(
        bg=bg,
        fg=fg,
        hover_bg=hover_bg,
        hover_fg=hover_fg,
        relief=relief,
    )
