"""メニューパネル・期限パネルホストの再構築（UI サイズ・テーマ変更対応）."""

from __future__ import annotations

from typing import TYPE_CHECKING

from petatto_kanban.display.ui_metrics import UiMetrics
from petatto_kanban.due_date_picker import DueDatePickerHost
from petatto_kanban.menu_panel import MenuPanel

if TYPE_CHECKING:
    import tkinter as tk
    from collections.abc import Callable

    from petatto_kanban.display.monitors import Monitor
    from petatto_kanban.display.ui_theme import UiThemePalette


class UiChrome:
    """スケール・テーマ変更時に再構築が必要な UI 部品を管理する."""

    def __init__(
        self,
        root: tk.Misc,
        menu_parent: tk.Misc,
        *,
        metrics: UiMetrics,
        palette: UiThemePalette,
        on_close: Callable[[], None],
        on_settings: Callable[[], None],
        on_add_card: Callable[[], None],
        on_menu_position_changed: Callable[[int, int], None],
        on_menu_activate: Callable[[], None],
        on_menu_deactivate: Callable[[], None],
        on_due_picker_outside_click: Callable[[], None],
    ) -> None:
        self._root = root
        self._menu_parent = menu_parent
        self._metrics = metrics
        self._palette = palette
        self._menu_callbacks = (
            on_close,
            on_settings,
            on_add_card,
            on_menu_position_changed,
            on_menu_activate,
            on_menu_deactivate,
        )
        self._on_due_picker_outside_click = on_due_picker_outside_click
        self.due_date_picker = self._create_due_date_picker()
        self.menu_panel = self._create_menu_panel()

    @property
    def metrics(self) -> UiMetrics:
        return self._metrics

    @property
    def palette(self) -> UiThemePalette:
        return self._palette

    def apply_appearance(self, metrics: UiMetrics, palette: UiThemePalette) -> None:
        """UI サイズ・テーマ変更後にメトリクスとパレットを更新し、部品を再構築する."""
        saved_position = self.menu_panel.position
        self.due_date_picker.close()
        self.menu_panel.widget.destroy()
        self._metrics = metrics
        self._palette = palette
        self.due_date_picker = self._create_due_date_picker()
        self.menu_panel = self._create_menu_panel()
        self.menu_panel.place_at(*saved_position)

    def apply_metrics(self, metrics: UiMetrics) -> None:
        """後方互換。パレットは維持して apply_appearance を呼ぶ."""
        self.apply_appearance(metrics, self._palette)

    def clamp_menu_to_monitor(self, monitor: Monitor) -> None:
        self.menu_panel.clamp_to_monitor(monitor.width, monitor.height)

    def _create_due_date_picker(self) -> DueDatePickerHost:
        palette = self._palette
        return DueDatePickerHost(
            self._root,
            bg=palette.due_picker_bg,
            fg=palette.due_picker_fg,
            panel_width=self._metrics.due_picker_panel_width,
            month_font=self._metrics.due_picker_month_font,
            weekday_font=self._metrics.due_picker_day_font,
            on_outside_click=self._on_due_picker_outside_click,
        )

    def _create_menu_panel(self) -> MenuPanel:
        (
            on_close,
            on_settings,
            on_add_card,
            on_position_changed,
            on_activate,
            on_deactivate,
        ) = self._menu_callbacks
        return MenuPanel(
            self._menu_parent,
            on_close=on_close,
            on_settings=on_settings,
            on_add_card=on_add_card,
            on_position_changed=on_position_changed,
            on_activate=on_activate,
            on_deactivate=on_deactivate,
            metrics=self._metrics,
            palette=self._palette,
        )
