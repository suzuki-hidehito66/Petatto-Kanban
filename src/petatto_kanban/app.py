"""Tkinter ベースの GUI アプリケーション（オーバーレイモード）."""

from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from tkinter import messagebox, simpledialog, ttk

from petatto_kanban.display import list_monitors, load_display_settings, save_display_settings
from petatto_kanban.display.desktop import TRANSPARENT_COLOR
from petatto_kanban.display.monitors import Monitor, get_monitor, monitor_index_for_name
from petatto_kanban.display.overlay import apply_overlay_mode
from petatto_kanban.due_date import due_date_panel_style, format_due_date
from petatto_kanban.due_date_picker import DueDatePicker
from petatto_kanban.models import Card
from petatto_kanban.progress import PROGRESS_STEP, clamp_progress, progress_color
from petatto_kanban.storage import load_board, save_board

APP_TITLE = "Petatto-Kanban"
CARD_BG = "#fffef8"
CARD_FG = "#222222"
CARD_TITLE_FRAME_BD = 1
CARD_MIN_WIDTH = 220
CARD_MIN_HEIGHT = 120
DUE_PANEL_BD = 1
DUE_PICKER_PANEL_WIDTH = 240
DUE_PICKER_OUTSIDE_CLICK_GRACE_SEC = 0.35
TOOLBAR_BG = "#f0f0f0"
PROGRESS_TRACK_BG = "#e8e8e8"
PROGRESS_BAR_HEIGHT = 18
NEW_CARD_NEAR_TOOLBAR_OFFSET_X = 0
NEW_CARD_NEAR_TOOLBAR_OFFSET_Y = 8
NEW_CARD_STACK_OFFSET = 32
DEFAULT_NEW_CARD_TITLE = "新しいタスク"
CARD_LABEL_WRAP = 200


@dataclass(frozen=True)
class SettingsDialogResult:
    """設定ダイアログの確定値."""

    confirm_delete: bool
    monitor_index: int


class KanbanApp:
    """オーバーレイ上の自由配置カンバン."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.board = load_board()
        self.display_settings = load_display_settings()
        self._card_widgets: dict[str, tk.Frame] = {}
        self._card_progress_widgets: dict[str, tk.Canvas] = {}
        self._drag_state: dict[int, tuple[int, int]] = {}
        self._title_drag_moved = False
        self._inline_edit_card_id: str | None = None
        self._inline_edit_finish: Callable[[bool], None] | None = None
        self._due_date_edit_card_id: str | None = None
        self._due_date_picker_host: tk.Frame | None = None
        self._due_date_picker: DueDatePicker | None = None
        self._due_date_picker_cancel: Callable[[], None] | None = None
        self._due_date_outside_click_bound = False
        self._due_date_picker_opened_at = 0.0
        self._due_panel_close_after_id: str | None = None
        self._due_drag_moved = False
        self._progress_drag_moved = False
        self._monitors = list_monitors()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.configure(bg=TRANSPARENT_COLOR)

        self._build_toolbar()
        self._apply_overlay_mode()
        self.refresh()

    def _apply_overlay_mode(self) -> None:
        monitor = get_monitor(self.display_settings.monitor_index)
        apply_overlay_mode(self.root, monitor)
        self.toolbar.place(x=monitor.width - 16, y=16, anchor=tk.NE)

    def _lift_ui(self) -> None:
        """カードの上にツールバーが来るよう Z 順を整える."""
        for frame in self._card_widgets.values():
            frame.lift()
        if self._due_date_picker_host is not None:
            self._due_date_picker_host.lift()
        self.toolbar.lift()

    def _build_toolbar(self) -> None:
        self.toolbar = tk.Frame(
            self.root,
            bg=TOOLBAR_BG,
            bd=1,
            relief=tk.RIDGE,
            padx=4,
            pady=4,
        )
        ttk.Button(self.toolbar, text="×", width=3, command=self._on_close).pack(
            side=tk.RIGHT,
            padx=2,
        )
        ttk.Button(self.toolbar, text="設定", command=self._open_settings).pack(
            side=tk.RIGHT,
            padx=2,
        )
        ttk.Button(self.toolbar, text="+ カード", command=self._add_card).pack(
            side=tk.RIGHT,
            padx=2,
        )

    def refresh(
        self,
        *,
        begin_inline_edit_for: str | None = None,
        begin_due_edit_for: str | None = None,
    ) -> None:
        """カードを再描画する."""
        self._close_due_date_picker()
        self._inline_edit_card_id = None
        self._inline_edit_finish = None
        self._title_drag_moved = False
        self._due_drag_moved = False
        self._progress_drag_moved = False
        for widget in self._card_widgets.values():
            widget.destroy()
        self._card_widgets.clear()
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
            bd=1,
            relief=tk.RIDGE,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        frame.place(x=card.x, y=card.y)
        self._card_widgets[card.id] = frame

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
        self._bind_card_interactions(
            frame,
            card,
            title_frame,
            title_label,
            due_panel,
            due_label,
            progress_canvas,
        )

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

    @staticmethod
    def _widget_is_descendant(widget: tk.Misc, ancestor: tk.Misc) -> bool:
        current: tk.Misc | None = widget
        while current is not None:
            if current == ancestor:
                return True
            current = current.master if isinstance(current.master, tk.Misc) else None
        return False

    def _bind_due_date_picker_outside_click(self) -> None:
        if self._due_date_outside_click_bound:
            return
        self.root.bind_all("<Button-1>", self._on_due_date_picker_outside_click, add="+")
        self.root.bind_all("<ButtonRelease-1>", self._on_due_date_picker_outside_click, add="+")
        self._due_date_outside_click_bound = True

    def _unbind_due_date_picker_outside_click(self) -> None:
        if not self._due_date_outside_click_bound:
            return
        self.root.unbind_all("<Button-1>")
        self.root.unbind_all("<ButtonRelease-1>")
        self._due_date_outside_click_bound = False

    def _on_due_date_picker_outside_click(self, event: tk.Event) -> None:
        if self._due_date_picker_host is None:
            return
        x_root = event.x_root
        y_root = event.y_root
        widget = event.widget
        self.root.after_idle(
            lambda w=widget, x=x_root, y=y_root: self._maybe_cancel_due_date_picker_for_click(
                w, x, y
            ),
        )

    def _maybe_cancel_due_date_picker_for_click(
        self,
        widget: tk.Misc | str,
        x_root: int,
        y_root: int,
    ) -> None:
        host = self._due_date_picker_host
        if host is None:
            return
        opened_at = self._due_date_picker_opened_at
        if time.monotonic() - opened_at < DUE_PICKER_OUTSIDE_CLICK_GRACE_SEC:
            return
        if isinstance(widget, tk.Misc) and self._widget_is_descendant(widget, host):
            return
        host.update_idletasks()
        left = host.winfo_rootx()
        top = host.winfo_rooty()
        right = left + host.winfo_width()
        bottom = top + host.winfo_height()
        if left <= x_root <= right and top <= y_root <= bottom:
            return
        self._cancel_due_date_picker_if_any()

    def _cancel_scheduled_due_panel_close(self) -> None:
        if self._due_panel_close_after_id is not None:
            self.root.after_cancel(self._due_panel_close_after_id)
            self._due_panel_close_after_id = None

    def _schedule_due_panel_single_click_close(self, card_id: str) -> None:
        self._cancel_scheduled_due_panel_close()

        def close_if_still_editing() -> None:
            self._due_panel_close_after_id = None
            if self._due_date_edit_card_id != card_id:
                return
            if self._due_date_picker_host is None:
                return
            opened_at = self._due_date_picker_opened_at
            if time.monotonic() - opened_at < DUE_PICKER_OUTSIDE_CLICK_GRACE_SEC:
                return
            self._cancel_due_date_picker_if_any()

        self._due_panel_close_after_id = self.root.after(250, close_if_still_editing)

    def _cancel_due_date_picker_if_any(self) -> bool:
        """進行中の期限編集があれば「閉じる」と同様にキャンセルする."""
        if self._due_date_picker_cancel is None:
            return False
        self._due_date_picker_cancel()
        return True

    def _close_due_date_picker(self) -> None:
        self._cancel_scheduled_due_panel_close()
        self._unbind_due_date_picker_outside_click()
        if self._due_date_picker_host is not None:
            self._due_date_picker_host.destroy()
            self._due_date_picker_host = None
        self._due_date_picker = None
        self._due_date_edit_card_id = None
        self._due_date_picker_cancel = None

    def _place_due_date_picker_panel(self, host: tk.Frame, anchor: tk.Misc) -> None:
        """期限パネル付近に、カード外へフロート表示する."""
        self.root.update_idletasks()
        host.update_idletasks()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        anchor_x = anchor.winfo_rootx() - self.root.winfo_rootx()
        anchor_y = anchor.winfo_rooty() - self.root.winfo_rooty()
        anchor_height = anchor.winfo_height()
        panel_width = max(DUE_PICKER_PANEL_WIDTH, host.winfo_reqwidth())
        panel_height = host.winfo_reqheight()
        x = min(max(0, anchor_x), max(0, root_width - panel_width))
        y = anchor_y + anchor_height + 4
        if y + panel_height > root_height:
            y = max(0, anchor_y - panel_height - 4)
        host.place(x=x, y=y, width=panel_width)

    def _set_card_due_date(self, card: Card, value: date | None) -> None:
        if card.due_date == value:
            return
        card.due_date = value
        card.touch()
        save_board(self.board)

    def _open_due_date_picker(
        self,
        card: Card,
        due_panel: tk.Frame,
    ) -> None:
        if self._inline_edit_card_id is not None:
            return
        self._close_due_date_picker()
        self._due_date_edit_card_id = card.id

        def apply(value: date | None) -> None:
            self._set_card_due_date(card, value)
            self._close_due_date_picker()
            self.refresh()

        def cancel() -> None:
            self._close_due_date_picker()

        host = tk.Frame(
            self.root,
            bg=CARD_BG,
            bd=1,
            relief=tk.RIDGE,
            padx=2,
            pady=2,
            highlightthickness=0,
        )
        picker = DueDatePicker(
            host,
            initial=card.due_date,
            on_apply=apply,
            on_cancel=cancel,
            bg=CARD_BG,
        )
        picker.pack(fill=tk.BOTH, expand=True)
        self._due_date_picker_host = host
        self._due_date_picker = picker
        self._due_date_picker_cancel = cancel
        self._place_due_date_picker_panel(host, due_panel)
        self._due_date_picker_opened_at = time.monotonic()
        self._bind_due_date_picker_outside_click()
        host.lift()
        self.toolbar.lift()
        picker.focus_set()

    def _open_due_date_picker_for_card(self, card_id: str) -> None:
        frame = self._card_widgets.get(card_id)
        card = self.board.find_card(card_id)
        if frame is None or card is None:
            return

        children = frame.winfo_children()
        if len(children) < 2 or not isinstance(children[1], tk.Frame):
            return

        due_panel = children[1]
        self._open_due_date_picker(card, due_panel)

    def _begin_inline_title_edit(
        self,
        card: Card,
        frame: tk.Frame,
        title_frame: tk.Frame,
        title_label: tk.Label,
    ) -> None:
        if self._inline_edit_card_id is not None:
            return

        self._inline_edit_card_id = card.id
        title_label.pack_forget()

        entry = tk.Entry(
            title_frame,
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

        def finish(save: bool) -> None:
            if self._inline_edit_card_id != card.id:
                return

            if save:
                new_title = entry.get().strip()
                if not new_title:
                    messagebox.showwarning(
                        APP_TITLE,
                        "タイトルは空にできません。",
                        parent=self.root,
                    )
                    entry.focus_set()
                    return
                card.title = new_title
                card.touch()
                save_board(self.board)

            self._inline_edit_card_id = None
            self._inline_edit_finish = None
            self.refresh()

        self._inline_edit_finish = finish
        entry.bind("<Return>", lambda _e: finish(save=True))
        entry.bind("<Escape>", lambda _e: finish(save=False))
        entry.bind("<FocusOut>", lambda _e: finish(save=True))

    def _begin_inline_edit_for_card(self, card_id: str) -> None:
        frame = self._card_widgets.get(card_id)
        card = self.board.find_card(card_id)
        if frame is None or card is None:
            return

        children = frame.winfo_children()
        if not children or not isinstance(children[0], tk.Frame):
            return

        title_frame = children[0]
        label_children = title_frame.winfo_children()
        if not label_children or not isinstance(label_children[0], tk.Label):
            return

        title_label = label_children[0]
        self._begin_inline_title_edit(card, frame, title_frame, title_label)

    def _commit_inline_title_edit_if_any(self, save: bool = True) -> bool:
        """進行中のタイトル編集があれば確定またはキャンセルする."""
        if self._inline_edit_finish is None:
            return False
        self._inline_edit_finish(save)
        return True

    def _bind_card_interactions(
        self,
        frame: tk.Frame,
        card: Card,
        title_frame: tk.Frame,
        title_label: tk.Label,
        due_panel: tk.Frame,
        due_label: tk.Label,
        progress_canvas: tk.Canvas,
    ) -> None:
        def on_delete(_event: tk.Event) -> None:
            self._delete_card(card)

        def bind_drag(widget: tk.Misc) -> None:
            widget.bind(
                "<Button-1>",
                lambda e, c=card, f=frame: self._on_frame_press(e, c, f),
            )
            widget.bind("<B1-Motion>", lambda e, c=card, f=frame: self._on_drag(e, c, f))
            widget.bind("<ButtonRelease-1>", lambda _e, c=card: self._end_drag(c))

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

        def bind_title_interactions(widget: tk.Misc) -> None:
            widget.bind("<ButtonRelease-3>", on_delete)
            widget.bind(
                "<Button-1>",
                lambda e, c=card, f=frame: self._on_title_press(e, c, f),
            )
            widget.bind(
                "<B1-Motion>",
                lambda e, c=card, f=frame: self._on_title_drag(e, c, f),
            )
            widget.bind(
                "<ButtonRelease-1>",
                lambda e, c=card, f=frame: self._on_title_release(e, c, f),
            )
            widget.bind(
                "<Double-Button-1>",
                lambda _e, c=card, f=frame, tf=title_frame, label=title_label: (
                    self._on_title_double_click(c, f, tf, label)
                ),
            )

        def bind_due_interactions(widget: tk.Misc) -> None:
            widget.bind("<ButtonRelease-3>", on_delete)
            widget.bind(
                "<Button-1>",
                lambda e, c=card, f=frame: self._on_due_press(e, c, f),
            )
            widget.bind(
                "<B1-Motion>",
                lambda e, c=card, f=frame: self._on_due_drag(e, c, f),
            )
            widget.bind(
                "<ButtonRelease-1>",
                lambda e, c=card, f=frame: self._on_due_release(e, c, f),
            )
            widget.bind(
                "<Double-Button-1>",
                lambda _e, c=card, f=frame, panel=due_panel: self._on_due_double_click(
                    c, f, panel
                ),
            )

        def bind_progress_interactions(widget: tk.Misc) -> None:
            widget.bind("<ButtonRelease-3>", on_delete)
            widget.bind(
                "<Button-1>",
                lambda e, c=card, f=frame: self._on_progress_press(e, c, f),
            )
            widget.bind(
                "<B1-Motion>",
                lambda e, c=card, f=frame: self._on_progress_drag(e, c, f),
            )
            widget.bind(
                "<ButtonRelease-1>",
                lambda e, c=card, f=frame: self._on_progress_release(e, c, f),
            )

        frame.bind("<ButtonRelease-3>", on_delete)
        bind_drag(frame)
        bind_scroll(frame)

        bind_title_interactions(title_frame)
        bind_title_interactions(title_label)
        bind_scroll(title_frame)
        bind_scroll(title_label)
        bind_due_interactions(due_panel)
        bind_due_interactions(due_label)
        bind_scroll(due_panel)
        bind_scroll(due_label)
        bind_scroll(progress_canvas)
        bind_progress_interactions(progress_canvas)

    def _on_frame_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._cancel_due_date_picker_if_any():
            return
        if self._inline_edit_card_id == card.id:
            self._commit_inline_title_edit_if_any()
            return
        if self._commit_inline_title_edit_if_any():
            return
        self._start_drag(event, frame)

    def _on_title_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._cancel_due_date_picker_if_any():
            return
        if self._inline_edit_card_id == card.id:
            return
        if self._commit_inline_title_edit_if_any():
            return
        self._title_drag_moved = False
        self._start_drag(event, frame)

    def _on_title_drag(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        self._title_drag_moved = True
        self._on_drag(event, card, frame)

    def _on_title_release(self, _event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._title_drag_moved:
            self._end_drag(card)
        self._drag_state.pop(frame.winfo_id(), None)
        self._title_drag_moved = False

    def _on_title_double_click(
        self,
        card: Card,
        frame: tk.Frame,
        title_frame: tk.Frame,
        title_label: tk.Label,
    ) -> None:
        if self._cancel_due_date_picker_if_any():
            return
        if self._commit_inline_title_edit_if_any():
            return
        self._drag_state.pop(frame.winfo_id(), None)
        self._title_drag_moved = False
        self._begin_inline_title_edit(card, frame, title_frame, title_label)

    def _on_due_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if (
            self._due_date_picker_host is not None
            and self._due_date_edit_card_id == card.id
        ):
            if self._commit_inline_title_edit_if_any():
                return
            self._due_drag_moved = False
            self._start_drag(event, frame)
            return
        if self._cancel_due_date_picker_if_any():
            return
        if self._commit_inline_title_edit_if_any():
            return
        self._due_drag_moved = False
        self._start_drag(event, frame)

    def _on_due_drag(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        self._due_drag_moved = True
        self._on_drag(event, card, frame)

    def _on_due_release(self, _event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._due_drag_moved:
            self._end_drag(card)
        elif (
            self._due_date_picker_host is not None
            and self._due_date_edit_card_id == card.id
        ):
            self._schedule_due_panel_single_click_close(card.id)
        self._drag_state.pop(frame.winfo_id(), None)
        self._due_drag_moved = False

    def _on_due_double_click(self, card: Card, frame: tk.Frame, due_panel: tk.Frame) -> None:
        self._cancel_scheduled_due_panel_close()
        if (
            self._due_date_edit_card_id == card.id
            and self._due_date_picker_host is not None
        ):
            return
        if self._due_date_picker_host is not None:
            self._cancel_due_date_picker_if_any()
        if self._commit_inline_title_edit_if_any():
            return
        self._drag_state.pop(frame.winfo_id(), None)
        self._due_drag_moved = False
        self._open_due_date_picker(card, due_panel)

    def _on_progress_press(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._cancel_due_date_picker_if_any():
            return
        if self._commit_inline_title_edit_if_any():
            return
        self._progress_drag_moved = False
        self._start_drag(event, frame)

    def _on_progress_drag(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        self._progress_drag_moved = True
        self._on_drag(event, card, frame)

    def _on_progress_release(self, _event: tk.Event, card: Card, frame: tk.Frame) -> None:
        if self._progress_drag_moved:
            self._end_drag(card)
        self._drag_state.pop(frame.winfo_id(), None)
        self._progress_drag_moved = False

    def _card_position_near_add_button(self, stack_index: int) -> tuple[int, int]:
        """ツールバー「+ カード」付近に新規カードを置く座標を返す."""
        self.root.update_idletasks()
        self.toolbar.update_idletasks()
        toolbar_x = self.toolbar.winfo_x()
        toolbar_y = self.toolbar.winfo_y()
        toolbar_height = self.toolbar.winfo_height()
        base_x = toolbar_x + NEW_CARD_NEAR_TOOLBAR_OFFSET_X
        base_y = toolbar_y + toolbar_height + NEW_CARD_NEAR_TOOLBAR_OFFSET_Y
        return (
            base_x + (stack_index % 4) * NEW_CARD_STACK_OFFSET,
            base_y + (stack_index // 4) * NEW_CARD_STACK_OFFSET,
        )

    def _start_drag(self, event: tk.Event, frame: tk.Frame) -> None:
        self._drag_state[frame.winfo_id()] = (event.x, event.y)

    def _on_drag(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        origin = self._drag_state.get(frame.winfo_id())
        if origin is None:
            return
        new_x = frame.winfo_x() + event.x - origin[0]
        new_y = frame.winfo_y() + event.y - origin[1]
        frame.place(x=new_x, y=new_y)
        card.x = new_x
        card.y = new_y

    def _end_drag(self, card: Card) -> None:
        card.touch()
        save_board(self.board)

    def _add_card(self) -> None:
        self._cancel_due_date_picker_if_any()
        stack_index = len(self.board.cards)
        card_x, card_y = self._card_position_near_add_button(stack_index)
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
        self._cancel_due_date_picker_if_any()
        dialog = _SettingsDialog(
            self.root,
            confirm_delete=self.display_settings.confirm_delete,
            monitor_index=self.display_settings.monitor_index,
            monitors=self._monitors,
        )
        if dialog.result is None:
            return

        self._apply_settings(dialog.result)
        messagebox.showinfo(APP_TITLE, "設定を保存しました。", parent=self.root)

    def _apply_settings(self, settings: SettingsDialogResult) -> None:
        monitor_changed = settings.monitor_index != self.display_settings.monitor_index
        self.display_settings.confirm_delete = settings.confirm_delete
        self.display_settings.monitor_index = settings.monitor_index
        save_display_settings(self.display_settings)

        if monitor_changed:
            self._apply_overlay_mode()
            self.refresh()

    def _persist_and_refresh(self) -> None:
        save_board(self.board)
        self.refresh()

    def _on_close(self) -> None:
        save_board(self.board)
        save_display_settings(self.display_settings)
        self.root.destroy()


class _SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        confirm_delete: bool,
        monitor_index: int,
        monitors: list[Monitor],
    ) -> None:
        self._confirm_delete = confirm_delete
        self._monitor_index = monitor_index
        self._monitors = monitors
        self.result: SettingsDialogResult | None = None
        super().__init__(parent, title="設定")

    def body(self, master: tk.Misc) -> tk.Widget:
        ttk.Label(master, text="表示ディスプレイ").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
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
        self.monitor_menu.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        self.confirm_var = tk.BooleanVar(value=self._confirm_delete)
        ttk.Checkbutton(
            master,
            text="カード削除時に確認ダイアログを表示する",
            variable=self.confirm_var,
        ).grid(row=2, column=0, sticky=tk.W)
        master.columnconfigure(0, weight=1)
        return self.monitor_menu

    def apply(self) -> None:
        self.result = SettingsDialogResult(
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
