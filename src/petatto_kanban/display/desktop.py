"""デスクトップモード（透過・背面全画面）."""

from __future__ import annotations

from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.transparent import (
    TRANSPARENT_COLOR,
    apply_fullscreen_transparent_shell,
    apply_non_windows_fallback,
    configure_windows_transparency,
    is_windows,
)

if TYPE_CHECKING:
    import tkinter as tk

# 後方互換の re-export
__all__ = [
    "TRANSPARENT_COLOR",
    "apply_desktop_mode",
    "bring_board_to_front",
    "is_desktop_mode_supported",
    "restore_desktop_board_z_order",
    "send_window_to_back",
]

HWND_BOTTOM = 1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010


def send_window_to_back(root: tk.Tk) -> None:
    """ウィンドウを Z オーダー最背面へ送る（Windows のみ）。"""
    if not is_windows():
        return

    import ctypes

    root.update_idletasks()
    hwnd = root.winfo_id()
    ctypes.windll.user32.SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
    )


def bring_board_to_front(root: tk.Tk) -> None:
    """デスクトップモード中、カード等を含む本体を一時的に最前面へ."""
    if not is_windows():
        root.lift()
        return

    root.attributes("-topmost", True)
    root.lift()
    root.update_idletasks()


def restore_desktop_board_z_order(root: tk.Tk) -> None:
    """デスクトップモードの本体 Z オーダー（通常ウィンドウより背面）を復元する."""
    if not is_windows():
        return

    root.attributes("-topmost", False)
    send_window_to_back(root)


def apply_desktop_mode(root: tk.Tk, monitor: Monitor) -> None:
    """デスクトップモードを適用する（オーバーレイ共通シェル + 背面 Z オーダー）。"""
    apply_fullscreen_transparent_shell(root, monitor)

    if is_windows():
        root.attributes("-topmost", False)
        configure_windows_transparency(root)
        send_window_to_back(root)
        return

    apply_non_windows_fallback(root, title="Petatto-Kanban (desktop mode fallback)")


def is_desktop_mode_supported() -> bool:
    """デスクトップモードが OS 上でサポートされるか."""
    return is_windows()
