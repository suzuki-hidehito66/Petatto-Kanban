"""表示モード適用のテスト."""

import sys
import types
from unittest.mock import MagicMock, patch

# Linux CI 等 tkinter 非搭載環境向け
if "tkinter" not in sys.modules:
    _tk = types.ModuleType("tkinter")
    _tk.Tk = MagicMock
    _tk.W = "w"
    sys.modules["tkinter"] = _tk
    sys.modules["tkinter.ttk"] = types.ModuleType("tkinter.ttk")

from petatto_kanban.display.modes import apply_display_mode
from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode

_MONITOR = Monitor(index=0, name="Test", x=0, y=0, width=1920, height=1080)


def test_apply_display_mode_uses_overlay() -> None:
    root = MagicMock()
    with patch("petatto_kanban.display.overlay.apply_overlay_mode") as overlay:
        apply_display_mode(root, _MONITOR, DisplayMode.OVERLAY)
    overlay.assert_called_once_with(root, _MONITOR)


def test_apply_display_mode_uses_desktop() -> None:
    root = MagicMock()
    with patch("petatto_kanban.display.desktop.apply_desktop_mode") as desktop:
        apply_display_mode(root, _MONITOR, DisplayMode.DESKTOP)
    desktop.assert_called_once_with(root, _MONITOR)


def test_apply_display_mode_window_falls_back_to_overlay() -> None:
    root = MagicMock()
    with patch("petatto_kanban.display.overlay.apply_overlay_mode") as overlay:
        apply_display_mode(root, _MONITOR, DisplayMode.WINDOW)
    overlay.assert_called_once_with(root, _MONITOR)
