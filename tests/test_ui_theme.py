"""UI カラーテーマ（FR-028）のテスト."""

from datetime import date

from petatto_kanban.display.ui_theme import (
    UiTheme,
    palette_for_theme,
    parse_ui_theme,
)
from petatto_kanban.display.ui_theme_labels import (
    selectable_ui_theme_labels,
    ui_theme_from_label,
    ui_theme_label,
)
from petatto_kanban.due_date import (
    DUE_PANEL_OVERDUE_BG,
    DUE_PANEL_TODAY_BG,
    due_date_panel_style,
)


def test_parse_ui_theme_defaults_to_default() -> None:
    assert parse_ui_theme(None) == UiTheme.DEFAULT
    assert parse_ui_theme("invalid") == UiTheme.DEFAULT


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


def test_due_date_panel_style_keeps_semantic_colors_with_palette() -> None:
    palette = palette_for_theme(UiTheme.DARK)
    today = date(2026, 8, 12)
    overdue_bg, _ = due_date_panel_style(date(2026, 8, 11), today, palette=palette)
    today_bg, _ = due_date_panel_style(date(2026, 8, 12), today, palette=palette)
    future_bg, future_fg = due_date_panel_style(date(2026, 8, 20), today, palette=palette)

    assert overdue_bg == DUE_PANEL_OVERDUE_BG
    assert today_bg == DUE_PANEL_TODAY_BG
    assert future_bg == palette.due_future_bg
    assert future_fg == palette.due_future_fg


def test_default_palette_matches_legacy_card_colors() -> None:
    from petatto_kanban.display.ui_theme import UiTheme, palette_for_theme

    palette = palette_for_theme(UiTheme.DEFAULT)
    assert palette.card_bg == "#fffef8"
    assert palette.card_fg == "#222222"
