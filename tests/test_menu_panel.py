"""メニューパネル座標・ヒット判定のテスト."""

from petatto_kanban.menu_panel_layout import (
    MENU_ACTION_LABELS,
    MENU_CIRCLE_CENTER,
    MENU_CIRCLE_SIZE,
    MenuPanelRect,
    action_canvas_width,
    action_center_x,
    action_index_at,
    circle_radius,
)


def test_action_canvas_width() -> None:
    assert action_canvas_width() == len(MENU_ACTION_LABELS) * MENU_CIRCLE_SIZE


def test_action_center_x_is_evenly_spaced() -> None:
    assert action_center_x(0) == MENU_CIRCLE_SIZE // 2
    assert action_center_x(1) - action_center_x(0) == MENU_CIRCLE_SIZE


def test_action_index_at_detects_each_button() -> None:
    for index in range(len(MENU_ACTION_LABELS)):
        assert action_index_at(action_center_x(index), MENU_CIRCLE_SIZE // 2) == index


def test_action_index_at_returns_none_outside_buttons() -> None:
    assert action_index_at(-10, -10) is None
    assert action_index_at(action_canvas_width() + 10, MENU_CIRCLE_CENTER) is None


def test_circle_radius_uses_full_circle_with_zero_pad() -> None:
    assert circle_radius() == MENU_CIRCLE_SIZE // 2


def test_menu_panel_rect_exposes_right_and_bottom() -> None:
    panel = MenuPanelRect(x=10, y=20, width=80, height=36)
    assert panel.right == 90
    assert panel.bottom == 56

