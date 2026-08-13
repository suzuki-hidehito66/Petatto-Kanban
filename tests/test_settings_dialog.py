"""設定ダイアログのテスト."""

from petatto_kanban.display.mode_labels import display_mode_label
from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.display.settings_dialog import (
    SettingsFormValues,
    result_from_form_values,
)
from petatto_kanban.display.settings_dialog_tabs import (
    DISPLAY_TAB_FIELDS,
    SETTINGS_TAB_DISPLAY,
    SETTINGS_TAB_SYSTEM,
    SYSTEM_TAB_ACTIONS,
    SYSTEM_TAB_FIELDS,
)
from petatto_kanban.display.ui_font import UiFont
from petatto_kanban.display.ui_font_labels import ui_font_label
from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_scale_labels import ui_size_label

_MONITORS = [
    Monitor(index=0, name="ディスプレイ 1", x=0, y=0, width=1920, height=1080),
    Monitor(index=1, name="ディスプレイ 2", x=1920, y=0, width=1920, height=1080),
]


def test_settings_tab_labels_and_field_groups() -> None:
    assert SETTINGS_TAB_DISPLAY == "表示"
    assert SETTINGS_TAB_SYSTEM == "システム"
    assert DISPLAY_TAB_FIELDS == ("mode", "monitor_index", "ui_size", "ui_font")
    assert SYSTEM_TAB_FIELDS == ("confirm_delete", "confirm_exit")
    assert SYSTEM_TAB_ACTIONS == ("delete_all_cards",)


def test_result_from_form_values_display_tab() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label="デスクトップ",
            monitor_name="ディスプレイ 2",
            ui_size_label=ui_size_label(UiSize.MEDIUM),
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            confirm_delete=True,
            confirm_exit=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
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
            confirm_delete=True,
            confirm_exit=False,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
    )
    assert result.ui_size == UiSize.LARGE
    assert result.ui_font == UiFont.MEIRYO


def test_result_from_form_values_system_tab_only_change() -> None:
    result = result_from_form_values(
        SettingsFormValues(
            mode_label=display_mode_label(DisplayMode.OVERLAY),
            monitor_name="ディスプレイ 1",
            ui_size_label="大",
            ui_font_label=ui_font_label(UiFont.SEGOE_UI),
            confirm_delete=False,
            confirm_exit=True,
        ),
        monitors=_MONITORS,
        default_mode=DisplayMode.OVERLAY,
        default_monitor_index=0,
        default_ui_size=UiSize.MEDIUM,
        default_ui_font=UiFont.SEGOE_UI,
    )
    assert result.mode == DisplayMode.OVERLAY
    assert result.monitor_index == 0
    assert result.confirm_delete is False
    assert result.confirm_exit is True
