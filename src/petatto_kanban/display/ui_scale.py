"""UI サイズプリセットと基準寸法（FR-026 / UC-009）."""

from __future__ import annotations

from enum import StrEnum

MIN_FONT_SIZE = 8

BASE_CARD_MIN_WIDTH = 220
BASE_CARD_MIN_HEIGHT = 120
BASE_CARD_LABEL_WRAP = 200
BASE_CARD_FRAME_BORDER = 1
BASE_PROGRESS_BAR_HEIGHT = 18
BASE_MENU_CIRCLE_SIZE = 36
BASE_DUE_PICKER_PANEL_WIDTH = 240

BASE_TITLE_FONT_SIZE = 10
BASE_DUE_FONT_SIZE = 9
BASE_PROGRESS_FONT_SIZE = 9
BASE_MENU_CIRCLE_FONT_SIZE = 14
BASE_DUE_PICKER_MONTH_FONT_SIZE = 9
BASE_DUE_PICKER_DAY_FONT_SIZE = 8


class UiSize(StrEnum):
    """UI サイズプリセット."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


UI_SIZE_SCALE: dict[UiSize, float] = {
    UiSize.SMALL: 0.85,
    UiSize.MEDIUM: 1.0,
    UiSize.LARGE: 1.15,
}


def parse_ui_size(value: str | None) -> UiSize:
    """settings.json の ui_size をパース。不正値は medium。"""
    if value is None:
        return UiSize.MEDIUM
    try:
        return UiSize(value)
    except ValueError:
        return UiSize.MEDIUM


def _scale_int(base: int, scale: float) -> int:
    return round(base * scale)
