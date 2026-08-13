"""全画面透過ウィンドウの共通設定."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor

if TYPE_CHECKING:
    import tkinter as tk

# UI で使わない透過キー色（カード・メニューパネルは別色）
TRANSPARENT_COLOR = "#010101"


def apply_fullscreen_transparent_shell(root: tk.Tk, monitor: Monitor) -> None:
    """オーバーレイ/デスクトップ共通の全画面フレームを適用する."""
    root.overrideredirect(True)
    root.title("")
    root.configure(bg=TRANSPARENT_COLOR)
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")


def configure_windows_transparency(root: tk.Tk) -> None:
    """Windows 向け透過色を設定する."""
    root.attributes("-transparentcolor", TRANSPARENT_COLOR)
    root.update_idletasks()


def apply_non_windows_fallback(root: tk.Tk, *, title: str) -> None:
    """非 Windows 開発環境向けの通常ウィンドウフォールバック."""
    root.overrideredirect(False)
    root.title(title)
    root.minsize(960, 540)


def is_windows() -> bool:
    return sys.platform == "win32"
