"""設定ダイアログ各タブのウィジェット構築."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from petatto_kanban.display.mode_labels import (
    display_mode_label,
    selectable_display_mode_labels,
)
from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.display.settings_dialog_labels import (
    BUTTON_DELETE_ALL_CARDS,
    CHECK_CONFIRM_DELETE,
    CHECK_CONFIRM_EXIT,
    COMBOBOX_WIDTH,
    LABEL_DISPLAY_MODE,
    LABEL_DISPLAY_MONITOR,
    LABEL_UI_FONT,
    LABEL_UI_SIZE,
    LABEL_UI_THEME,
)
from petatto_kanban.display.ui_font import UiFont
from petatto_kanban.display.ui_font_labels import (
    selectable_ui_font_labels,
    ui_font_label,
)
from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_scale_labels import (
    selectable_ui_size_labels,
    ui_size_label,
)
from petatto_kanban.display.ui_theme import UiTheme
from petatto_kanban.display.ui_theme_labels import (
    selectable_ui_theme_labels,
    ui_theme_label,
)

if TYPE_CHECKING:
    import tkinter as tk
    from collections.abc import Callable


@dataclass
class DisplayTabState:
    """表示タブの入力状態."""

    mode_var: tk.StringVar
    monitor_var: tk.StringVar
    ui_size_var: tk.StringVar
    ui_font_var: tk.StringVar


@dataclass
class SystemTabState:
    """システムタブの入力状態."""

    confirm_delete_var: tk.BooleanVar
    confirm_exit_var: tk.BooleanVar


@dataclass
class ThemeTabState:
    """テーマタブの入力状態."""

    ui_theme_var: tk.StringVar


def build_display_tab(
    parent: tk.Misc,
    *,
    mode: DisplayMode,
    monitor_index: int,
    ui_size: UiSize,
    ui_font: UiFont,
    monitors: list[Monitor],
) -> DisplayTabState:
    """表示タブ（モード・ディスプレイ）を構築する."""
    import tkinter as tk
    from tkinter import ttk

    ttk.Label(parent, text=LABEL_DISPLAY_MODE).grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
    mode_var = tk.StringVar(value=display_mode_label(mode))
    ttk.Combobox(
        parent,
        textvariable=mode_var,
        values=selectable_display_mode_labels(),
        state="readonly",
        width=COMBOBOX_WIDTH,
    ).grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

    ttk.Label(parent, text=LABEL_DISPLAY_MONITOR).grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
    monitor_names = [monitor.name for monitor in monitors]
    default_name = monitor_names[min(monitor_index, len(monitor_names) - 1)]
    monitor_var = tk.StringVar(value=default_name)
    ttk.Combobox(
        parent,
        textvariable=monitor_var,
        values=monitor_names,
        state="readonly",
        width=COMBOBOX_WIDTH,
    ).grid(row=3, column=0, sticky=tk.EW, pady=(0, 12))

    ttk.Label(parent, text=LABEL_UI_SIZE).grid(row=4, column=0, sticky=tk.W, pady=(0, 4))
    ui_size_var = tk.StringVar(value=ui_size_label(ui_size))
    ttk.Combobox(
        parent,
        textvariable=ui_size_var,
        values=selectable_ui_size_labels(),
        state="readonly",
        width=COMBOBOX_WIDTH,
    ).grid(row=5, column=0, sticky=tk.EW, pady=(0, 12))

    ttk.Label(parent, text=LABEL_UI_FONT).grid(row=6, column=0, sticky=tk.W, pady=(0, 4))
    ui_font_var = tk.StringVar(value=ui_font_label(ui_font))
    ttk.Combobox(
        parent,
        textvariable=ui_font_var,
        values=selectable_ui_font_labels(),
        state="readonly",
        width=COMBOBOX_WIDTH,
    ).grid(row=7, column=0, sticky=tk.EW)
    parent.columnconfigure(0, weight=1)
    return DisplayTabState(
        mode_var=mode_var,
        monitor_var=monitor_var,
        ui_size_var=ui_size_var,
        ui_font_var=ui_font_var,
    )


def build_theme_tab(
    parent: tk.Misc,
    *,
    ui_theme: UiTheme,
) -> ThemeTabState:
    """テーマタブ（カラーテーマ）を構築する."""
    import tkinter as tk
    from tkinter import ttk

    ttk.Label(parent, text=LABEL_UI_THEME).grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
    ui_theme_var = tk.StringVar(value=ui_theme_label(ui_theme))
    ttk.Combobox(
        parent,
        textvariable=ui_theme_var,
        values=selectable_ui_theme_labels(),
        state="readonly",
        width=COMBOBOX_WIDTH,
    ).grid(row=1, column=0, sticky=tk.EW)
    parent.columnconfigure(0, weight=1)
    return ThemeTabState(ui_theme_var=ui_theme_var)


def build_system_tab(
    parent: tk.Misc,
    *,
    confirm_delete: bool,
    confirm_exit: bool,
    on_delete_all_cards: Callable[[], None] | None,
) -> SystemTabState:
    """システムタブ（確認オプション・一括削除）を構築する."""
    import tkinter as tk
    from tkinter import ttk

    confirm_delete_var = tk.BooleanVar(value=confirm_delete)
    ttk.Checkbutton(
        parent,
        text=CHECK_CONFIRM_DELETE,
        variable=confirm_delete_var,
    ).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

    confirm_exit_var = tk.BooleanVar(value=confirm_exit)
    ttk.Checkbutton(
        parent,
        text=CHECK_CONFIRM_EXIT,
        variable=confirm_exit_var,
    ).grid(row=1, column=0, sticky=tk.W, pady=(0, 8))

    if on_delete_all_cards is not None:
        ttk.Button(
            parent,
            text=BUTTON_DELETE_ALL_CARDS,
            command=on_delete_all_cards,
        ).grid(row=2, column=0, sticky=tk.W, pady=(8, 0))

    parent.columnconfigure(0, weight=1)
    return SystemTabState(
        confirm_delete_var=confirm_delete_var,
        confirm_exit_var=confirm_exit_var,
    )
