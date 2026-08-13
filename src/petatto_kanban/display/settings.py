"""表示設定の永続化."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from petatto_kanban.display.ui_font import UiFont, parse_ui_font
from petatto_kanban.display.ui_scale import UiSize, parse_ui_size
from petatto_kanban.display.ui_theme import UiTheme, parse_ui_theme

SETTINGS_FILE_NAME = "settings.json"


class DisplayMode(StrEnum):
    """UI 表示モード."""

    WINDOW = "window"
    DESKTOP = "desktop"
    OVERLAY = "overlay"


@dataclass
class DisplaySettings:
    """表示モードとアプリ設定."""

    mode: DisplayMode = DisplayMode.OVERLAY
    monitor_index: int = 0
    window_geometry: str = "960x540+100+100"
    confirm_delete: bool = True
    confirm_exit: bool = False
    ui_size: UiSize = UiSize.MEDIUM
    ui_font: UiFont = UiFont.SEGOE_UI
    ui_theme: UiTheme = UiTheme.DEFAULT
    menu_panel_x: int | None = None
    menu_panel_y: int | None = None


def get_settings_path() -> Path:
    """設定ファイルのパスを返す."""
    base = Path.home() / ".petatto-kanban"
    base.mkdir(parents=True, exist_ok=True)
    return base / SETTINGS_FILE_NAME


def _parse_mode(value: str) -> DisplayMode:
    try:
        return DisplayMode(value)
    except ValueError:
        return DisplayMode.OVERLAY


def display_settings_to_dict(settings: DisplaySettings) -> dict[str, Any]:
    data: dict[str, Any] = {
        "mode": settings.mode.value,
        "monitor_index": settings.monitor_index,
        "window_geometry": settings.window_geometry,
        "confirm_delete": settings.confirm_delete,
        "confirm_exit": settings.confirm_exit,
        "ui_size": settings.ui_size.value,
        "ui_font": settings.ui_font.value,
        "ui_theme": settings.ui_theme.value,
    }
    if settings.menu_panel_x is not None:
        data["menu_panel_x"] = settings.menu_panel_x
    if settings.menu_panel_y is not None:
        data["menu_panel_y"] = settings.menu_panel_y
    return data


def display_settings_from_dict(data: dict[str, Any]) -> DisplaySettings:
    menu_x = data.get("menu_panel_x")
    menu_y = data.get("menu_panel_y")
    return DisplaySettings(
        mode=_parse_mode(data.get("mode", DisplayMode.OVERLAY.value)),
        monitor_index=int(data.get("monitor_index", 0)),
        window_geometry=str(data.get("window_geometry", "960x540+100+100")),
        confirm_delete=bool(data.get("confirm_delete", True)),
        confirm_exit=bool(data.get("confirm_exit", False)),
        ui_size=parse_ui_size(data.get("ui_size")),
        ui_font=parse_ui_font(data.get("ui_font")),
        ui_theme=parse_ui_theme(data.get("ui_theme")),
        menu_panel_x=int(menu_x) if menu_x is not None else None,
        menu_panel_y=int(menu_y) if menu_y is not None else None,
    )


def load_display_settings(path: Path | None = None) -> DisplaySettings:
    """表示設定を読み込む。不存在時はオーバーレイモード既定値。"""
    target = path or get_settings_path()
    if not target.exists():
        return DisplaySettings()

    with target.open(encoding="utf-8") as file:
        data = json.load(file)
    return display_settings_from_dict(data)


def save_display_settings(settings: DisplaySettings, path: Path | None = None) -> None:
    """表示設定を保存する."""
    target = path or get_settings_path()
    with target.open("w", encoding="utf-8") as file:
        json.dump(display_settings_to_dict(settings), file, ensure_ascii=False, indent=2)
