"""他アプリ操作の判定（DM-DESKTOP-03）。"""

from __future__ import annotations

import os

from petatto_kanban.display.mouse_buttons import is_any_mouse_button_down
from petatto_kanban.display.transparent import is_windows


def _is_foreign_pid(pid: int | None) -> bool:
    if pid is None:
        return False
    return pid != os.getpid()


def is_foreign_app_foreground() -> bool:
    """前面ウィンドウが自プロセス以外なら True（非 Windows は常に False）。"""
    if not is_windows():
        return False

    from petatto_kanban.display.win32_user32 import foreground_process_id

    return _is_foreign_pid(foreground_process_id())


def is_foreign_app_under_cursor() -> bool:
    """カーソル下のウィンドウが自プロセス以外なら True（非 Windows は常に False）。"""
    if not is_windows():
        return False

    from petatto_kanban.display.win32_user32 import cursor_window_process_id

    return _is_foreign_pid(cursor_window_process_id())


def is_foreign_pointer_press() -> bool:
    """他アプリ上でマウスボタンが押下中なら True（離しを待たない）。"""
    return is_any_mouse_button_down() and is_foreign_app_under_cursor()
