"""進捗率ユーティリティのテスト."""

from petatto_kanban.display.ui_theme import UiTheme, palette_for_theme
from petatto_kanban.progress import (
    PROGRESS_MAX,
    PROGRESS_MIN,
    clamp_progress,
)
from petatto_kanban.progress_fill import progress_color, progress_label_color


def test_clamp_progress_bounds() -> None:
    assert clamp_progress(-20) == PROGRESS_MIN
    assert clamp_progress(0) == 0
    assert clamp_progress(50) == 50
    assert clamp_progress(120) == PROGRESS_MAX


def test_progress_color_endpoints_use_default_palette() -> None:
    palette = palette_for_theme(UiTheme.DEFAULT)
    assert progress_color(0).lower() == palette.progress_fill_low
    assert progress_color(50).lower() == palette.progress_fill_mid
    assert progress_color(100).lower() == palette.progress_fill_high
    assert progress_color(0).lower() == "#dc3c3c"
    assert progress_color(50).lower() == "#f0c828"
    assert progress_color(100).lower() == "#3cb450"


def test_progress_color_follows_theme() -> None:
    light = palette_for_theme(UiTheme.DEFAULT)
    dark = palette_for_theme(UiTheme.DARK)
    assert progress_color(0, dark) == dark.progress_fill_low
    assert progress_color(50, dark) == dark.progress_fill_mid
    assert progress_color(100, dark) == dark.progress_fill_high
    assert dark.progress_fill_low != light.progress_fill_low
    assert dark.progress_fill_mid != light.progress_fill_mid
    assert dark.progress_fill_high != light.progress_fill_high


def test_dark_themes_share_muted_progress_fills() -> None:
    forest = palette_for_theme(UiTheme.FOREST)
    midnight = palette_for_theme(UiTheme.MIDNIGHT)
    assert forest.progress_fill_low == midnight.progress_fill_low == "#c45c5c"
    assert forest.progress_fill_mid == "#c9a63a"
    assert forest.progress_fill_high == "#4aa862"


def test_progress_label_color_light_theme_uses_threshold() -> None:
    palette = palette_for_theme(UiTheme.DEFAULT)
    assert progress_label_color(0, palette) == palette.card_fg
    assert progress_label_color(54, palette) == palette.card_fg
    assert progress_label_color(55, palette) == "#ffffff"


def test_progress_label_color_dark_theme_is_always_white() -> None:
    palette = palette_for_theme(UiTheme.DARK)
    assert progress_label_color(0, palette) == "#ffffff"
    assert progress_label_color(100, palette) == "#ffffff"
