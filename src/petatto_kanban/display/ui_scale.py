"""UI サイズプリセット（FR-026 / UC-009）。カード基準寸法は card_layout を参照。"""

from __future__ import annotations

from enum import StrEnum

from petatto_kanban.display.card_layout import CARD_LAYOUT_BASELINE

MIN_FONT_SIZE = 8

# card_layout 互換（既存 import 向け）
BASE_CARD_MIN_HEIGHT = CARD_LAYOUT_BASELINE.min_height
BASE_CARD_MIN_WIDTH = CARD_LAYOUT_BASELINE.min_width
BASE_CARD_LABEL_WRAP = CARD_LAYOUT_BASELINE.label_wrap
BASE_CARD_TITLE_FONT_SIZE = CARD_LAYOUT_BASELINE.title_font_size
BASE_CARD_DUE_FONT_SIZE = CARD_LAYOUT_BASELINE.due_font_size
BASE_CARD_PROGRESS_FONT_SIZE = CARD_LAYOUT_BASELINE.progress_font_size
BASE_CARD_FRAME_BORDER = CARD_LAYOUT_BASELINE.frame_border
BASE_CARD_FRAME_PAD = CARD_LAYOUT_BASELINE.frame_pad
BASE_CARD_TITLE_FRAME_PADX = CARD_LAYOUT_BASELINE.title_frame_padx
BASE_CARD_TITLE_FRAME_PADY = CARD_LAYOUT_BASELINE.title_frame_pady
BASE_CARD_DUE_PANEL_PADX = CARD_LAYOUT_BASELINE.due_panel_padx
BASE_CARD_DUE_PANEL_PADY = CARD_LAYOUT_BASELINE.due_panel_pady
BASE_CARD_DUE_SECTION_GAP = CARD_LAYOUT_BASELINE.due_section_gap
BASE_CARD_PROGRESS_SECTION_GAP = CARD_LAYOUT_BASELINE.progress_section_gap
BASE_PROGRESS_BAR_HEIGHT = CARD_LAYOUT_BASELINE.progress_bar_height

# --- メニュー・期限ピッカー（カード幅とは独立） ---

BASE_MENU_CIRCLE_SIZE = 36
BASE_DUE_PICKER_PANEL_WIDTH = 240
BASE_MENU_CIRCLE_FONT_SIZE = 14
BASE_DUE_PICKER_MONTH_FONT_SIZE = 9
BASE_DUE_PICKER_DAY_FONT_SIZE = 8


class UiSize(StrEnum):
    """UI サイズプリセット."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


UI_SIZE_SCALE: dict[UiSize, float] = {
    UiSize.SMALL: 0.85,
    UiSize.MEDIUM: 1.0,
    UiSize.LARGE: 1.15,
    UiSize.XLARGE: 1.25,
}


def parse_ui_size(value: str | None) -> UiSize:
    """settings.json の ui_size をパース。不正値は medium。"""
    if value is None:
        return UiSize.MEDIUM
    try:
        return UiSize(value)
    except ValueError:
        return UiSize.MEDIUM
