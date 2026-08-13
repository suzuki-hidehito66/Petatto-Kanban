"""Tkinter ベースの GUI アプリケーション（オーバーレイ / デスクトップモード）."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from tkinter import messagebox, simpledialog, ttk

from petatto_kanban.card_ui import (
    CardUiRefs,
    ClickReleaseTracker,
    double_click_interval_ms,
)
from petatto_kanban.display import (
    DisplayMode,
    list_monitors,
    load_display_settings,
    save_display_settings,
)
from petatto_kanban.display.desktop import TRANSPARENT_COLOR
from petatto_kanban.display.modes import apply_display_mode
from petatto_kanban.display.monitors import Monitor, get_monitor, monitor_index_for_name
from petatto_kanban.due_date import due_date_panel_style, format_due_date
from petatto_kanban.due_date_picker import DueDatePickerHost
from petatto_kanban.menu_panel import MenuPanel
from petatto_kanban.models import Card
from petatto_kanban.new_card_placement import (
    DEFAULT_NEW_CARD_TITLE,
    clamp_card_position_to_monitor,
    compute_new_card_position,
)
from petatto_kanban.progress import PROGRESS_STEP, clamp_progress, progress_color
from petatto_kanban.storage import load_board, save_board

APP_TITLE = "Petatto-Kanban"
CARD_BG = "#fffef8"
CARD_FG = "#222222"
CARD_TITLE_FRAME_BD = 1
CARD_MIN_WIDTH = 220
CARD_MIN_HEIGHT = 120
CARD_FRAME_BORDER = 1
DUE_PANEL_BD = 1
DUE_PICKER_PANEL_WIDTH = 240
PROGRESS_TRACK_BG = "#e8e8e8"
PROGRESS_BAR_HEIGHT = 18
CARD_LABEL_WRAP = 200

DISPLAY_MODE_LABELS: dict[DisplayMode, str] = {
    DisplayMode.OVERLAY: "オーバーレイ",
    DisplayMode.DESKTOP: "デスクトップ",
}
DISPLAY_MODE_BY_LABEL = {label: mode for mode, label in DISPLAY_MODE_LABELS.items()}


@dataclass(frozen=True)
class SettingsDialogResult:
    """設定ダイアログの確定値."""

    mode: DisplayMode
    confirm_delete: bool
    monitor_index: int


class KanbanApp:
    """オーバーレイ上の自由配置カンバン."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.board = load_board()
        self.display_settings = load_display_settings()
        self._card_ui: dict[str, CardUiRefs] = {}
        self._card_progress_widgets: dict[str, tk.Canvas] = {}
        self._drag_state: dict[int, tuple[int, int]] = {}
        self._card_drag_moved: dict[str, bool] = {}
        self._inline_edit_card_id: str | None = None
        self._inline_edit_entry: tk.Entry | None = None
        self._due_date_picker = DueDatePickerHost(
            root,
            bg=CARD_BG,
            panel_width=DUE_PICKER_PANEL_WIDTH,
            on_outside_click=self._cancel_due_date_picker,
        )
        self._due_panel_clicks = ClickReleaseTracker()
        self._title_clicks = ClickReleaseTracker()
        self._monitors = list_monitors()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.configure(bg=TRANSPARENT_COLOR)

        self._build_menu_panel()
        self._apply_display_mode()
        self.refresh()

    def _apply_display_mode(self) -> None:
        monitor = get_monitor(self.display_settings.monitor_index)
        apply_display_mode(self.root, monitor, self.display_settings.mode)
        self._place_menu_panel(monitor)

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
        self.menu_panel.widget.lift()

    def _build_menu_panel(self) -> None:
        self.menu_panel = MenuPanel(
            self.root,
            on_close=self._on_close,
            on_settings=self._open_settings,
            on_add_card=self._add_card,
            on_position_changed=self._on_menu_panel_position_changed,
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
        frame = tk.Frame(
            self.root,
            bg=CARD_BG,
            bd=CARD_FRAME_BORDER,
            relief=tk.RIDGE,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        frame.place(x=card.x, y=card.y)

        title_frame = tk.Frame(
            frame,
            bg=CARD_BG,
            bd=CARD_TITLE_FRAME_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        title_frame.pack(anchor=tk.NW, fill=tk.X)

        title_label = self._card_label(
            title_frame,
            text=card.title,
            font=("Segoe UI", 10, "bold"),
            fg=CARD_FG,
            cursor="xterm",
        )
        title_label.pack(anchor=tk.NW, fill=tk.X)

        due_panel, due_label = self._create_due_date_panel(frame, card)
        due_panel.pack(anchor=tk.NW, fill=tk.X, pady=(4, 0))

        progress_canvas = self._create_progress_canvas(frame, card)
        progress_canvas.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))

        self._finalize_card_frame(frame)
        ui = CardUiRefs(
            frame=frame,
            title_frame=title_frame,
            title_label=title_label,
            due_panel=due_panel,
            due_label=due_label,
            progress_canvas=progress_canvas,
        )
        self._card_ui[card.id] = ui
        self._bind_card_interactions(card, ui)

    def _card_label(self, parent: tk.Misc, **kwargs) -> tk.Label:
        defaults = {
            "bg": CARD_BG,
            "wraplength": CARD_LABEL_WRAP,
            "justify": tk.LEFT,
            "anchor": tk.W,
        }
        defaults.update(kwargs)
        return tk.Label(parent, **defaults)

    def _finalize_card_frame(self, frame: tk.Frame) -> None:
        frame.update_idletasks()
        frame.config(
            width=max(CARD_MIN_WIDTH, frame.winfo_reqwidth()),
            height=max(CARD_MIN_HEIGHT, frame.winfo_reqheight()),
        )
        frame.pack_propagate(False)

    def _create_progress_canvas(self, parent: tk.Frame, card: Card) -> tk.Canvas:
        canvas = tk.Canvas(
            parent,
            height=PROGRESS_BAR_HEIGHT,
            bg=PROGRESS_TRACK_BG,
            highlightthickness=0,
            bd=0,
        )
        self._card_progress_widgets[card.id] = canvas

        def redraw(_event: tk.Event | None = None) -> None:
            self._draw_progress_canvas(canvas, card.progress)

        canvas.bind("<Configure>", redraw)
        parent.after_idle(redraw)
        return canvas

    def _draw_progress_canvas(self, canvas: tk.Canvas, progress: int) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), PROGRESS_BAR_HEIGHT)
        canvas.create_rectangle(0, 0, width, height, fill=PROGRESS_TRACK_BG, outline="")
        fill_width = width * progress / 100
        if fill_width > 0:
            canvas.create_rectangle(
                0,
                0,
                fill_width,
                height,
                fill=progress_color(progress),
                outline="",
            )
        text_color = "#ffffff" if progress >= 55 else CARD_FG
        canvas.create_text(
            width / 2,
            height / 2,
            text=f"{progress}%",
            fill=text_color,
            font=("Segoe UI", 9, "bold"),
        )

    def _adjust_card_progress(self, card: Card, delta: int) -> None:
        new_progress = clamp_progress(card.progress + delta)
        if new_progress == card.progress:
            return
        card.progress = new_progress
        card.touch()
        save_board(self.board)
        canvas = self._card_progress_widgets.get(card.id)
        if canvas is not None:
            self._draw_progress_canvas(canvas, card.progress)

    def _create_due_date_panel(self, frame: tk.Frame, card: Card) -> tuple[tk.Frame, tk.Label]:
        panel_bg, panel_fg = due_date_panel_style(card.due_date)
        due_panel = tk.Frame(
            frame,
            bg=panel_bg,
            bd=DUE_PANEL_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=6,
            pady=3,
        )
        due_label = tk.Label(
            due_panel,
            text=format_due_date(card.due_date),
            bg=panel_bg,
            fg=panel_fg,
            font=("Segoe UI", 9),
            anchor=tk.W,
            cursor="hand2",
        )
        due_label.pack(anchor=tk.W, fill=tk.X)
        return due_panel, due_label

    def _cancel_due_date_picker(self) -> None:
        self._due_date_picker.cancel_if_any()

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
            bg=CARD_BG,
            fg=CARD_FG,
            font=("Segoe UI", 10, "bold"),
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
        card_width = CARD_MIN_WIDTH + 2 * CARD_FRAME_BORDER
        card_height = CARD_MIN_HEIGHT + 2 * CARD_FRAME_BORDER
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

    def _delete_card(self, card: Card) -> None:
        if self.display_settings.confirm_delete and not messagebox.askyesno(
            APP_TITLE,
            f"「{card.title}」を削除しますか？",
            parent=self.root,
        ):
            return

        self.board.remove_card(card.id)
        self._persist_and_refresh()

    def _open_settings(self) -> None:
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        dialog = _SettingsDialog(
            self.root,
            mode=self.display_settings.mode,
            confirm_delete=self.display_settings.confirm_delete,
            monitor_index=self.display_settings.monitor_index,
            monitors=self._monitors,
        )
        if dialog.result is None:
            return

        self._apply_settings(dialog.result)
        messagebox.showinfo(APP_TITLE, "設定を保存しました。", parent=self.root)

    def _apply_settings(self, settings: SettingsDialogResult) -> None:
        mode_changed = settings.mode != self.display_settings.mode
        monitor_changed = settings.monitor_index != self.display_settings.monitor_index
        self.display_settings.mode = settings.mode
        self.display_settings.confirm_delete = settings.confirm_delete
        self.display_settings.monitor_index = settings.monitor_index
        save_display_settings(self.display_settings)

        if mode_changed or monitor_changed:
            self._apply_display_mode()
            self.refresh()

    def _persist_and_refresh(self) -> None:
        save_board(self.board)
        self.refresh()

    def _on_close(self) -> None:
        self._due_date_picker.cancel_if_any()
        self._commit_inline_title_edit_if_any(refresh_after=False)
        save_board(self.board)
        save_display_settings(self.display_settings)
        self.root.destroy()


class _SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        mode: DisplayMode,
        confirm_delete: bool,
        monitor_index: int,
        monitors: list[Monitor],
    ) -> None:
        self._mode = mode
        self._confirm_delete = confirm_delete
        self._monitor_index = monitor_index
        self._monitors = monitors
        self.result: SettingsDialogResult | None = None
        super().__init__(parent, title="設定")

    def body(self, master: tk.Misc) -> tk.Widget:
        ttk.Label(master, text="表示モード").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        self.mode_var = tk.StringVar(value=DISPLAY_MODE_LABELS[self._mode])
        self.mode_menu = ttk.Combobox(
            master,
            textvariable=self.mode_var,
            values=list(DISPLAY_MODE_LABELS.values()),
            state="readonly",
            width=28,
        )
        self.mode_menu.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        ttk.Label(master, text="表示ディスプレイ").grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
        monitor_names = [monitor.name for monitor in self._monitors]
        default_name = monitor_names[min(self._monitor_index, len(monitor_names) - 1)]
        self.monitor_var = tk.StringVar(value=default_name)
        self.monitor_menu = ttk.Combobox(
            master,
            textvariable=self.monitor_var,
            values=monitor_names,
            state="readonly",
            width=28,
        )
        self.monitor_menu.grid(row=3, column=0, sticky=tk.EW, pady=(0, 12))

        self.confirm_var = tk.BooleanVar(value=self._confirm_delete)
        ttk.Checkbutton(
            master,
            text="カード削除時に確認ダイアログを表示する",
            variable=self.confirm_var,
        ).grid(row=4, column=0, sticky=tk.W)
        master.columnconfigure(0, weight=1)
        return self.mode_menu

    def apply(self) -> None:
        mode_label = self.mode_var.get()
        mode = DISPLAY_MODE_BY_LABEL.get(mode_label, self._mode)
        self.result = SettingsDialogResult(
            mode=mode,
            confirm_delete=self.confirm_var.get(),
            monitor_index=monitor_index_for_name(
                self._monitors,
                self.monitor_var.get(),
                self._monitor_index,
            ),
        )


def run_app() -> None:
    """アプリケーションを起動する."""
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    KanbanApp(root)
    root.mainloop()
