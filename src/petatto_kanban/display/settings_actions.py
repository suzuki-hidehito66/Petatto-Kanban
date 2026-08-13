"""設定ダイアログ確定値の適用とシステム操作."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from petatto_kanban.display.settings_dialog import SettingsDialogResult
from petatto_kanban.display.settings_dialog_labels import (
    MSG_CONFIRM_DELETE_ALL,
    MSG_CONFIRM_EXIT,
    MSG_NO_CARDS_TO_DELETE,
)
from petatto_kanban.storage import save_board

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

    @property
    def needs_display_refresh(self) -> bool:
        return self.mode_changed or self.monitor_changed

    @property
    def needs_ui_refresh(self) -> bool:
        return self.ui_size_changed


def apply_dialog_result(
    display_settings: DisplaySettings,
    result: SettingsDialogResult,
) -> SettingsApplyChanges:
    """ダイアログ結果を DisplaySettings に反映する（未保存）。"""
    changes = SettingsApplyChanges(
        mode_changed=result.mode != display_settings.mode,
        monitor_changed=result.monitor_index != display_settings.monitor_index,
        ui_size_changed=result.ui_size != display_settings.ui_size,
    )
    display_settings.mode = result.mode
    display_settings.confirm_delete = result.confirm_delete
    display_settings.confirm_exit = result.confirm_exit
    display_settings.monitor_index = result.monitor_index
    display_settings.ui_size = result.ui_size
    return changes


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
