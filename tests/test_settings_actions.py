"""settings_actions のテスト."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from petatto_kanban.display.settings import DisplayMode, DisplaySettings
from petatto_kanban.display.settings_actions import (
    apply_dialog_result,
    confirm_exit,
    delete_all_cards_with_confirm,
)
from petatto_kanban.display.settings_dialog import SettingsDialogResult
from petatto_kanban.models import Board, Card
from petatto_kanban.storage import load_board


@dataclass
class FakeMessageBox:
    """messagebox 差し替え."""

    askyesno_results: list[bool] = field(default_factory=list)
    showinfo_calls: list[tuple[str, str]] = field(default_factory=list)
    askyesno_calls: list[tuple[str, str]] = field(default_factory=list)

    def showinfo(self, title: str, message: str, *, parent: Any) -> None:
        self.showinfo_calls.append((title, message))

    def askyesno(self, title: str, message: str, *, parent: Any) -> bool:
        self.askyesno_calls.append((title, message))
        if not self.askyesno_results:
            return False
        return self.askyesno_results.pop(0)


def test_apply_dialog_result_updates_settings_and_detects_changes() -> None:
    settings = DisplaySettings(
        mode=DisplayMode.OVERLAY,
        monitor_index=0,
        confirm_delete=True,
        confirm_exit=False,
    )
    result = SettingsDialogResult(
        mode=DisplayMode.DESKTOP,
        confirm_delete=False,
        confirm_exit=True,
        monitor_index=1,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.mode_changed is True
    assert changes.monitor_changed is True
    assert changes.needs_display_refresh is True
    assert settings.mode == DisplayMode.DESKTOP
    assert settings.monitor_index == 1
    assert settings.confirm_delete is False
    assert settings.confirm_exit is True


def test_apply_dialog_result_no_display_refresh_when_only_flags_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=False,
        confirm_exit=True,
        monitor_index=0,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.mode_changed is False
    assert changes.monitor_changed is False
    assert changes.needs_display_refresh is False


def test_confirm_exit_skips_dialog_when_disabled() -> None:
    messagebox = FakeMessageBox()

    assert (
        confirm_exit(
            parent=object(),
            app_title="Petatto Kanban",
            confirm_exit_enabled=False,
            messagebox=messagebox,
        )
        is True
    )
    assert messagebox.askyesno_calls == []


def test_confirm_exit_asks_when_enabled() -> None:
    messagebox = FakeMessageBox(askyesno_results=[False, True])

    assert (
        confirm_exit(
            parent=object(),
            app_title="Petatto Kanban",
            confirm_exit_enabled=True,
            messagebox=messagebox,
        )
        is False
    )
    assert (
        confirm_exit(
            parent=object(),
            app_title="Petatto Kanban",
            confirm_exit_enabled=True,
            messagebox=messagebox,
        )
        is True
    )
    assert len(messagebox.askyesno_calls) == 2


def test_delete_all_cards_with_confirm_empty_board() -> None:
    board = Board.create_default()
    messagebox = FakeMessageBox()

    assert (
        delete_all_cards_with_confirm(
            parent=object(),
            app_title="Petatto Kanban",
            board=board,
            messagebox=messagebox,
        )
        is False
    )
    assert len(messagebox.showinfo_calls) == 1
    assert messagebox.askyesno_calls == []


def test_delete_all_cards_with_confirm_cancelled() -> None:
    board = Board.create_default()
    board.cards.append(Card(title="A"))
    messagebox = FakeMessageBox(askyesno_results=[False])

    assert (
        delete_all_cards_with_confirm(
            parent=object(),
            app_title="Petatto Kanban",
            board=board,
            messagebox=messagebox,
        )
        is False
    )
    assert len(board.cards) == 1


def test_delete_all_cards_with_confirm_deletes_and_saves(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    data_path = tmp_path / "board.json"
    board = Board.create_default()
    board.cards.append(Card(title="A"))
    board.cards.append(Card(title="B"))

    import petatto_kanban.storage as storage_module

    monkeypatch.setattr(storage_module, "get_data_path", lambda: data_path)

    messagebox = FakeMessageBox(askyesno_results=[True])
    assert (
        delete_all_cards_with_confirm(
            parent=object(),
            app_title="Petatto Kanban",
            board=board,
            messagebox=messagebox,
        )
        is True
    )
    assert board.cards == []
    assert load_board(data_path).cards == []
