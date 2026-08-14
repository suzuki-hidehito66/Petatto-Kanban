"""カードレイアウト基準寸法（UC-003 / UC-009 / medium 標準・黄金比）."""

from __future__ import annotations

from dataclasses import dataclass

GOLDEN_RATIO = (1 + 5**0.5) / 2
CARD_LABEL_WRAP_INSET = 20
CARD_TITLE_FRAME_BORDER = 1
CARD_DUE_PANEL_BORDER = 1


@dataclass(frozen=True)
class CardLayoutBaseline:
    """medium（scale 1.0）時のカード寸法・余白・フォント pt。"""

    min_height: int = 108
    title_font_size: int = 10
    due_font_size: int = 10
    progress_font_size: int = 10
    frame_border: int = 1
    frame_pad: int = 6
    title_frame_padx: int = 5
    title_frame_pady: int = 3
    due_panel_padx: int = 5
    due_panel_pady: int = 2
    due_section_gap: int = 3
    progress_section_gap: int = 4
    progress_bar_height: int = 16

    @property
    def min_width(self) -> int:
        return round(self.min_height * GOLDEN_RATIO)

    @property
    def label_wrap(self) -> int:
        return self.min_width - CARD_LABEL_WRAP_INSET

    @property
    def placement_width(self) -> int:
        return self.min_width + 2 * self.frame_border

    @property
    def placement_height(self) -> int:
        return self.min_height + 2 * self.frame_border


@dataclass(frozen=True)
class ScaledCardLayout:
    """ui_size スケール適用後のカードレイアウト。"""

    min_width: int
    min_height: int
    label_wrap: int
    frame_border: int
    frame_pad: int
    title_frame_padx: int
    title_frame_pady: int
    due_panel_padx: int
    due_panel_pady: int
    due_section_gap: int
    progress_section_gap: int
    progress_bar_height: int
    title_font_size: int
    due_font_size: int
    progress_font_size: int

    @property
    def placement_width(self) -> int:
        return self.min_width + 2 * self.frame_border

    @property
    def placement_height(self) -> int:
        return self.min_height + 2 * self.frame_border


CARD_LAYOUT_BASELINE = CardLayoutBaseline()


def scale_int(base: int, scale: float) -> int:
    return round(base * scale)


def scale_card_layout(baseline: CardLayoutBaseline, scale: float) -> ScaledCardLayout:
    """基準レイアウトを ui_size 係数でスケールする。枠線 px はスケールしない。"""
    return ScaledCardLayout(
        min_width=scale_int(baseline.min_width, scale),
        min_height=scale_int(baseline.min_height, scale),
        label_wrap=scale_int(baseline.label_wrap, scale),
        frame_border=baseline.frame_border,
        frame_pad=scale_int(baseline.frame_pad, scale),
        title_frame_padx=scale_int(baseline.title_frame_padx, scale),
        title_frame_pady=scale_int(baseline.title_frame_pady, scale),
        due_panel_padx=scale_int(baseline.due_panel_padx, scale),
        due_panel_pady=scale_int(baseline.due_panel_pady, scale),
        due_section_gap=scale_int(baseline.due_section_gap, scale),
        progress_section_gap=scale_int(baseline.progress_section_gap, scale),
        progress_bar_height=scale_int(baseline.progress_bar_height, scale),
        title_font_size=baseline.title_font_size,
        due_font_size=baseline.due_font_size,
        progress_font_size=baseline.progress_font_size,
    )
