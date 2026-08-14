"""カード枠サイズ決定のテスト."""

from petatto_kanban.display.card_frame import resolve_card_frame_size


def test_resolve_card_frame_size_keeps_min_when_content_fits() -> None:
    size = resolve_card_frame_size(
        min_width=175,
        min_height=108,
        required_height=100,
    )
    assert size.width == 175
    assert size.height == 108


def test_resolve_card_frame_size_grows_height_only_for_wrapped_title() -> None:
    size = resolve_card_frame_size(
        min_width=175,
        min_height=108,
        required_height=160,
    )
    assert size.width == 175
    assert size.height == 160
