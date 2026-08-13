"""新規カード配置座標のテスト."""

from petatto_kanban.new_card_placement import (
    DEFAULT_NEW_CARD_GAP_Y,
    DEFAULT_NEW_CARD_STACK_OFFSET,
    compute_new_card_position,
)


def test_first_card_below_panel_right_aligned() -> None:
    x, y = compute_new_card_position(
        menu_panel_x=100,
        menu_panel_y=20,
        menu_panel_width=80,
        menu_panel_height=40,
        card_width=220,
        stack_index=0,
    )
    assert x == 100 + 80 - 220
    assert y == 20 + 40 + DEFAULT_NEW_CARD_GAP_Y


def test_stack_index_offsets_left_and_down() -> None:
    x0, y0 = compute_new_card_position(
        menu_panel_x=0,
        menu_panel_y=0,
        menu_panel_width=300,
        menu_panel_height=50,
        card_width=220,
        stack_index=0,
    )
    x1, y1 = compute_new_card_position(
        menu_panel_x=0,
        menu_panel_y=0,
        menu_panel_width=300,
        menu_panel_height=50,
        card_width=220,
        stack_index=1,
    )
    assert x1 == x0 - DEFAULT_NEW_CARD_STACK_OFFSET
    assert y1 == y0

    x4, y4 = compute_new_card_position(
        menu_panel_x=0,
        menu_panel_y=0,
        menu_panel_width=300,
        menu_panel_height=50,
        card_width=220,
        stack_index=4,
    )
    assert x4 == x0
    assert y4 == y0 + DEFAULT_NEW_CARD_STACK_OFFSET
