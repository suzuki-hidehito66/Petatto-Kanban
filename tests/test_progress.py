"""進捗率ユーティリティのテスト."""

from petatto_kanban.progress import (
    PROGRESS_MAX,
    PROGRESS_MIN,
    clamp_progress,
    progress_color,
)


def test_clamp_progress_bounds() -> None:
    assert clamp_progress(-20) == PROGRESS_MIN
    assert clamp_progress(0) == 0
    assert clamp_progress(50) == 50
    assert clamp_progress(120) == PROGRESS_MAX


def test_progress_color_endpoints() -> None:
    assert progress_color(0).lower() == "#dc3c3c"
    assert progress_color(50).lower() == "#f0c828"
    assert progress_color(100).lower() == "#3cb450"
