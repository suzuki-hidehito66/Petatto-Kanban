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
    build_actions_tab,
    build_display_tab,
    build_system_tab,
    build_theme_tab,
)
from petatto_kanban.display.settings_dialog_tabs import (
    SETTINGS_TAB_ACTIONS,
    SETTINGS_TAB_DISPLAY,
    SETTINGS_TAB_SYSTEM,
    SETTINGS_TAB_THEME,
)
from petatto_kanban.display.ui_font import UiFont
from petatto_kanban.display.ui_font_labels import ui_font_from_label
from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_scale_labels import ui_size_from_label
from petatto_kanban.display.ui_theme import UiTheme
from petatto_kanban.display.ui_theme_labels import ui_theme_from_label
from petatto_kanban.system.auto_start import is_auto_start_supported
from petatto_kanban.system.hotkey import (
    DEFAULT_NEW_CARD_SHORTCUT,
    chord_from_tk_key,
    normalize_shortcut,
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
    launch_at_login: bool
    monitor_index: int
    ui_size: UiSize
    ui_font: UiFont
    ui_theme: UiTheme
    shortcut_new_card: str = DEFAULT_NEW_CARD_SHORTCUT


@dataclass(frozen=True)
class SettingsFormValues:
    """ダイアログ確定時の入力値（テスト・apply 用）."""

    mode_label: str
    monitor_name: str
    ui_size_label: str
    ui_font_label: str
    ui_theme_label: str
    confirm_delete: bool
    confirm_exit: bool
    launch_at_login: bool
    shortcut_new_card: str = DEFAULT_NEW_CARD_SHORTCUT


@dataclass(frozen=True)
class SettingsDialogInput:
    """設定ダイアログ初期値."""

    mode: DisplayMode
    confirm_delete: bool
    confirm_exit: bool
    launch_at_login: bool
    monitor_index: int
    ui_size: UiSize
    ui_font: UiFont
    ui_theme: UiTheme
    monitors: list[Monitor]
    shortcut_new_card: str = DEFAULT_NEW_CARD_SHORTCUT


def result_from_form_values(
    values: SettingsFormValues,
    *,
    monitors: list[Monitor],
    default_mode: DisplayMode,
    default_monitor_index: int,
    default_ui_size: UiSize,
    default_ui_font: UiFont,
    default_ui_theme: UiTheme,
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
        ui_size=ui_size_from_label(values.ui_size_label, default_ui_size),
        ui_font=ui_font_from_label(values.ui_font_label, default_ui_font),
        ui_theme=ui_theme_from_label(values.ui_theme_label, default_ui_theme),
        launch_at_login=values.launch_at_login,
        shortcut_new_card=normalize_shortcut(values.shortcut_new_card),
    )


class SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ（UC-006）。「表示」「テーマ」「操作」「システム」タブ."""

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
        theme_tab = ttk.Frame(notebook, padding=12)
        actions_tab = ttk.Frame(notebook, padding=12)
        system_tab = ttk.Frame(notebook, padding=12)
        notebook.add(display_tab, text=SETTINGS_TAB_DISPLAY)
        notebook.add(theme_tab, text=SETTINGS_TAB_THEME)
        notebook.add(actions_tab, text=SETTINGS_TAB_ACTIONS)
        notebook.add(system_tab, text=SETTINGS_TAB_SYSTEM)

        self._display_tab = build_display_tab(
            display_tab,
            mode=self._input.mode,
            monitor_index=self._input.monitor_index,
            ui_size=self._input.ui_size,
            ui_font=self._input.ui_font,
            monitors=self._input.monitors,
        )
        self._theme_tab = build_theme_tab(
            theme_tab,
            ui_theme=self._input.ui_theme,
        )
        self._actions_tab = build_actions_tab(
            actions_tab,
            shortcut_new_card=self._input.shortcut_new_card,
            on_change=self._begin_shortcut_capture,
            on_reset=self._reset_shortcut,
        )
        self._system_tab = build_system_tab(
            system_tab,
            confirm_delete=self._input.confirm_delete,
            confirm_exit=self._input.confirm_exit,
            launch_at_login=self._input.launch_at_login,
            auto_start_supported=is_auto_start_supported(),
            on_delete_all_cards=self._on_delete_all_cards,
        )
        self.bind("<KeyPress>", self._on_shortcut_capture_key)

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        return notebook

    def _begin_shortcut_capture(self) -> None:
        self._actions_tab.start_capture()
        self.focus_set()

    def _reset_shortcut(self) -> None:
        self._actions_tab.reset_to_default()

    def _on_shortcut_capture_key(self, event: tk.Event) -> str | None:
        if not self._actions_tab.capturing:
            return None
        if event.keysym == "Escape":
            return None
        chord = chord_from_tk_key(event.keysym, event.state)
        if chord is None:
            return "break"
        self._actions_tab.commit_capture(chord.format())
        return "break"

    def ok(self, event: tk.Event | None = None) -> None:
        if getattr(self, "_actions_tab", None) is not None and self._actions_tab.capturing:
            return
        super().ok(event)

    def cancel(self, event: tk.Event | None = None) -> None:
        if getattr(self, "_actions_tab", None) is not None and self._actions_tab.capturing:
            self._actions_tab.cancel_capture()
            return
        super().cancel(event)

    def apply(self) -> None:
        self._actions_tab.cancel_capture()
        self.result = result_from_form_values(
            SettingsFormValues(
                mode_label=self._display_tab.mode_var.get(),
                monitor_name=self._display_tab.monitor_var.get(),
                ui_size_label=self._display_tab.ui_size_var.get(),
                ui_font_label=self._display_tab.ui_font_var.get(),
                ui_theme_label=self._theme_tab.ui_theme_var.get(),
                confirm_delete=self._system_tab.confirm_delete_var.get(),
                confirm_exit=self._system_tab.confirm_exit_var.get(),
                launch_at_login=self._system_tab.launch_at_login_var.get(),
                shortcut_new_card=self._actions_tab.shortcut_new_card_var.get(),
            ),
            monitors=self._input.monitors,
            default_mode=self._input.mode,
            default_monitor_index=self._input.monitor_index,
            default_ui_size=self._input.ui_size,
            default_ui_font=self._input.ui_font,
            default_ui_theme=self._input.ui_theme,
        )
