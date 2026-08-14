"""新規カード用グローバルホットキーのセッション（Win32 非依存）."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Protocol

from petatto_kanban.system.hotkey_pump import Win32HotkeyPump
from petatto_kanban.system.shortcut import ShortcutChord, parse_shortcut

HOTKEY_ID_NEW_CARD = 1
HOTKEY_POLL_MS = 50


class HotkeyPump(Protocol):
    """WM_HOTKEY を Tk スレッドの外で受け、id をキューイングする."""

    def set_hotkey(self, hotkey_id: int, modifiers: int, vk: int) -> None: ...

    def clear_hotkey(self, hotkey_id: int) -> None: ...

    def drain(self) -> list[int]: ...

    def close(self) -> None: ...


class NewCardHotkey:
    """新規カード用ホットキーの登録セッション."""

    def __init__(
        self,
        on_new_card: Callable[[], None],
        *,
        pump: HotkeyPump | None = None,
    ) -> None:
        self._on_new_card = on_new_card
        self._pump = pump
        self._active: ShortcutChord | None = None
        self._closed = False

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

    def poll(self) -> None:
        """Tk スレッドから呼ぶ。キューに溜まった WM_HOTKEY を処理する."""
        if self._closed or self._pump is None:
            return
        for hotkey_id in self._pump.drain():
            if hotkey_id == HOTKEY_ID_NEW_CARD:
                self._on_new_card()

    def clear(self) -> None:
        if self._active is None:
            return
        if self._pump is not None:
            self._pump.clear_hotkey(HOTKEY_ID_NEW_CARD)
        self._active = None

    def close(self) -> None:
        try:
            self.clear()
        finally:
            self._closed = True
            if self._pump is not None:
                self._pump.close()
                self._pump = None

    def _bind(self, chord: ShortcutChord) -> None:
        if self._pump is not None:
            self._pump.set_hotkey(
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
    pump: HotkeyPump | None = None,
) -> NewCardHotkey:
    """本番用セッションを組み立てる。"""
    if pump is None and is_hotkey_supported():
        win32_pump = Win32HotkeyPump()
        win32_pump.start()
        pump = win32_pump
    return NewCardHotkey(on_new_card, pump=pump)
