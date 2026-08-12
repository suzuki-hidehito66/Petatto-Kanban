"""ディスプレイ（モニター）列挙."""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Monitor:
    """モニター情報."""

    index: int
    name: str
    x: int
    y: int
    width: int
    height: int


def _fallback_monitor() -> list[Monitor]:
    return [Monitor(index=0, name="ディスプレイ 1", x=0, y=0, width=1920, height=1080)]


def list_monitors() -> list[Monitor]:
    """接続モニター一覧を返す。非 Windows ではフォールバック 1 件。"""
    if sys.platform != "win32":
        return _fallback_monitor()

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", wintypes.LONG),
            ("top", wintypes.LONG),
            ("right", wintypes.LONG),
            ("bottom", wintypes.LONG),
        ]

    monitors: list[Monitor] = []

    def _callback(_hmonitor, _hdc, rect_ptr, _lparam):  # noqa: ANN001
        rect = rect_ptr.contents
        index = len(monitors)
        monitors.append(
            Monitor(
                index=index,
                name=f"ディスプレイ {index + 1}",
                x=rect.left,
                y=rect.top,
                width=rect.right - rect.left,
                height=rect.bottom - rect.top,
            )
        )
        return 1

    callback_type = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )
    user32.EnumDisplayMonitors(0, 0, callback_type(_callback), 0)

    return monitors or _fallback_monitor()


def get_monitor(index: int) -> Monitor:
    """インデックスでモニターを取得。範囲外は先頭にフォールバック。"""
    monitors = list_monitors()
    if 0 <= index < len(monitors):
        return monitors[index]
    return monitors[0]
