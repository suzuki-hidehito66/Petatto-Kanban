"""デスクトップモード（透過・背面全画面）."""

from __future__ import annotations

import sys
import tkinter as tk

from petatto_kanban.display.monitors import Monitor

# UI で使わない透過キー色
TRANSPARENT_COLOR = "#010101"

HWND_BOTTOM = 1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010


def _get_hwnd(root: tk.Tk) -> int:
    root.update_idletasks()
    return root.winfo_id()


def send_window_to_back(root: tk.Tk) -> None:
    """ウィンドウを Z オーダー最背面へ送る（Windows のみ）。"""
    if sys.platform != "win32":
        return

    import ctypes

    hwnd = _get_hwnd(root)
    ctypes.windll.user32.SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
    )


def apply_desktop_mode(root: tk.Tk, monitor: Monitor) -> None:
    """デスクトップモードを適用する."""
    root.overrideredirect(True)
    root.title("")
    root.configure(bg=TRANSPARENT_COLOR)
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

    if sys.platform == "win32":
        root.attributes("-transparentcolor", TRANSPARENT_COLOR)
        root.update_idletasks()
        send_window_to_back(root)
    else:
        # 開発環境（非 Windows）: 通常ウィンドウにフォールバック
        root.overrideredirect(False)
        root.title("Petatto-Kanban (desktop mode fallback)")
        root.minsize(960, 540)


def is_desktop_mode_supported() -> bool:
    """デスクトップモードが OS 上でサポートされるか."""
    return sys.platform == "win32"
