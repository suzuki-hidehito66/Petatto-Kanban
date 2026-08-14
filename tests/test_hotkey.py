"""グローバルホットキーとショートカット正規化のテスト."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from petatto_kanban.system.hotkey import (
    DEFAULT_NEW_CARD_SHORTCUT,
    HOTKEY_ID_NEW_CARD,
    MOD_CONTROL,
    MOD_NOREPEAT,
    MOD_SHIFT,
    NewCardHotkey,
    ShortcutChord,
    chord_from_tk_key,
    create_new_card_hotkey,
    normalize_shortcut,
    parse_shortcut,
)


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


def test_parse_shortcut_default() -> None:
    chord = parse_shortcut("Ctrl+Shift+N")
    assert chord == ShortcutChord(ctrl=True, alt=False, shift=True, key="N")
    assert chord.format() == DEFAULT_NEW_CARD_SHORTCUT


def test_parse_shortcut_normalizes_modifier_order_and_case() -> None:
    chord = parse_shortcut("shift+ctrl+k")
    assert chord is not None
    assert chord.format() == "Ctrl+Shift+K"


def test_parse_shortcut_rejects_invalid() -> None:
    assert parse_shortcut(None) is None
    assert parse_shortcut("") is None
    assert parse_shortcut("N") is None
    assert parse_shortcut("Ctrl") is None
    assert parse_shortcut("Ctrl+Shift") is None
    assert parse_shortcut("Win+N") is None
    assert parse_shortcut("Ctrl+F13") is None


def test_normalize_shortcut_falls_back_to_default() -> None:
    assert normalize_shortcut(None) == DEFAULT_NEW_CARD_SHORTCUT
    assert normalize_shortcut("nope") == DEFAULT_NEW_CARD_SHORTCUT
    assert normalize_shortcut("Ctrl+Shift+K") == "Ctrl+Shift+K"


def test_virtual_key_and_modifiers() -> None:
    chord = parse_shortcut("Ctrl+Shift+N")
    assert chord is not None
    assert chord.virtual_key() == 0x4E
    assert chord.win_modifiers() == (MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT)
    f12 = parse_shortcut("Alt+F12")
    assert f12 is not None
    assert f12.virtual_key() == 0x70 + 11


def test_chord_from_tk_key_requires_modifier() -> None:
    assert chord_from_tk_key("n", 0) is None
    assert chord_from_tk_key("Escape", 0x0004) is None
    chord = chord_from_tk_key("n", 0x0004 | 0x0001)
    assert chord is not None
    assert chord.format() == "Ctrl+Shift+N"


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
