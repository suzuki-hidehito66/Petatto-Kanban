"""新規カード配置座標のテスト."""

from petatto_kanban.menu_panel_layout import MenuPanelRect
from petatto_kanban.new_card_placement import (
    DEFAULT_NEW_CARD_GAP_Y,
    DEFAULT_NEW_CARD_STACK_OFFSET,
    compute_new_card_position,
)


def _panel(*, x: int = 0, y: int = 0, width: int = 300, height: int = 50) -> MenuPanelRect:
    return MenuPanelRect(x=x, y=y, width=width, height=height)


def test_first_card_below_panel_right_aligned() -> None:
    panel = _panel(x=100, y=20, width=80, height=40)
    x, y = compute_new_card_position(
        panel=panel,
        card_width=220,
        stack_index=0,
    )
    assert x == panel.right - 220
    assert y == panel.bottom + DEFAULT_NEW_CARD_GAP_Y


def test_stack_index_offsets_left_and_down() -> None:
    panel = _panel()
    x0, y0 = compute_new_card_position(panel=panel, card_width=220, stack_index=0)
    x1, y1 = compute_new_card_position(panel=panel, card_width=220, stack_index=1)
    assert x1 == x0 - DEFAULT_NEW_CARD_STACK_OFFSET
    assert y1 == y0

    x4, y4 = compute_new_card_position(panel=panel, card_width=220, stack_index=4)
    assert x4 == x0
    assert y4 == y0 + DEFAULT_NEW_CARD_STACK_OFFSET
