"""新規カードの初期配置座標（tkinter 非依存）."""

from __future__ import annotations

from petatto_kanban.menu_panel_layout import MenuPanelRect

DEFAULT_NEW_CARD_GAP_Y = 2
DEFAULT_NEW_CARD_INSET_X = 28
DEFAULT_NEW_CARD_STACK_OFFSET_X = 12
DEFAULT_NEW_CARD_STACK_OFFSET_Y = 12
DEFAULT_NEW_CARD_TITLE = "新しいタスク"


def compute_new_card_position(
    *,
    panel: MenuPanelRect,
    card_width: int,
    stack_index: int,
    gap_y: int = DEFAULT_NEW_CARD_GAP_Y,
    inset_x: int = DEFAULT_NEW_CARD_INSET_X,
    stack_offset_x: int = DEFAULT_NEW_CARD_STACK_OFFSET_X,
    stack_offset_y: int = DEFAULT_NEW_CARD_STACK_OFFSET_Y,
) -> tuple[int, int]:
    """メニューパネル直下・右端揃えで新規カードの左上座標を返す."""
    base_x = panel.right - card_width - inset_x
    base_y = panel.bottom + gap_y
    return (
        base_x - stack_index * stack_offset_x,
        base_y + stack_index * stack_offset_y,
    )
