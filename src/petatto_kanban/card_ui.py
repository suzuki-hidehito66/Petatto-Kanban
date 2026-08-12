"""カード UI ウィジェット参照とクリック判定."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass


@dataclass(frozen=True)
class CardUiRefs:
    """1 枚のカードに紐づく Tk ウィジェット参照."""

    frame: tk.Frame
    title_frame: tk.Frame
    title_label: tk.Label
    due_panel: tk.Frame
    due_label: tk.Label
    progress_canvas: tk.Canvas


@dataclass
class ClickReleaseTracker:
    """クリック→離す→クリック→離す の二回目離しを検出する."""

    last_time: int = 0
    last_card_id: str | None = None

    def reset(self) -> None:
        self.last_time = 0
        self.last_card_id = None

    def is_second_release(self, card_id: str, event_time: int, interval_ms: int) -> bool:
        return (
            self.last_card_id == card_id
            and event_time - self.last_time <= interval_ms
        )

    def record(self, card_id: str, event_time: int) -> None:
        self.last_time = event_time
        self.last_card_id = card_id


def widget_is_descendant(widget: tk.Misc, ancestor: tk.Misc) -> bool:
    """widget が ancestor の子孫かどうか."""
    current: tk.Misc | None = widget
    while current is not None:
        if current == ancestor:
            return True
        current = current.master if isinstance(current.master, tk.Misc) else None
    return False


def double_click_interval_ms(root: tk.Misc) -> int:
    """Tk のダブルクリック判定間隔（ミリ秒）."""
    try:
        return int(root.tk.call("set", "tk_clicktime"))
    except tk.TclError:
        return 500
