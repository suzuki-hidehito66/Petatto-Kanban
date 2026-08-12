"""表示設定のテスト."""

from pathlib import Path

from petatto_kanban.display.settings import (
    DisplayMode,
    DisplaySettings,
    display_settings_from_dict,
    display_settings_to_dict,
    load_display_settings,
    save_display_settings,
)


def test_default_display_settings_is_desktop_mode() -> None:
    settings = DisplaySettings()
    assert settings.mode == DisplayMode.DESKTOP
    assert settings.monitor_index == 0


def test_save_and_load_display_settings(tmp_path: Path) -> None:
    settings = DisplaySettings(mode=DisplayMode.DESKTOP, monitor_index=1)
    path = tmp_path / "settings.json"
    save_display_settings(settings, path)

    loaded = load_display_settings(path)
    assert loaded.mode == DisplayMode.DESKTOP
    assert loaded.monitor_index == 1


def test_display_settings_roundtrip_dict() -> None:
    settings = DisplaySettings(mode=DisplayMode.DESKTOP, monitor_index=2)
    restored = display_settings_from_dict(display_settings_to_dict(settings))
    assert restored.mode == DisplayMode.DESKTOP
    assert restored.monitor_index == 2
