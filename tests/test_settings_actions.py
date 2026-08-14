"""settings_actions のテスト."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from petatto_kanban.display.settings import DisplayMode, DisplaySettings
from petatto_kanban.display.settings_actions import (
    apply_dialog_result,
    apply_launch_at_login,
    apply_shortcut_setting,
    confirm_exit,
    delete_all_cards_with_confirm,
    persist_dialog_result,
)
from petatto_kanban.display.settings_dialog import SettingsDialogResult
from petatto_kanban.display.ui_font import UiFont
from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_theme import UiTheme
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
        ui_size=UiSize.LARGE,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
        launch_at_login=False,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.mode_changed is True
    assert changes.monitor_changed is True
    assert changes.needs_display_refresh is True
    assert settings.mode == DisplayMode.DESKTOP
    assert settings.monitor_index == 1
    assert settings.confirm_delete is False
    assert settings.confirm_exit is True
    assert settings.ui_size == UiSize.LARGE


def test_apply_dialog_result_no_display_refresh_when_only_flags_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=False,
        confirm_exit=True,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
        launch_at_login=False,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.mode_changed is False
    assert changes.monitor_changed is False
    assert changes.ui_size_changed is False
    assert changes.needs_display_refresh is False
    assert changes.needs_ui_refresh is False


def test_apply_dialog_result_detects_ui_size_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        monitor_index=0,
        ui_size=UiSize.SMALL,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
        launch_at_login=False,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.ui_size_changed is True
    assert changes.needs_ui_refresh is True
    assert changes.needs_display_refresh is False
    assert settings.ui_size == UiSize.SMALL


def test_apply_dialog_result_detects_ui_font_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.MEIRYO,
        ui_theme=UiTheme.DEFAULT,
        launch_at_login=False,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.ui_font_changed is True
    assert changes.ui_size_changed is False
    assert changes.needs_ui_refresh is True
    assert changes.needs_display_refresh is False
    assert settings.ui_font == UiFont.MEIRYO


def test_apply_dialog_result_detects_ui_theme_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DARK,
        launch_at_login=False,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.ui_theme_changed is True
    assert changes.ui_font_changed is False
    assert changes.needs_ui_refresh is True
    assert settings.ui_theme == UiTheme.DARK


def test_apply_dialog_result_detects_launch_at_login_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        launch_at_login=True,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
    )

    changes = apply_dialog_result(settings, result)

    assert changes.launch_at_login_changed is True
    assert settings.launch_at_login is True
    assert changes.shortcut_new_card_changed is False


def test_apply_dialog_result_detects_shortcut_change() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=0)
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        launch_at_login=False,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
        shortcut_new_card="Ctrl+Shift+K",
    )

    changes = apply_dialog_result(settings, result)

    assert changes.shortcut_new_card_changed is True
    assert settings.shortcut_new_card == "Ctrl+Shift+K"


def test_apply_launch_at_login_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = DisplaySettings(launch_at_login=True)
    messagebox = FakeMessageBox()

    def raise_oserror(_enabled: bool) -> None:
        msg = "denied"
        raise OSError(msg)

    monkeypatch.setattr(
        "petatto_kanban.display.settings_actions.apply_auto_start_setting",
        raise_oserror,
    )
    assert (
        apply_launch_at_login(
            settings,
            messagebox=messagebox,
            parent=object(),
            app_title="Petatto Kanban",
        )
        is False
    )
    assert len(messagebox.showinfo_calls) == 1


def test_persist_dialog_result_saves_when_auto_start_ok(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr(
        "petatto_kanban.display.settings.get_settings_path",
        lambda: settings_path,
    )
    monkeypatch.setattr(
        "petatto_kanban.display.settings_actions.apply_auto_start_setting",
        lambda _enabled: None,
    )
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, launch_at_login=False)
    result = SettingsDialogResult(
        mode=DisplayMode.DESKTOP,
        confirm_delete=True,
        confirm_exit=False,
        launch_at_login=True,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
    )

    changes = persist_dialog_result(
        settings,
        result,
        messagebox=FakeMessageBox(),
        parent=object(),
        app_title="Petatto Kanban",
    )

    assert changes is not None
    assert changes.launch_at_login_changed is True
    assert settings.mode == DisplayMode.DESKTOP
    assert settings.launch_at_login is True
    assert settings_path.exists()


def test_persist_dialog_result_rolls_back_all_fields_on_auto_start_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr(
        "petatto_kanban.display.settings.get_settings_path",
        lambda: settings_path,
    )

    def raise_oserror(_enabled: bool) -> None:
        msg = "denied"
        raise OSError(msg)

    monkeypatch.setattr(
        "petatto_kanban.display.settings_actions.apply_auto_start_setting",
        raise_oserror,
    )
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, launch_at_login=False)
    result = SettingsDialogResult(
        mode=DisplayMode.DESKTOP,
        confirm_delete=False,
        confirm_exit=True,
        launch_at_login=True,
        monitor_index=1,
        ui_size=UiSize.LARGE,
        ui_font=UiFont.MEIRYO,
        ui_theme=UiTheme.DARK,
    )

    changes = persist_dialog_result(
        settings,
        result,
        messagebox=FakeMessageBox(),
        parent=object(),
        app_title="Petatto Kanban",
    )

    assert changes is None
    assert settings.mode == DisplayMode.OVERLAY
    assert settings.launch_at_login is False
    assert settings.confirm_delete is True
    assert settings.monitor_index == 0
    assert settings.ui_size == UiSize.MEDIUM
    assert not settings_path.exists()


def test_apply_shortcut_setting_reports_failure() -> None:
    messagebox = FakeMessageBox()

    def raise_oserror(_shortcut: str) -> None:
        msg = "busy"
        raise OSError(msg)

    assert (
        apply_shortcut_setting(
            "Ctrl+Shift+K",
            apply_shortcut=raise_oserror,
            messagebox=messagebox,
            parent=object(),
            app_title="Petatto Kanban",
        )
        is False
    )
    assert len(messagebox.showinfo_calls) == 1


def test_persist_dialog_result_saves_when_shortcut_ok(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr(
        "petatto_kanban.display.settings.get_settings_path",
        lambda: settings_path,
    )
    applied: list[str] = []
    settings = DisplaySettings()
    result = SettingsDialogResult(
        mode=DisplayMode.OVERLAY,
        confirm_delete=True,
        confirm_exit=False,
        launch_at_login=False,
        monitor_index=0,
        ui_size=UiSize.MEDIUM,
        ui_font=UiFont.SEGOE_UI,
        ui_theme=UiTheme.DEFAULT,
        shortcut_new_card="Ctrl+Shift+K",
    )

    changes = persist_dialog_result(
        settings,
        result,
        messagebox=FakeMessageBox(),
        parent=object(),
        app_title="Petatto Kanban",
        apply_shortcut=applied.append,
    )

    assert changes is not None
    assert changes.shortcut_new_card_changed is True
    assert settings.shortcut_new_card == "Ctrl+Shift+K"
    assert applied == ["Ctrl+Shift+K"]
    assert settings_path.exists()


def test_persist_dialog_result_rolls_back_on_hotkey_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings_path = tmp_path / "settings.json"
    monkeypatch.setattr(
        "petatto_kanban.display.settings.get_settings_path",
        lambda: settings_path,
    )

    def raise_oserror(_shortcut: str) -> None:
        msg = "busy"
        raise OSError(msg)

    settings = DisplaySettings(mode=DisplayMode.OVERLAY, shortcut_new_card="Ctrl+Shift+N")
    result = SettingsDialogResult(
        mode=DisplayMode.DESKTOP,
        confirm_delete=False,
        confirm_exit=True,
        launch_at_login=False,
        monitor_index=1,
        ui_size=UiSize.LARGE,
        ui_font=UiFont.MEIRYO,
        ui_theme=UiTheme.DARK,
        shortcut_new_card="Ctrl+Shift+K",
    )

    changes = persist_dialog_result(
        settings,
        result,
        messagebox=FakeMessageBox(),
        parent=object(),
        app_title="Petatto Kanban",
        apply_shortcut=raise_oserror,
    )

    assert changes is None
    assert settings.mode == DisplayMode.OVERLAY
    assert settings.shortcut_new_card == "Ctrl+Shift+N"
    assert settings.confirm_delete is True
    assert not settings_path.exists()


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
