"""キーボードショートカットのコード正規化と Windows グローバルホットキー."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

DEFAULT_NEW_CARD_SHORTCUT = "Ctrl+Shift+N"
HOTKEY_ID_NEW_CARD = 1

_MODIFIER_ORDER = ("Ctrl", "Alt", "Shift")
_MODIFIER_ALIASES = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "alt": "Alt",
    "shift": "Shift",
}

_VK_A = 0x41
_VK_0 = 0x30
_VK_F1 = 0x70
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
GWL_WNDPROC = -4

# Tk event.state bits（Windows / 共通）
_TK_SHIFT = 0x0001
_TK_CONTROL = 0x0004
_TK_ALT_MASKS = (0x0008, 0x20000)

_IGNORED_KEYSYMS = {
    "Shift_L",
    "Shift_R",
    "Control_L",
    "Control_R",
    "Alt_L",
    "Alt_R",
    "Meta_L",
    "Meta_R",
    "Win_L",
    "Win_R",
    "Caps_Lock",
    "Num_Lock",
    "Scroll_Lock",
}


@dataclass(frozen=True)
class ShortcutChord:
    """修飾キー + 1 キーのショートカット."""

    ctrl: bool
    alt: bool
    shift: bool
    key: str

    def format(self) -> str:
        parts: list[str] = []
        if self.ctrl:
            parts.append("Ctrl")
        if self.alt:
            parts.append("Alt")
        if self.shift:
            parts.append("Shift")
        parts.append(self.key)
        return "+".join(parts)

    def win_modifiers(self) -> int:
        modifiers = 0
        if self.alt:
            modifiers |= MOD_ALT
        if self.ctrl:
            modifiers |= MOD_CONTROL
        if self.shift:
            modifiers |= MOD_SHIFT
        return modifiers | MOD_NOREPEAT

    def virtual_key(self) -> int:
        if len(self.key) == 1 and "A" <= self.key <= "Z":
            return _VK_A + (ord(self.key) - ord("A"))
        if len(self.key) == 1 and "0" <= self.key <= "9":
            return _VK_0 + (ord(self.key) - ord("0"))
        if self.key.startswith("F") and self.key[1:].isdigit():
            index = int(self.key[1:])
            if 1 <= index <= 12:
                return _VK_F1 + (index - 1)
        msg = f"未対応のキーです: {self.key}"
        raise ValueError(msg)

    def has_modifier(self) -> bool:
        return self.ctrl or self.alt or self.shift


def parse_shortcut(text: str | None) -> ShortcutChord | None:
    """正規形のショートカット文字列を解析する。不正なら None。"""
    if text is None:
        return None
    tokens = [token.strip() for token in text.split("+") if token.strip()]
    if len(tokens) < 2:
        return None

    ctrl = alt = shift = False
    key_token: str | None = None
    for token in tokens:
        modifier = _MODIFIER_ALIASES.get(token.lower())
        if modifier == "Ctrl":
            ctrl = True
            continue
        if modifier == "Alt":
            alt = True
            continue
        if modifier == "Shift":
            shift = True
            continue
        if key_token is not None:
            return None
        key_token = token

    if key_token is None or not (ctrl or alt or shift):
        return None
    key = _normalize_key(key_token)
    if key is None:
        return None
    return ShortcutChord(ctrl=ctrl, alt=alt, shift=shift, key=key)


def normalize_shortcut(text: str | None) -> str:
    """不正・欠損時は既定 Ctrl+Shift+N。"""
    chord = parse_shortcut(text)
    if chord is None:
        return DEFAULT_NEW_CARD_SHORTCUT
    return chord.format()


def chord_from_tk_key(keysym: str, state: int) -> ShortcutChord | None:
    """Tk KeyPress からコードを組み立てる。Escape・修飾のみは None。"""
    if keysym == "Escape" or keysym in _IGNORED_KEYSYMS:
        return None
    key = _normalize_key(keysym)
    if key is None:
        return None
    chord = ShortcutChord(
        ctrl=bool(state & _TK_CONTROL),
        alt=any(state & mask for mask in _TK_ALT_MASKS),
        shift=bool(state & _TK_SHIFT),
        key=key,
    )
    if not chord.has_modifier():
        return None
    return chord


def _normalize_key(token: str) -> str | None:
    if len(token) == 1:
        char = token.upper()
        if "A" <= char <= "Z" or "0" <= char <= "9":
            return char
        return None
    upper = token.upper()
    if upper.startswith("F") and upper[1:].isdigit():
        index = int(upper[1:])
        if 1 <= index <= 12:
            return f"F{index}"
    return None


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
    """非 Windows ホスト用（製品対象外）。"""

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

        def _wnd_proc(
            hwnd: int, message: int, wparam: int, lparam: int
        ) -> int:
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
        hook: Win32HotkeyHook | None = None,
    ) -> None:
        self._hwnd = hwnd
        self._on_new_card = on_new_card
        self._registrar = registrar or _default_registrar()
        self._hook = hook
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
            self._registrar.register(
                self._hwnd,
                HOTKEY_ID_NEW_CARD,
                chord.win_modifiers(),
                chord.virtual_key(),
            )
        except (OSError, RuntimeError):
            if previous is not None:
                try:
                    self._registrar.register(
                        self._hwnd,
                        HOTKEY_ID_NEW_CARD,
                        previous.win_modifiers(),
                        previous.virtual_key(),
                    )
                    self._active = previous
                except (OSError, RuntimeError):
                    self._active = None
            raise
        self._active = chord

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


def create_new_card_hotkey(
    hwnd: int,
    on_new_card: Callable[[], None],
    *,
    registrar: HotkeyRegistrar | None = None,
) -> NewCardHotkey:
    """本番用セッションを組み立てる。"""
    session = NewCardHotkey(hwnd, on_new_card, registrar=registrar)
    if registrar is None and sys.platform == "win32":
        session.attach_hook(Win32HotkeyHook(hwnd, session.handle_hotkey_id))
    return session


def _default_registrar() -> HotkeyRegistrar:
    if sys.platform == "win32":
        return Win32HotkeyRegistrar()
    return NoOpHotkeyRegistrar()
