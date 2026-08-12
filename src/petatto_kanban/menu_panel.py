"""画面右上のメニューパネル（円形＜・ホバー展開・ドラッグ移動）."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

MENU_PANEL_BG = "#f0f0f0"
MENU_CIRCLE_SIZE = 36
MENU_CIRCLE_OUTLINE = "#888888"
MENU_CIRCLE_FILL = "#ffffff"
MENU_CHEVRON_FG = "#333333"
MENU_DEFAULT_MARGIN_X = 16
MENU_DEFAULT_MARGIN_Y = 16
MENU_HOVER_PADX = 4


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
        bg: str = MENU_PANEL_BG,
    ) -> None:
        self._on_add_card = on_add_card
        self._on_position_changed = on_position_changed
        self._bg = bg
        self._place_x = 0
        self._place_y = 0
        self._drag_origin: tuple[int, int] | None = None
        self._drag_moved = False
        self._hide_after_id: str | None = None

        self.widget = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)
        row = tk.Frame(self.widget, bg=bg, bd=0, highlightthickness=0)
        row.pack()

        self._actions = tk.Frame(row, bg=bg, bd=0, highlightthickness=0)
        ttk.Button(self._actions, text="⚙", width=3, command=on_settings).pack(
            side=tk.LEFT,
            padx=(0, MENU_HOVER_PADX),
        )
        ttk.Button(self._actions, text="×", width=3, command=on_close).pack(
            side=tk.LEFT,
            padx=(0, MENU_HOVER_PADX),
        )

        self._circle = tk.Canvas(
            row,
            width=MENU_CIRCLE_SIZE,
            height=MENU_CIRCLE_SIZE,
            bg=bg,
            highlightthickness=0,
            bd=0,
        )
        self._circle.pack(side=tk.LEFT)
        pad = 2
        self._circle.create_oval(
            pad,
            pad,
            MENU_CIRCLE_SIZE - pad,
            MENU_CIRCLE_SIZE - pad,
            outline=MENU_CIRCLE_OUTLINE,
            width=1,
            fill=MENU_CIRCLE_FILL,
        )
        self._circle.create_text(
            MENU_CIRCLE_SIZE // 2,
            MENU_CIRCLE_SIZE // 2,
            text="<",
            font=("Segoe UI", 14, "bold"),
            fill=MENU_CHEVRON_FG,
        )

        row.bind("<Enter>", self._on_enter)
        row.bind("<Leave>", self._on_leave)

        self._circle.bind("<Button-1>", self._on_drag_press)
        self._circle.bind("<B1-Motion>", self._on_drag_motion)
        self._circle.bind("<ButtonRelease-1>", self._on_drag_release)

        self._hide_actions()

    def place_at(self, x: int, y: int) -> None:
        """左上基準で配置する."""
        self._place_x = x
        self._place_y = y
        self.widget.place(x=x, y=y)

    def place_default(self, monitor_width: int, monitor_height: int) -> None:
        """画面右上（デフォルト位置）に配置する."""
        self.widget.update_idletasks()
        width = self.widget.winfo_reqwidth()
        x = max(0, monitor_width - MENU_DEFAULT_MARGIN_X - width)
        y = MENU_DEFAULT_MARGIN_Y
        self.place_at(x, y)
        _ = monitor_height

    def clamp_to_monitor(self, monitor_width: int, monitor_height: int) -> None:
        """モニター内に収まるよう座標を調整する."""
        self.widget.update_idletasks()
        width = self.widget.winfo_width()
        height = self.widget.winfo_height()
        if width <= 1:
            width = self.widget.winfo_reqwidth()
        if height <= 1:
            height = self.widget.winfo_reqheight()
        x = min(max(0, self._place_x), max(0, monitor_width - width))
        y = min(max(0, self._place_y), max(0, monitor_height - height))
        self.place_at(x, y)

    @property
    def position(self) -> tuple[int, int]:
        return self._place_x, self._place_y

    def _show_actions(self) -> None:
        if self._actions.winfo_ismapped():
            return
        self._actions.pack(side=tk.LEFT, padx=(0, MENU_HOVER_PADX))

    def _hide_actions(self) -> None:
        if not self._actions.winfo_ismapped():
            return
        self._actions.pack_forget()

    def _on_enter(self, _event: tk.Event) -> None:
        if self._hide_after_id is not None:
            self.widget.after_cancel(self._hide_after_id)
            self._hide_after_id = None
        self._show_actions()

    def _on_leave(self, _event: tk.Event) -> None:
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
        if self._drag_moved:
            if self._on_position_changed is not None:
                self._on_position_changed(self._place_x, self._place_y)
        else:
            self._on_add_card()
        self._drag_origin = None
        self._drag_moved = False
