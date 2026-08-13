"""表示設定のテスト."""

from pathlib import Path

from petatto_kanban.display.monitors import Monitor, monitor_index_for_name
from petatto_kanban.display.settings import (
    DisplayMode,
    DisplaySettings,
    display_settings_from_dict,
    display_settings_to_dict,
    load_display_settings,
    save_display_settings,
)


def test_default_display_settings_is_overlay_mode() -> None:
    settings = DisplaySettings()
    assert settings.mode == DisplayMode.OVERLAY
    assert settings.confirm_delete is True


def test_save_and_load_display_settings(tmp_path: Path) -> None:
    settings = DisplaySettings(
        mode=DisplayMode.OVERLAY,
        monitor_index=1,
        confirm_delete=False,
    )
    path = tmp_path / "settings.json"
    save_display_settings(settings, path)

    loaded = load_display_settings(path)
    assert loaded.mode == DisplayMode.OVERLAY
    assert loaded.monitor_index == 1
    assert loaded.confirm_delete is False


def test_save_and_load_desktop_mode(tmp_path: Path) -> None:
    settings = DisplaySettings(mode=DisplayMode.DESKTOP, monitor_index=0)
    path = tmp_path / "settings.json"
    save_display_settings(settings, path)

    loaded = load_display_settings(path)
    assert loaded.mode == DisplayMode.DESKTOP


def test_invalid_mode_falls_back_to_overlay() -> None:
    restored = display_settings_from_dict({"mode": "unknown"})
    assert restored.mode == DisplayMode.OVERLAY


def test_display_settings_roundtrip_dict() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=2, confirm_delete=False)
    restored = display_settings_from_dict(display_settings_to_dict(settings))
    assert restored.mode == DisplayMode.OVERLAY
    assert restored.monitor_index == 2
    assert restored.confirm_delete is False


def test_display_settings_menu_panel_position_roundtrip() -> None:
    settings = DisplaySettings(menu_panel_x=100, menu_panel_y=200)
    restored = display_settings_from_dict(display_settings_to_dict(settings))
    assert restored.menu_panel_x == 100
    assert restored.menu_panel_y == 200


def test_display_settings_omits_unset_menu_panel_position() -> None:
    data = display_settings_to_dict(DisplaySettings())
    assert "menu_panel_x" not in data
    assert "menu_panel_y" not in data


def test_monitor_index_for_name() -> None:
    monitors = [
        Monitor(index=0, name="ディスプレイ 1", x=0, y=0, width=1920, height=1080),
        Monitor(index=1, name="ディスプレイ 2", x=1920, y=0, width=1920, height=1080),
    ]
    assert monitor_index_for_name(monitors, "ディスプレイ 2", default=0) == 1
    assert monitor_index_for_name(monitors, "不明", default=0) == 0
