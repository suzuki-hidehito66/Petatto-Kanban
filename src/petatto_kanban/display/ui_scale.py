"""UI サイズプリセットと基準寸法（FR-026 / UC-009）."""

from __future__ import annotations

from enum import StrEnum

MIN_FONT_SIZE = 8

GOLDEN_RATIO = (1 + 5**0.5) / 2

# --- カード（medium / 標準 UI・フォント 10pt・横長黄金比） ---

BASE_CARD_TITLE_FONT_SIZE = 10
BASE_CARD_DUE_FONT_SIZE = 10
BASE_CARD_PROGRESS_FONT_SIZE = 10

BASE_CARD_FRAME_BORDER = 1
BASE_CARD_FRAME_PAD = 6
BASE_CARD_TITLE_FRAME_PADX = 5
BASE_CARD_TITLE_FRAME_PADY = 3
BASE_CARD_DUE_PANEL_PADX = 5
BASE_CARD_DUE_PANEL_PADY = 2
BASE_CARD_DUE_SECTION_GAP = 3
BASE_CARD_PROGRESS_SECTION_GAP = 4
BASE_PROGRESS_BAR_HEIGHT = 16

# 10pt 3 行（タイトル・期限・進捗）が収まる高さを基準に、幅 = 高さ × φ
BASE_CARD_MIN_HEIGHT = 108
BASE_CARD_MIN_WIDTH = round(BASE_CARD_MIN_HEIGHT * GOLDEN_RATIO)
BASE_CARD_LABEL_WRAP = BASE_CARD_MIN_WIDTH - 20

# ui_metrics 互換エイリアス（カード描画のみ使用）
BASE_TITLE_FONT_SIZE = BASE_CARD_TITLE_FONT_SIZE
BASE_DUE_FONT_SIZE = BASE_CARD_DUE_FONT_SIZE
BASE_PROGRESS_FONT_SIZE = BASE_CARD_PROGRESS_FONT_SIZE

# --- メニュー・期限ピッカー等（カード幅とは独立） ---

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
