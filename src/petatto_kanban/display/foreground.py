"""フォアグラウンドウィンドウが自プロセス外かどうかの判定（Windows）."""

from __future__ import annotations

import os

from petatto_kanban.display.transparent import is_windows


def _foreground_process_id() -> int | None:
    import ctypes

    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return None

    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
    return pid.value


def is_foreign_app_foreground() -> bool:
    """前面ウィンドウが自プロセス以外なら True（Windows のみ。非 Windows は常に False）。"""
    if not is_windows():
        return False

    fg_pid = _foreground_process_id()
    if fg_pid is None:
        return False
    return fg_pid != os.getpid()
