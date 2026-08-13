"""表示モードの UI ラベル（tkinter 非依存）."""

from __future__ import annotations

from petatto_kanban.display.settings import DisplayMode

DISPLAY_MODE_LABELS: dict[DisplayMode, str] = {
    DisplayMode.OVERLAY: "オーバーレイ",
    DisplayMode.DESKTOP: "デスクトップ",
}

SELECTABLE_DISPLAY_MODES: tuple[DisplayMode, ...] = (
    DisplayMode.OVERLAY,
    DisplayMode.DESKTOP,
)


def display_mode_label(mode: DisplayMode) -> str:
    return DISPLAY_MODE_LABELS.get(mode, DISPLAY_MODE_LABELS[DisplayMode.OVERLAY])


def display_mode_from_label(label: str, default: DisplayMode) -> DisplayMode:
    for mode, mode_label in DISPLAY_MODE_LABELS.items():
        if mode_label == label:
            return mode
    return default


def selectable_display_mode_labels() -> list[str]:
    return [DISPLAY_MODE_LABELS[mode] for mode in SELECTABLE_DISPLAY_MODES]
