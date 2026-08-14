"""Tkinter ベースの GUI アプリケーション（オーバーレイ / デスクトップモード）."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import date
from tkinter import messagebox, ttk

from petatto_kanban.card_renderer import CardRenderer
from petatto_kanban.card_ui import (
    CardUiRefs,
    ClickReleaseTracker,
    double_click_interval_ms,
)
from petatto_kanban.display import (
    list_monitors,
    load_display_settings,
    save_display_settings,
)
from petatto_kanban.display.desktop_board_controller import DesktopBoardController
from petatto_kanban.display.menu_panel_host import MenuPanelHost
from petatto_kanban.display.modes import apply_display_mode
from petatto_kanban.display.monitors import Monitor, get_monitor
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.display.settings_actions import (
    confirm_exit,
    delete_all_cards_with_confirm,
    persist_dialog_result,
)
from petatto_kanban.display.settings_dialog import (
    SettingsDialog,
    SettingsDialogResult,
    dialog_input_from_settings,
)
from petatto_kanban.display.settings_dialog_labels import MSG_HOTKEY_FAILED, MSG_SETTINGS_SAVED
from petatto_kanban.display.transparent import TRANSPARENT_COLOR
from petatto_kanban.display.ui_chrome import UiChrome
from petatto_kanban.display.ui_metrics import metrics_for_display
from petatto_kanban.display.ui_theme import palette_for_theme
from petatto_kanban.models import Card
from petatto_kanban.new_card_placement import (
    DEFAULT_NEW_CARD_TITLE,
    clamp_card_position_to_monitor,
    compute_new_card_position,
)
from petatto_kanban.progress import PROGRESS_STEP, clamp_progress
from petatto_kanban.storage import load_board, save_board
from petatto_kanban.system.auto_start import sync_auto_start_from_settings
from petatto_kanban.system.hotkey import NewCardHotkey, create_new_card_hotkey

APP_TITLE = "Petatto-Kanban"
_HOTKEY_POLL_MS = 50


class KanbanApp:
    """オーバーレイ上の自由配置カンバン."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.board = load_board()
        self.display_settings = load_display_settings()
        self._ui_metrics = metrics_for_display(
            self.display_settings.ui_size,
            self.display_settings.ui_font,
        )
        self._ui_palette = palette_for_theme(self.display_settings.ui_theme)
        self._card_ui: dict[str, CardUiRefs] = {}
        self._card_progress_widgets: dict[str, tk.Canvas] = {}
        self._drag_state: dict[int, tuple[int, int]] = {}
        self._card_drag_moved: dict[str, bool] = {}
        self._inline_edit_card_id: str | None = None
        self._inline_edit_entry: tk.Entry | None = None
        self._due_panel_clicks = ClickReleaseTracker()
        self._title_clicks = ClickReleaseTracker()
        self._monitors = list_monitors()
        self._desktop_board: DesktopBoardController | None = None
        self._chrome: UiChrome
        self._card_renderer: CardRenderer
        self._new_card_hotkey: NewCardHotkey | None = None
        self._settings_dialog_open = False

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.configure(bg=TRANSPARENT_COLOR)

        self._build_menu_panel()
        self._sync_card_renderer()
        if self.display_settings.launch_at_login:
            sync_auto_start_from_settings(True)
        self._apply_display_mode()
        self._install_new_card_hotkey()
        self.refresh()

    @property
    def menu_panel(self):
        return self._chrome.menu_panel

    @property
    def _due_date_picker(self):
        return self._chrome.due_date_picker

    def _sync_card_renderer(self) -> None:
        self._card_renderer = CardRenderer(
            self.root,
            metrics=self._ui_metrics,
            palette=self._ui_palette,
            on_card_enter=self._on_kanban_card_enter,
            progress_widgets=self._card_progress_widgets,
        )

    def _apply_display_mode(self) -> None:
        monitor = get_monitor(self.display_settings.monitor_index)
        apply_display_mode(self.root, monitor, self.display_settings.mode)
        self._menu_panel_host.apply(monitor, self.display_settings.mode)
        self._place_menu_panel(monitor)
        if self._desktop_board is not None:
            self._desktop_board.on_display_mode_applied(
                desktop=self.display_settings.mode == DisplayMode.DESKTOP,
            )

    def _sync_ui_appearance(self) -> None:
        """UI サイズ・フォント・テーマ変更時に外観を更新する."""
        self._ui_metrics = metrics_for_display(
            self.display_settings.ui_size,
            self.display_settings.ui_font,
        )
        self._ui_palette = palette_for_theme(self.display_settings.ui_theme)
        monitor = get_monitor(self.display_settings.monitor_index)
        self._chrome.apply_appearance(self._ui_metrics, self._ui_palette)
        self._chrome.clamp_menu_to_monitor(monitor)
        self._sync_card_renderer()

    def _can_lower_desktop_board(self) -> bool:
        if self._inline_edit_card_id is not None:
            return False
        if self._due_date_picker.is_open:
            return False
        try:
            if self.root.grab_current() is not None:
                return False
        except tk.TclError:
            pass
        return True

    def _is_desktop_display_mode(self) -> bool:
        return self.display_settings.mode == DisplayMode.DESKTOP

    def _on_kanban_card_enter(self, _event: tk.Event) -> None:
        if self._desktop_board is not None:
            self._desktop_board.on_card_pointer_enter()

    def _place_menu_panel(self, monitor: Monitor | None = None) -> None:
        monitor = monitor or get_monitor(self.display_settings.monitor_index)
        if (
            self.display_settings.menu_panel_x is not None
            and self.display_settings.menu_panel_y is not None
        ):
            self.menu_panel.place_at(
                self.display_settings.menu_panel_x,
                self.display_settings.menu_panel_y,
            )
            self.menu_panel.clamp_to_monitor(monitor.width, monitor.height)
            x, y = self.menu_panel.position
            if (
                x != self.display_settings.menu_panel_x
                or y != self.display_settings.menu_panel_y
            ):
                self.display_settings.menu_panel_x = x
                self.display_settings.menu_panel_y = y
                save_display_settings(self.display_settings)
        else:
            self.menu_panel.place_default(monitor.width, monitor.height)

    def _lift_ui(self) -> None:
        """カードの上にメニューパネルが来るよう Z 順を整える."""
        for ui in self._card_ui.values():
            ui.frame.lift()
        if self._due_date_picker.host_frame is not None:
            self._due_date_picker.host_frame.lift()
        self._menu_panel_host.lift()

    def _build_menu_panel(self) -> None:
        self._menu_panel_host = MenuPanelHost(self.root)
        self._desktop_board = DesktopBoardController(
            self.root,
            self._menu_panel_host,
            is_desktop_mode=self._is_desktop_display_mode,
            can_lower=self._can_lower_desktop_board,
        )
        self._chrome = UiChrome(
            self.root,
            self._menu_panel_host.window,
            metrics=self._ui_metrics,
            palette=self._ui_palette,
            on_close=self._on_close,
            on_settings=self._open_settings,
            on_add_card=self._add_card,
            on_menu_position_changed=self._on_menu_panel_position_changed,
            on_menu_activate=self._desktop_board.activate_from_menu,
            on_menu_deactivate=self._desktop_board.on_menu_deactivate,
            on_due_picker_outside_click=self._cancel_due_date_picker,
        )
        self._menu_panel_host.window.bind(
            "<FocusIn>",
            lambda _event: self._desktop_board.activate_from_menu(),
            add="+",
        )
        self._desktop_board.bind_focus_handlers(
            self.root,
            self._menu_panel_host.window,
        )

    def _on_menu_panel_position_changed(self, x: int, y: int) -> None:
        self.display_settings.menu_panel_x = x
        self.display_settings.menu_panel_y = y
        save_display_settings(self.display_settings)

    def refresh(
        self,
        *,
        begin_inline_edit_for: str | None = None,
        begin_due_edit_for: str | None = None,
    ) -> None:
        """カードを再描画する."""
        self._due_date_picker.close()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        self._card_drag_moved.clear()
        self._due_panel_clicks.reset()
        self._title_clicks.reset()
        for ui in self._card_ui.values():
            ui.frame.destroy()
        self._card_ui.clear()
        self._card_progress_widgets.clear()
        self._drag_state.clear()

        for card in self.board.cards:
            self._render_card(card)
        self._lift_ui()

        if begin_inline_edit_for is not None:
            self.root.after_idle(
                lambda card_id=begin_inline_edit_for: self._begin_inline_edit_for_card(card_id)
            )
        if begin_due_edit_for is not None:
            self.root.after_idle(
                lambda card_id=begin_due_edit_for: self._open_due_date_picker_for_card(card_id)
            )

    def _render_card(self, card: Card) -> None:
        ui = self._card_renderer.render(card)
        self._card_ui[card.id] = ui
        self._bind_card_interactions(card, ui)

    def _adjust_card_progress(self, card: Card, delta: int) -> None:
        new_progress = clamp_progress(card.progress + delta)
        if new_progress == card.progress:
            return
        card.progress = new_progress
        card.touch()
        save_board(self.board)
        canvas = self._card_progress_widgets.get(card.id)
        if canvas is not None:
            self._card_renderer.draw_progress(canvas, card.progress)

    def _cancel_due_date_picker(self) -> None:
        if (
            self._due_date_picker.cancel_if_any()
            and self._desktop_board is not None
        ):
            self._desktop_board.schedule_lower()

    def _set_card_due_date(self, card: Card, value: date | None) -> None:
        if card.due_date == value:
            return
        card.due_date = value
        card.touch()
        save_board(self.board)

    def _open_due_date_picker(self, card: Card, due_panel: tk.Frame) -> None:
        if self._inline_edit_card_id is not None:
            return

        def on_apply(value: date | None) -> None:
            self._set_card_due_date(card, value)
            self.refresh()

        self._due_date_picker.open(
            card_id=card.id,
            due_panel=due_panel,
            initial=card.due_date,
            on_apply=on_apply,
            lift_targets=[self.menu_panel.widget],
        )

    def _open_due_date_picker_for_card(self, card_id: str) -> None:
        ui = self._card_ui.get(card_id)
        card = self.board.find_card(card_id)
        if ui is None or card is None:
            return
        self._open_due_date_picker(card, ui.due_panel)

    def _begin_inline_title_edit(self, card: Card, ui: CardUiRefs) -> None:
        if self._inline_edit_card_id is not None:
            return

        self._inline_edit_card_id = card.id
        ui.title_label.pack_forget()

        entry = tk.Entry(
            ui.title_frame,
            bg=self._ui_palette.card_bg,
            fg=self._ui_palette.card_fg,
            font=self._ui_metrics.title_font,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
        )
        entry.pack(anchor=tk.W, fill=tk.X)
        entry.insert(0, card.title)
        entry.select_range(0, tk.END)
        entry.focus_set()
        self._inline_edit_entry = entry

        entry.bind("<Return>", lambda _e: self._commit_inline_title_edit_if_any())
        entry.bind("<Escape>", lambda _e: self._commit_inline_title_edit_if_any(save=False))
        entry.bind("<FocusOut>", lambda _e: self._commit_inline_title_edit_if_any())

    def _begin_inline_edit_for_card(self, card_id: str) -> None:
        ui = self._card_ui.get(card_id)
        card = self.board.find_card(card_id)
        if ui is None or card is None:
            return
        self._begin_inline_title_edit(card, ui)

    def _commit_inline_title_edit_if_any(
        self,
        save: bool = True,
        *,
        refresh_after: bool = True,
    ) -> bool:
        """進行中のタイトル編集があれば確定またはキャンセルする."""
        if self._inline_edit_card_id is None:
            return False
        if not self._apply_inline_title_edit(save):
            return True
        if refresh_after:
            self.refresh()
        return True

    def _apply_inline_title_edit(self, save: bool) -> bool:
        """タイトル編集内容を反映する。空タイトル時は False."""
        card_id = self._inline_edit_card_id
        entry = self._inline_edit_entry
        if card_id is None or entry is None:
            self._clear_inline_edit_state()
            return True

        card = self.board.find_card(card_id)
        if card is None:
            self._clear_inline_edit_state()
            return True

        if save:
            new_title = entry.get().strip()
            if not new_title:
                messagebox.showwarning(
                    APP_TITLE,
                    "タイトルは空にできません。",
                    parent=self.root,
                )
                entry.focus_set()
                return False
            card.title = new_title
            card.touch()
            save_board(self.board)

        self._clear_inline_edit_state()
        if self.display_settings.mode == DisplayMode.DESKTOP and self._desktop_board is not None:
            self._desktop_board.schedule_lower()
        return True

    def _clear_inline_edit_state(self) -> None:
        self._inline_edit_card_id = None
        self._inline_edit_entry = None

    def _prepare_card_pointer_down(
        self,
        card: Card,
        *,
        skip_inline_commit_for_card: bool = False,
        skip_due_picker_cancel_for_card: bool = False,
    ) -> bool:
        """期限パネル／インライン編集を処理。True なら呼び出し元は続行しない."""
        if (
            not skip_due_picker_cancel_for_card
            and not (
                self._due_date_picker.is_open
                and self._due_date_picker.edit_card_id == card.id
            )
            and self._due_date_picker.cancel_if_any()
        ):
            return True

        if skip_inline_commit_for_card and self._inline_edit_card_id == card.id:
            return False

        if self._inline_edit_card_id == card.id:
            self._commit_inline_title_edit_if_any()
            return True

        return bool(self._commit_inline_title_edit_if_any())

    def _bind_card_interactions(self, card: Card, ui: CardUiRefs) -> None:
        def on_delete(_event: tk.Event) -> None:
            self._delete_card(card)

        def bind_scroll(widget: tk.Misc) -> None:
            def on_wheel(event: tk.Event) -> str:
                button = getattr(event, "num", None)
                if button == 5:
                    delta = -PROGRESS_STEP
                elif button == 4 or event.delta > 0:
                    delta = PROGRESS_STEP
                else:
                    delta = -PROGRESS_STEP
                self._adjust_card_progress(card, delta)
                return "break"

            widget.bind("<MouseWheel>", on_wheel)
            widget.bind("<Button-4>", on_wheel)
            widget.bind("<Button-5>", on_wheel)

        def bind_drag_region(
            widget: tk.Misc,
            *,
            on_press: Callable[[tk.Event], None] | None = None,
            on_release: Callable[[tk.Event], None] | None = None,
        ) -> None:
            def press(event: tk.Event) -> None:
                if on_press is not None:
                    on_press(event)
                    return
                self._on_card_drag_press(event, card, ui.frame)

            def release(event: tk.Event) -> None:
                if on_release is not None:
                    on_release(event)
                    return
                self._on_card_drag_release(event, card, ui.frame)

            widget.bind("<Button-1>", press)
            widget.bind("<B1-Motion>", lambda e: self._on_card_drag_motion(e, card, ui.frame))
            widget.bind("<ButtonRelease-1>", release)

        ui.frame.bind("<ButtonRelease-3>", on_delete)
        bind_drag_region(ui.frame)
        bind_scroll(ui.frame)

        for widget in (ui.title_frame, ui.title_label):
            widget.bind("<ButtonRelease-3>", on_delete)
            bind_drag_region(
                widget,
                on_press=lambda e: self._on_title_press(e, card, ui.frame),
                on_release=lambda e: self._on_title_release(e, card, ui),
            )
            bind_scroll(widget)

        for widget in (ui.due_panel, ui.due_label):
            widget.bind("<ButtonRelease-3>", on_delete)
            bind_drag_region(
                widget,
                on_press=lambda e: self._on_due_press(e, card, ui.frame),
                on_release=lambda e: self._on_due_release(e, card, ui),
            )
            bind_scroll(widget)

        ui.progress_canvas.bind("<ButtonRelease-3>", on_delete)
        bind_drag_region(
            ui.progress_canvas,
            on_press=lambda e: self._on_card_region_press(e, card, ui.frame),
            on_release=lambda e: self._on_card_drag_release(e, card, ui.frame),
        )
        bind_scroll(ui.progress_canvas)

    def _on_card_region_press(
        self,
        event: tk.Event,
        card: Card,
        frame: tk.Frame,
    ) -> None:
        if self._prepare_card_pointer_down(card):
            return
        self._on_card_drag_press(event, card, frame)

    def _on_title_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._prepare_card_pointer_down(card, skip_inline_commit_for_card=True):
            return
        self._on_card_drag_press(event, card, frame)

    def _on_due_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._prepare_card_pointer_down(
            card,
            skip_due_picker_cancel_for_card=True,
        ):
            return
        self._on_card_drag_press(event, card, frame)

    def _on_card_drag_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        self._card_drag_moved[card.id] = False
        self._drag_state[frame.winfo_id()] = (event.x, event.y)

    def _on_card_drag_motion(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        origin = self._drag_state.get(frame.winfo_id())
        if origin is None:
            return
        self._card_drag_moved[card.id] = True
        new_x = frame.winfo_x() + event.x - origin[0]
        new_y = frame.winfo_y() + event.y - origin[1]
        frame.place(x=new_x, y=new_y)
        card.x = new_x
        card.y = new_y

    def _on_card_drag_release(self, _event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._card_drag_moved.get(card.id):
            card.touch()
            save_board(self.board)
        self._drag_state.pop(frame.winfo_id(), None)
        self._card_drag_moved.pop(card.id, None)

    def _on_title_release(self, event: tk.Event, card: Card, ui: CardUiRefs) -> None:
        if self._card_drag_moved.get(card.id):
            card.touch()
            save_board(self.board)
            self._title_clicks.reset()
        elif self._inline_edit_card_id == card.id:
            entry = self._inline_edit_entry
            if entry is not None and event.widget is not entry:
                self._commit_inline_title_edit_if_any()
            self._title_clicks.reset()
        else:
            self._handle_title_release(event, card, ui)
        self._drag_state.pop(ui.frame.winfo_id(), None)
        self._card_drag_moved.pop(card.id, None)

    def _handle_title_release(
        self,
        event: tk.Event,
        card: Card,
        ui: CardUiRefs,
    ) -> None:
        interval = double_click_interval_ms(self.root)
        if self._title_clicks.is_second_release(card.id, event.time, interval):
            self._title_clicks.reset()
            if self._inline_edit_card_id == card.id:
                return
            if self._prepare_card_pointer_down(card):
                return
            self._begin_inline_title_edit(card, ui)
            return

        self._title_clicks.record(card.id, event.time)

    def _on_due_release(self, event: tk.Event, card: Card, ui: CardUiRefs) -> None:
        if self._card_drag_moved.get(card.id):
            card.touch()
            save_board(self.board)
            self._due_panel_clicks.reset()
        else:
            self._handle_due_panel_release(event, card, ui.due_panel)
        self._drag_state.pop(ui.frame.winfo_id(), None)
        self._card_drag_moved.pop(card.id, None)

    def _handle_due_panel_release(
        self,
        event: tk.Event,
        card: Card,
        due_panel: tk.Frame,
    ) -> None:
        interval = double_click_interval_ms(self.root)
        if self._due_panel_clicks.is_second_release(card.id, event.time, interval):
            self._due_panel_clicks.reset()
            if (
                self._due_date_picker.is_open
                and self._due_date_picker.edit_card_id == card.id
            ):
                return
            if self._prepare_card_pointer_down(card):
                return
            self._open_due_date_picker(card, due_panel)
            return

        self._due_panel_clicks.record(card.id, event.time)

        if (
            self._due_date_picker.is_open
            and self._due_date_picker.edit_card_id == card.id
        ):
            self._cancel_due_date_picker()
            self._due_panel_clicks.reset()

    def _add_card(self) -> None:
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        self.root.update_idletasks()
        monitor = get_monitor(self.display_settings.monitor_index)
        metrics = self._ui_metrics
        card_width = metrics.card_placement_width
        card_height = metrics.card_placement_height
        card_x, card_y = compute_new_card_position(
            panel=self.menu_panel.bounds(),
            card_width=card_width,
            stack_index=len(self.board.cards),
        )
        card_x, card_y = clamp_card_position_to_monitor(
            card_x,
            card_y,
            card_width=card_width,
            card_height=card_height,
            monitor_width=monitor.width,
            monitor_height=monitor.height,
        )
        card = Card(title=DEFAULT_NEW_CARD_TITLE, x=card_x, y=card_y)
        self.board.cards.append(card)
        save_board(self.board)
        self.refresh(begin_inline_edit_for=card.id)

    def _install_new_card_hotkey(self) -> None:
        try:
            self._new_card_hotkey = create_new_card_hotkey(self._on_new_card_hotkey)
            self._new_card_hotkey.set_shortcut(self.display_settings.shortcut_new_card)
        except (OSError, RuntimeError) as error:
            messagebox.showinfo(
                APP_TITLE,
                MSG_HOTKEY_FAILED.format(error=error),
                parent=self.root,
            )
        if self._new_card_hotkey is not None:
            self._schedule_hotkey_poll()

    def _schedule_hotkey_poll(self) -> None:
        if self._new_card_hotkey is None:
            return
        self._new_card_hotkey.poll()
        try:
            self.root.after(_HOTKEY_POLL_MS, self._schedule_hotkey_poll)
        except tk.TclError:
            return

    def _on_new_card_hotkey(self) -> None:
        if self._settings_dialog_open:
            return
        try:
            if self.root.grab_current() is not None:
                return
        except tk.TclError:
            pass
        self.root.after(0, self._add_card)

    def _apply_shortcut(self, shortcut: str) -> None:
        if self._new_card_hotkey is None:
            return
        self._new_card_hotkey.set_shortcut(shortcut)

    def _delete_card(self, card: Card) -> None:
        if self.display_settings.confirm_delete and not messagebox.askyesno(
            APP_TITLE,
            f"「{card.title}」を削除しますか？",
            parent=self.root,
        ):
            return

        self.board.remove_card(card.id)
        self._persist_and_refresh()

    def _delete_all_cards(self) -> None:
        """設定ダイアログから全カードを削除する（常に確認ダイアログ）。"""
        if not delete_all_cards_with_confirm(
            parent=self.root,
            app_title=APP_TITLE,
            board=self.board,
            messagebox=messagebox,
        ):
            return
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        self.refresh()

    def _open_settings(self) -> None:
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        self._settings_dialog_open = True
        try:
            dialog = SettingsDialog(
                self.root,
                dialog_input=dialog_input_from_settings(
                    self.display_settings,
                    self._monitors,
                ),
                on_delete_all_cards=self._delete_all_cards,
            )
        finally:
            self._settings_dialog_open = False
        if dialog.result is None:
            return

        if not self._apply_settings(dialog.result):
            return
        messagebox.showinfo(APP_TITLE, MSG_SETTINGS_SAVED, parent=self.root)

    def _apply_settings(self, settings: SettingsDialogResult) -> bool:
        changes = persist_dialog_result(
            self.display_settings,
            settings,
            messagebox=messagebox,
            parent=self.root,
            app_title=APP_TITLE,
            apply_shortcut=self._apply_shortcut,
        )
        if changes is None:
            return False

        if changes.needs_ui_refresh:
            self._sync_ui_appearance()
        if changes.needs_display_refresh:
            self._apply_display_mode()
        if changes.needs_ui_refresh or changes.needs_display_refresh:
            self.refresh()
        return True

    def _persist_and_refresh(self) -> None:
        save_board(self.board)
        self.refresh()

    def _on_close(self) -> None:
        if not confirm_exit(
            parent=self.root,
            app_title=APP_TITLE,
            confirm_exit_enabled=self.display_settings.confirm_exit,
            messagebox=messagebox,
        ):
            return
        if self._desktop_board is not None:
            self._desktop_board.stop()
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        if self._new_card_hotkey is not None:
            self._new_card_hotkey.close()
            self._new_card_hotkey = None
        save_board(self.board)
        save_display_settings(self.display_settings)
        self.root.destroy()


def run_app() -> None:
    """アプリケーションを起動する."""
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    KanbanApp(root)
    root.mainloop()
