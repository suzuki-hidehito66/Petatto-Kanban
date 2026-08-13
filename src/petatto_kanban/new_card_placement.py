"""新規カードの初期配置座標."""

from __future__ import annotations

DEFAULT_NEW_CARD_GAP_Y = 8
DEFAULT_NEW_CARD_STACK_OFFSET = 32
DEFAULT_NEW_CARD_STACK_COLUMNS = 4


def compute_new_card_position(
    *,
    menu_panel_x: int,
    menu_panel_y: int,
    menu_panel_width: int,
    menu_panel_height: int,
    card_width: int,
    stack_index: int,
    gap_y: int = DEFAULT_NEW_CARD_GAP_Y,
    stack_offset: int = DEFAULT_NEW_CARD_STACK_OFFSET,
    stack_columns: int = DEFAULT_NEW_CARD_STACK_COLUMNS,
) -> tuple[int, int]:
    """メニューパネル直下・右端揃えで新規カードの左上座標を返す."""
    menu_right = menu_panel_x + menu_panel_width
    base_x = menu_right - card_width
    base_y = menu_panel_y + menu_panel_height + gap_y
    column = stack_index % stack_columns
    row = stack_index // stack_columns
    return (
        base_x - column * stack_offset,
        base_y + row * stack_offset,
    )
