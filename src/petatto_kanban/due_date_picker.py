"""フロート期限編集パネル（カレンダー）."""

from __future__ import annotations

import calendar
import tkinter as tk
from collections.abc import Callable
from datetime import date
from tkinter import ttk

from petatto_kanban.card_ui import widget_is_descendant
from petatto_kanban.due_date import DUE_DATE_NONE_LABEL, calendar_day_button_style

_WEEKDAY_LABELS = ("日", "月", "火", "水", "木", "金", "土")


class DueDatePicker(tk.Frame):
    """オーバーレイ上のフロート期限選択パネル用 UI."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        initial: date | None,
        on_apply: Callable[[date | None], None],
        on_cancel: Callable[[], None],
        bg: str,
        month_font: tuple[str, int, str] | tuple[str, int] = ("Segoe UI", 9, "bold"),
        weekday_font: tuple[str, int] | tuple[str, int, str] = ("Segoe UI", 8),
    ) -> None:
        super().__init__(parent, bg=bg, bd=1, relief=tk.RIDGE, padx=4, pady=4)
        self._on_apply = on_apply
        self._on_cancel = on_cancel
        self._bg = bg
        self._selected = initial
        anchor = initial or date.today()
        self._view_year = anchor.year
        self._view_month = anchor.month

        header = tk.Frame(self, bg=bg)
        header.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(header, text="◀", width=3, command=self._prev_month).pack(side=tk.LEFT)
        self._month_label = tk.Label(header, bg=bg, font=month_font)
        self._month_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(header, text="▶", width=3, command=self._next_month).pack(side=tk.RIGHT)

        weekday_row = tk.Frame(self, bg=bg)
        weekday_row.pack(fill=tk.X)
        for label in _WEEKDAY_LABELS:
            tk.Label(
                weekday_row,
                text=label,
                bg=bg,
                width=3,
                font=weekday_font,
            ).pack(side=tk.LEFT, expand=True)

        self._days_frame = tk.Frame(self, bg=bg)
        self._days_frame.pack(fill=tk.X)

        actions = tk.Frame(self, bg=bg)
        actions.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(actions, text=DUE_DATE_NONE_LABEL, command=self._apply_none).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        ttk.Button(actions, text="閉じる", command=on_cancel).pack(side=tk.RIGHT)

        self.bind("<Escape>", lambda _e: on_cancel())
        self._render_days()

    def _month_title(self) -> str:
        return f"{self._view_year}年 {self._view_month}月"

    def _prev_month(self) -> None:
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._render_days()

    def _next_month(self) -> None:
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._render_days()

    def _apply_none(self) -> None:
        self._on_apply(None)

    def _select_day(self, day: date) -> None:
        self._selected = day
        self._on_apply(day)

    def _render_days(self) -> None:
        self._month_label.config(text=self._month_title())
        for child in self._days_frame.winfo_children():
            child.destroy()

        weeks = calendar.Calendar(firstweekday=calendar.SUNDAY).monthdayscalendar(
            self._view_year,
            self._view_month,
        )
        for week in weeks:
            row = tk.Frame(self._days_frame, bg=self._bg)
            row.pack(fill=tk.X)
            for day_number in week:
                if day_number == 0:
                    tk.Label(row, text="", bg=self._bg, width=3).pack(
                        side=tk.LEFT, expand=True
                    )
                    continue
                day = date(self._view_year, self._view_month, day_number)
                bg, fg, relief_name = calendar_day_button_style(
                    day,
                    selected=self._selected,
                    default_bg=self._bg,
                )
                tk.Button(
                    row,
                    text=str(day_number),
                    width=3,
                    bg=bg,
                    fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    relief=tk.SUNKEN if relief_name == "sunken" else tk.FLAT,
                    command=lambda picked=day: self._select_day(picked),
                ).pack(side=tk.LEFT, expand=True, padx=1, pady=1)


class DueDatePickerHost:
    """カード外に place するフロート期限編集パネルのホスト."""

    def __init__(
        self,
        root: tk.Misc,
        *,
        bg: str,
        panel_width: int,
        month_font: tuple[str, int, str] | tuple[str, int] = ("Segoe UI", 9, "bold"),
        weekday_font: tuple[str, int] | tuple[str, int, str] = ("Segoe UI", 8),
        on_outside_click: Callable[[], None] | None = None,
    ) -> None:
        self._root = root
        self._bg = bg
        self._panel_width = panel_width
        self._month_font = month_font
        self._weekday_font = weekday_font
        self._on_outside_click = on_outside_click
        self._host: tk.Frame | None = None
        self._picker: DueDatePicker | None = None
        self._cancel: Callable[[], None] | None = None
        self._outside_bound = False
        self.edit_card_id: str | None = None

    @property
    def is_open(self) -> bool:
        return self._host is not None

    @property
    def host_frame(self) -> tk.Frame | None:
        return self._host

    def cancel_if_any(self) -> bool:
        if self._cancel is None:
            return False
        self._cancel()
        return True

    def close(self) -> None:
        self._unbind_outside_click()
        if self._host is not None:
            self._host.destroy()
            self._host = None
        self._picker = None
        self._cancel = None
        self.edit_card_id = None

    def open(
        self,
        *,
        card_id: str,
        due_panel: tk.Misc,
        initial: date | None,
        on_apply: Callable[[date | None], None],
        lift_targets: list[tk.Misc],
    ) -> None:
        self.close()
        self.edit_card_id = card_id

        def cancel() -> None:
            self.close()

        def apply(value: date | None) -> None:
            on_apply(value)
            self.close()

        host = tk.Frame(
            self._root,
            bg=self._bg,
            bd=1,
            relief=tk.RIDGE,
            padx=2,
            pady=2,
            highlightthickness=0,
        )
        picker = DueDatePicker(
            host,
            initial=initial,
            on_apply=apply,
            on_cancel=cancel,
            bg=self._bg,
            month_font=self._month_font,
            weekday_font=self._weekday_font,
        )
        picker.pack(fill=tk.BOTH, expand=True)
        self._host = host
        self._picker = picker
        self._cancel = cancel
        self._place_near(due_panel, host)
        self._bind_outside_click()
        for target in lift_targets:
            target.lift()
        picker.focus_set()

    def _place_near(self, anchor: tk.Misc, host: tk.Frame) -> None:
        self._root.update_idletasks()
        host.update_idletasks()
        root_width = self._root.winfo_width()
        root_height = self._root.winfo_height()
        anchor_x = anchor.winfo_rootx() - self._root.winfo_rootx()
        anchor_y = anchor.winfo_rooty() - self._root.winfo_rooty()
        anchor_height = anchor.winfo_height()
        panel_width = max(self._panel_width, host.winfo_reqwidth())
        panel_height = host.winfo_reqheight()
        x = min(max(0, anchor_x), max(0, root_width - panel_width))
        y = anchor_y + anchor_height + 4
        if y + panel_height > root_height:
            y = max(0, anchor_y - panel_height - 4)
        host.place(x=x, y=y, width=panel_width)

    def _bind_outside_click(self) -> None:
        if self._outside_bound:
            return
        self._root.bind_all("<Button-1>", self._handle_outside_click, add="+")
        self._root.bind_all("<ButtonRelease-1>", self._handle_outside_click, add="+")
        self._outside_bound = True

    def _unbind_outside_click(self) -> None:
        if not self._outside_bound:
            return
        self._root.unbind_all("<Button-1>")
        self._root.unbind_all("<ButtonRelease-1>")
        self._outside_bound = False

    def _handle_outside_click(self, event: tk.Event) -> None:
        host = self._host
        if host is None:
            return
        widget = event.widget
        if isinstance(widget, tk.Misc) and widget_is_descendant(widget, host):
            return
        host.update_idletasks()
        x, y = event.x_root, event.y_root
        left = host.winfo_rootx()
        top = host.winfo_rooty()
        right = left + host.winfo_width()
        bottom = top + host.winfo_height()
        if left <= x <= right and top <= y <= bottom:
            return
        if self._on_outside_click is not None:
            self._on_outside_click()

