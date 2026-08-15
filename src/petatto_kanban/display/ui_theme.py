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
    due_future_bg: str
    due_future_fg: str
    due_none_bg: str
    due_none_fg: str
    due_picker_bg: str
    due_picker_fg: str
    due_picker_day_hover_bg: str
    due_picker_day_hover_fg: str


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
        due_picker_bg="#f5f5f0",
        due_picker_fg="#222222",
        due_picker_day_hover_bg="#d8d8cc",
        due_picker_day_hover_fg="#222222",
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
        due_picker_bg="#222222",
        due_picker_fg="#e8e8e8",
        due_picker_day_hover_bg="#3d3d3d",
        due_picker_day_hover_fg="#e8e8e8",
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
        due_picker_bg="#f5ede3",
        due_picker_fg="#3d3429",
        due_picker_day_hover_bg="#e0d0bc",
        due_picker_day_hover_fg="#3d3429",
    ),
    UiTheme.FOREST: UiThemePalette(
        ui_theme=UiTheme.FOREST,
        card_bg="#f4f9f4",
        card_fg="#1b3d2a",
        menu_fill="#e8f5e9",
        menu_fg="#1b4332",
        menu_outline="#6b9080",
        progress_track_bg="#d4e8d4",
        due_future_bg="#e0efe0",
        due_future_fg="#2d5a3d",
        due_none_bg="#e0efe0",
        due_none_fg="#4a6b55",
        due_picker_bg="#edf5ed",
        due_picker_fg="#1b3d2a",
        due_picker_day_hover_bg="#c8e0c8",
        due_picker_day_hover_fg="#1b3d2a",
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
        due_picker_bg="#f5effa",
        due_picker_fg="#3d2a4a",
        due_picker_day_hover_bg="#e0d0f0",
        due_picker_day_hover_fg="#3d2a4a",
    ),
    UiTheme.OCEAN: UiThemePalette(
        ui_theme=UiTheme.OCEAN,
        card_bg="#f0f8ff",
        card_fg="#0d3b5c",
        menu_fill="#e3f2fd",
        menu_fg="#1565c0",
        menu_outline="#64b5f6",
        progress_track_bg="#cce4f5",
        due_future_bg="#ddeef8",
        due_future_fg="#1a5276",
        due_none_bg="#ddeef8",
        due_none_fg="#4a7a9a",
        due_picker_bg="#e8f4fc",
        due_picker_fg="#0d3b5c",
        due_picker_day_hover_bg="#c5e0f5",
        due_picker_day_hover_fg="#0d3b5c",
    ),
    UiTheme.SUNSET: UiThemePalette(
        ui_theme=UiTheme.SUNSET,
        card_bg="#fff8f3",
        card_fg="#4a2c2a",
        menu_fill="#ffe8e0",
        menu_fg="#8b4513",
        menu_outline="#e8a598",
        progress_track_bg="#f5ddd4",
        due_future_bg="#fceee8",
        due_future_fg="#6b3a35",
        due_none_bg="#fceee8",
        due_none_fg="#8a5a55",
        due_picker_bg="#fff0ea",
        due_picker_fg="#4a2c2a",
        due_picker_day_hover_bg="#f0d4c8",
        due_picker_day_hover_fg="#4a2c2a",
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
        due_picker_bg="#edf1f5",
        due_picker_fg="#1e293b",
        due_picker_day_hover_bg="#d0d8e2",
        due_picker_day_hover_fg="#1e293b",
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
        due_picker_bg="#fef0f3",
        due_picker_fg="#4a1942",
        due_picker_day_hover_bg="#f0cdd8",
        due_picker_day_hover_fg="#4a1942",
    ),
    UiTheme.MIDNIGHT: UiThemePalette(
        ui_theme=UiTheme.MIDNIGHT,
        card_bg="#1e2433",
        card_fg="#e8eaf0",
        menu_fill="#2a3142",
        menu_fg="#d0d4de",
        menu_outline="#5c6a82",
        progress_track_bg="#323848",
        due_future_bg="#252b3a",
        due_future_fg="#c0c8d4",
        due_none_bg="#252b3a",
        due_none_fg="#9098a8",
        due_picker_bg="#222838",
        due_picker_fg="#e0e4ec",
        due_picker_day_hover_bg="#3a4458",
        due_picker_day_hover_fg="#e0e4ec",
    ),
}
