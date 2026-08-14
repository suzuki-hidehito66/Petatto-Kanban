"""user32 の遅延バインド（Windows のみ。呼び出し側が is_windows を保証する）."""

from __future__ import annotations

from ctypes import wintypes
from typing import Any

_api: Any | None = None


def _load_user32() -> Any:
    import ctypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    get_foreground_window = ctypes.WINFUNCTYPE(wintypes.HWND)(
        ("GetForegroundWindow", user32),
    )
    get_cursor_pos = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        ctypes.POINTER(wintypes.POINT),
    )(("GetCursorPos", user32))
    window_from_point = ctypes.WINFUNCTYPE(wintypes.HWND, wintypes.POINT)(
        ("WindowFromPoint", user32),
    )
    get_window_thread_process_id = ctypes.WINFUNCTYPE(
        wintypes.DWORD,
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    )(("GetWindowThreadProcessId", user32))
    get_async_key_state = ctypes.WINFUNCTYPE(ctypes.c_short, ctypes.c_int)(
        ("GetAsyncKeyState", user32),
    )

    class User32Api:
        GetForegroundWindow = staticmethod(get_foreground_window)
        GetCursorPos = staticmethod(get_cursor_pos)
        WindowFromPoint = staticmethod(window_from_point)
        GetWindowThreadProcessId = staticmethod(get_window_thread_process_id)
        GetAsyncKeyState = staticmethod(get_async_key_state)

    return User32Api()


def user32_api() -> Any:
    """user32 プロトタイプを返す（初回のみバインド）。"""
    global _api
    if _api is None:
        _api = _load_user32()
    return _api


def process_id_for_hwnd(hwnd: int | None) -> int | None:
    """ウィンドウハンドルのプロセス ID。無効なら None。"""
    import ctypes

    if not hwnd:
        return None
    pid = wintypes.DWORD()
    user32_api().GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def foreground_process_id() -> int | None:
    """前面ウィンドウのプロセス ID。"""
    return process_id_for_hwnd(user32_api().GetForegroundWindow())


def cursor_window_process_id() -> int | None:
    """カーソル下ウィンドウのプロセス ID。"""
    import ctypes

    point = wintypes.POINT()
    if not user32_api().GetCursorPos(ctypes.byref(point)):
        return None
    return process_id_for_hwnd(user32_api().WindowFromPoint(point))


def async_key_state(virtual_key: int) -> int:
    """GetAsyncKeyState の戻り値。"""
    return int(user32_api().GetAsyncKeyState(virtual_key))
