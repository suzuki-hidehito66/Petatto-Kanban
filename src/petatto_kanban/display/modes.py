"""表示モード適用のエントリポイント."""

from __future__ import annotations

from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode

if TYPE_CHECKING:
    import tkinter as tk


def apply_display_mode(root: tk.Tk, monitor: Monitor, mode: DisplayMode) -> None:
    """settings.mode に応じて全画面表示モードを適用する."""
    if mode == DisplayMode.DESKTOP:
        from petatto_kanban.display.desktop import apply_desktop_mode

        apply_desktop_mode(root, monitor)
        return
    from petatto_kanban.display.overlay import apply_overlay_mode

    apply_overlay_mode(root, monitor)
