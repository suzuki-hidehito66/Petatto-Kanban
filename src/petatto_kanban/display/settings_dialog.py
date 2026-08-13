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

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import Widget


@dataclass(frozen=True)
class SettingsDialogResult:
    """設定ダイアログの確定値."""

    mode: DisplayMode
    confirm_delete: bool
    monitor_index: int


class SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ（UC-006）."""

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

        ttk.Label(master, text="表示モード").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        self.mode_var = tk.StringVar(value=display_mode_label(self._mode))
        self.mode_menu = ttk.Combobox(
            master,
            textvariable=self.mode_var,
            values=selectable_display_mode_labels(),
            state="readonly",
            width=28,
        )
        self.mode_menu.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        ttk.Label(master, text="表示ディスプレイ").grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
        monitor_names = [monitor.name for monitor in self._monitors]
        default_name = monitor_names[min(self._monitor_index, len(monitor_names) - 1)]
        self.monitor_var = tk.StringVar(value=default_name)
        self.monitor_menu = ttk.Combobox(
            master,
            textvariable=self.monitor_var,
            values=monitor_names,
            state="readonly",
            width=28,
        )
        self.monitor_menu.grid(row=3, column=0, sticky=tk.EW, pady=(0, 12))

        self.confirm_var = tk.BooleanVar(value=self._confirm_delete)
        ttk.Checkbutton(
            master,
            text="カード削除時に確認ダイアログを表示する",
            variable=self.confirm_var,
        ).grid(row=4, column=0, sticky=tk.W)
        master.columnconfigure(0, weight=1)
        return self.mode_menu

    def apply(self) -> None:
        self.result = SettingsDialogResult(
            mode=display_mode_from_label(self.mode_var.get(), self._mode),
            confirm_delete=self.confirm_var.get(),
            monitor_index=monitor_index_for_name(
                self._monitors,
                self.monitor_var.get(),
                self._monitor_index,
            ),
        )
