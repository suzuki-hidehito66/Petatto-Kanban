"""グローバルホットキー登録セッションのテスト."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from petatto_kanban.system import hotkey as hotkey_module
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


@dataclass
class FakeHotkeyPump:
    """専用スレッドの代わりに id を返すテスト用ポンプ."""

    queued: list[int] = field(default_factory=list)
    bindings: list[tuple[int, int, int]] = field(default_factory=list)
    cleared: list[int] = field(default_factory=list)
    closed: bool = False
    fail_next: bool = False

    def set_hotkey(self, hotkey_id: int, modifiers: int, vk: int) -> None:
        if self.fail_next:
            self.fail_next = False
            msg = "already registered"
            raise OSError(msg)
        self.bindings.append((hotkey_id, modifiers, vk))

    def clear_hotkey(self, hotkey_id: int) -> None:
        self.cleared.append(hotkey_id)

    def drain(self) -> list[int]:
        ids, self.queued = self.queued, []
        return ids

    def close(self) -> None:
        self.closed = True


def test_new_card_hotkey_registers_and_fires() -> None:
    registrar = FakeHotkeyRegistrar()
    fired: list[str] = []
    session = NewCardHotkey(on_new_card=lambda: fired.append("n"), registrar=registrar)

    session.set_shortcut("Ctrl+Shift+N")
    session.handle_hotkey_id(HOTKEY_ID_NEW_CARD)
    session.handle_hotkey_id(99)
    session.close()

    assert len(registrar.registered) == 1
    assert registrar.registered[0][0] == 0
    assert registrar.unregistered == [(0, HOTKEY_ID_NEW_CARD)]
    assert fired == ["n"]


def test_new_card_hotkey_restores_previous_on_register_failure() -> None:
    registrar = FakeHotkeyRegistrar()
    session = NewCardHotkey(on_new_card=lambda: None, registrar=registrar)
    session.set_shortcut("Ctrl+Shift+N")
    registrar.fail_next = True

    with pytest.raises(OSError, match="already registered"):
        session.set_shortcut("Ctrl+Shift+K")

    assert registrar.registered[-1][2] == (MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT)
    assert registrar.registered[-1][3] == 0x4E


def test_create_new_card_hotkey_uses_injected_registrar() -> None:
    registrar = FakeHotkeyRegistrar()
    session = create_new_card_hotkey(lambda: None, registrar=registrar)
    session.set_shortcut("Alt+1")
    assert len(registrar.registered) == 1
    session.close()


def test_poll_dispatches_only_new_card_ids_from_pump() -> None:
    fired: list[str] = []
    pump = FakeHotkeyPump(queued=[HOTKEY_ID_NEW_CARD, 99, HOTKEY_ID_NEW_CARD])
    session = NewCardHotkey(
        on_new_card=lambda: fired.append("n"),
        registrar=FakeHotkeyRegistrar(),
        pump=pump,
    )

    session.poll()
    session.poll()

    assert fired == ["n", "n"]
    session.close()
    assert pump.closed


def test_set_shortcut_uses_pump_instead_of_registrar() -> None:
    registrar = FakeHotkeyRegistrar()
    pump = FakeHotkeyPump()
    session = NewCardHotkey(on_new_card=lambda: None, registrar=registrar, pump=pump)

    session.set_shortcut("Ctrl+Shift+N")
    session.close()

    assert pump.bindings == [
        (HOTKEY_ID_NEW_CARD, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, 0x4E),
    ]
    assert registrar.registered == []
    assert pump.cleared == [HOTKEY_ID_NEW_CARD]


def test_pump_register_failure_restores_previous() -> None:
    pump = FakeHotkeyPump()
    session = NewCardHotkey(
        on_new_card=lambda: None,
        registrar=FakeHotkeyRegistrar(),
        pump=pump,
    )
    session.set_shortcut("Ctrl+Shift+N")
    pump.fail_next = True

    with pytest.raises(OSError, match="already registered"):
        session.set_shortcut("Ctrl+Shift+K")

    assert pump.bindings[-1] == (
        HOTKEY_ID_NEW_CARD,
        MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
        0x4E,
    )
    session.close()


def test_hotkey_module_does_not_use_python_wndproc() -> None:
    source = hotkey_module.__file__
    assert source is not None
    text = Path(source).read_text(encoding="utf-8")
    assert "WINFUNCTYPE" not in text
