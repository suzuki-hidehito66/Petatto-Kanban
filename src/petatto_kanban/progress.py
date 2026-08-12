"""カード進捗率の値域・色."""

from __future__ import annotations

PROGRESS_MIN = 0
PROGRESS_MAX = 100
PROGRESS_STEP = 10

_PROGRESS_RED = (220, 60, 60)
_PROGRESS_YELLOW = (240, 200, 40)
_PROGRESS_GREEN = (60, 180, 80)


def clamp_progress(value: int) -> int:
    """進捗率を 0〜100 に収める."""
    return max(PROGRESS_MIN, min(PROGRESS_MAX, value))


def progress_color(percent: int) -> str:
    """0% 付近は赤、50% 付近は黄、100% 付近は緑になる色を返す."""
    percent = clamp_progress(percent)
    if percent <= 50:
        ratio = percent / 50
        source, target = _PROGRESS_RED, _PROGRESS_YELLOW
    else:
        ratio = (percent - 50) / 50
        source, target = _PROGRESS_YELLOW, _PROGRESS_GREEN
    channels = tuple(
        int(source[index] + (target[index] - source[index]) * ratio) for index in range(3)
    )
    return f"#{channels[0]:02x}{channels[1]:02x}{channels[2]:02x}"
