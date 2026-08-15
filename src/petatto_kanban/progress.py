"""カード進捗率の値域・色."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from petatto_kanban.display.ui_theme import UiThemePalette

PROGRESS_MIN = 0
PROGRESS_MAX = 100
PROGRESS_STEP = 10
PROGRESS_LABEL_WHITE_FROM = 55


def clamp_progress(value: int) -> int:
    """進捗率を 0〜100 に収める."""
    return max(PROGRESS_MIN, min(PROGRESS_MAX, value))


def progress_color(percent: int, palette: UiThemePalette | None = None) -> str:
    """0% 付近は赤、50% 付近は黄、100% 付近は緑。明度はテーマに従う."""
    from petatto_kanban.display.ui_theme import resolved_palette

    colors = resolved_palette(palette)
    percent = clamp_progress(percent)
    if percent <= 50:
        ratio = percent / 50
        source, target = colors.progress_fill_low, colors.progress_fill_mid
    else:
        ratio = (percent - 50) / 50
        source, target = colors.progress_fill_mid, colors.progress_fill_high
    return _lerp_hex(source, target, ratio)


def progress_label_color(percent: int, palette: UiThemePalette | None = None) -> str:
    """進捗バー中央 % の文字色."""
    from petatto_kanban.display.ui_theme import resolved_palette

    colors = resolved_palette(palette)
    if _relative_luminance(colors.card_bg) < 0.25:
        return "#ffffff"
    return "#ffffff" if clamp_progress(percent) >= PROGRESS_LABEL_WHITE_FROM else colors.card_fg


def _lerp_hex(source: str, target: str, ratio: float) -> str:
    start = _hex_to_rgb(source)
    end = _hex_to_rgb(target)
    channels = tuple(
        int(start[index] + (end[index] - start[index]) * ratio) for index in range(3)
    )
    return f"#{channels[0]:02x}{channels[1]:02x}{channels[2]:02x}"


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    hex_value = value.removeprefix("#")
    return int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)


def _relative_luminance(value: str) -> float:
    red, green, blue = (_channel_to_linear(channel / 255) for channel in _hex_to_rgb(value))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _channel_to_linear(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4
