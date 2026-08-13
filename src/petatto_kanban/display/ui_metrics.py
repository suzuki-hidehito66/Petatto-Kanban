"""UI サイズ・フォントを合成した描画メトリクス（UC-009 / UC-010）."""

from __future__ import annotations

from dataclasses import dataclass

from petatto_kanban.display.card_layout import (
    CARD_DUE_PANEL_BORDER,
    CARD_LAYOUT_BASELINE,
    CARD_TITLE_FRAME_BORDER,
    scale_card_layout,
    scale_int,
)
from petatto_kanban.display.ui_font import UiFont, resolve_font_family, tkinter_family_name
from petatto_kanban.display.ui_scale import (
    BASE_DUE_PICKER_DAY_FONT_SIZE,
    BASE_DUE_PICKER_MONTH_FONT_SIZE,
    BASE_DUE_PICKER_PANEL_WIDTH,
    BASE_MENU_CIRCLE_FONT_SIZE,
    BASE_MENU_CIRCLE_SIZE,
    MIN_FONT_SIZE,
    UI_SIZE_SCALE,
    UiSize,
)


def _scaled_font(
    family: str,
    base_size: int,
    scale: float,
    *,
    bold: bool = False,
) -> tuple[str, int, str] | tuple[str, int]:
    scaled = max(MIN_FONT_SIZE, round(base_size * scale))
    if bold:
        return (family, scaled, "bold")
    return (family, scaled)


@dataclass(frozen=True)
class UiMetrics:
    """スケール・フォント適用後の UI 寸法."""

    ui_size: UiSize
    ui_font: UiFont
    font_family: str
    scale: float
    card_min_width: int
    card_min_height: int
    card_label_wrap: int
    card_frame_border: int
    card_frame_pad: int
    card_title_frame_padx: int
    card_title_frame_pady: int
    card_due_panel_padx: int
    card_due_panel_pady: int
    card_due_section_gap: int
    card_progress_section_gap: int
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

    @property
    def card_title_frame_border(self) -> int:
        return CARD_TITLE_FRAME_BORDER

    @property
    def card_due_panel_border(self) -> int:
        return CARD_DUE_PANEL_BORDER


def metrics_for_display(
    ui_size: UiSize,
    ui_font: UiFont,
    *,
    font_family: str | None = None,
    available_families: frozenset[str] | None = None,
) -> UiMetrics:
    """ui_size と ui_font から UiMetrics を生成する."""
    scale = UI_SIZE_SCALE[ui_size]
    card = scale_card_layout(CARD_LAYOUT_BASELINE, scale)
    requested = font_family or tkinter_family_name(ui_font)
    family = resolve_font_family(requested, available_families=available_families)
    return UiMetrics(
        ui_size=ui_size,
        ui_font=ui_font,
        font_family=family,
        scale=scale,
        card_min_width=card.min_width,
        card_min_height=card.min_height,
        card_label_wrap=card.label_wrap,
        card_frame_border=card.frame_border,
        card_frame_pad=card.frame_pad,
        card_title_frame_padx=card.title_frame_padx,
        card_title_frame_pady=card.title_frame_pady,
        card_due_panel_padx=card.due_panel_padx,
        card_due_panel_pady=card.due_panel_pady,
        card_due_section_gap=card.due_section_gap,
        card_progress_section_gap=card.progress_section_gap,
        progress_bar_height=card.progress_bar_height,
        menu_circle_size=scale_int(BASE_MENU_CIRCLE_SIZE, scale),
        due_picker_panel_width=scale_int(BASE_DUE_PICKER_PANEL_WIDTH, scale),
        title_font=_scaled_font(family, card.title_font_size, scale, bold=True),
        due_font=_scaled_font(family, card.due_font_size, scale),
        progress_font=_scaled_font(family, card.progress_font_size, scale, bold=True),
        menu_circle_font=_scaled_font(family, BASE_MENU_CIRCLE_FONT_SIZE, scale, bold=True),
        due_picker_month_font=_scaled_font(
            family, BASE_DUE_PICKER_MONTH_FONT_SIZE, scale, bold=True
        ),
        due_picker_day_font=_scaled_font(family, BASE_DUE_PICKER_DAY_FONT_SIZE, scale),
    )


def medium_metrics() -> UiMetrics:
    """標準サイズ・Segoe UI の UiMetrics（テスト・既定）。"""
    return metrics_for_display(UiSize.MEDIUM, UiFont.SEGOE_UI)
