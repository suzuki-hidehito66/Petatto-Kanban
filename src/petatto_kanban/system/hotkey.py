"""Windows グローバルホットキーの登録と WM_HOTKEY 受信."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from typing import Protocol

from petatto_kanban.system.shortcut import ShortcutChord, parse_shortcut

HOTKEY_ID_NEW_CARD = 1
WM_HOTKEY = 0x0312
HWND_MESSAGE = -3


class HotkeyRegistrar(Protocol):
    """RegisterHotKey 互換."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None: ...

    def unregister(self, hwnd: int, hotkey_id: int) -> None: ...


class Win32HotkeyRegistrar:
    """user32 RegisterHotKey / UnregisterHotKey."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        user32 = _user32()
        if not user32.RegisterHotKey(hwnd, hotkey_id, modifiers, vk):
            raise ctypes.WinError()

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        _user32().UnregisterHotKey(hwnd, hotkey_id)


class NoOpHotkeyRegistrar:
    """開発ホスト用（製品対象は Windows 11 以降）。"""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        return None

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        return None


class Win32HotkeyWindow:
    """WM_HOTKEY 受信用のメッセージ専用ウィンドウ（Tk HWND は触らない）."""

    def __init__(self, on_hotkey: Callable[[int], None]) -> None:
        self._on_hotkey = on_hotkey
        self._hwnd = 0
        self._wndproc: object | None = None
        self._class_name = f"PetattoKanbanHotkey_{id(self)}"
        self._hinstance: int | None = None
        self._create()

    @property
    def hwnd(self) -> int:
        return self._hwnd

    def _create(self) -> None:
        user32 = _user32()
        kernel32 = ctypes.windll.kernel32
        kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        hinstance = kernel32.GetModuleHandleW(None)
        self._hinstance = int(hinstance) if hinstance else None

        # Windows は LLP64。LRESULT / WPARAM / LPARAM はポインタ幅（c_long は溢れる）
        wndproc_type = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        )

        class _WndClassW(ctypes.Structure):
            _fields_ = [
                ("style", ctypes.c_uint),
                ("lpfnWndProc", wndproc_type),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p),
                ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p),
                ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_wchar_p),
                ("lpszClassName", ctypes.c_wchar_p),
            ]

        def _wnd_proc(
            hwnd: int,
            message: int,
            wparam: int,
            lparam: int,
        ) -> int:
            if message == WM_HOTKEY:
                self._on_hotkey(int(wparam))
                return 0
            return int(user32.DefWindowProcW(hwnd, message, wparam, lparam))

        self._wndproc = wndproc_type(_wnd_proc)
        window_class = _WndClassW()
        window_class.lpfnWndProc = self._wndproc
        window_class.hInstance = hinstance
        window_class.lpszClassName = self._class_name
        user32.RegisterClassW.argtypes = [ctypes.POINTER(_WndClassW)]
        user32.RegisterClassW.restype = ctypes.c_ushort
        if not user32.RegisterClassW(ctypes.byref(window_class)):
            raise ctypes.WinError()
        hwnd = user32.CreateWindowExW(
            0,
            self._class_name,
            None,
            0,
            0,
            0,
            0,
            0,
            HWND_MESSAGE,
            None,
            hinstance,
            None,
        )
        if not hwnd:
            user32.UnregisterClassW(self._class_name, hinstance)
            raise ctypes.WinError()
        self._hwnd = int(hwnd)

    def close(self) -> None:
        if self._hwnd == 0:
            return
        user32 = _user32()
        user32.DestroyWindow(self._hwnd)
        if self._hinstance is not None:
            user32.UnregisterClassW(self._class_name, self._hinstance)
        self._hwnd = 0
        self._wndproc = None
        self._hinstance = None


class NewCardHotkey:
    """新規カード用ホットキーの登録セッション."""

    def __init__(
        self,
        hwnd: int,
        on_new_card: Callable[[], None],
        *,
        registrar: HotkeyRegistrar | None = None,
    ) -> None:
        self._hwnd = hwnd
        self._on_new_card = on_new_card
        self._registrar = registrar or _default_registrar()
        self._window: Win32HotkeyWindow | None = None
        self._active: ShortcutChord | None = None

    def attach_window(self, window: Win32HotkeyWindow) -> None:
        self._window = window
        self._hwnd = window.hwnd

    def set_shortcut(self, text: str) -> None:
        chord = parse_shortcut(text)
        if chord is None:
            msg = f"不正なショートカットです: {text}"
            raise RuntimeError(msg)
        if self._active == chord:
            return
        previous = self._active
        self.clear()
        try:
            self._bind(chord)
        except (OSError, RuntimeError):
            if previous is not None:
                try:
                    self._bind(previous)
                except (OSError, RuntimeError):
                    self._active = None
            raise

    def handle_hotkey_id(self, hotkey_id: int) -> None:
        if hotkey_id == HOTKEY_ID_NEW_CARD:
            self._on_new_card()

    def clear(self) -> None:
        if self._active is None:
            return
        self._registrar.unregister(self._hwnd, HOTKEY_ID_NEW_CARD)
        self._active = None

    def close(self) -> None:
        self.clear()
        if self._window is not None:
            self._window.close()
            self._window = None

    def _bind(self, chord: ShortcutChord) -> None:
        self._registrar.register(
            self._hwnd,
            HOTKEY_ID_NEW_CARD,
            chord.win_modifiers(),
            chord.virtual_key(),
        )
        self._active = chord


def is_hotkey_supported() -> bool:
    """対象 OS（Windows 11 以降）上かどうか。"""
    return sys.platform == "win32"


def create_new_card_hotkey(
    on_new_card: Callable[[], None],
    *,
    registrar: HotkeyRegistrar | None = None,
) -> NewCardHotkey:
    """本番用セッションを組み立てる。"""
    session = NewCardHotkey(0, on_new_card, registrar=registrar)
    if registrar is None and is_hotkey_supported():
        session.attach_window(Win32HotkeyWindow(session.handle_hotkey_id))
    return session


def _default_registrar() -> HotkeyRegistrar:
    if is_hotkey_supported():
        return Win32HotkeyRegistrar()
    return NoOpHotkeyRegistrar()


def _user32() -> object:
    user32 = ctypes.windll.user32
    user32.RegisterHotKey.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_uint,
    ]
    user32.RegisterHotKey.restype = ctypes.c_int
    user32.UnregisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int]
    user32.UnregisterHotKey.restype = ctypes.c_int
    user32.DefWindowProcW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
    ]
    user32.DefWindowProcW.restype = ctypes.c_ssize_t
    user32.UnregisterClassW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p]
    user32.UnregisterClassW.restype = ctypes.c_int
    user32.CreateWindowExW.argtypes = [
        ctypes.c_uint,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    user32.CreateWindowExW.restype = ctypes.c_void_p
    user32.DestroyWindow.argtypes = [ctypes.c_void_p]
    user32.DestroyWindow.restype = ctypes.c_int
    return user32
