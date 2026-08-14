"""Windows グローバルホットキーの登録と WM_HOTKEY 受信."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from typing import Protocol

from petatto_kanban.system.shortcut import ShortcutChord, parse_shortcut

HOTKEY_ID_NEW_CARD = 1
WM_HOTKEY = 0x0312
GWL_WNDPROC = -4


class HotkeyRegistrar(Protocol):
    """RegisterHotKey 互換."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None: ...

    def unregister(self, hwnd: int, hotkey_id: int) -> None: ...


class Win32HotkeyRegistrar:
    """user32 RegisterHotKey / UnregisterHotKey."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(hwnd, hotkey_id, modifiers, vk):
            raise ctypes.WinError()

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        ctypes.windll.user32.UnregisterHotKey(hwnd, hotkey_id)


class NoOpHotkeyRegistrar:
    """開発ホスト用（製品対象は Windows 11 以降）。"""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        return None

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        return None


class Win32HotkeyHook:
    """WM_HOTKEY を Tk ウィンドウ手続きで受け取る."""

    def __init__(self, hwnd: int, on_hotkey: Callable[[int], None]) -> None:
        self._hwnd = hwnd
        self._on_hotkey = on_hotkey
        self._old_proc: int | None = None
        self._wndproc: object | None = None
        self._install()

    def _install(self) -> None:
        user32 = ctypes.windll.user32
        lresult = ctypes.c_ssize_t
        wndproc_type = ctypes.WINFUNCTYPE(
            lresult,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_void_p,
        )

        def _wnd_proc(hwnd: int, message: int, wparam: int, lparam: int) -> int:
            if message == WM_HOTKEY:
                self._on_hotkey(int(wparam))
                return 0
            return int(
                user32.CallWindowProcW(
                    ctypes.c_void_p(self._old_proc or 0),
                    hwnd,
                    message,
                    wparam,
                    lparam,
                )
            )

        self._wndproc = wndproc_type(_wnd_proc)
        user32.SetWindowLongPtrW.restype = ctypes.c_void_p
        user32.SetWindowLongPtrW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
        ]
        user32.GetWindowLongPtrW.restype = ctypes.c_void_p
        user32.GetWindowLongPtrW.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._old_proc = user32.GetWindowLongPtrW(self._hwnd, GWL_WNDPROC)
        user32.SetWindowLongPtrW(self._hwnd, GWL_WNDPROC, self._wndproc)

    def close(self) -> None:
        if self._old_proc is None:
            return
        ctypes.windll.user32.SetWindowLongPtrW(
            self._hwnd,
            GWL_WNDPROC,
            ctypes.c_void_p(self._old_proc),
        )
        self._old_proc = None
        self._wndproc = None


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
        self._hook: Win32HotkeyHook | None = None
        self._active: ShortcutChord | None = None

    def attach_hook(self, hook: Win32HotkeyHook) -> None:
        self._hook = hook

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
        if self._hook is not None:
            self._hook.close()
            self._hook = None

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
    hwnd: int,
    on_new_card: Callable[[], None],
    *,
    registrar: HotkeyRegistrar | None = None,
) -> NewCardHotkey:
    """本番用セッションを組み立てる。"""
    session = NewCardHotkey(hwnd, on_new_card, registrar=registrar)
    if registrar is None and is_hotkey_supported():
        session.attach_hook(Win32HotkeyHook(hwnd, session.handle_hotkey_id))
    return session


def _default_registrar() -> HotkeyRegistrar:
    if is_hotkey_supported():
        return Win32HotkeyRegistrar()
    return NoOpHotkeyRegistrar()
