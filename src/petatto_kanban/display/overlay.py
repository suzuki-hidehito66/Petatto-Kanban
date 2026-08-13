"""オーバーレイモード（透過・最前面全画面）."""

from __future__ import annotations

from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.transparent import (
    apply_fullscreen_transparent_shell,
    apply_non_windows_fallback,
    configure_windows_transparency,
    is_windows,
)

if TYPE_CHECKING:
    import tkinter as tk


def apply_overlay_mode(root: tk.Tk, monitor: Monitor) -> None:
    """オーバーレイモードを適用する（共通シェル + 最前面）。"""
    apply_fullscreen_transparent_shell(root, monitor)

    if is_windows():
        root.attributes("-topmost", True)
        configure_windows_transparency(root)
        return

    apply_non_windows_fallback(root, title="Petatto-Kanban (overlay fallback)")
    root.attributes("-topmost", True)
