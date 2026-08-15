"""カード進捗率の値域."""

from __future__ import annotations

PROGRESS_MIN = 0
PROGRESS_MAX = 100
PROGRESS_STEP = 10


def clamp_progress(value: int) -> int:
    """進捗率を 0〜100 に収める."""
    return max(PROGRESS_MIN, min(PROGRESS_MAX, value))
