"""user32 の遅延バインド（Windows のみ。呼び出し側が is_windows を保証する）."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Any

_api: Any | None = None


class _GuiThreadInfo(ctypes.Structure):
    """GetGUIThreadInfo 用。"""

    _fields_ = (
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    )


def _load_user32() -> Any:
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
    get_gui_thread_info = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.DWORD,
        ctypes.POINTER(_GuiThreadInfo),
    )(("GetGUIThreadInfo", user32))

    class User32Api:
        GetForegroundWindow = staticmethod(get_foreground_window)
        GetCursorPos = staticmethod(get_cursor_pos)
        WindowFromPoint = staticmethod(window_from_point)
        GetWindowThreadProcessId = staticmethod(get_window_thread_process_id)
        GetAsyncKeyState = staticmethod(get_async_key_state)
        GetGUIThreadInfo = staticmethod(get_gui_thread_info)

    return User32Api()


def user32_api() -> Any:
    """user32 プロトタイプを返す（初回のみバインド）。"""
    global _api
    if _api is None:
        _api = _load_user32()
    return _api


def process_id_for_hwnd(hwnd: int | None) -> int | None:
    """ウィンドウハンドルのプロセス ID。無効なら None。"""
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
    point = wintypes.POINT()
    if not user32_api().GetCursorPos(ctypes.byref(point)):
        return None
    return process_id_for_hwnd(user32_api().WindowFromPoint(point))


def async_key_state(virtual_key: int) -> int:
    """GetAsyncKeyState の戻り値。"""
    return int(user32_api().GetAsyncKeyState(virtual_key))


def _foreground_gui_thread_info() -> _GuiThreadInfo | None:
    info = _GuiThreadInfo()
    info.cbSize = ctypes.sizeof(info)
    if not user32_api().GetGUIThreadInfo(0, ctypes.byref(info)):
        return None
    return info


def capture_process_id() -> int | None:
    """前面スレッドがマウスキャプチャしているウィンドウのプロセス ID。"""
    info = _foreground_gui_thread_info()
    if info is None:
        return None
    return process_id_for_hwnd(info.hwndCapture)


def move_size_process_id() -> int | None:
    """前面スレッドが移動またはサイズ変更中のウィンドウのプロセス ID。"""
    info = _foreground_gui_thread_info()
    if info is None:
        return None
    return process_id_for_hwnd(info.hwndMoveSize)
