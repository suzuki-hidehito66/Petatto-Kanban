"""UI カラーテーマプリセット（FR-028 / UC-011）."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

_LIGHT_DUE_TODAY_BG = "#fff9c4"
_LIGHT_DUE_TODAY_FG = "#f57f17"
_LIGHT_DUE_OVERDUE_BG = "#ffcdd2"
_LIGHT_DUE_OVERDUE_FG = "#b71c1c"
_DARK_DUE_TODAY_BG = "#5c4d1a"
_DARK_DUE_TODAY_FG = "#ffe082"
_DARK_DUE_OVERDUE_BG = "#5c2a2a"
_DARK_DUE_OVERDUE_FG = "#ef9a9a"


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
    return _PALETTES[ui_theme]


_PALETTES: dict[UiTheme, UiThemePalette] = {
    UiTheme.DEFAULT: UiThemePalette(
        ui_theme=UiTheme.DEFAULT,
        card_bg="#fffef8",
        card_fg="#222222",
        menu_fill="#ffffff",
        menu_fg="#333333",
        menu_outline="#888888",
        progress_track_bg="#e8e8e8",
        due_future_bg="#f5f5f0",
        due_future_fg="#444444",
        due_none_bg="#f5f5f0",
        due_none_fg="#666666",
        due_today_bg=_LIGHT_DUE_TODAY_BG,
        due_today_fg=_LIGHT_DUE_TODAY_FG,
        due_overdue_bg=_LIGHT_DUE_OVERDUE_BG,
        due_overdue_fg=_LIGHT_DUE_OVERDUE_FG,
        due_picker_bg="#f5f5f0",
        due_picker_fg="#222222",
        due_picker_day_hover_bg="#d8d8cc",
        due_picker_day_hover_fg="#222222",
        calendar_today_bg="#43a047",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#2e7d32",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.DARK: UiThemePalette(
        ui_theme=UiTheme.DARK,
        card_bg="#1a1a1a",
        card_fg="#f2f2f2",
        menu_fill="#2b2b2b",
        menu_fg="#eeeeee",
        menu_outline="#555555",
        progress_track_bg="#333333",
        due_future_bg="#242424",
        due_future_fg="#cccccc",
        due_none_bg="#242424",
        due_none_fg="#aaaaaa",
        due_today_bg=_DARK_DUE_TODAY_BG,
        due_today_fg=_DARK_DUE_TODAY_FG,
        due_overdue_bg=_DARK_DUE_OVERDUE_BG,
        due_overdue_fg=_DARK_DUE_OVERDUE_FG,
        due_picker_bg="#222222",
        due_picker_fg="#e8e8e8",
        due_picker_day_hover_bg="#3d3d3d",
        due_picker_day_hover_fg="#e8e8e8",
        calendar_today_bg="#2e7d32",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#1b5e20",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.SANDY: UiThemePalette(
        ui_theme=UiTheme.SANDY,
        card_bg="#faf6ef",
        card_fg="#3d3429",
        menu_fill="#fff8ee",
        menu_fg="#4a4035",
        menu_outline="#c4b8a8",
        progress_track_bg="#e8dfd0",
        due_future_bg="#f0e8da",
        due_future_fg="#5c5044",
        due_none_bg="#f0e8da",
        due_none_fg="#7a6f62",
        due_today_bg=_LIGHT_DUE_TODAY_BG,
        due_today_fg=_LIGHT_DUE_TODAY_FG,
        due_overdue_bg=_LIGHT_DUE_OVERDUE_BG,
        due_overdue_fg=_LIGHT_DUE_OVERDUE_FG,
        due_picker_bg="#f5ede3",
        due_picker_fg="#3d3429",
        due_picker_day_hover_bg="#e0d0bc",
        due_picker_day_hover_fg="#3d3429",
        calendar_today_bg="#8d6e63",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#6d4c41",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.FOREST: UiThemePalette(
        ui_theme=UiTheme.FOREST,
        card_bg="#1a2e1f",
        card_fg="#e8f5e9",
        menu_fill="#243d2c",
        menu_fg="#e0eee2",
        menu_outline="#5a8a68",
        progress_track_bg="#2d4a35",
        due_future_bg="#1e3224",
        due_future_fg="#c8e6c9",
        due_none_bg="#1e3224",
        due_none_fg="#8fb59a",
        due_today_bg=_DARK_DUE_TODAY_BG,
        due_today_fg=_DARK_DUE_TODAY_FG,
        due_overdue_bg=_DARK_DUE_OVERDUE_BG,
        due_overdue_fg=_DARK_DUE_OVERDUE_FG,
        due_picker_bg="#1e3224",
        due_picker_fg="#e8f5e9",
        due_picker_day_hover_bg="#2f4d38",
        due_picker_day_hover_fg="#c8e6c9",
        calendar_today_bg="#2e7d32",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#1b5e20",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.FANCY: UiThemePalette(
        ui_theme=UiTheme.FANCY,
        card_bg="#faf5ff",
        card_fg="#3d2a4a",
        menu_fill="#f3e8ff",
        menu_fg="#5b3a6e",
        menu_outline="#b794c9",
        progress_track_bg="#eadcf5",
        due_future_bg="#efe4f8",
        due_future_fg="#4a3560",
        due_none_bg="#efe4f8",
        due_none_fg="#6b5580",
        due_today_bg=_LIGHT_DUE_TODAY_BG,
        due_today_fg=_LIGHT_DUE_TODAY_FG,
        due_overdue_bg=_LIGHT_DUE_OVERDUE_BG,
        due_overdue_fg=_LIGHT_DUE_OVERDUE_FG,
        due_picker_bg="#f5effa",
        due_picker_fg="#3d2a4a",
        due_picker_day_hover_bg="#e0d0f0",
        due_picker_day_hover_fg="#3d2a4a",
        calendar_today_bg="#8e24aa",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#6a1b9a",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.OCEAN: UiThemePalette(
        ui_theme=UiTheme.OCEAN,
        card_bg="#0d2133",
        card_fg="#e3f2fd",
        menu_fill="#163044",
        menu_fg="#d6ebf8",
        menu_outline="#4a90c0",
        progress_track_bg="#1a3a52",
        due_future_bg="#102433",
        due_future_fg="#bbdefb",
        due_none_bg="#102433",
        due_none_fg="#7aa0b8",
        due_today_bg=_DARK_DUE_TODAY_BG,
        due_today_fg=_DARK_DUE_TODAY_FG,
        due_overdue_bg=_DARK_DUE_OVERDUE_BG,
        due_overdue_fg=_DARK_DUE_OVERDUE_FG,
        due_picker_bg="#102433",
        due_picker_fg="#e3f2fd",
        due_picker_day_hover_bg="#1c3d55",
        due_picker_day_hover_fg="#bbdefb",
        calendar_today_bg="#0277bd",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#01579b",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.SUNSET: UiThemePalette(
        ui_theme=UiTheme.SUNSET,
        card_bg="#2a1a18",
        card_fg="#ffe8e0",
        menu_fill="#3d2420",
        menu_fg="#f5d5cc",
        menu_outline="#c47868",
        progress_track_bg="#4a302c",
        due_future_bg="#2e1c1a",
        due_future_fg="#ffccbc",
        due_none_bg="#2e1c1a",
        due_none_fg="#c4a098",
        due_today_bg=_DARK_DUE_TODAY_BG,
        due_today_fg=_DARK_DUE_TODAY_FG,
        due_overdue_bg=_DARK_DUE_OVERDUE_BG,
        due_overdue_fg=_DARK_DUE_OVERDUE_FG,
        due_picker_bg="#2e1c1a",
        due_picker_fg="#ffe8e0",
        due_picker_day_hover_bg="#4a2c28",
        due_picker_day_hover_fg="#ffccbc",
        calendar_today_bg="#e64a19",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#bf360c",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.SLATE: UiThemePalette(
        ui_theme=UiTheme.SLATE,
        card_bg="#f5f7fa",
        card_fg="#1e293b",
        menu_fill="#eef2f7",
        menu_fg="#334155",
        menu_outline="#94a3b8",
        progress_track_bg="#dde3ea",
        due_future_bg="#e8edf2",
        due_future_fg="#334155",
        due_none_bg="#e8edf2",
        due_none_fg="#64748b",
        due_today_bg=_LIGHT_DUE_TODAY_BG,
        due_today_fg=_LIGHT_DUE_TODAY_FG,
        due_overdue_bg=_LIGHT_DUE_OVERDUE_BG,
        due_overdue_fg=_LIGHT_DUE_OVERDUE_FG,
        due_picker_bg="#edf1f5",
        due_picker_fg="#1e293b",
        due_picker_day_hover_bg="#d0d8e2",
        due_picker_day_hover_fg="#1e293b",
        calendar_today_bg="#546e7a",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#37474f",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.ROSE: UiThemePalette(
        ui_theme=UiTheme.ROSE,
        card_bg="#fff5f7",
        card_fg="#4a1942",
        menu_fill="#fce4ec",
        menu_fg="#880e4f",
        menu_outline="#f48fb1",
        progress_track_bg="#f8d7e0",
        due_future_bg="#fdeef2",
        due_future_fg="#6b2149",
        due_none_bg="#fdeef2",
        due_none_fg="#8a4560",
        due_today_bg=_LIGHT_DUE_TODAY_BG,
        due_today_fg=_LIGHT_DUE_TODAY_FG,
        due_overdue_bg=_LIGHT_DUE_OVERDUE_BG,
        due_overdue_fg=_LIGHT_DUE_OVERDUE_FG,
        due_picker_bg="#fef0f3",
        due_picker_fg="#4a1942",
        due_picker_day_hover_bg="#f0cdd8",
        due_picker_day_hover_fg="#4a1942",
        calendar_today_bg="#ec407a",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#c2185b",
        calendar_today_hover_fg="#ffffff",
    ),
    UiTheme.MIDNIGHT: UiThemePalette(
        ui_theme=UiTheme.MIDNIGHT,
        card_bg="#12161f",
        card_fg="#f0f2f8",
        menu_fill="#1c2230",
        menu_fg="#e4e8f0",
        menu_outline="#6a7a98",
        progress_track_bg="#252b3c",
        due_future_bg="#161a26",
        due_future_fg="#c8d0dc",
        due_none_bg="#161a26",
        due_none_fg="#9aa4b4",
        due_today_bg=_DARK_DUE_TODAY_BG,
        due_today_fg=_DARK_DUE_TODAY_FG,
        due_overdue_bg=_DARK_DUE_OVERDUE_BG,
        due_overdue_fg=_DARK_DUE_OVERDUE_FG,
        due_picker_bg="#161a26",
        due_picker_fg="#f0f2f8",
        due_picker_day_hover_bg="#2a3144",
        due_picker_day_hover_fg="#e0e4ec",
        calendar_today_bg="#3949ab",
        calendar_today_fg="#ffffff",
        calendar_today_hover_bg="#283593",
        calendar_today_hover_fg="#ffffff",
    ),
}
