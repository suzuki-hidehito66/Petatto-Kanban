"""UI サイズプリセットとスケール後寸法（FR-026 / UC-009）."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

FONT_FAMILY = "Segoe UI"
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


def _scaled_font(
    base_size: int,
    scale: float,
    *,
    bold: bool = False,
) -> tuple[str, int, str] | tuple[str, int]:
    scaled = max(MIN_FONT_SIZE, round(base_size * scale))
    if bold:
        return (FONT_FAMILY, scaled, "bold")
    return (FONT_FAMILY, scaled)


@dataclass(frozen=True)
class UiMetrics:
    """スケール適用後の UI 寸法."""

    ui_size: UiSize
    scale: float
    card_min_width: int
    card_min_height: int
    card_label_wrap: int
    card_frame_border: int
    progress_bar_height: int
    menu_circle_size: int
    due_picker_panel_width: int
    title_font: tuple[str, int, str]
    due_font: tuple[str, int]
    progress_font: tuple[str, int, str]
    menu_circle_font: tuple[str, int, str]
    due_picker_month_font: tuple[str, int, str]
    due_picker_day_font: tuple[str, int]

    @property
    def menu_circle_center(self) -> int:
        return self.menu_circle_size // 2

    @property
    def card_placement_width(self) -> int:
        return self.card_min_width + 2 * self.card_frame_border

    @property
    def card_placement_height(self) -> int:
        return self.card_min_height + 2 * self.card_frame_border


def metrics_for_ui_size(ui_size: UiSize) -> UiMetrics:
    """UiSize から UiMetrics を生成する."""
    scale = UI_SIZE_SCALE[ui_size]
    return UiMetrics(
        ui_size=ui_size,
        scale=scale,
        card_min_width=_scale_int(BASE_CARD_MIN_WIDTH, scale),
        card_min_height=_scale_int(BASE_CARD_MIN_HEIGHT, scale),
        card_label_wrap=_scale_int(BASE_CARD_LABEL_WRAP, scale),
        card_frame_border=BASE_CARD_FRAME_BORDER,
        progress_bar_height=_scale_int(BASE_PROGRESS_BAR_HEIGHT, scale),
        menu_circle_size=_scale_int(BASE_MENU_CIRCLE_SIZE, scale),
        due_picker_panel_width=_scale_int(BASE_DUE_PICKER_PANEL_WIDTH, scale),
        title_font=_scaled_font(BASE_TITLE_FONT_SIZE, scale, bold=True),
        due_font=_scaled_font(BASE_DUE_FONT_SIZE, scale),
        progress_font=_scaled_font(BASE_PROGRESS_FONT_SIZE, scale, bold=True),
        menu_circle_font=_scaled_font(BASE_MENU_CIRCLE_FONT_SIZE, scale, bold=True),
        due_picker_month_font=_scaled_font(BASE_DUE_PICKER_MONTH_FONT_SIZE, scale, bold=True),
        due_picker_day_font=_scaled_font(BASE_DUE_PICKER_DAY_FONT_SIZE, scale),
    )


def medium_metrics() -> UiMetrics:
    """標準サイズの UiMetrics（テスト・既定）。"""
    return metrics_for_ui_size(UiSize.MEDIUM)
