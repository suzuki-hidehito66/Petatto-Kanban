"""新規カード配置座標のテスト."""

from petatto_kanban.menu_panel_layout import MenuPanelRect
from petatto_kanban.new_card_placement import (
    DEFAULT_NEW_CARD_GAP_Y,
    DEFAULT_NEW_CARD_INSET_X,
    DEFAULT_NEW_CARD_STACK_OFFSET_X,
    DEFAULT_NEW_CARD_STACK_OFFSET_Y,
    clamp_card_position_to_monitor,
    compute_new_card_position,
)


def _panel(
    *,
    x: int = 0,
    y: int = 0,
    width: int = 300,
    height: int = 50,
    right_edge: int | None = None,
) -> MenuPanelRect:
    return MenuPanelRect(x=x, y=y, width=width, height=height, right_edge=right_edge)


def test_first_card_below_panel_right_aligned() -> None:
    panel = _panel(x=100, y=20, width=80, height=40)
    x, y = compute_new_card_position(
        panel=panel,
        card_width=222,
        stack_index=0,
    )
    assert x == panel.right - 222 - DEFAULT_NEW_CARD_INSET_X
    assert y == panel.bottom + DEFAULT_NEW_CARD_GAP_Y


def test_right_edge_uses_anchor_not_stale_width() -> None:
    panel = _panel(x=100, y=20, width=36, height=36, right_edge=1916)
    x, _y = compute_new_card_position(panel=panel, card_width=222, stack_index=0)
    assert x == 1916 - 222 - DEFAULT_NEW_CARD_INSET_X
    assert x != panel.x + panel.width - 222


def test_stack_index_offsets_bottom_left() -> None:
    panel = _panel()
    x0, y0 = compute_new_card_position(panel=panel, card_width=222, stack_index=0)
    x1, y1 = compute_new_card_position(panel=panel, card_width=222, stack_index=1)
    assert x1 == x0 - DEFAULT_NEW_CARD_STACK_OFFSET_X
    assert y1 == y0 + DEFAULT_NEW_CARD_STACK_OFFSET_Y

    x2, y2 = compute_new_card_position(panel=panel, card_width=222, stack_index=2)
    assert x2 == x0 - 2 * DEFAULT_NEW_CARD_STACK_OFFSET_X
    assert y2 == y0 + 2 * DEFAULT_NEW_CARD_STACK_OFFSET_Y


def test_clamp_keeps_card_inside_monitor() -> None:
    x, y = clamp_card_position_to_monitor(
        -50,
        1000,
        card_width=222,
        card_height=138,
        monitor_width=1920,
        monitor_height=1080,
    )
    assert x == 0
    assert y == 1080 - 138


def test_clamp_does_not_move_in_bounds_position() -> None:
    x, y = clamp_card_position_to_monitor(
        100,
        200,
        card_width=222,
        card_height=138,
        monitor_width=1920,
        monitor_height=1080,
    )
    assert (x, y) == (100, 200)
