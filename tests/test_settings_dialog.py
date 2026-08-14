"""設定ダイアログのテスト."""

from petatto_kanban.display.mode_labels import display_mode_label
from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode, DisplaySettings
from petatto_kanban.display.settings_dialog import (
    SettingsFormValues,
    dialog_input_from_settings,
    result_from_form_values,
)
from petatto_kanban.display.settings_dialog_tabs import (
    ACTIONS_TAB_FIELDS,
    DISPLAY_TAB_FIELDS,
    SETTINGS_TAB_ACTIONS,
    SETTINGS_TAB_DISPLAY,
    SETTINGS_TAB_SYSTEM,
    SETTINGS_TAB_THEME,
    SYSTEM_TAB_ACTIONS,
    SYSTEM_TAB_FIELDS,
    THEME_TAB_FIELDS,
)
from petatto_kanban.display.ui_font import UiFont
from petatto_kanban.display.ui_font_labels import ui_font_label
from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_scale_labels import ui_size_label
from petatto_kanban.display.ui_theme import UiTheme
from petatto_kanban.display.ui_theme_labels import ui_theme_label
from petatto_kanban.system.shortcut import DEFAULT_NEW_CARD_SHORTCUT

_MONITORS = [
    Monitor(index=0, name="ディスプレイ 1", x=0, y=0, width=1920, height=1080),
    Monitor(index=1, name="ディスプレイ 2", x=1920, y=0, width=1920, height=1080),
]


def test_settings_tab_labels_and_field_groups() -> None:
    assert SETTINGS_TAB_DISPLAY == "表示"
    assert SETTINGS_TAB_THEME == "テーマ"
    assert SETTINGS_TAB_ACTIONS == "操作"
    assert SETTINGS_TAB_SYSTEM == "システム"
    assert DISPLAY_TAB_FIELDS == ("mode", "monitor_index", "ui_size", "ui_font")
    assert THEME_TAB_FIELDS == ("ui_theme",)
    assert ACTIONS_TAB_FIELDS == ("shortcut_new_card",)
    assert SYSTEM_TAB_FIELDS == ("confirm_delete", "confirm_exit", "launch_at_login")
    assert SYSTEM_TAB_ACTIONS == ("delete_all_cards",)


def test_result_from_form_values_display_tab() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label="デスクトップ",
            monitor_name="ディスプレイ 2",
            ui_size_label=ui_size_label(UiSize.MEDIUM),
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.mode == DisplayMode.DESKTOP
    assert result.monitor_index == 1
    assert result.confirm_delete is True
    assert result.confirm_exit is False


def test_result_from_form_values_ui_size() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label="大",
            ui_font_label=ui_font_label(UiFont.MEIRYO),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.ui_size == UiSize.LARGE
    assert result.ui_font == UiFont.MEIRYO


def test_result_from_form_values_ui_size_xlarge() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label="極大",
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.ui_size == UiSize.XLARGE


def test_result_from_form_values_ui_theme() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label=ui_size_label(UiSize.MEDIUM),
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label="ダーク",
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.ui_theme == UiTheme.DARK


def test_result_from_form_values_system_tab_only_change() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label="大",
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=False,
            confirm_exit=True,
            launch_at_login=True,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.mode == DisplayMode.OVERLAY
    assert result.monitor_index == 0
    assert result.confirm_delete is False
    assert result.confirm_exit is True
    assert result.launch_at_login is True
    assert result.shortcut_new_card == DEFAULT_NEW_CARD_SHORTCUT


def test_result_from_form_values_shortcut_new_card() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label=ui_size_label(UiSize.MEDIUM),
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
            shortcut_new_card="ctrl+shift+k",
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.shortcut_new_card == "Ctrl+Shift+K"


def test_result_from_form_values_invalid_shortcut_falls_back() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label=ui_size_label(UiSize.MEDIUM),
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            ui_theme_label=ui_theme_label(UiTheme.DEFAULT),
            confirm_delete=True,
            confirm_exit=False,
            launch_at_login=False,
            shortcut_new_card="N",
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
        default_ui_theme=UiTheme.DEFAULT,
    )
    assert result.shortcut_new_card == DEFAULT_NEW_CARD_SHORTCUT


def test_dialog_input_from_settings_copies_display_fields() -> None:
    settings = DisplaySettings(
        mode=DisplayMode.DESKTOP,
        confirm_delete=False,
        confirm_exit=True,
        launch_at_login=True,
        monitor_index=1,
        shortcut_new_card="Ctrl+Shift+K",
    )
    dialog_input = dialog_input_from_settings(settings, _MONITORS)
    assert dialog_input.mode == DisplayMode.DESKTOP
    assert dialog_input.confirm_delete is False
    assert dialog_input.confirm_exit is True
    assert dialog_input.launch_at_login is True
    assert dialog_input.monitor_index == 1
    assert dialog_input.shortcut_new_card == "Ctrl+Shift+K"
    assert dialog_input.monitors == _MONITORS
