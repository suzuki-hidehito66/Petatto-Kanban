"""オーバーレイモード（透過・最前面全画面）."""

from __future__ import annotations

import sys
import tkinter as tk

from petatto_kanban.display.desktop import TRANSPARENT_COLOR
from petatto_kanban.display.monitors import Monitor


def apply_overlay_mode(root: tk.Tk, monitor: Monitor) -> None:
    """オーバーレイモードを適用する（最前面・全画面・背景透過）."""
    root.overrideredirect(True)
    root.title("")
    root.configure(bg=TRANSPARENT_COLOR)
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

    if sys.platform == "win32":
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", TRANSPARENT_COLOR)
        root.update_idletasks()
    else:
        root.overrideredirect(False)
        root.title("Petatto-Kanban (overlay fallback)")
        root.attributes("-topmost", True)
        root.minsize(960, 540)
