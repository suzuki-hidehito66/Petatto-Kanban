"""UI スケール（FR-026）のテスト."""

from petatto_kanban.display.ui_metrics import medium_metrics, metrics_for_ui_size
from petatto_kanban.display.ui_scale import (
    BASE_CARD_MIN_HEIGHT,
    BASE_CARD_MIN_WIDTH,
    BASE_MENU_CIRCLE_SIZE,
    GOLDEN_RATIO,
    UiSize,
    parse_ui_size,
)


def test_parse_ui_size_defaults_to_medium() -> None:
    assert parse_ui_size(None) == UiSize.MEDIUM
    assert parse_ui_size("invalid") == UiSize.MEDIUM


def test_parse_ui_size_accepts_presets() -> None:
    assert parse_ui_size("small") == UiSize.SMALL
    assert parse_ui_size("large") == UiSize.LARGE


def test_medium_metrics_matches_baseline() -> None:
    metrics = medium_metrics()
    assert metrics.ui_size == UiSize.MEDIUM
    assert metrics.scale == 1.0
    assert metrics.card_min_width == BASE_CARD_MIN_WIDTH
    assert metrics.card_min_height == BASE_CARD_MIN_HEIGHT
    assert metrics.menu_circle_size == BASE_MENU_CIRCLE_SIZE


def test_card_min_dimensions_are_landscape_with_comfortable_height() -> None:
    assert BASE_CARD_MIN_WIDTH > BASE_CARD_MIN_HEIGHT
    assert BASE_CARD_MIN_HEIGHT >= 100
    golden_height = round(BASE_CARD_MIN_WIDTH / GOLDEN_RATIO)
    assert golden_height < BASE_CARD_MIN_HEIGHT


def test_card_label_metrics_match_card_width_baseline() -> None:
    from petatto_kanban.display.ui_scale import (
        BASE_CARD_FRAME_PAD,
        BASE_DUE_FONT_SIZE,
        BASE_PROGRESS_BAR_HEIGHT,
        BASE_PROGRESS_FONT_SIZE,
        BASE_TITLE_FONT_SIZE,
    )

    metrics = medium_metrics()
    assert metrics.title_font[1] == BASE_TITLE_FONT_SIZE == 8
    assert metrics.due_font[1] == BASE_DUE_FONT_SIZE == 8
    assert metrics.progress_font[1] == BASE_PROGRESS_FONT_SIZE == 8
    assert metrics.progress_bar_height == BASE_PROGRESS_BAR_HEIGHT == 11
    assert metrics.card_frame_pad == BASE_CARD_FRAME_PAD == 5


def test_large_metrics_scales_up() -> None:
    medium = medium_metrics()
    large = metrics_for_ui_size(UiSize.LARGE)
    assert large.card_min_width > medium.card_min_width
    assert large.menu_circle_size > medium.menu_circle_size
    assert large.title_font[1] >= medium.title_font[1]


def test_small_metrics_scales_down_but_font_has_minimum() -> None:
    small = metrics_for_ui_size(UiSize.SMALL)
    assert small.title_font[1] >= 8
