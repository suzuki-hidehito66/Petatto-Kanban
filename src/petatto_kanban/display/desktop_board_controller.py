"""デスクトップモードの本体 Z オーダー制御（DM-DESKTOP-02 / DM-DESKTOP-03）."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from petatto_kanban.display.desktop import (
    bring_board_to_front,
    restore_desktop_board_z_order,
)
from petatto_kanban.display.foreground import is_foreign_app_foreground

if TYPE_CHECKING:
    import tkinter as tk

    from petatto_kanban.display.menu_panel_host import MenuPanelHost

BOARD_LOWER_DELAY_MS = 1500
FOREGROUND_POLL_MS = 300


class DesktopBoardController:
    """メニューアクティブ時の昇格と、非アクティブ・他アプリ時の背面復帰."""

    def __init__(
        self,
        root: tk.Tk,
        menu_host: MenuPanelHost,
        *,
        is_desktop_mode: Callable[[], bool],
        can_lower: Callable[[], bool],
    ) -> None:
        self._root = root
        self._menu_host = menu_host
        self._is_desktop_mode = is_desktop_mode
        self._can_lower = can_lower
        self._lower_after_id: str | None = None
        self._foreground_poll_after_id: str | None = None
        self._elevated = False

    @property
    def is_elevated(self) -> bool:
        return self._elevated

    def on_display_mode_applied(self, *, desktop: bool) -> None:
        """表示モード適用直後に呼ぶ（タイマー停止・状態リセット）."""
        self.stop()
        self._elevated = False
        if desktop:
            self.start_foreground_watch()

    def stop(self) -> None:
        """ポーリングと降格タイマーを停止する."""
        self._cancel_lower()
        self._stop_foreground_watch()

    def bind_focus_handlers(self, *widgets: tk.Misc) -> None:
        """他アプリアクティブ検知用 FocusOut を登録する."""
        for widget in widgets:
            widget.bind(
                "<FocusOut>",
                lambda _event: self._root.after_idle(self.lower_on_foreign_app_active),
                add="+",
            )

    def activate_from_menu(self) -> None:
        """DM-DESKTOP-02: メニュー操作で本体を一時最前面へ."""
        if not self._is_desktop_mode():
            return
        self._cancel_lower()
        bring_board_to_front(self._root)
        self._elevated = True
        self._menu_host.lift()

    def on_menu_deactivate(self) -> None:
        """メニュー非アクティブ後、一定時間で背面復帰を予約."""
        self.schedule_lower()

    def on_card_pointer_enter(self) -> None:
        """カードへポインタ移動中は降格を延期."""
        self._cancel_lower()

    def schedule_lower(self) -> None:
        if not self._is_desktop_mode():
            return
        self._cancel_lower()
        self._lower_after_id = self._root.after(
            BOARD_LOWER_DELAY_MS,
            self._lower_if_idle,
        )

    def lower_on_foreign_app_active(self) -> None:
        """DM-DESKTOP-03: 他アプリ前面時は待機なしで背面復帰."""
        if not self._is_desktop_mode():
            return
        if not is_foreign_app_foreground():
            return
        self._cancel_lower()
        if not self._can_lower() or not self._elevated:
            return
        self._restore_z_order()

    def start_foreground_watch(self) -> None:
        if not self._is_desktop_mode():
            return
        self._stop_foreground_watch()
        self._schedule_foreground_poll()

    def _restore_z_order(self) -> None:
        if not self._is_desktop_mode():
            return
        restore_desktop_board_z_order(self._root)
        self._elevated = False
        self._menu_host.lift()

    def _lower_if_idle(self) -> None:
        self._lower_after_id = None
        if not self._can_lower():
            self.schedule_lower()
            return
        if not self._is_desktop_mode():
            return
        self._restore_z_order()

    def _cancel_lower(self) -> None:
        if self._lower_after_id is not None:
            self._root.after_cancel(self._lower_after_id)
            self._lower_after_id = None

    def _stop_foreground_watch(self) -> None:
        if self._foreground_poll_after_id is not None:
            self._root.after_cancel(self._foreground_poll_after_id)
            self._foreground_poll_after_id = None

    def _schedule_foreground_poll(self) -> None:
        self._foreground_poll_after_id = self._root.after(
            FOREGROUND_POLL_MS,
            self._on_foreground_poll,
        )

    def _on_foreground_poll(self) -> None:
        self._foreground_poll_after_id = None
        if not self._is_desktop_mode():
            return
        self.lower_on_foreign_app_active()
        self._schedule_foreground_poll()
