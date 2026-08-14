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


def is_foreign_app_capturing() -> bool:
    """前面スレッドのマウスキャプチャが自プロセス外なら True。"""
    if not is_windows():
        return False

    from petatto_kanban.display.win32_user32 import capture_process_id

    return _is_foreign_pid(capture_process_id())


def is_foreign_window_being_moved() -> bool:
    """他アプリのウィンドウを移動またはサイズ変更中なら True。"""
    if not is_windows():
        return False

    from petatto_kanban.display.win32_user32 import move_size_process_id

    return _is_foreign_pid(move_size_process_id())


def is_foreign_pointer_press() -> bool:
    """他アプリの押下・ドラッグ・サイズ変更中なら True（離しを待たない）。"""
    if is_foreign_window_being_moved():
        return True
    if not is_any_mouse_button_down():
        return False
    return is_foreign_app_under_cursor() or is_foreign_app_capturing()
