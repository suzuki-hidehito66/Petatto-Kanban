"""カード上に表示するインライン期限編集（カレンダー）."""

from __future__ import annotations

import calendar
import tkinter as tk
from collections.abc import Callable
from datetime import date
from tkinter import ttk

from petatto_kanban.due_date import DUE_DATE_NONE_LABEL

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
        self._month_label = tk.Label(header, bg=bg, font=("Segoe UI", 9, "bold"))
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
                font=("Segoe UI", 8),
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
                is_selected = self._selected == day
                tk.Button(
                    row,
                    text=str(day_number),
                    width=3,
                    relief=tk.SUNKEN if is_selected else tk.FLAT,
                    command=lambda picked=day: self._select_day(picked),
                ).pack(side=tk.LEFT, expand=True, padx=1, pady=1)
