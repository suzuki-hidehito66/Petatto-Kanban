"""設定ダイアログ UI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from tkinter import simpledialog, ttk
from typing import TYPE_CHECKING

from petatto_kanban.display.mode_labels import display_mode_from_label
from petatto_kanban.display.monitors import Monitor, monitor_index_for_name
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.display.settings_dialog_labels import SETTINGS_DIALOG_TITLE
from petatto_kanban.display.settings_dialog_panels import (
    build_display_tab,
    build_system_tab,
)
from petatto_kanban.display.settings_dialog_tabs import (
    SETTINGS_TAB_DISPLAY,
    SETTINGS_TAB_SYSTEM,
)

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import Widget


@dataclass(frozen=True)
class SettingsDialogResult:
    """設定ダイアログの確定値."""

    mode: DisplayMode
    confirm_delete: bool
    confirm_exit: bool
    monitor_index: int


@dataclass(frozen=True)
class SettingsFormValues:
    """ダイアログ確定時の入力値（テスト・apply 用）."""

    mode_label: str
    monitor_name: str
    confirm_delete: bool
    confirm_exit: bool


@dataclass(frozen=True)
class SettingsDialogInput:
    """設定ダイアログ初期値."""

    mode: DisplayMode
    confirm_delete: bool
    confirm_exit: bool
    monitor_index: int
    monitors: list[Monitor]


def result_from_form_values(
    values: SettingsFormValues,
    *,
    monitors: list[Monitor],
    default_mode: DisplayMode,
    default_monitor_index: int,
) -> SettingsDialogResult:
    """フォーム値から SettingsDialogResult を組み立てる."""
    return SettingsDialogResult(
        mode=display_mode_from_label(values.mode_label, default_mode),
        confirm_delete=values.confirm_delete,
        confirm_exit=values.confirm_exit,
        monitor_index=monitor_index_for_name(
            monitors,
            values.monitor_name,
            default_monitor_index,
        ),
    )


class SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ（UC-006）。「表示」「システム」タブ."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        dialog_input: SettingsDialogInput,
        on_delete_all_cards: Callable[[], None] | None = None,
    ) -> None:
        self._input = dialog_input
        self._on_delete_all_cards = on_delete_all_cards
        self.result: SettingsDialogResult | None = None
        super().__init__(parent, title=SETTINGS_DIALOG_TITLE)

    def body(self, master: tk.Misc) -> Widget:
        import tkinter as tk

        notebook = ttk.Notebook(master)
        notebook.pack(fill=tk.BOTH, expand=True)

        display_tab = ttk.Frame(notebook, padding=12)
        system_tab = ttk.Frame(notebook, padding=12)
        notebook.add(display_tab, text=SETTINGS_TAB_DISPLAY)
        notebook.add(system_tab, text=SETTINGS_TAB_SYSTEM)

        self._display_tab = build_display_tab(
            display_tab,
            mode=self._input.mode,
            monitor_index=self._input.monitor_index,
            monitors=self._input.monitors,
        )
        self._system_tab = build_system_tab(
            system_tab,
            confirm_delete=self._input.confirm_delete,
            confirm_exit=self._input.confirm_exit,
            on_delete_all_cards=self._on_delete_all_cards,
        )

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        return notebook

    def apply(self) -> None:
        self.result = result_from_form_values(
            SettingsFormValues(
                mode_label=self._display_tab.mode_var.get(),
                monitor_name=self._display_tab.monitor_var.get(),
                confirm_delete=self._system_tab.confirm_delete_var.get(),
                confirm_exit=self._system_tab.confirm_exit_var.get(),
            ),
            monitors=self._input.monitors,
            default_mode=self._input.mode,
            default_monitor_index=self._input.monitor_index,
        )
