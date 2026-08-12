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


def test_display_settings_roundtrip_dict() -> None:
    settings = DisplaySettings(mode=DisplayMode.OVERLAY, monitor_index=2, confirm_delete=False)
    restored = display_settings_from_dict(display_settings_to_dict(settings))
    assert restored.mode == DisplayMode.OVERLAY
    assert restored.monitor_index == 2
    assert restored.confirm_delete is False
