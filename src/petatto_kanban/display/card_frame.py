"""カード枠サイズ（幅固定・高さは内容に合わせて下限以上）.

幅は最小幅に固定する。子ウィジェットの fill=X による reqwidth 膨張は採用しない。
高さはタイトル改行・wraplength 折り返しを含む必要高さと最小高さの大きい方とし、
期限パネルと進捗バーが隠れないようにする。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CardFrameSize:
    """描画時のカード外枠サイズ（px）。"""

    width: int
    height: int


def resolve_card_frame_size(
    *,
    min_width: int,
    min_height: int,
    required_height: int,
) -> CardFrameSize:
    """幅は最小幅に固定し、高さは内容が収まるよう下限以上に伸ばす."""
    return CardFrameSize(
        width=min_width,
        height=max(min_height, required_height),
    )
