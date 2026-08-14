"""表示モード適用のテスト."""

import sys
import types
from collections.abc import Iterator
from contextlib import contextmanager
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

from petatto_kanban.display.desktop_board_controller import DesktopBoardController
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


def test_bring_board_to_front_sets_topmost_on_windows() -> None:
    root = MagicMock()
    with patch("petatto_kanban.display.desktop.is_windows", return_value=True):
        from petatto_kanban.display.desktop import bring_board_to_front

        bring_board_to_front(root)
    root.attributes.assert_called_with("-topmost", True)
    root.lift.assert_called_once()


def test_restore_desktop_board_z_order_clears_topmost_on_windows() -> None:
    root = MagicMock()
    with (
        patch("petatto_kanban.display.desktop.is_windows", return_value=True),
        patch("petatto_kanban.display.desktop.send_window_to_back") as send_back,
    ):
        from petatto_kanban.display.desktop import restore_desktop_board_z_order

        restore_desktop_board_z_order(root)
    root.attributes.assert_called_with("-topmost", False)
    send_back.assert_called_once_with(root)


def test_desktop_board_controller_activate_and_restore() -> None:
    root = MagicMock()
    menu_host = MagicMock()
    is_desktop = MagicMock(return_value=True)
    can_lower = MagicMock(return_value=True)

    with (
        patch("petatto_kanban.display.desktop_board_controller.bring_board_to_front") as bring,
        patch(
            "petatto_kanban.display.desktop_board_controller.restore_desktop_board_z_order"
        ) as restore,
    ):
        controller = DesktopBoardController(
            root,
            menu_host,
            is_desktop_mode=is_desktop,
            can_lower=can_lower,
        )
        controller.activate_from_menu()
        assert controller.is_elevated is True
        bring.assert_called_once_with(root)
        menu_host.lift.assert_called()

        controller.on_display_mode_applied(desktop=False)
        assert controller.is_elevated is False

        controller.on_display_mode_applied(desktop=True)
        controller.activate_from_menu()
        with patch(
            "petatto_kanban.display.desktop_board_controller.is_foreign_app_foreground",
            return_value=True,
        ):
            controller.lower_on_foreign_app_active()
        restore.assert_called_once_with(root)


@contextmanager
def _elevated_controller(
    *,
    pointer_press: bool = False,
    foreign_foreground: bool = False,
) -> Iterator[tuple[DesktopBoardController, MagicMock]]:
    root = MagicMock()
    with (
        patch("petatto_kanban.display.desktop_board_controller.bring_board_to_front"),
        patch(
            "petatto_kanban.display.desktop_board_controller.restore_desktop_board_z_order"
        ) as restore,
        patch(
            "petatto_kanban.display.desktop_board_controller.is_foreign_app_foreground",
            return_value=foreign_foreground,
        ),
        patch(
            "petatto_kanban.display.desktop_board_controller.is_foreign_pointer_press",
            return_value=pointer_press,
        ),
    ):
        controller = DesktopBoardController(
            root,
            MagicMock(),
            is_desktop_mode=MagicMock(return_value=True),
            can_lower=MagicMock(return_value=True),
        )
        controller.activate_from_menu()
        restore.reset_mock()
        yield controller, restore


def test_desktop_board_controller_lowers_on_foreign_mouse_press_not_release() -> None:
    with _elevated_controller(pointer_press=True) as (controller, restore):
        controller.lower_on_foreign_pointer_press()
    restore.assert_called_once()
    assert controller.is_elevated is False


def test_desktop_board_controller_does_not_lower_without_foreign_pointer_press() -> None:
    with _elevated_controller() as (controller, restore):
        controller.lower_on_foreign_pointer_press()
    restore.assert_not_called()
    assert controller.is_elevated is True


def test_foreign_app_poll_lowers_on_foreign_mouse_press() -> None:
    with _elevated_controller(pointer_press=True) as (controller, restore):
        controller._on_foreign_app_poll()
    restore.assert_called_once()
    assert controller.is_elevated is False
