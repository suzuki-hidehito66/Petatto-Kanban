"""デスクトップモードでメニューパネルを最前面に維持する透過ホスト."""

from __future__ import annotations

from typing import TYPE_CHECKING

from petatto_kanban.display.monitors import Monitor
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.display.transparent import (
    apply_fullscreen_transparent_shell,
    configure_windows_transparency,
    is_windows,
)

if TYPE_CHECKING:
    import tkinter as tk


class MenuPanelHost:
    """メニューパネル専用の透過トップレベル（デスクトップ時は常に最前面）."""

    def __init__(self, root: tk.Tk) -> None:
        import tkinter as tk

        self.root = root
        self.window = tk.Toplevel(root)
        self.window.withdraw()

    def apply(self, monitor: Monitor, mode: DisplayMode) -> None:
        """表示モードに応じてホストウィンドウの geometry / Z オーダーを更新する."""
        apply_fullscreen_transparent_shell(self.window, monitor)

        if is_windows():
            configure_windows_transparency(self.window)

        # デスクトップ: ルート背面でもメニューのみ最前面。オーバーレイ: カードより前面。
        if mode in (DisplayMode.DESKTOP, DisplayMode.OVERLAY, DisplayMode.WINDOW):
            self.window.attributes("-topmost", True)
            self.window.lift()
        self.window.deiconify()

    def lift(self) -> None:
        """メニューパネルを他 UI より前面に出す."""
        self.window.lift()
