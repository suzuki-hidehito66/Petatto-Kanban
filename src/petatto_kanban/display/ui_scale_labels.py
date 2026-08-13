"""UI サイズの UI ラベル（tkinter 非依存）."""

from __future__ import annotations

from petatto_kanban.display.ui_scale import UiSize

UI_SIZE_LABELS: dict[UiSize, str] = {
    UiSize.SMALL: "小",
    UiSize.MEDIUM: "標準",
    UiSize.LARGE: "大",
    UiSize.XLARGE: "極大",
}

SELECTABLE_UI_SIZES: tuple[UiSize, ...] = (
    UiSize.SMALL,
    UiSize.MEDIUM,
    UiSize.LARGE,
    UiSize.XLARGE,
)

_LABEL_TO_UI_SIZE: dict[str, UiSize] = {
    label: size for size, label in UI_SIZE_LABELS.items()
}


def ui_size_label(ui_size: UiSize) -> str:
    return UI_SIZE_LABELS.get(ui_size, UI_SIZE_LABELS[UiSize.MEDIUM])


def ui_size_from_label(label: str, default: UiSize) -> UiSize:
    return _LABEL_TO_UI_SIZE.get(label, default)


def selectable_ui_size_labels() -> list[str]:
    return [UI_SIZE_LABELS[size] for size in SELECTABLE_UI_SIZES]
