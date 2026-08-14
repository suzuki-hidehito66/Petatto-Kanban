"""カードレイアウト基準寸法のテスト."""

from petatto_kanban.display.card_layout import (
    CARD_LAYOUT_BASELINE,
    GOLDEN_RATIO,
    resolve_card_frame_size,
    scale_card_layout,
)


def test_card_layout_baseline_golden_ratio_at_medium() -> None:
    baseline = CARD_LAYOUT_BASELINE
    assert baseline.min_width == 175
    assert baseline.min_height == 108
    assert baseline.label_wrap == 155
    assert baseline.placement_width == 177
    assert baseline.placement_height == 110
    ratio = baseline.min_width / baseline.min_height
    assert abs(ratio - GOLDEN_RATIO) < 0.01


def test_scale_card_layout_applies_ui_size_scale() -> None:
    scaled = scale_card_layout(CARD_LAYOUT_BASELINE, 1.25)
    assert scaled.min_width == 219
    assert scaled.min_height == 135
    assert scaled.frame_border == 1


def test_resolve_card_frame_size_keeps_min_when_content_fits() -> None:
    width, height = resolve_card_frame_size(
        min_width=175,
        min_height=108,
        required_height=100,
    )
    assert width == 175
    assert height == 108


def test_resolve_card_frame_size_grows_height_only_for_wrapped_title() -> None:
    width, height = resolve_card_frame_size(
        min_width=175,
        min_height=108,
        required_height=160,
    )
    assert width == 175
    assert height == 160
