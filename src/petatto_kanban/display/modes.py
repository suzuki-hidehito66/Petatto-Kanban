"""表示モード適用のエントリポイント."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode

if TYPE_CHECKING:
    import tkinter as tk


def apply_display_mode(root: tk.Tk, monitor: Monitor, mode: DisplayMode) -> None:
    """settings.mode に応じて全画面表示モードを適用する."""
    apply_fn = _MODE_APPLIERS.get(mode, _apply_overlay)
    apply_fn(root, monitor)


def _apply_overlay(root: tk.Tk, monitor: Monitor) -> None:
    from petatto_kanban.display.overlay import apply_overlay_mode

    apply_overlay_mode(root, monitor)


def _apply_desktop(root: tk.Tk, monitor: Monitor) -> None:
    from petatto_kanban.display.desktop import apply_desktop_mode

    apply_desktop_mode(root, monitor)


_MODE_APPLIERS: dict[DisplayMode, Callable[[tk.Tk, Monitor], None]] = {
    DisplayMode.OVERLAY: _apply_overlay,
    DisplayMode.DESKTOP: _apply_desktop,
    DisplayMode.WINDOW: _apply_overlay,  # M2 未実装: 暫定フォールバック
}
