"""グローバルホットキー登録セッションのテスト."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from petatto_kanban.system import hotkey as hotkey_module
from petatto_kanban.system import hotkey_pump as hotkey_pump_module
from petatto_kanban.system.hotkey import (
    HOTKEY_ID_NEW_CARD,
    NewCardHotkey,
    create_new_card_hotkey,
)
from petatto_kanban.system.shortcut import MOD_CONTROL, MOD_NOREPEAT, MOD_SHIFT


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


def test_new_card_hotkey_registers_and_polls() -> None:
    fired: list[str] = []
    pump = FakeHotkeyPump(queued=[HOTKEY_ID_NEW_CARD, 99])
    session = NewCardHotkey(on_new_card=lambda: fired.append("n"), pump=pump)

    session.set_shortcut("Ctrl+Shift+N")
    session.poll()
    session.close()

    assert pump.bindings == [
        (HOTKEY_ID_NEW_CARD, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, 0x4E),
    ]
    assert pump.cleared == [HOTKEY_ID_NEW_CARD]
    assert fired == ["n"]
    assert pump.closed


def test_new_card_hotkey_restores_previous_on_register_failure() -> None:
    pump = FakeHotkeyPump()
    session = NewCardHotkey(on_new_card=lambda: None, pump=pump)
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


def test_create_new_card_hotkey_uses_injected_pump() -> None:
    pump = FakeHotkeyPump()
    session = create_new_card_hotkey(lambda: None, pump=pump)
    session.set_shortcut("Alt+1")
    assert len(pump.bindings) == 1
    session.close()


def test_poll_after_close_does_not_fire() -> None:
    fired: list[str] = []
    pump = FakeHotkeyPump(queued=[HOTKEY_ID_NEW_CARD])
    session = NewCardHotkey(on_new_card=lambda: fired.append("n"), pump=pump)
    session.close()
    pump.queued = [HOTKEY_ID_NEW_CARD]
    session.poll()
    assert fired == []


def test_hotkey_session_module_is_win32_free() -> None:
    source = hotkey_module.__file__
    assert source is not None
    text = Path(source).read_text(encoding="utf-8")
    assert "ctypes" not in text
    assert "WINFUNCTYPE" not in text


def test_hotkey_pump_module_does_not_use_python_wndproc() -> None:
    source = hotkey_pump_module.__file__
    assert source is not None
    text = Path(source).read_text(encoding="utf-8")
    assert "WINFUNCTYPE" not in text
