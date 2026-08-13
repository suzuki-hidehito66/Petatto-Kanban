"""画面右上のメニューパネル（円形＜・ホバー展開・ドラッグ移動）."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from petatto_kanban.display.desktop import TRANSPARENT_COLOR

MENU_CIRCLE_SIZE = 36
MENU_CIRCLE_OUTLINE = "#888888"
MENU_CIRCLE_FILL = "#ffffff"
MENU_CIRCLE_FG = "#333333"
MENU_CIRCLE_PAD = 2
MENU_ACTION_CIRCLE_PAD = 0
MENU_CIRCLE_FONT = ("Segoe UI", 14, "bold")
MENU_DEFAULT_MARGIN_X = 16
MENU_DEFAULT_MARGIN_Y = 16
MENU_ACTION_LABELS = ("＋", "⚙", "×")


def _action_canvas_width() -> int:
    return len(MENU_ACTION_LABELS) * MENU_CIRCLE_SIZE


def _action_center_x(index: int) -> int:
    return MENU_CIRCLE_SIZE // 2 + index * MENU_CIRCLE_SIZE


def _circle_radius(*, pad: int) -> int:
    return MENU_CIRCLE_SIZE // 2 - pad


def _draw_circle(
    canvas: tk.Canvas,
    center_x: int,
    center_y: int,
    *,
    text: str,
    font: tuple[str, int, str] = MENU_CIRCLE_FONT,
    pad: int = MENU_CIRCLE_PAD,
) -> None:
    radius = _circle_radius(pad=pad)
    canvas.create_oval(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        outline=MENU_CIRCLE_OUTLINE,
        width=1,
        fill=MENU_CIRCLE_FILL,
    )
    canvas.create_text(
        center_x,
        center_y,
        text=text,
        font=font,
        fill=MENU_CIRCLE_FG,
    )


def _create_circle_canvas(
    parent: tk.Misc,
    *,
    text: str,
    bg: str,
    font: tuple[str, int, str] = MENU_CIRCLE_FONT,
) -> tk.Canvas:
    """`<` パネルと同型の円形 Canvas を作る."""
    canvas = tk.Canvas(
        parent,
        width=MENU_CIRCLE_SIZE,
        height=MENU_CIRCLE_SIZE,
        bg=bg,
        highlightthickness=0,
        bd=0,
        cursor="hand2",
    )
    _draw_circle(
        canvas,
        MENU_CIRCLE_SIZE // 2,
        MENU_CIRCLE_SIZE // 2,
        text=text,
        font=font,
        pad=MENU_ACTION_CIRCLE_PAD,
    )
    return canvas


class MenuPanel:
    """円形＜アイコンのメニューパネル。ホバーで左側に操作ボタンを展開し、ドラッグで移動できる."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        on_close: Callable[[], None],
        on_settings: Callable[[], None],
        on_add_card: Callable[[], None],
        on_position_changed: Callable[[int, int], None] | None = None,
        bg: str = TRANSPARENT_COLOR,
    ) -> None:
        self._on_position_changed = on_position_changed
        self._action_handlers = (on_add_card, on_settings, on_close)
        self._bg = bg
        self._place_x = 0
        self._place_y = 0
        self._anchor_right_x = 0
        self._drag_origin: tuple[int, int] | None = None
        self._drag_moved = False
        self._hide_after_id: str | None = None
        self._hover_depth = 0
        self._actions_expanded = False
        self._action_press_index: int | None = None

        self.widget = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)
        self._row = tk.Frame(self.widget, bg=bg, bd=0, highlightthickness=0)
        self._row.pack()

        self._actions = tk.Canvas(
            self._row,
            width=_action_canvas_width(),
            height=MENU_CIRCLE_SIZE,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._draw_action_buttons()
        self._actions.bind("<Button-1>", self._on_action_press)
        self._actions.bind("<ButtonRelease-1>", self._on_action_release)

        self._circle = _create_circle_canvas(self._row, text="<", bg=bg)
        self._circle.pack(side=tk.RIGHT)
        self._circle.configure(cursor="fleur")

        self._bind_hover(self.widget)

        self._circle.bind("<Button-1>", self._on_drag_press)
        self._circle.bind("<B1-Motion>", self._on_drag_motion)
        self._circle.bind("<ButtonRelease-1>", self._on_drag_release)

    def _bind_hover(self, widget: tk.Misc) -> None:
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        for child in widget.winfo_children():
            self._bind_hover(child)

    def _draw_action_buttons(self) -> None:
        center_y = MENU_CIRCLE_SIZE // 2
        for index, label in enumerate(MENU_ACTION_LABELS):
            _draw_circle(
                self._actions,
                _action_center_x(index),
                center_y,
                text=label,
                pad=MENU_ACTION_CIRCLE_PAD,
            )

    def _action_index_at(self, x: int, y: int) -> int | None:
        center_y = MENU_CIRCLE_SIZE // 2
        hit_radius = _circle_radius(pad=MENU_ACTION_CIRCLE_PAD)
        for index in range(len(MENU_ACTION_LABELS)):
            center_x = _action_center_x(index)
            if abs(x - center_x) <= hit_radius and abs(y - center_y) <= hit_radius:
                return index
        return None

    def _on_action_press(self, event: tk.Event) -> None:
        self._action_press_index = self._action_index_at(event.x, event.y)

    def _on_action_release(self, event: tk.Event) -> None:
        release_index = self._action_index_at(event.x, event.y)
        if (
            self._action_press_index is not None
            and release_index == self._action_press_index
        ):
            self._action_handlers[release_index]()
        self._action_press_index = None

    def _widget_width(self) -> int:
        width = self.widget.winfo_width()
        return width if width > 1 else self.widget.winfo_reqwidth()

    def _widget_height(self) -> int:
        height = self.widget.winfo_height()
        return height if height > 1 else self.widget.winfo_reqheight()

    def _sync_place_from_widget(self) -> None:
        self.widget.update_idletasks()
        self._place_x = self.widget.winfo_x()
        self._place_y = self.widget.winfo_y()
        self._anchor_right_x = self._place_x + self._widget_width()

    def _apply_place(self) -> None:
        """`<` 円の右端を _anchor_right_x に固定して配置する."""
        self.widget.place(x=self._anchor_right_x, y=self._place_y, anchor=tk.NE)

    def place_at(self, x: int, y: int) -> None:
        """左上座標で配置する（永続化・ドラッグ用）."""
        self._place_x = x
        self._place_y = y
        self.widget.update_idletasks()
        self._anchor_right_x = x + self._widget_width()
        self._apply_place()
        self._sync_place_from_widget()

    def place_default(self, monitor_width: int, monitor_height: int) -> None:
        """画面右上（デフォルト位置）に配置する."""
        self._anchor_right_x = monitor_width - MENU_DEFAULT_MARGIN_X
        self._place_y = MENU_DEFAULT_MARGIN_Y
        self._apply_place()
        self._sync_place_from_widget()
        _ = monitor_height

    def clamp_to_monitor(self, monitor_width: int, monitor_height: int) -> None:
        """モニター内に収まるよう座標を調整する."""
        self.widget.update_idletasks()
        width = self._widget_width()
        height = self._widget_height()
        self._anchor_right_x = min(max(width, self._anchor_right_x), monitor_width)
        self._place_y = min(max(0, self._place_y), max(0, monitor_height - height))
        self._apply_place()
        self._sync_place_from_widget()

    @property
    def position(self) -> tuple[int, int]:
        return self._place_x, self._place_y

    def _show_actions(self) -> None:
        if self._actions_expanded:
            return
        self._actions_expanded = True
        self._actions.pack(side=tk.RIGHT)
        self._apply_place()
        self._sync_place_from_widget()

    def _hide_actions(self) -> None:
        if not self._actions_expanded:
            return
        self._actions_expanded = False
        self._actions.pack_forget()
        self._apply_place()
        self._sync_place_from_widget()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover_depth += 1
        if self._hide_after_id is not None:
            self.widget.after_cancel(self._hide_after_id)
            self._hide_after_id = None
        if self._hover_depth == 1:
            self._show_actions()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover_depth = max(0, self._hover_depth - 1)
        if self._hover_depth > 0:
            return
        if self._hide_after_id is not None:
            self.widget.after_cancel(self._hide_after_id)
        self._hide_after_id = self.widget.after(120, self._hide_actions)

    def _on_drag_press(self, event: tk.Event) -> None:
        self._drag_moved = False
        self._drag_origin = (event.x, event.y)

    def _on_drag_motion(self, event: tk.Event) -> None:
        if self._drag_origin is None:
            return
        self._drag_moved = True
        new_x = self.widget.winfo_x() + event.x - self._drag_origin[0]
        new_y = self.widget.winfo_y() + event.y - self._drag_origin[1]
        self.place_at(new_x, new_y)

    def _on_drag_release(self, _event: tk.Event) -> None:
        if self._drag_moved and self._on_position_changed is not None:
            self._on_position_changed(self._place_x, self._place_y)
        self._drag_origin = None
        self._drag_moved = False
