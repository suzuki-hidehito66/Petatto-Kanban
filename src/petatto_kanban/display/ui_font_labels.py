"""UI フォントの UI ラベル（tkinter 非依存）."""

from __future__ import annotations

from petatto_kanban.display.ui_font import UiFont

UI_FONT_LABELS: dict[UiFont, str] = {
    UiFont.SEGOE_UI: "Segoe UI",
    UiFont.MEIRYO: "メイリオ",
    UiFont.YU_GOTHIC_UI: "游ゴシック",
    UiFont.MS_GOTHIC: "MS ゴシック",
}

SELECTABLE_UI_FONTS: tuple[UiFont, ...] = (
    UiFont.SEGOE_UI,
    UiFont.MEIRYO,
    UiFont.YU_GOTHIC_UI,
    UiFont.MS_GOTHIC,
)


def ui_font_label(ui_font: UiFont) -> str:
    return UI_FONT_LABELS.get(ui_font, UI_FONT_LABELS[UiFont.SEGOE_UI])


def ui_font_from_label(label: str, default: UiFont) -> UiFont:
    for font, font_label in UI_FONT_LABELS.items():
        if font_label == label:
            return font
    return default


def selectable_ui_font_labels() -> list[str]:
    return [UI_FONT_LABELS[font] for font in SELECTABLE_UI_FONTS]
