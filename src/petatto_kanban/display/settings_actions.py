"""設定ダイアログ確定値の適用とシステム操作."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING, Protocol

from petatto_kanban.display.settings import save_display_settings
from petatto_kanban.display.settings_dialog import SettingsDialogResult
from petatto_kanban.display.settings_dialog_labels import (
    MSG_AUTO_START_FAILED,
    MSG_CONFIRM_DELETE_ALL,
    MSG_CONFIRM_EXIT,
    MSG_HOTKEY_FAILED,
    MSG_NO_CARDS_TO_DELETE,
)
from petatto_kanban.storage import save_board
from petatto_kanban.system.auto_start import apply_auto_start_setting
from petatto_kanban.system.shortcut import normalize_shortcut

if TYPE_CHECKING:
    import tkinter as tk

    from petatto_kanban.display.settings import DisplaySettings
    from petatto_kanban.models import Board


class MessageBoxHost(Protocol):
    """messagebox 呼び出しのテスト差し替え用."""

    def showinfo(self, title: str, message: str, *, parent: tk.Misc) -> None: ...

    def askyesno(self, title: str, message: str, *, parent: tk.Misc) -> bool: ...


@dataclass(frozen=True)
class SettingsApplyChanges:
    """設定適用後に表示モード再配置が必要か."""

    mode_changed: bool
    monitor_changed: bool
    ui_size_changed: bool
    ui_font_changed: bool
    ui_theme_changed: bool
    launch_at_login_changed: bool
    shortcut_new_card_changed: bool

    @property
    def needs_display_refresh(self) -> bool:
        return self.mode_changed or self.monitor_changed

    @property
    def needs_ui_refresh(self) -> bool:
        return self.ui_size_changed or self.ui_font_changed or self.ui_theme_changed


def apply_dialog_result(
    display_settings: DisplaySettings,
    result: SettingsDialogResult,
) -> SettingsApplyChanges:
    """ダイアログ結果を DisplaySettings に反映する（未保存）。"""
    shortcut = normalize_shortcut(result.shortcut_new_card)
    changes = SettingsApplyChanges(
        mode_changed=result.mode != display_settings.mode,
        monitor_changed=result.monitor_index != display_settings.monitor_index,
        ui_size_changed=result.ui_size != display_settings.ui_size,
        ui_font_changed=result.ui_font != display_settings.ui_font,
        ui_theme_changed=result.ui_theme != display_settings.ui_theme,
        launch_at_login_changed=result.launch_at_login != display_settings.launch_at_login,
        shortcut_new_card_changed=shortcut != display_settings.shortcut_new_card,
    )
    display_settings.mode = result.mode
    display_settings.confirm_delete = result.confirm_delete
    display_settings.confirm_exit = result.confirm_exit
    display_settings.launch_at_login = result.launch_at_login
    display_settings.monitor_index = result.monitor_index
    display_settings.ui_size = result.ui_size
    display_settings.ui_font = result.ui_font
    display_settings.ui_theme = result.ui_theme
    display_settings.shortcut_new_card = shortcut
    return changes


def persist_dialog_result(
    display_settings: DisplaySettings,
    result: SettingsDialogResult,
    *,
    messagebox: MessageBoxHost,
    parent: tk.Misc,
    app_title: str,
    apply_shortcut: Callable[[str], None] | None = None,
) -> SettingsApplyChanges | None:
    """ダイアログ結果を OS 反映してから settings.json に保存する.

    自動起動またはホットキーの反映に失敗した場合はメモリ上の設定を全項目ロールバックし、
    ファイルは更新しない。
    """
    snapshot = replace(display_settings)
    changes = apply_dialog_result(display_settings, result)
    restores: list[Callable[[], bool]] = []
    if changes.shortcut_new_card_changed:
        if not apply_shortcut_setting(
            display_settings.shortcut_new_card,
            apply_shortcut=apply_shortcut,
            messagebox=messagebox,
            parent=parent,
            app_title=app_title,
        ):
            _restore_display_settings(display_settings, snapshot)
            return None
        restores.append(
            lambda: apply_shortcut_setting(
                snapshot.shortcut_new_card,
                apply_shortcut=apply_shortcut,
                messagebox=messagebox,
                parent=parent,
                app_title=app_title,
            )
        )
    if changes.launch_at_login_changed and not apply_launch_at_login(
        display_settings,
        messagebox=messagebox,
        parent=parent,
        app_title=app_title,
    ):
        _restore_display_settings(display_settings, snapshot)
        for restore in reversed(restores):
            restore()
        return None
    save_display_settings(display_settings)
    return changes


def apply_shortcut_setting(
    shortcut: str,
    *,
    apply_shortcut: Callable[[str], None] | None,
    messagebox: MessageBoxHost,
    parent: tk.Misc,
    app_title: str,
) -> bool:
    """ショートカットを OS に反映。失敗時はダイアログを表示し False。"""
    if apply_shortcut is None:
        return True
    try:
        apply_shortcut(shortcut)
    except (OSError, RuntimeError) as error:
        messagebox.showinfo(
            app_title,
            MSG_HOTKEY_FAILED.format(error=error),
            parent=parent,
        )
        return False
    return True


def apply_launch_at_login(
    display_settings: DisplaySettings,
    *,
    messagebox: MessageBoxHost,
    parent: tk.Misc,
    app_title: str,
) -> bool:
    """launch_at_login を OS に反映。失敗時はダイアログを表示し False。"""
    try:
        apply_auto_start_setting(display_settings.launch_at_login)
    except (OSError, RuntimeError) as error:
        messagebox.showinfo(
            app_title,
            MSG_AUTO_START_FAILED.format(error=error),
            parent=parent,
        )
        return False
    return True


def _restore_display_settings(target: DisplaySettings, snapshot: DisplaySettings) -> None:
    for field in fields(target):
        setattr(target, field.name, getattr(snapshot, field.name))


def confirm_exit(
    *,
    parent: tk.Misc,
    app_title: str,
    confirm_exit_enabled: bool,
    messagebox: MessageBoxHost,
) -> bool:
    """終了確認が有効ならダイアログを表示。続行可能なら True。"""
    if not confirm_exit_enabled:
        return True
    return messagebox.askyesno(app_title, MSG_CONFIRM_EXIT, parent=parent)


def delete_all_cards_with_confirm(
    *,
    parent: tk.Misc,
    app_title: str,
    board: Board,
    messagebox: MessageBoxHost,
) -> bool:
    """確認後に全カードを削除して保存。実行したら True。"""
    count = len(board.cards)
    if count == 0:
        messagebox.showinfo(app_title, MSG_NO_CARDS_TO_DELETE, parent=parent)
        return False

    if not messagebox.askyesno(
        app_title,
        MSG_CONFIRM_DELETE_ALL.format(count=count),
        parent=parent,
    ):
        return False

    board.clear_cards()
    save_board(board)
    return True
