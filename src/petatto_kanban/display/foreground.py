"""他アプリの前面・カーソル下・マウス押下の判定（Windows）。"""

from __future__ import annotations

import os
from ctypes import wintypes

from petatto_kanban.display.transparent import is_windows

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06
_MOUSE_BUTTON_VKS = (VK_LBUTTON, VK_RBUTTON, VK_MBUTTON, VK_XBUTTON1, VK_XBUTTON2)
_KEY_DOWN_MASK = 0x8000


def _process_id_for_hwnd(hwnd: int) -> int | None:
    import ctypes

    if not hwnd:
        return None
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _foreground_process_id() -> int | None:
    import ctypes

    foreground = ctypes.windll.user32.GetForegroundWindow()
    return _process_id_for_hwnd(foreground)


def _cursor_window_process_id() -> int | None:
    import ctypes

    class POINT(ctypes.Structure):
        _fields_ = (("x", wintypes.LONG), ("y", wintypes.LONG))

    user32 = ctypes.windll.user32
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.WindowFromPoint.argtypes = [POINT]
    user32.WindowFromPoint.restype = wintypes.HWND

    point = POINT()
    if not user32.GetCursorPos(ctypes.byref(point)):
        return None
    hwnd = user32.WindowFromPoint(point)
    return _process_id_for_hwnd(hwnd)


def _is_foreign_pid(pid: int | None) -> bool:
    if pid is None:
        return False
    return pid != os.getpid()


def is_foreign_app_foreground() -> bool:
    """前面ウィンドウが自プロセス以外なら True（Windows のみ。非 Windows は常に False）。"""
    if not is_windows():
        return False
    return _is_foreign_pid(_foreground_process_id())


def is_foreign_app_under_cursor() -> bool:
    """カーソル下のウィンドウが自プロセス以外なら True（非 Windows は常に False）。"""
    if not is_windows():
        return False
    return _is_foreign_pid(_cursor_window_process_id())


def is_any_mouse_button_down() -> bool:
    """いずれかのマウスボタンが押下中なら True（非 Windows は常に False）。"""
    if not is_windows():
        return False

    import ctypes

    get_async_key_state = ctypes.windll.user32.GetAsyncKeyState
    get_async_key_state.argtypes = [ctypes.c_int]
    get_async_key_state.restype = ctypes.c_short
    return any(
        get_async_key_state(virtual_key) & _KEY_DOWN_MASK
        for virtual_key in _MOUSE_BUTTON_VKS
    )
