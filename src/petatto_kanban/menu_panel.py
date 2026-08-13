"""画面右上のメニューパネル（円形＜・ホバー展開・ドラッグ移動）."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from petatto_kanban.display.transparent import TRANSPARENT_COLOR
from petatto_kanban.display.ui_metrics import UiMetrics, medium_metrics
from petatto_kanban.menu_panel_layout import (
    MENU_ACTION_LABELS,
    MENU_CIRCLE_PAD,
    MenuPanelRect,
    action_canvas_width,
    action_center_x,
    action_index_at,
    circle_radius,
)

MENU_CIRCLE_OUTLINE = "#888888"
MENU_CIRCLE_FILL = "#ffffff"
MENU_CIRCLE_FG = "#333333"
MENU_DEFAULT_MARGIN_X = 16
MENU_DEFAULT_MARGIN_Y = 16
MENU_HOVER_HIDE_DELAY_MS = 120


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
        on_activate: Callable[[], None] | None = None,
        on_deactivate: Callable[[], None] | None = None,
        metrics: UiMetrics | None = None,
        bg: str = TRANSPARENT_COLOR,
    ) -> None:
        self._metrics = metrics or medium_metrics()
        self._on_position_changed = on_position_changed
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate
        self._action_handlers = (on_add_card, on_settings, on_close)
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
            width=action_canvas_width(self._metrics),
            height=self._metrics.menu_circle_size,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        for index, label in enumerate(MENU_ACTION_LABELS):
            self._draw_circle(
                self._actions,
                action_center_x(index, self._metrics),
                self._metrics.menu_circle_center,
                text=label,
            )
        self._actions.bind("<Button-1>", self._on_action_press)
        self._actions.bind("<ButtonRelease-1>", self._on_action_release)

        self._circle = self._create_circle_canvas(
            self._row,
            text="<",
            bg=bg,
            cursor="fleur",
        )
        self._circle.pack(side=tk.RIGHT)
        self._bind_hover(self.widget)

        self._circle.bind("<Button-1>", self._on_drag_press)
        self._circle.bind("<B1-Motion>", self._on_drag_motion)
        self._circle.bind("<ButtonRelease-1>", self._on_drag_release)

    def _draw_circle(
        self,
        canvas: tk.Canvas,
        center_x: int,
        center_y: int,
        *,
        text: str,
        pad: int = MENU_CIRCLE_PAD,
    ) -> None:
        radius = circle_radius(self._metrics, pad=pad)
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
            font=self._metrics.menu_circle_font,
            fill=MENU_CIRCLE_FG,
        )

    def _create_circle_canvas(
        self,
        parent: tk.Misc,
        *,
        text: str,
        bg: str,
        cursor: str,
    ) -> tk.Canvas:
        canvas = tk.Canvas(
            parent,
            width=self._metrics.menu_circle_size,
            height=self._metrics.menu_circle_size,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor=cursor,
        )
        self._draw_circle(
            canvas,
            self._metrics.menu_circle_center,
            self._metrics.menu_circle_center,
            text=text,
        )
        return canvas

    def _bind_hover(self, widget: tk.Misc) -> None:
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        for child in widget.winfo_children():
            self._bind_hover(child)

    def _content_width(self) -> int:
        if self._actions_expanded:
            return action_canvas_width(self._metrics) + self._metrics.menu_circle_size
        return self._metrics.menu_circle_size

    def _widget_width(self) -> int:
        self.widget.update_idletasks()
        width = self.widget.winfo_width()
        if width > 1:
            return width
        return self._content_width()

    def _widget_height(self) -> int:
        self.widget.update_idletasks()
        height = self.widget.winfo_height()
        if height > 1:
            return height
        return self._metrics.menu_circle_size

    def _sync_place_from_widget(self) -> None:
        self.widget.update_idletasks()
        self._place_x = self.widget.winfo_x()
        self._place_y = self.widget.winfo_y()
        self._anchor_right_x = self._place_x + self._widget_width()

    def _relayout(self) -> None:
        self.widget.place(x=self._anchor_right_x, y=self._place_y, anchor=tk.NE)
        self._sync_place_from_widget()

    def place_at(self, x: int, y: int) -> None:
        """左上座標で配置する（永続化・ドラッグ用）."""
        self._place_x = x
        self._place_y = y
        self.widget.update_idletasks()
        self._anchor_right_x = x + self._widget_width()
        self._relayout()

    def place_default(self, monitor_width: int, monitor_height: int) -> None:
        """画面右上（デフォルト位置）に配置する."""
        self._anchor_right_x = monitor_width - MENU_DEFAULT_MARGIN_X
        self._place_y = MENU_DEFAULT_MARGIN_Y
        self._relayout()
        _ = monitor_height

    def clamp_to_monitor(self, monitor_width: int, monitor_height: int) -> None:
        """モニター内に収まるよう座標を調整する."""
        self.widget.update_idletasks()
        width = self._widget_width()
        height = self._widget_height()
        self._anchor_right_x = min(max(width, self._anchor_right_x), monitor_width)
        self._place_y = min(max(0, self._place_y), max(0, monitor_height - height))
        self._relayout()

    @property
    def position(self) -> tuple[int, int]:
        return self._place_x, self._place_y

    def bounds(self) -> MenuPanelRect:
        """配置計算用のパネル矩形（展開/収納状態を反映）."""
        self._sync_place_from_widget()
        return MenuPanelRect(
            x=self._place_x,
            y=self._place_y,
            width=self._widget_width(),
            height=self._widget_height(),
            right_edge=self._anchor_right_x,
        )

    def _set_actions_expanded(self, expanded: bool) -> None:
        if self._actions_expanded == expanded:
            return
        self._actions_expanded = expanded
        if expanded:
            self._actions.pack(side=tk.RIGHT)
        else:
            self._actions.pack_forget()
        self._relayout()

    def _cancel_hide_timer(self) -> None:
        if self._hide_after_id is not None:
            self.widget.after_cancel(self._hide_after_id)
            self._hide_after_id = None

    def _on_action_press(self, event: tk.Event) -> None:
        self._notify_activate()
        self._action_press_index = action_index_at(event.x, event.y, self._metrics)

    def _on_action_release(self, event: tk.Event) -> None:
        release_index = action_index_at(event.x, event.y, self._metrics)
        if (
            self._action_press_index is not None
            and release_index == self._action_press_index
        ):
            self._action_handlers[release_index]()
        self._action_press_index = None

    def _notify_activate(self) -> None:
        if self._on_activate is not None:
            self._on_activate()

    def _notify_deactivate_if_idle(self) -> None:
        if self._hover_depth == 0 and self._on_deactivate is not None:
            self._on_deactivate()

    def _collapse_after_hover(self) -> None:
        self._set_actions_expanded(False)
        self._notify_deactivate_if_idle()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover_depth += 1
        self._cancel_hide_timer()
        if self._hover_depth == 1:
            self._set_actions_expanded(True)
            self._notify_activate()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover_depth = max(0, self._hover_depth - 1)
        if self._hover_depth > 0:
            return
        self._cancel_hide_timer()
        self._hide_after_id = self.widget.after(
            MENU_HOVER_HIDE_DELAY_MS,
            self._collapse_after_hover,
        )

    def _on_drag_press(self, event: tk.Event) -> None:
        self._notify_activate()
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
