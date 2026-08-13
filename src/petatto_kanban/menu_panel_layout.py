"""メニューパネルのレイアウト・ヒット判定（tkinter 非依存）."""

from __future__ import annotations

from dataclasses import dataclass

from petatto_kanban.display.ui_scale import UiMetrics, medium_metrics

MENU_CIRCLE_PAD = 0
MENU_ACTION_LABELS = ("＋", "⚙", "×")

# 後方互換: 標準サイズの定数（テスト参照用）
_MEDIUM = medium_metrics()
MENU_CIRCLE_SIZE = _MEDIUM.menu_circle_size
MENU_CIRCLE_CENTER = _MEDIUM.menu_circle_center


@dataclass(frozen=True)
class MenuPanelRect:
    """メニューパネルの画面上の矩形（左上原点・px）."""

    x: int
    y: int
    width: int
    height: int
    right_edge: int | None = None

    @property
    def right(self) -> int:
        if self.right_edge is not None:
            return self.right_edge
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


def action_canvas_width(metrics: UiMetrics) -> int:
    return len(MENU_ACTION_LABELS) * metrics.menu_circle_size


def action_center_x(index: int, metrics: UiMetrics) -> int:
    return metrics.menu_circle_center + index * metrics.menu_circle_size


def circle_radius(metrics: UiMetrics, *, pad: int = MENU_CIRCLE_PAD) -> int:
    return metrics.menu_circle_center - pad


def action_index_at(x: int, y: int, metrics: UiMetrics) -> int | None:
    """操作ボタン Canvas 上の座標からボタン index を返す."""
    hit_radius = circle_radius(metrics)
    for index in range(len(MENU_ACTION_LABELS)):
        center_x = action_center_x(index, metrics)
        if abs(x - center_x) <= hit_radius and abs(y - metrics.menu_circle_center) <= hit_radius:
            return index
    return None
