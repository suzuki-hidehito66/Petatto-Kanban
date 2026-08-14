"""ショートカットコード正規化のテスト."""

from __future__ import annotations

from petatto_kanban.system.shortcut import (
    DEFAULT_NEW_CARD_SHORTCUT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    MOD_SHIFT,
    ShortcutChord,
    chord_from_tk_key,
    normalize_shortcut,
    parse_shortcut,
)


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
