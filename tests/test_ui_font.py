"""UI フォント（FR-027）のテスト."""

from petatto_kanban.display.ui_font import (
    UiFont,
    parse_ui_font,
    resolve_font_family,
    tkinter_family_name,
)
from petatto_kanban.display.ui_font_labels import (
    selectable_ui_font_labels,
    ui_font_from_label,
    ui_font_label,
)
from petatto_kanban.display.ui_metrics import metrics_for_display
from petatto_kanban.display.ui_scale import UiSize


def test_parse_ui_font_defaults_to_segoe_ui() -> None:
    assert parse_ui_font(None) == UiFont.SEGOE_UI
    assert parse_ui_font("invalid") == UiFont.SEGOE_UI


def test_parse_ui_font_accepts_presets() -> None:
    assert parse_ui_font("meiryo") == UiFont.MEIRYO
    assert parse_ui_font("ms_gothic") == UiFont.MS_GOTHIC


def test_tkinter_family_name() -> None:
    assert tkinter_family_name(UiFont.SEGOE_UI) == "Segoe UI"
    assert tkinter_family_name(UiFont.MEIRYO) == "Meiryo"
    assert tkinter_family_name(UiFont.YU_GOTHIC_UI) == "Yu Gothic UI"
    assert tkinter_family_name(UiFont.MS_GOTHIC) == "MS Gothic"


def test_ui_font_labels_roundtrip() -> None:
    for ui_font in UiFont:
        label = ui_font_label(ui_font)
        assert ui_font_from_label(label, UiFont.SEGOE_UI) == ui_font


def test_selectable_ui_font_labels() -> None:
    labels = selectable_ui_font_labels()
    assert labels == ["Segoe UI", "メイリオ", "游ゴシック", "MS ゴシック"]


def test_resolve_font_family_uses_requested_when_available() -> None:
    families = frozenset({"Meiryo", "Segoe UI"})
    assert resolve_font_family("Meiryo", available_families=families) == "Meiryo"


def test_resolve_font_family_falls_back_to_segoe_ui() -> None:
    families = frozenset({"Segoe UI"})
    assert resolve_font_family("Meiryo", available_families=families) == "Segoe UI"


def test_resolve_font_family_returns_requested_when_no_families() -> None:
    assert resolve_font_family("Meiryo", available_families=frozenset()) == "Meiryo"


def test_metrics_for_display_applies_font_family() -> None:
    metrics = metrics_for_display(
        UiSize.MEDIUM,
        UiFont.MEIRYO,
        available_families=frozenset({"Meiryo"}),
    )
    assert metrics.ui_font == UiFont.MEIRYO
    assert metrics.font_family == "Meiryo"
    assert metrics.title_font[0] == "Meiryo"
