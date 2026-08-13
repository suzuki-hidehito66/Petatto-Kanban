"""設定ダイアログ UI."""

from __future__ import annotations

from dataclasses import dataclass
from tkinter import simpledialog, ttk
from typing import TYPE_CHECKING

from petatto_kanban.display.mode_labels import (
    display_mode_from_label,
    display_mode_label,
    selectable_display_mode_labels,
)
from petatto_kanban.display.monitors import Monitor, monitor_index_for_name
from petatto_kanban.display.settings import DisplayMode
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
    monitor_index: int


@dataclass(frozen=True)
class SettingsFormValues:
    """ダイアログ確定時の入力値（テスト・apply 用）."""

    mode_label: str
    monitor_name: str
    confirm_delete: bool


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
        mode: DisplayMode,
        confirm_delete: bool,
        monitor_index: int,
        monitors: list[Monitor],
    ) -> None:
        self._mode = mode
        self._confirm_delete = confirm_delete
        self._monitor_index = monitor_index
        self._monitors = monitors
        self.result: SettingsDialogResult | None = None
        super().__init__(parent, title="設定")

    def body(self, master: tk.Misc) -> Widget:
        import tkinter as tk

        self._notebook = ttk.Notebook(master)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        display_tab = ttk.Frame(self._notebook, padding=12)
        system_tab = ttk.Frame(self._notebook, padding=12)
        self._notebook.add(display_tab, text=SETTINGS_TAB_DISPLAY)
        self._notebook.add(system_tab, text=SETTINGS_TAB_SYSTEM)

        self._build_display_tab(display_tab)
        self._build_system_tab(system_tab)

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        return self._notebook

    def _build_display_tab(self, parent: tk.Misc) -> None:
        import tkinter as tk

        ttk.Label(parent, text="表示モード").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        self.mode_var = tk.StringVar(value=display_mode_label(self._mode))
        self.mode_menu = ttk.Combobox(
            parent,
            textvariable=self.mode_var,
            values=selectable_display_mode_labels(),
            state="readonly",
            width=28,
        )
        self.mode_menu.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        ttk.Label(parent, text="表示ディスプレイ").grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
        monitor_names = [monitor.name for monitor in self._monitors]
        default_name = monitor_names[min(self._monitor_index, len(monitor_names) - 1)]
        self.monitor_var = tk.StringVar(value=default_name)
        self.monitor_menu = ttk.Combobox(
            parent,
            textvariable=self.monitor_var,
            values=monitor_names,
            state="readonly",
            width=28,
        )
        self.monitor_menu.grid(row=3, column=0, sticky=tk.EW)
        parent.columnconfigure(0, weight=1)

    def _build_system_tab(self, parent: tk.Misc) -> None:
        import tkinter as tk

        self.confirm_var = tk.BooleanVar(value=self._confirm_delete)
        ttk.Checkbutton(
            parent,
            text="カード削除時に確認ダイアログを表示する",
            variable=self.confirm_var,
        ).grid(row=0, column=0, sticky=tk.W)
        parent.columnconfigure(0, weight=1)

    def apply(self) -> None:
        self.result = result_from_form_values(
            SettingsFormValues(
                mode_label=self.mode_var.get(),
                monitor_name=self.monitor_var.get(),
                confirm_delete=self.confirm_var.get(),
            ),
            monitors=self._monitors,
            default_mode=self._mode,
            default_monitor_index=self._monitor_index,
        )
