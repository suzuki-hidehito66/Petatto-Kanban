"""UI カラーテーマ（FR-028）のテスト."""

from datetime import date

from petatto_kanban.display.ui_theme import (
    UiTheme,
    palette_for_theme,
    parse_ui_theme,
    resolved_palette,
)
from petatto_kanban.display.ui_theme_labels import (
    selectable_ui_theme_labels,
    ui_theme_from_label,
    ui_theme_label,
)
from petatto_kanban.display.ui_theme_palettes import PALETTES
from petatto_kanban.due_date import due_date_panel_style


def test_parse_ui_theme_defaults_to_default() -> None:
    assert parse_ui_theme(None) == UiTheme.DEFAULT
    assert parse_ui_theme("invalid") == UiTheme.DEFAULT


def test_resolved_palette_defaults_to_default() -> None:
    assert resolved_palette(None) == palette_for_theme(UiTheme.DEFAULT)
    assert set(PALETTES) == set(UiTheme)


def test_parse_ui_theme_accepts_presets() -> None:
    assert parse_ui_theme("dark") == UiTheme.DARK
    assert parse_ui_theme("midnight") == UiTheme.MIDNIGHT


def test_ui_theme_labels_roundtrip() -> None:
    for ui_theme in UiTheme:
        label = ui_theme_label(ui_theme)
        assert ui_theme_from_label(label, UiTheme.DEFAULT) == ui_theme


def test_selectable_ui_theme_labels_count() -> None:
    labels = selectable_ui_theme_labels()
    assert len(labels) == 10
    assert labels[0] == "Default"
    assert "ダーク" in labels


def test_dark_palette_has_light_text_on_dark_card() -> None:
    palette = palette_for_theme(UiTheme.DARK)
    assert palette.card_bg == "#1a1a1a"
    assert palette.card_fg == "#f2f2f2"


def test_due_date_panel_style_uses_theme_today_and_overdue() -> None:
    palette = palette_for_theme(UiTheme.DARK)
    today = date(2026, 8, 12)
    overdue_bg, overdue_fg = due_date_panel_style(
        date(2026, 8, 11), today, palette=palette
    )
    today_bg, today_fg = due_date_panel_style(date(2026, 8, 12), today, palette=palette)
    future_bg, future_fg = due_date_panel_style(date(2026, 8, 20), today, palette=palette)

    assert overdue_bg == palette.due_overdue_bg
    assert overdue_fg == palette.due_overdue_fg
    assert today_bg == palette.due_today_bg
    assert today_fg == palette.due_today_fg
    assert overdue_bg != today_bg
    assert future_bg == palette.due_future_bg
    assert future_fg == palette.due_future_fg


def test_light_and_dark_due_colors_keep_yellow_and_red_hues() -> None:
    light = palette_for_theme(UiTheme.DEFAULT)
    dark = palette_for_theme(UiTheme.FOREST)
    assert light.due_today_bg == "#fff9c4"
    assert light.due_overdue_bg == "#ffcdd2"
    assert dark.due_today_bg == "#5c4d1a"
    assert dark.due_overdue_bg == "#5c2a2a"


def test_default_palette_matches_legacy_card_colors() -> None:
    palette = palette_for_theme(UiTheme.DEFAULT)
    assert palette.card_bg == "#fffef8"
    assert palette.card_fg == "#222222"


def test_all_palettes_define_calendar_day_hover() -> None:
    for ui_theme in UiTheme:
        palette = palette_for_theme(ui_theme)
        assert palette.due_picker_day_hover_bg != palette.due_picker_bg
        assert palette.due_picker_day_hover_bg.startswith("#")
        assert palette.due_picker_day_hover_fg.startswith("#")


def test_all_palettes_define_progress_fill() -> None:
    for ui_theme in UiTheme:
        palette = palette_for_theme(ui_theme)
        assert palette.progress_fill_low != palette.progress_fill_mid
        assert palette.progress_fill_mid != palette.progress_fill_high
        assert palette.progress_fill_low != palette.progress_track_bg


def test_all_palettes_define_today_and_calendar_tokens() -> None:
    for ui_theme in UiTheme:
        palette = palette_for_theme(ui_theme)
        assert palette.due_today_bg != palette.due_overdue_bg
        assert palette.calendar_today_bg != palette.calendar_today_hover_bg
        assert palette.calendar_today_bg != palette.due_picker_bg
        assert palette.calendar_today_hover_bg != palette.due_picker_day_hover_bg


def test_forest_ocean_sunset_midnight_are_dark_with_light_text() -> None:
    expected = {
        UiTheme.FOREST: ("#1a2e1f", "#e8f5e9"),
        UiTheme.OCEAN: ("#0d2133", "#e3f2fd"),
        UiTheme.SUNSET: ("#2a1a18", "#ffe8e0"),
        UiTheme.MIDNIGHT: ("#12161f", "#f0f2f8"),
    }
    for ui_theme, (card_bg, card_fg) in expected.items():
        palette = palette_for_theme(ui_theme)
        assert palette.card_bg == card_bg
        assert palette.card_fg == card_fg
        assert palette.calendar_today_bg == {
            UiTheme.FOREST: "#2e7d32",
            UiTheme.OCEAN: "#0277bd",
            UiTheme.SUNSET: "#e64a19",
            UiTheme.MIDNIGHT: "#3949ab",
        }[ui_theme]
