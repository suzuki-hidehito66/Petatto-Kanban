"""UI サイズラベルのテスト."""

from petatto_kanban.display.ui_scale import UiSize
from petatto_kanban.display.ui_scale_labels import (
    selectable_ui_size_labels,
    ui_size_from_label,
    ui_size_label,
)


def test_selectable_ui_size_labels_includes_xlarge() -> None:
    labels = selectable_ui_size_labels()
    assert labels == ["小", "標準", "大", "極大"]


def test_ui_size_labels_roundtrip() -> None:
    for ui_size in UiSize:
        label = ui_size_label(ui_size)
        assert ui_size_from_label(label, UiSize.MEDIUM) == ui_size
