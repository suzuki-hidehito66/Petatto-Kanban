"""UI サイズプリセットと基準寸法（FR-026 / UC-009）."""

from __future__ import annotations

from enum import StrEnum

MIN_FONT_SIZE = 8

# 横長カード: 幅 / 高さ = φ（黄金比）
GOLDEN_RATIO = (1 + 5**0.5) / 2
BASE_CARD_MIN_WIDTH = 160
BASE_CARD_MIN_HEIGHT = round(BASE_CARD_MIN_WIDTH / GOLDEN_RATIO)
BASE_CARD_LABEL_WRAP = BASE_CARD_MIN_WIDTH - 20
BASE_CARD_FRAME_BORDER = 1

# 220px 幅カード向けに設計した UI を、現在のカード幅比で縮小する
_CARD_LAYOUT_REFERENCE_WIDTH = 220


def _card_layout_scale() -> float:
    return BASE_CARD_MIN_WIDTH / _CARD_LAYOUT_REFERENCE_WIDTH


def _card_layout_size(base_at_ref: int, *, min_value: int = 1) -> int:
    return max(min_value, round(base_at_ref * _card_layout_scale()))


BASE_PROGRESS_BAR_HEIGHT = _card_layout_size(18, min_value=10)
BASE_MENU_CIRCLE_SIZE = 36
BASE_DUE_PICKER_PANEL_WIDTH = 240

BASE_TITLE_FONT_SIZE = max(MIN_FONT_SIZE, _card_layout_size(10))
BASE_DUE_FONT_SIZE = max(MIN_FONT_SIZE, _card_layout_size(9))
BASE_PROGRESS_FONT_SIZE = max(MIN_FONT_SIZE, _card_layout_size(9))
BASE_MENU_CIRCLE_FONT_SIZE = 14
BASE_DUE_PICKER_MONTH_FONT_SIZE = 9
BASE_DUE_PICKER_DAY_FONT_SIZE = 8

BASE_CARD_FRAME_PAD = _card_layout_size(8, min_value=4)
BASE_CARD_TITLE_FRAME_PADX = _card_layout_size(6, min_value=2)
BASE_CARD_TITLE_FRAME_PADY = _card_layout_size(4, min_value=1)
BASE_CARD_DUE_PANEL_PADX = _card_layout_size(6, min_value=2)
BASE_CARD_DUE_PANEL_PADY = _card_layout_size(3, min_value=1)
BASE_CARD_DUE_SECTION_GAP = _card_layout_size(4, min_value=2)
BASE_CARD_PROGRESS_SECTION_GAP = _card_layout_size(6, min_value=2)


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
