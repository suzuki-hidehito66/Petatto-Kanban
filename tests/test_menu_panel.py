"""メニューパネル座標・ヒット判定のテスト."""

from petatto_kanban.display.ui_scale import medium_metrics
from petatto_kanban.menu_panel_layout import (
    MENU_ACTION_LABELS,
    MenuPanelRect,
    action_canvas_width,
    action_center_x,
    action_index_at,
    circle_radius,
)

_METRICS = medium_metrics()


def test_action_canvas_width() -> None:
    assert action_canvas_width(_METRICS) == len(MENU_ACTION_LABELS) * _METRICS.menu_circle_size


def test_action_center_x_is_evenly_spaced() -> None:
    assert action_center_x(0, _METRICS) == _METRICS.menu_circle_size // 2
    assert action_center_x(1, _METRICS) - action_center_x(0, _METRICS) == _METRICS.menu_circle_size


def test_action_index_at_detects_each_button() -> None:
    for index in range(len(MENU_ACTION_LABELS)):
        assert action_index_at(
            action_center_x(index, _METRICS),
            _METRICS.menu_circle_center,
            _METRICS,
        ) == index


def test_action_index_at_returns_none_outside_buttons() -> None:
    assert action_index_at(-10, -10, _METRICS) is None
    assert action_index_at(
        action_canvas_width(_METRICS) + 10,
        _METRICS.menu_circle_center,
        _METRICS,
    ) is None


def test_circle_radius_uses_full_circle_with_zero_pad() -> None:
    assert circle_radius(_METRICS) == _METRICS.menu_circle_size // 2


def test_menu_panel_rect_exposes_right_and_bottom() -> None:
    panel = MenuPanelRect(x=10, y=20, width=80, height=36)
    assert panel.right == 90
    assert panel.bottom == 56


def test_menu_panel_rect_prefers_right_edge_anchor() -> None:
    panel = MenuPanelRect(x=100, y=20, width=36, height=36, right_edge=500)
    assert panel.right == 500
    assert panel.right != panel.x + panel.width
