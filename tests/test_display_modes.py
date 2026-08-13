"""表示モード適用のテスト."""

import sys
import types
from unittest.mock import MagicMock, patch

# Linux CI 等 tkinter 非搭載環境向け
if "tkinter" not in sys.modules:
    _tk = types.ModuleType("tkinter")
    _tk.Tk = MagicMock
    _tk.Toplevel = MagicMock
    _tk.W = "w"
    _tk.BooleanVar = MagicMock
    _tk.StringVar = MagicMock
    sys.modules["tkinter"] = _tk
    _ttk = types.ModuleType("tkinter.ttk")
    sys.modules["tkinter.ttk"] = _ttk
    _simpledialog = types.ModuleType("tkinter.simpledialog")
    _simpledialog.Dialog = type("Dialog", (), {})
    sys.modules["tkinter.simpledialog"] = _simpledialog

from petatto_kanban.display.mode_labels import (
    display_mode_from_label,
    display_mode_label,
    selectable_display_mode_labels,
)
from petatto_kanban.display.modes import apply_display_mode
from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode

_MONITOR = Monitor(index=0, name="Test", x=0, y=0, width=1920, height=1080)


def test_display_mode_labels_for_selectable_modes() -> None:
    labels = selectable_display_mode_labels()
    assert labels == ["オーバーレイ", "デスクトップ"]
    assert display_mode_label(DisplayMode.OVERLAY) == "オーバーレイ"
    assert display_mode_from_label("デスクトップ", DisplayMode.OVERLAY) == DisplayMode.DESKTOP
    assert display_mode_from_label("不明", DisplayMode.OVERLAY) == DisplayMode.OVERLAY


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


def test_menu_panel_host_topmost_in_desktop_mode() -> None:
    root = MagicMock()
    host_window = MagicMock()
    with patch("tkinter.Toplevel", return_value=host_window, create=True):
        from petatto_kanban.display.menu_panel_host import MenuPanelHost

        host = MenuPanelHost(root)
    host.apply(_MONITOR, DisplayMode.DESKTOP)
    host_window.attributes.assert_any_call("-topmost", True)
    host_window.lift.assert_called()
    host_window.deiconify.assert_called_once()


def test_menu_panel_host_topmost_in_overlay_mode() -> None:
    root = MagicMock()
    host_window = MagicMock()
    with patch("tkinter.Toplevel", return_value=host_window, create=True):
        from petatto_kanban.display.menu_panel_host import MenuPanelHost

        host = MenuPanelHost(root)
    host.apply(_MONITOR, DisplayMode.OVERLAY)
    host_window.attributes.assert_any_call("-topmost", True)
