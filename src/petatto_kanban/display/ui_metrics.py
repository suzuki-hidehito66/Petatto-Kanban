"""UI サイズ・フォントを合成した描画メトリクス（UC-009 / UC-010）."""

from __future__ import annotations

from dataclasses import dataclass

from petatto_kanban.display.ui_font import UiFont, resolve_font_family, tkinter_family_name
from petatto_kanban.display.ui_scale import (
    BASE_CARD_DUE_PANEL_PADX,
    BASE_CARD_DUE_PANEL_PADY,
    BASE_CARD_DUE_SECTION_GAP,
    BASE_CARD_FRAME_BORDER,
    BASE_CARD_FRAME_PAD,
    BASE_CARD_LABEL_WRAP,
    BASE_CARD_MIN_HEIGHT,
    BASE_CARD_MIN_WIDTH,
    BASE_CARD_PROGRESS_SECTION_GAP,
    BASE_CARD_TITLE_FRAME_PADX,
    BASE_CARD_TITLE_FRAME_PADY,
    BASE_DUE_FONT_SIZE,
    BASE_DUE_PICKER_DAY_FONT_SIZE,
    BASE_DUE_PICKER_MONTH_FONT_SIZE,
    BASE_DUE_PICKER_PANEL_WIDTH,
    BASE_MENU_CIRCLE_FONT_SIZE,
    BASE_MENU_CIRCLE_SIZE,
    BASE_PROGRESS_BAR_HEIGHT,
    BASE_PROGRESS_FONT_SIZE,
    BASE_TITLE_FONT_SIZE,
    MIN_FONT_SIZE,
    UI_SIZE_SCALE,
    UiSize,
    _scale_int,
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


def metrics_for_display(
    ui_size: UiSize,
    ui_font: UiFont,
    *,
    font_family: str | None = None,
    available_families: frozenset[str] | None = None,
) -> UiMetrics:
    """ui_size と ui_font から UiMetrics を生成する."""
    scale = UI_SIZE_SCALE[ui_size]
    requested = font_family or tkinter_family_name(ui_font)
    family = resolve_font_family(requested, available_families=available_families)
    return UiMetrics(
        ui_size=ui_size,
        ui_font=ui_font,
        font_family=family,
        scale=scale,
        card_min_width=_scale_int(BASE_CARD_MIN_WIDTH, scale),
        card_min_height=_scale_int(BASE_CARD_MIN_HEIGHT, scale),
        card_label_wrap=_scale_int(BASE_CARD_LABEL_WRAP, scale),
        card_frame_border=BASE_CARD_FRAME_BORDER,
        card_frame_pad=_scale_int(BASE_CARD_FRAME_PAD, scale),
        card_title_frame_padx=_scale_int(BASE_CARD_TITLE_FRAME_PADX, scale),
        card_title_frame_pady=_scale_int(BASE_CARD_TITLE_FRAME_PADY, scale),
        card_due_panel_padx=_scale_int(BASE_CARD_DUE_PANEL_PADX, scale),
        card_due_panel_pady=_scale_int(BASE_CARD_DUE_PANEL_PADY, scale),
        card_due_section_gap=_scale_int(BASE_CARD_DUE_SECTION_GAP, scale),
        card_progress_section_gap=_scale_int(BASE_CARD_PROGRESS_SECTION_GAP, scale),
        progress_bar_height=_scale_int(BASE_PROGRESS_BAR_HEIGHT, scale),
        menu_circle_size=_scale_int(BASE_MENU_CIRCLE_SIZE, scale),
        due_picker_panel_width=_scale_int(BASE_DUE_PICKER_PANEL_WIDTH, scale),
        title_font=_scaled_font(family, BASE_TITLE_FONT_SIZE, scale, bold=True),
        due_font=_scaled_font(family, BASE_DUE_FONT_SIZE, scale),
        progress_font=_scaled_font(family, BASE_PROGRESS_FONT_SIZE, scale, bold=True),
        menu_circle_font=_scaled_font(family, BASE_MENU_CIRCLE_FONT_SIZE, scale, bold=True),
        due_picker_month_font=_scaled_font(
            family, BASE_DUE_PICKER_MONTH_FONT_SIZE, scale, bold=True
        ),
        due_picker_day_font=_scaled_font(family, BASE_DUE_PICKER_DAY_FONT_SIZE, scale),
    )


def metrics_for_ui_size(ui_size: UiSize) -> UiMetrics:
    """ui_size のみ指定（フォントは Segoe UI 既定）。後方互換用。"""
    return metrics_for_display(ui_size, UiFont.SEGOE_UI)


def medium_metrics() -> UiMetrics:
    """標準サイズ・Segoe UI の UiMetrics（テスト・既定）。"""
    return metrics_for_display(UiSize.MEDIUM, UiFont.SEGOE_UI)
