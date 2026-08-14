"""グローバルホットキー登録セッションのテスト."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from petatto_kanban.system.hotkey import (
    HOTKEY_ID_NEW_CARD,
    NewCardHotkey,
    create_new_card_hotkey,
)
from petatto_kanban.system.shortcut import MOD_CONTROL, MOD_NOREPEAT, MOD_SHIFT


@dataclass
class FakeHotkeyRegistrar:
    """RegisterHotKey 互換の記録用."""

    registered: list[tuple[int, int, int, int]] = field(default_factory=list)
    unregistered: list[tuple[int, int]] = field(default_factory=list)
    fail_next: bool = False

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        if self.fail_next:
            self.fail_next = False
            msg = "already registered"
            raise OSError(msg)
        self.registered.append((hwnd, hotkey_id, modifiers, vk))

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        self.unregistered.append((hwnd, hotkey_id))


def test_new_card_hotkey_registers_and_fires() -> None:
    registrar = FakeHotkeyRegistrar()
    fired: list[str] = []
    session = NewCardHotkey(hwnd=42, on_new_card=lambda: fired.append("n"), registrar=registrar)

    session.set_shortcut("Ctrl+Shift+N")
    session.handle_hotkey_id(HOTKEY_ID_NEW_CARD)
    session.handle_hotkey_id(99)
    session.close()

    assert len(registrar.registered) == 1
    assert registrar.registered[0][0] == 42
    assert registrar.unregistered == [(42, HOTKEY_ID_NEW_CARD)]
    assert fired == ["n"]


def test_new_card_hotkey_restores_previous_on_register_failure() -> None:
    registrar = FakeHotkeyRegistrar()
    session = NewCardHotkey(hwnd=1, on_new_card=lambda: None, registrar=registrar)
    session.set_shortcut("Ctrl+Shift+N")
    registrar.fail_next = True

    with pytest.raises(OSError, match="already registered"):
        session.set_shortcut("Ctrl+Shift+K")

    assert registrar.registered[-1][2] == (MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT)
    assert registrar.registered[-1][3] == 0x4E


def test_create_new_card_hotkey_uses_injected_registrar() -> None:
    registrar = FakeHotkeyRegistrar()
    session = create_new_card_hotkey(1, lambda: None, registrar=registrar)
    session.set_shortcut("Alt+1")
    assert len(registrar.registered) == 1
