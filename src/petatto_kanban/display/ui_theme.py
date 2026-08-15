"""UI カラーテーマプリセット（FR-028 / UC-011）."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UiTheme(StrEnum):
    """UI カラーテーマ."""

    DEFAULT = "default"
    DARK = "dark"
    SANDY = "sandy"
    FOREST = "forest"
    FANCY = "fancy"
    OCEAN = "ocean"
    SUNSET = "sunset"
    SLATE = "slate"
    ROSE = "rose"
    MIDNIGHT = "midnight"


@dataclass(frozen=True)
class UiThemePalette:
    """テーマ適用後の配色トークン."""

    ui_theme: UiTheme
    card_bg: str
    card_fg: str
    menu_fill: str
    menu_fg: str
    menu_outline: str
    progress_track_bg: str
    progress_fill_low: str
    progress_fill_mid: str
    progress_fill_high: str
    due_future_bg: str
    due_future_fg: str
    due_none_bg: str
    due_none_fg: str
    due_today_bg: str
    due_today_fg: str
    due_overdue_bg: str
    due_overdue_fg: str
    due_picker_bg: str
    due_picker_fg: str
    due_picker_day_hover_bg: str
    due_picker_day_hover_fg: str
    calendar_today_bg: str
    calendar_today_fg: str
    calendar_today_hover_bg: str
    calendar_today_hover_fg: str


def parse_ui_theme(value: str | None) -> UiTheme:
    """settings.json の ui_theme をパース。不正値は default。"""
    if value is None:
        return UiTheme.DEFAULT
    try:
        return UiTheme(value)
    except ValueError:
        return UiTheme.DEFAULT


def palette_for_theme(ui_theme: UiTheme) -> UiThemePalette:
    """テーマ ID からパレットを返す."""
    from petatto_kanban.display.ui_theme_palettes import PALETTES

    return PALETTES[ui_theme]


def resolved_palette(palette: UiThemePalette | None) -> UiThemePalette:
    """未指定時は default パレットを使う."""
    if palette is not None:
        return palette
    return palette_for_theme(UiTheme.DEFAULT)
