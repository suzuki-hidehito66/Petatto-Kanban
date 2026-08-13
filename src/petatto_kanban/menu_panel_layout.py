"""メニューパネルのレイアウト・ヒット判定（tkinter 非依存）."""

from __future__ import annotations

from dataclasses import dataclass

MENU_CIRCLE_SIZE = 36
MENU_CIRCLE_CENTER = MENU_CIRCLE_SIZE // 2
MENU_CIRCLE_PAD = 0
MENU_ACTION_LABELS = ("＋", "⚙", "×")


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


def action_canvas_width() -> int:
    return len(MENU_ACTION_LABELS) * MENU_CIRCLE_SIZE


def action_center_x(index: int) -> int:
    return MENU_CIRCLE_CENTER + index * MENU_CIRCLE_SIZE


def circle_radius(*, pad: int = MENU_CIRCLE_PAD) -> int:
    return MENU_CIRCLE_CENTER - pad


def action_index_at(x: int, y: int) -> int | None:
    """操作ボタン Canvas 上の座標からボタン index を返す."""
    hit_radius = circle_radius()
    for index in range(len(MENU_ACTION_LABELS)):
        center_x = action_center_x(index)
        if abs(x - center_x) <= hit_radius and abs(y - MENU_CIRCLE_CENTER) <= hit_radius:
            return index
    return None
